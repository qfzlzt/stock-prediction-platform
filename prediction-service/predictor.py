"""
predictor.py
────────────
加载三种生产模型（LGBM / LSTM / GNN）并对单只股票执行推理。

推理逻辑：
  LGBM  —— 取最新一行特征向量，直接 predict_proba。
  LSTM  —— 取最近 lookback 行（默认20行）构造时序张量，forward pass。
  GNN   —— 取所有股票最新一行，构造全图特征矩阵，forward pass，返回目标股票结果。
"""
from __future__ import annotations

from settings import MODEL_SRC_DIR, ARTIFACTS_DIR, INDUSTRY_EXCEL, database_config


import logging
import pickle
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import torch

# ─── 路径配置 ────────────────────────────────────────────────────────────────



# 将模型源码目录加入 sys.path，以便 import LSTM / GNN 模块
if str(MODEL_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(MODEL_SRC_DIR))

log = logging.getLogger(__name__)

# 预测标签文字（2 分类：0=看跌 1=看涨）
_LABEL_NAMES = {0: "看跌", 1: "看涨"}


# ══════════════════════════════════════════════════════════════════════════════
# 工具函数
# ══════════════════════════════════════════════════════════════════════════════
def _load_pkl(path: Path) -> Any:
    with open(path, "rb") as f:
        return pickle.load(f)


def _build_feature_row(row: pd.Series, feature_cols: list[str]) -> np.ndarray:
    """从 DataFrame 行提取特征向量，缺失列填 0。"""
    vec = np.zeros(len(feature_cols), dtype=np.float32)
    for i, col in enumerate(feature_cols):
        val = row.get(col)
        try:
            v = float(val)
            vec[i] = 0.0 if (v != v) else v      # NaN → 0
        except (TypeError, ValueError):
            vec[i] = 0.0
    return vec


def _build_sequence(df_sorted: pd.DataFrame,
                    feature_cols: list[str],
                    lookback: int) -> np.ndarray:
    """
    从按 trade_date 升序排列的 DataFrame 末尾取 lookback 行，
    构造形状 [lookback, n_features] 的数组。
    """
    seq = df_sorted.tail(lookback)
    X = np.zeros((lookback, len(feature_cols)), dtype=np.float32)
    for i, col in enumerate(feature_cols):
        if col in seq.columns:
            vals = seq[col].values.astype(float)
            X[:, i] = np.where(np.isnan(vals), 0.0, vals)
    return X


# ══════════════════════════════════════════════════════════════════════════════
# LGBM 推理
# ══════════════════════════════════════════════════════════════════════════════
def predict_lgbm(stock_code: str, feature_df: pd.DataFrame) -> dict:
    """
    参数
        stock_code  : 股票代码
        feature_df  : model_input_features 中该股票的历史特征 DataFrame
    返回
        dict，含预测方向、置信度、概率等
    """
    bundle       = _load_pkl(ARTIFACTS_DIR / "lgbm_prod.pkl")
    clf          = bundle["model"]
    feature_cols = bundle["feature_cols"]
    threshold    = float(bundle.get("threshold") or 0.5)
    n_classes    = int(bundle.get("n_classes", 2))
    horizon      = int(bundle.get("label_horizon", 5))

    df_sorted = feature_df.sort_values("trade_date")
    if df_sorted.empty:
        return {"error": f"{stock_code} 暂无特征数据，请先运行 build_features.py"}

    row   = df_sorted.iloc[-1]
    X_vec = _build_feature_row(row, feature_cols).reshape(1, -1)

    proba = clf.predict_proba(X_vec)[0]
    if n_classes == 2:
        pred_label = int(proba[1] >= threshold)
    else:
        pred_label = int(np.argmax(proba))

    return {
        "model":        "LightGBM",
        "stock_code":   stock_code,
        "trade_date":   str(row["trade_date"])[:10],
        "pred_label":   pred_label,
        "label_name":   _LABEL_NAMES.get(pred_label, str(pred_label)),
        "confidence":   round(float(max(proba)) * 100, 2),
        "proba_up":     round(float(proba[1]) * 100, 2) if n_classes == 2 else None,
        "proba_down":   round(float(proba[0]) * 100, 2) if n_classes == 2 else None,
        "threshold_pct": round(threshold * 100, 1),
        "horizon_days": horizon,
        "desc": f"基于最新日频特征，预测未来 {horizon} 个交易日走势",
    }


