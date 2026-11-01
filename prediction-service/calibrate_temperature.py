"""
calibrate_temperature.py
────────────────────────
对 LSTM 和 GNN 做 Temperature Scaling 后处理校准。

原理：
  calibrated_proba = softmax(logits / T)
  T > 1 → 概率更保守（接近 0.5）
  T < 1 → 概率更极端（接近 0 或 1）

步骤：
  1. 从 model_input_features 读取验证期数据（2024-07-01 ~ 2025-12-31）
  2. 从 daily_market_data 计算 5 日前向收益，生成伪标签
  3. 对每个股票/每个日期跑推理，收集 logits
  4. scipy 最小化 NLL 找最优 T
  5. 将 T 写入对应 meta pkl

用法：
  python calibrate_temperature.py
"""
from __future__ import annotations

from settings import MODEL_SRC_DIR, ARTIFACTS_DIR, INDUSTRY_EXCEL, database_config


import logging
import pickle
import sys
from pathlib import Path

import numpy as np
import pymysql
import pymysql.cursors
import torch
from scipy.optimize import minimize_scalar

logging.basicConfig(level=logging.INFO, format="%(levelname)-8s %(message)s")
log = logging.getLogger(__name__)

# ─── 路径配置 ────────────────────────────────────────────────────────


if str(MODEL_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(MODEL_SRC_DIR))

DB_CONFIG = database_config()

# 验证期：使用 model_input_features 中实际有数据的范围
# 末尾留 HORIZON 个交易日用于计算前向收益，因此 END 向前推约 7 天
CALIB_START = "2026-01-26"
CALIB_END   = "2026-03-18"   # 留出最后 ~5 个交易日计算标签
HORIZON     = 5   # 与训练 label_horizon 一致


# ══════════════════════════════════════════════════════════════════════
# 工具函数
# ══════════════════════════════════════════════════════════════════════
def _get_conn():
    return pymysql.connect(**DB_CONFIG)


def _query(conn, sql, params=()):
    with conn.cursor() as cur:
        cur.execute(sql, params)
        return cur.fetchall()


def _nll_loss(T: float, logits: np.ndarray, labels: np.ndarray) -> float:
    """给定温度 T，计算 NLL（负对数似然）。"""
    scaled = logits / max(T, 1e-6)
    # softmax
    e = np.exp(scaled - scaled.max(axis=1, keepdims=True))
    proba = e / e.sum(axis=1, keepdims=True)
    proba = np.clip(proba, 1e-7, 1 - 1e-7)
    n = len(labels)
    nll = -np.sum(np.log(proba[np.arange(n), labels])) / n
    return float(nll)


def find_temperature(logits: np.ndarray, labels: np.ndarray) -> float:
    """在 [0.1, 10.0] 范围内搜索最优温度 T。"""
    result = minimize_scalar(
        lambda T: _nll_loss(T, logits, labels),
        bounds=(0.1, 10.0),
        method="bounded",
    )
    return float(result.x)


# ══════════════════════════════════════════════════════════════════════
# 读取数据
# ══════════════════════════════════════════════════════════════════════
def load_features(conn, stocks: list[str]) -> dict:
    """
    返回 {stock_code: DataFrame(sorted by trade_date)}，
    只取验证期及其前 lookback 天所需的数据。
    """
    from src.train_lstm import LSTMClassifier   # 先导入检查路径
    meta_lstm = pickle.load(open(ARTIFACTS_DIR / "lstm_prod_meta.pkl", "rb"))
    lookback = int(meta_lstm.get("lookback", 20))

    result = {}
    for s in stocks:
        rows = _query(conn,
            """
            SELECT trade_date, stock_code,
                   pe AS pe_ttm, pb AS pb_mrq, pct_chg,
                   ev AS total_mv, mkt_cap_float AS float_mv,
                   total_shares, share_issuing_mkt AS float_shares,
                   maxup AS limit_up, maxdown AS limit_down, chg,
                   vwap AS avg_price, volume, amt AS amount,
                   turn AS turnover, vol_ratio AS volume_ratio,
                   high, low, `open` AS open_price, close,
                   pre_close AS prev_close, adjfactor AS adj_factor
            FROM daily_market_data
            WHERE stock_code = %s
              AND trade_date >= DATE_SUB(%s, INTERVAL %s DAY)
              AND trade_date <= %s
            ORDER BY trade_date ASC
            """,
            (s, CALIB_START, lookback * 3, CALIB_END),
        )
        if rows:
            import pandas as pd
            result[s] = pd.DataFrame(rows)
    return result


def load_calib_features_from_mif(conn) -> "pd.DataFrame":
    """从 model_input_features 读验证期特征。"""
    import pandas as pd
    rows = _query(conn,
        """
        SELECT * FROM model_input_features
        WHERE trade_date BETWEEN %s AND %s
        ORDER BY stock_code, trade_date
        """,
        (CALIB_START, CALIB_END),
    )
    return pd.DataFrame(rows) if rows else pd.DataFrame()


def load_forward_returns(conn, stocks: list[str]) -> "pd.DataFrame":
    """
    计算验证期内每只股票每天的 HORIZON 日前向收益，生成 label (0/1)。
    label=1 如果 5 日收益 > 截面中位数。
    """
    import pandas as pd
    all_rows = []
    for s in stocks:
        rows = _query(conn,
            """
            SELECT trade_date, close
            FROM daily_market_data
            WHERE stock_code = %s
              AND trade_date BETWEEN DATE_SUB(%s, INTERVAL 5 DAY) AND DATE_ADD(%s, INTERVAL 10 DAY)
            ORDER BY trade_date ASC
            """,
            (s, CALIB_START, CALIB_END),
        )
        if rows:
            df = pd.DataFrame(rows)
            df["stock_code"] = s
            all_rows.append(df)
    if not all_rows:
        return pd.DataFrame()

    df_all = pd.concat(all_rows, ignore_index=True)
    df_all["trade_date"] = pd.to_datetime(df_all["trade_date"])
    df_all["close"] = df_all["close"].astype(float)
    df_all = df_all.sort_values(["stock_code", "trade_date"])

    # 计算前向收益
    df_all["fwd_ret"] = (
        df_all.groupby("stock_code")["close"]
        .transform(lambda x: x.shift(-HORIZON) / x - 1)
    )
    df_all = df_all.dropna(subset=["fwd_ret"])

    # 截面中位数分标签
    df_all["label"] = df_all.groupby("trade_date")["fwd_ret"].transform(
        lambda x: (x > x.median()).astype(int)
    )
    df_all["trade_date"] = df_all["trade_date"].dt.strftime("%Y-%m-%d")
    return df_all[["trade_date", "stock_code", "fwd_ret", "label"]]