# ══════════════════════════════════════════════════════════════════════════════
# LSTM 推理
# ══════════════════════════════════════════════════════════════════════════════
def predict_lstm(stock_code: str, feature_df: pd.DataFrame) -> dict:
    """
    参数同 predict_lgbm。
    需要至少 lookback（默认20）行的历史数据。
    """
    from src.train_lstm import LSTMClassifier

    meta         = _load_pkl(ARTIFACTS_DIR / "lstm_prod_meta.pkl")
    feature_cols = meta["feature_cols"]
    lookback     = int(meta.get("lookback", 20))
    hidden_size  = int(meta.get("hidden_size", 64))
    num_layers   = int(meta.get("num_layers", 2))
    dropout      = float(meta.get("dropout", 0.2))
    n_classes    = int(meta.get("n_classes", 2))
    threshold    = float(meta.get("threshold") or 0.5)
    horizon      = int(meta.get("label_horizon", 5))

    df_sorted = feature_df.sort_values("trade_date")
    if len(df_sorted) < lookback:
        return {
            "error": (
                f"{stock_code} 历史数据仅 {len(df_sorted)} 行，"
                f"LSTM 需要至少 {lookback} 行，请先运行 build_features.py"
            )
        }

    X = _build_sequence(df_sorted, feature_cols, lookback)   # [lookback, F]

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = LSTMClassifier(
        in_dim     = len(feature_cols),
        hidden     = hidden_size,
        num_layers = num_layers,
        dropout    = 0.0,        # 推理时关闭 dropout
        num_classes= n_classes,
    ).to(device)

    weights_path = ARTIFACTS_DIR / "lstm_prod.pt"
    state_dict   = torch.load(weights_path, map_location=device, weights_only=True)
    model.load_state_dict(state_dict)
    model.eval()

    temperature = float(meta.get("temperature") or 1.0)

    x_tensor = torch.tensor(X, dtype=torch.float32).unsqueeze(0).to(device)  # [1, T, F]
    with torch.no_grad():
        logits = model(x_tensor) / temperature
        proba  = torch.softmax(logits, dim=1).cpu().numpy()[0]

    if n_classes == 2:
        pred_label = int(proba[1] >= threshold)
    else:
        pred_label = int(np.argmax(proba))

    latest_date = str(df_sorted.iloc[-1]["trade_date"])[:10]

    return {
        "model":         "LSTM",
        "stock_code":    stock_code,
        "trade_date":    latest_date,
        "pred_label":    pred_label,
        "label_name":    _LABEL_NAMES.get(pred_label, str(pred_label)),
        "confidence":    round(float(max(proba)) * 100, 2),
        "proba_up":      round(float(proba[1]) * 100, 2) if n_classes == 2 else None,
        "proba_down":    round(float(proba[0]) * 100, 2) if n_classes == 2 else None,
        "threshold_pct": round(threshold * 100, 1),
        "horizon_days":  horizon,
        "sequence_len":  lookback,
        "desc": f"基于最近 {lookback} 个交易日时序特征，预测未来 {horizon} 个交易日走势",
    }