# ══════════════════════════════════════════════════════════════════════
# LSTM 校准
# ══════════════════════════════════════════════════════════════════════
def calibrate_lstm(conn):
    from src.train_lstm import LSTMClassifier
    import pandas as pd

    meta = pickle.load(open(ARTIFACTS_DIR / "lstm_prod_meta.pkl", "rb"))
    feature_cols = meta["feature_cols"]
    lookback     = int(meta.get("lookback", 20))
    hidden_size  = int(meta.get("hidden_size", 64))
    num_layers   = int(meta.get("num_layers", 2))
    n_classes    = int(meta.get("n_classes", 2))

    device = torch.device("cpu")
    model = LSTMClassifier(
        in_dim=len(feature_cols), hidden=hidden_size,
        num_layers=num_layers, dropout=0.0, num_classes=n_classes,
    ).to(device)
    model.load_state_dict(torch.load(
        ARTIFACTS_DIR / "lstm_prod.pt", map_location=device, weights_only=True
    ))
    model.eval()

    # 读取 model_input_features 验证期数据
    log.info("读取 model_input_features 验证期数据...")
    feat_df = load_calib_features_from_mif(conn)
    if feat_df.empty:
        log.warning("验证期特征为空，跳过 LSTM 校准")
        return

    feat_df["trade_date"] = feat_df["trade_date"].astype(str).str[:10]
    feat_df = feat_df.sort_values(["stock_code", "trade_date"])

    # 读取标签
    stocks = feat_df["stock_code"].str.split(".").str[0].unique().tolist()
    stocks_full = feat_df["stock_code"].unique().tolist()
    log.info(f"读取前向收益标签，共 {len(stocks_full)} 只股票...")
    label_df = load_forward_returns(conn, stocks_full)
    if label_df.empty:
        log.warning("无法获取前向收益，跳过 LSTM 校准")
        return

    # 逐股票逐日期推理
    all_logits, all_labels = [], []
    dates = sorted(feat_df["trade_date"].unique())
    n_ok = 0

    for stock_code in stocks_full:
        stk_feat = feat_df[feat_df["stock_code"] == stock_code].sort_values("trade_date")
        stk_lbl  = label_df[label_df["stock_code"] == stock_code].set_index("trade_date")

        for dt in dates:
            if dt not in stk_lbl.index:
                continue
            # 取 dt 之前（含）的最近 lookback 行
            hist = stk_feat[stk_feat["trade_date"] <= dt].tail(lookback)
            if len(hist) < lookback:
                continue

            X = np.zeros((lookback, len(feature_cols)), dtype=np.float32)
            for i, col in enumerate(feature_cols):
                if col in hist.columns:
                    vals = hist[col].values.astype(float)
                    X[:, i] = np.where(np.isnan(vals), 0.0, vals)

            x_t = torch.tensor(X).unsqueeze(0)   # [1, T, F]
            with torch.no_grad():
                logits = model(x_t).cpu().numpy()[0]   # [n_classes]
            all_logits.append(logits)
            all_labels.append(int(stk_lbl.loc[dt, "label"]))
            n_ok += 1

    if n_ok < 50:
        log.warning(f"有效样本过少（{n_ok}），跳过 LSTM 校准")
        return

    logits_arr = np.array(all_logits)
    labels_arr = np.array(all_labels)
    log.info(f"LSTM 校准样本数：{n_ok}，正例比例：{labels_arr.mean():.2%}")

    T = find_temperature(logits_arr, labels_arr)
    log.info(f"LSTM 最优温度 T = {T:.4f}")

    # 写入 meta
    meta["temperature"] = T
    with open(ARTIFACTS_DIR / "lstm_prod_meta.pkl", "wb") as f:
        pickle.dump(meta, f)
    log.info("LSTM meta 已更新（temperature 字段）")


# ══════════════════════════════════════════════════════════════════════
# GNN 校准
# ══════════════════════════════════════════════════════════════════════
def calibrate_gnn(conn):
    from src.train_gnn import HeteroRegimeGNN
    import pandas as pd

    meta = pickle.load(open(ARTIFACTS_DIR / "gnn_prod_meta.pkl", "rb"))
    feature_cols = meta["feature_cols"]
    regime_cols  = meta.get("regime_cols", ["mkt_ret_1","mkt_ret_5","mkt_vol_20","mkt_drawdown_60"])
    stocks       = meta["stocks"]
    rel_adjs     = meta["adj_matrices"]
    hidden_size  = int(meta.get("hidden_size", 128))
    n_classes    = int(meta.get("n_classes", 2))
    use_gate     = bool(meta.get("use_gate", False))
    mlp_layers   = int(meta.get("mlp_layers", 0))
    mlp_hidden   = int(meta.get("mlp_hidden", hidden_size))
    fixed_rel_w  = meta.get("fixed_rel_w")

    device = torch.device("cpu")
    model = HeteroRegimeGNN(
        in_dim=len(feature_cols), hidden=hidden_size,
        n_rel=rel_adjs.shape[0], regime_dim=len(regime_cols),
        dropout=0.0, num_classes=n_classes, use_gate=use_gate,
        fixed_rel_w=fixed_rel_w, mlp_layers=mlp_layers, mlp_hidden=mlp_hidden,
    ).to(device)
    model.load_state_dict(torch.load(
        ARTIFACTS_DIR / "gnn_prod.pt", map_location=device, weights_only=True
    ))
    model.eval()

    adjs_tensor = torch.tensor(rel_adjs, dtype=torch.float32)

    log.info("读取 model_input_features 验证期数据（GNN）...")
    feat_df = load_calib_features_from_mif(conn)
    if feat_df.empty:
        log.warning("验证期特征为空，跳过 GNN 校准")
        return

    feat_df["trade_date"] = feat_df["trade_date"].astype(str).str[:10]
    feat_df["_code_short"] = feat_df["stock_code"].str.split(".").str[0]

    # 读取标签（只对训练股票）
    stocks_full = feat_df["stock_code"].unique().tolist()
    log.info(f"读取前向收益标签（GNN），共 {len(stocks_full)} 只股票...")
    label_df = load_forward_returns(conn, stocks_full)
    if label_df.empty:
        log.warning("无法获取前向收益，跳过 GNN 校准")
        return
    label_df["_code_short"] = label_df["stock_code"].str.split(".").str[0]

    # 逐日期推理全图
    all_logits, all_labels = [], []
    dates = sorted(feat_df["trade_date"].unique())
    n_ok = 0

    for dt in dates:
        day_feat = feat_df[feat_df["trade_date"] == dt]

        # 构造全图特征矩阵 [n_stocks, n_features]
        X = np.zeros((len(stocks), len(feature_cols)), dtype=np.float32)
        for i, s in enumerate(stocks):
            row_df = day_feat[day_feat["_code_short"] == s]
            if row_df.empty:
                continue
            row = row_df.iloc[0]
            for j, col in enumerate(feature_cols):
                try:
                    v = float(row.get(col, 0))
                    X[i, j] = 0.0 if (v != v) else v
                except (TypeError, ValueError):
                    pass

        # regime
        regime_vals = []
        for col in regime_cols:
            if col in day_feat.columns and not day_feat[col].isna().all():
                regime_vals.append(float(day_feat[col].mean()))
            else:
                regime_vals.append(0.0)
        regime = torch.tensor(regime_vals, dtype=torch.float32)

        x_tensor = torch.tensor(X, dtype=torch.float32)
        with torch.no_grad():
            logits_all, _ = model(x_tensor, adjs_tensor, regime)
            logits_np = logits_all.cpu().numpy()   # [n_stocks, n_classes]

        # 对每只训练股票收集 logits + label
        day_lbl = label_df[label_df["trade_date"] == dt].set_index("_code_short")
        for i, s in enumerate(stocks):
            if s not in day_lbl.index:
                continue
            all_logits.append(logits_np[i])
            all_labels.append(int(day_lbl.loc[s, "label"]))
            n_ok += 1

    if n_ok < 50:
        log.warning(f"有效样本过少（{n_ok}），跳过 GNN 校准")
        return

    logits_arr = np.array(all_logits)
    labels_arr = np.array(all_labels)
    log.info(f"GNN 校准样本数：{n_ok}，正例比例：{labels_arr.mean():.2%}")

    T = find_temperature(logits_arr, labels_arr)
    log.info(f"GNN 最优温度 T = {T:.4f}")

    meta["temperature"] = T
    with open(ARTIFACTS_DIR / "gnn_prod_meta.pkl", "wb") as f:
        pickle.dump(meta, f)
    log.info("GNN meta 已更新（temperature 字段）")


# ══════════════════════════════════════════════════════════════════════
# 主程序
# ══════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    conn = _get_conn()
    try:
        log.info("=== 开始 LSTM Temperature Scaling 校准 ===")
        calibrate_lstm(conn)
        log.info("")
        log.info("=== 开始 GNN Temperature Scaling 校准 ===")
        calibrate_gnn(conn)
    finally:
        conn.close()
    log.info("校准完成！")