# ══════════════════════════════════════════════════════════════════════════════
# GNN 推理
# ══════════════════════════════════════════════════════════════════════════════
def predict_gnn(stock_code: str, all_stocks_df: pd.DataFrame) -> dict:
    """
    参数
        stock_code    : 目标股票代码
        all_stocks_df : model_input_features 中【所有股票】的最新一行特征
    返回
        dict，含预测方向、置信度、概率及关系权重
    """
    from src.train_gnn import HeteroRegimeGNN

    meta         = _load_pkl(ARTIFACTS_DIR / "gnn_prod_meta.pkl")
    feature_cols = meta["feature_cols"]
    regime_cols  = meta.get("regime_cols",
                            ["mkt_ret_1", "mkt_ret_5", "mkt_vol_20", "mkt_drawdown_60"])
    stocks       = meta["stocks"]            # 训练时的股票列表
    rel_adjs     = meta["adj_matrices"]      # [n_rel, n_stocks, n_stocks]
    hidden_size  = int(meta.get("hidden_size", 128))
    n_classes    = int(meta.get("n_classes", 2))
    threshold    = float(meta.get("threshold") or 0.5)
    horizon      = int(meta.get("label_horizon", 5))
    use_gate     = bool(meta.get("use_gate", False))
    mlp_layers   = int(meta.get("mlp_layers", 0))
    mlp_hidden   = int(meta.get("mlp_hidden", hidden_size))
    fixed_rel_w  = meta.get("fixed_rel_w")   # np.ndarray [n_rel] 或 None
    n_rel        = rel_adjs.shape[0]
    n_stocks     = len(stocks)

    # 统一代码格式：训练时用纯数字（如 688082），前端传来可能带后缀（688082.SH）
    stock_code_lookup = stock_code.split(".")[0]
    if stock_code_lookup not in stocks:
        return {
            "error": (
                f"{stock_code} 不在 GNN 训练股票列表中，"
                f"GNN 只能预测训练集内的 {n_stocks} 只股票：{', '.join(stocks)}"
            )
        }

    stock_idx = stocks.index(stock_code_lookup)

    # ── 按股票取最新一行特征 ───────────────────────────────
    latest = (
        all_stocks_df
        .sort_values("trade_date")
        .groupby("stock_code")
        .last()
        .reset_index()
    )
    # 纯数字代码（去掉 .SH）
    latest["_code_short"] = latest["stock_code"].str.split(".").str[0]

    # ── 重建训练时存在但 model_input_features 缺失的列 ────
    # 1. open（训练时叫 open，DB 存为 open_price）
    if "open" not in latest.columns and "open_price" in latest.columns:
        latest["open"] = latest["open_price"]

    # 2. ret_1_raw（用 pct_chg / 100 近似）
    if "ret_1_raw" not in latest.columns and "pct_chg" in latest.columns:
        latest["ret_1_raw"] = latest["pct_chg"] / 100.0

    # 3. stock 哑变量（每只训练股票对应一列）
    for s in stocks:
        col = f"stock_{s}"
        if col not in latest.columns:
            latest[col] = (latest["_code_short"] == s).astype(float)

    # 4. 行业哑变量（从 industry_l3 还原，使用 feature_cols 里的 ind_ 前缀列）
    ind_cols_needed = [c for c in feature_cols if c.startswith("ind_") and c not in latest.columns]
    if ind_cols_needed and "industry_l3" in latest.columns:
        for ind_col in ind_cols_needed:
            # ind_col 格式: ind_<行业名>，industry_l3 值就是行业名
            ind_name = ind_col[4:]   # 去掉 "ind_" 前缀
            if ind_name == "nan":
                latest[ind_col] = latest["industry_l3"].isna().astype(float)
            else:
                latest[ind_col] = (latest["industry_l3"] == ind_name).astype(float)

    # 5. 跨截面 Alpha 因子（超额收益 = 个股收益 - 截面均值）
    for ret_col, alpha_col in [('ret_1_calc','alpha_1'),
                                ('ret_5',     'alpha_5'),
                                ('ret_20',    'alpha_20')]:
        if alpha_col not in latest.columns and ret_col in latest.columns:
            cross_mean = latest[ret_col].mean()
            latest[alpha_col] = latest[ret_col] - cross_mean

    # 6. 市值权重（个股市值 / 全部样本市值之和）
    if 'star_close_total_w' not in latest.columns and 'total_mv' in latest.columns:
        total_mv_sum = latest['total_mv'].sum()
        latest['star_close_total_w'] = (
            latest['total_mv'] / total_mv_sum if total_mv_sum > 0 else 0.0
        )

    # 7. 行业收益均值 / 标准差（按 industry_l3 分组）
    if 'ind_ret_mean' not in latest.columns and \
       'ret_1_calc' in latest.columns and 'industry_l3' in latest.columns:
        ind_stats = latest.groupby('industry_l3')['ret_1_calc'].agg(['mean','std'])
        latest['ind_ret_mean'] = latest['industry_l3'].map(ind_stats['mean']).fillna(0.0)
        latest['ind_ret_std']  = latest['industry_l3'].map(ind_stats['std']).fillna(0.0)

    # 8. 其余仍缺失的列置 0
    for col in feature_cols:
        if col not in latest.columns:
            latest[col] = 0.0

    # ── 构造特征矩阵 [n_stocks, n_features] ──────────────
    X = np.zeros((n_stocks, len(feature_cols)), dtype=np.float32)
    for i, s in enumerate(stocks):
        row_df = latest[latest["_code_short"] == s]
        if row_df.empty:
            continue
        X[i] = _build_feature_row(row_df.iloc[0], feature_cols)

    # ── 构造 regime（市场情境）向量 [regime_dim] ──────────
    regime_vals = []
    for col in regime_cols:
        if col in latest.columns:
            regime_vals.append(float(latest[col].mean()))
        else:
            regime_vals.append(0.0)
    regime = np.array(regime_vals, dtype=np.float32)

    # ── 加载模型 ──────────────────────────────────────────
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = HeteroRegimeGNN(
        in_dim      = len(feature_cols),
        hidden      = hidden_size,
        n_rel       = n_rel,
        regime_dim  = len(regime_cols),
        dropout     = 0.0,
        num_classes = n_classes,
        use_gate    = use_gate,
        fixed_rel_w = fixed_rel_w,   # 传入训练时的固定权重 [0.4, 0.3, 0.3]
        mlp_layers  = mlp_layers,
        mlp_hidden  = mlp_hidden,
    ).to(device)

    weights_path = ARTIFACTS_DIR / "gnn_prod.pt"
    state_dict   = torch.load(weights_path, map_location=device, weights_only=True)
    model.load_state_dict(state_dict)
    model.eval()

    # ── Tensors ───────────────────────────────────────────
    x_tensor      = torch.tensor(X,       dtype=torch.float32, device=device)
    adjs_tensor   = torch.tensor(rel_adjs,dtype=torch.float32, device=device)
    regime_tensor = torch.tensor(regime,  dtype=torch.float32, device=device)   # [regime_dim]，不加 batch 维度

    temperature = float(meta.get("temperature") or 1.0)

    # ── Forward pass ──────────────────────────────────────
    with torch.no_grad():
        logits, rel_w = model(x_tensor, adjs_tensor, regime_tensor)
        proba = torch.softmax(logits / temperature, dim=1).cpu().numpy()

    stock_proba = proba[stock_idx]

    # ── 跨截面百分位排名（GNN 核心：相对强弱，而非绝对概率）─────
    # GNN 输出的绝对概率差异很小（~0.5%），真正有意义的是该股在全图中的相对排名。
    # 百分位排名：0% = 全图最弱，100% = 全图最强
    all_p_up = proba[:, 1] if n_classes == 2 else None
    if all_p_up is not None and n_stocks > 1:
        # 计算目标股票在所有股票中的排名百分位
        rank = float(np.sum(all_p_up < all_p_up[stock_idx]))   # 比它弱的股票数量
        percentile = rank / (n_stocks - 1) * 100               # 0~100
        # 用百分位作为"置信度"：>50 看涨，<50 看跌
        pred_label = 1 if percentile >= 50.0 else 0
        # 置信度 = 百分位离中点的距离映射到 50%~100% 区间
        # percentile=100 → confidence=100%, percentile=50 → confidence=50%, percentile=0 → confidence=100%
        confidence = 50.0 + abs(percentile - 50.0)
        proba_up_pct   = round(percentile, 1)          # 前端显示"图内排名百分位"
        proba_down_pct = round(100 - percentile, 1)
    else:
        percentile  = float(stock_proba[1]) * 100 if n_classes == 2 else 50.0
        pred_label  = int(stock_proba[1] >= threshold) if n_classes == 2 else int(np.argmax(stock_proba))
        confidence  = round(float(max(stock_proba)) * 100, 2)
        proba_up_pct   = round(float(stock_proba[1]) * 100, 2) if n_classes == 2 else None
        proba_down_pct = round(float(stock_proba[0]) * 100, 2) if n_classes == 2 else None

    # ── 关系权重 ──────────────────────────────────────────
    rel_names  = meta.get("relation_names", [])
    rel_weights: dict = {}
    if rel_w is not None and len(rel_names):
        rel_w_1d = rel_w.squeeze().cpu()   # 确保是 1D [n_rel]
        for k, name in enumerate(rel_names):
            if k < rel_w_1d.numel():
                rel_weights[name] = round(float(rel_w_1d[k].item()), 4)

    target_rows = latest[latest["_code_short"] == stock_code_lookup]
    latest_date = str(target_rows.iloc[0]["trade_date"])[:10] if not target_rows.empty else "N/A"

    return {
        "model":          "GNN",
        "stock_code":     stock_code,
        "trade_date":     latest_date,
        "pred_label":     pred_label,
        "label_name":     _LABEL_NAMES.get(pred_label, str(pred_label)),
        "confidence":     round(confidence, 2),
        "proba_up":       proba_up_pct,
        "proba_down":     proba_down_pct,
        "percentile":     round(percentile, 1),       # 图内排名百分位（额外字段）
        "threshold_pct":  50.0,                        # 基于中位数排名
        "horizon_days":   horizon,
        "n_stocks_graph": n_stocks,
        "relation_weights": rel_weights,
        "desc": (
            f"基于 {n_stocks} 只股票构成的异质图，"
            f"该股图内排名前 {round(100 - percentile, 1)}%，"
            f"预测未来 {horizon} 个交易日走势"
        ),
    }
