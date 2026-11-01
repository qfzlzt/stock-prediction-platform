"""
build_features.py
─────────────────
从数据库读取日频数据，计算技术指标、市场特征，
合并行业分类后写入 model_input_features 表。

用法：
    python build_features.py                  # 处理所有正常交易股票
    python build_features.py --stock 688001.SH  # 只处理单只股票
"""
from __future__ import annotations

from settings import MODEL_SRC_DIR, ARTIFACTS_DIR, INDUSTRY_EXCEL, database_config


import argparse
import logging
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pymysql
import pymysql.cursors

# ─── 数据库连接配置（请修改密码）────────────────────────────────
DB_CONFIG = database_config()

# 行业分类 Excel 路径


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    stream=sys.stdout,
)
log = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════════════════════════
# RSI 辅助函数
# ══════════════════════════════════════════════════════════════════════════════
def _rsi(series: pd.Series, period: int) -> pd.Series:
    delta    = series.diff()
    gain     = delta.clip(lower=0.0)
    loss     = -delta.clip(upper=0.0)
    avg_gain = gain.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()
    avg_loss = loss.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()
    rs  = avg_gain / avg_loss.replace(0, np.nan)
    out = 100 - (100 / (1 + rs))
    out = out.where(avg_loss.notna())
    out = out.mask((avg_loss == 0) & (avg_gain > 0), 100)
    out = out.mask((avg_loss == 0) & (avg_gain == 0), 50)
    return out


# ══════════════════════════════════════════════════════════════════════════════
# 技术指标计算（与 add_technical_indicators 3.py 保持完全一致）
# ══════════════════════════════════════════════════════════════════════════════
def compute_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    输入：含 close / high / low / prev_close / volume / open_price 的 DataFrame，
          按 trade_date 升序排列，仅限单只股票。
    输出：追加所有技术指标列后的 DataFrame。
    """
    df = df.copy().sort_values("trade_date").reset_index(drop=True)

    close      = df["close"].astype(float)
    high       = df["high"].astype(float)
    low        = df["low"].astype(float)
    prev_close = df["prev_close"].astype(float)
    volume     = df["volume"].astype(float)

    # ── 收益率 ────────────────────────────────────────────
    df["ret_1_calc"] = close.div(prev_close.replace(0, np.nan)).sub(1.0)
    df["ret_5"]      = close.pct_change(5)
    df["ret_20"]     = close.pct_change(20)
    df["ret_60"]     = close.pct_change(60)

    # ── RSI ──────────────────────────────────────────────
    df["rsi_6"]  = _rsi(close, 6)
    df["rsi_14"] = _rsi(close, 14)

    # ── MACD (12, 26, 9) ─────────────────────────────────
    ema12 = close.ewm(span=12, adjust=False, min_periods=12).mean()
    ema26 = close.ewm(span=26, adjust=False, min_periods=26).mean()
    df["macd"]        = ema12 - ema26
    df["macd_signal"] = df["macd"].ewm(span=9, adjust=False, min_periods=9).mean()
    df["macd_hist"]   = df["macd"] - df["macd_signal"]

    # ── 布林带 (20) ───────────────────────────────────────
    df["bb_mid"]   = close.rolling(20, min_periods=20).mean()
    df["bb_std"]   = close.rolling(20, min_periods=20).std(ddof=0)
    df["bb_upper"] = df["bb_mid"] + 2 * df["bb_std"]
    df["bb_lower"] = df["bb_mid"] - 2 * df["bb_std"]
    df["bb_width"] = (df["bb_upper"] - df["bb_lower"]) / df["bb_mid"].replace(0, np.nan)
    band_range     = (df["bb_upper"] - df["bb_lower"]).replace(0, np.nan)
    df["bb_pos"]   = (close - df["bb_lower"]) / band_range

    # ── TR / ATR ──────────────────────────────────────────
    tr1        = high - low
    tr2        = (high - prev_close).abs()
    tr3        = (low  - prev_close).abs()
    df["tr"]      = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    df["atr_14"]  = df["tr"].ewm(alpha=1 / 14, adjust=False, min_periods=14).mean()
    df["atr_pct"] = df["atr_14"] / close.replace(0, np.nan)

    # ── 波动率 ────────────────────────────────────────────
    df["vol_20"] = df["ret_1_calc"].rolling(20, min_periods=20).std(ddof=0)
    df["vol_60"] = df["ret_1_calc"].rolling(60, min_periods=60).std(ddof=0)

    # ── 均线 ──────────────────────────────────────────────
    df["ma5"]     = close.rolling(5,  min_periods=5).mean()
    df["ma10"]    = close.rolling(10, min_periods=10).mean()
    df["ma20"]    = close.rolling(20, min_periods=20).mean()
    df["ma60"]    = close.rolling(60, min_periods=60).mean()
    df["ma5_dev"] = (close - df["ma5"])  / df["ma5"].replace(0, np.nan)
    df["ma20_dev"]= (close - df["ma20"]) / df["ma20"].replace(0, np.nan)

    # ── 成交量 ────────────────────────────────────────────
    df["volume_ma5"]  = volume.rolling(5,  min_periods=5).mean()
    df["volume_ma20"] = volume.rolling(20, min_periods=20).mean()
    df["vol_surge"]   = volume / df["volume_ma20"].replace(0, np.nan)

    # ── 价量相关（20日滚动） ─────────────────────────────
    vol_chg          = volume.pct_change(fill_method=None)
    df["price_vol_corr"] = df["ret_1_calc"].rolling(20, min_periods=20).corr(vol_chg)

    return df


# ══════════════════════════════════════════════════════════════════════════════
# 市场特征计算（来自 kcb_close_daily）
# ══════════════════════════════════════════════════════════════════════════════
def compute_market_features(mkt: pd.DataFrame) -> pd.DataFrame:
    """
    输入：kcb_close_daily 数据，含 trade_date / close_total_weighted。
    输出：含 mkt_ret_1/5/20, mkt_vol_20, mkt_drawdown_60 的 DataFrame。
    """
    mkt = mkt.copy().sort_values("trade_date").reset_index(drop=True)
    idx = mkt["close_total_weighted"].astype(float)

    mkt["mkt_ret_1"]       = idx.pct_change(1)
    mkt["mkt_ret_5"]       = idx.pct_change(5)
    mkt["mkt_ret_20"]      = idx.pct_change(20)
    mkt["mkt_vol_20"]      = mkt["mkt_ret_1"].rolling(20, min_periods=20).std(ddof=0)
    rolling_max            = idx.rolling(60, min_periods=1).max()
    mkt["mkt_drawdown_60"] = (idx - rolling_max) / rolling_max.replace(0, np.nan)

    return mkt[["trade_date", "mkt_ret_1", "mkt_ret_5", "mkt_ret_20",
                "mkt_vol_20", "mkt_drawdown_60"]]


# ══════════════════════════════════════════════════════════════════════════════
# 数据库读写
# ══════════════════════════════════════════════════════════════════════════════
def get_connection() -> pymysql.Connection:
    return pymysql.connect(**DB_CONFIG)


def ensure_table(conn) -> None:
    """如果 model_input_features 表不存在则自动创建。"""
    ddl = """
    CREATE TABLE IF NOT EXISTS `model_input_features` (
      `id`              BIGINT        NOT NULL AUTO_INCREMENT,
      `stock_code`      VARCHAR(20)   NOT NULL,
      `trade_date`      DATE          NOT NULL,
      `pe_ttm`          DOUBLE        DEFAULT NULL,
      `pb_mrq`          DOUBLE        DEFAULT NULL,
      `pct_chg`         DOUBLE        DEFAULT NULL,
      `total_mv`        DOUBLE        DEFAULT NULL,
      `float_mv`        DOUBLE        DEFAULT NULL,
      `total_shares`    DOUBLE        DEFAULT NULL,
      `float_shares`    DOUBLE        DEFAULT NULL,
      `limit_up`        DOUBLE        DEFAULT NULL,
      `limit_down`      DOUBLE        DEFAULT NULL,
      `chg`             DOUBLE        DEFAULT NULL,
      `avg_price`       DOUBLE        DEFAULT NULL,
      `volume`          DOUBLE        DEFAULT NULL,
      `amount`          DOUBLE        DEFAULT NULL,
      `turnover`        DOUBLE        DEFAULT NULL,
      `volume_ratio`    DOUBLE        DEFAULT NULL,
      `high`            DOUBLE        DEFAULT NULL,
      `low`             DOUBLE        DEFAULT NULL,
      `open_price`      DOUBLE        DEFAULT NULL,
      `close`           DOUBLE        DEFAULT NULL,
      `prev_close`      DOUBLE        DEFAULT NULL,
      `adj_factor`      DOUBLE        DEFAULT NULL,
      `ret_1_calc`      DOUBLE        DEFAULT NULL,
      `ret_5`           DOUBLE        DEFAULT NULL,
      `ret_20`          DOUBLE        DEFAULT NULL,
      `ret_60`          DOUBLE        DEFAULT NULL,
      `rsi_6`           DOUBLE        DEFAULT NULL,
      `rsi_14`          DOUBLE        DEFAULT NULL,
      `macd`            DOUBLE        DEFAULT NULL,
      `macd_signal`     DOUBLE        DEFAULT NULL,
      `macd_hist`       DOUBLE        DEFAULT NULL,
      `bb_mid`          DOUBLE        DEFAULT NULL,
      `bb_std`          DOUBLE        DEFAULT NULL,
      `bb_upper`        DOUBLE        DEFAULT NULL,
      `bb_lower`        DOUBLE        DEFAULT NULL,
      `bb_width`        DOUBLE        DEFAULT NULL,
      `bb_pos`          DOUBLE        DEFAULT NULL,
      `tr`              DOUBLE        DEFAULT NULL,
      `atr_14`          DOUBLE        DEFAULT NULL,
      `atr_pct`         DOUBLE        DEFAULT NULL,
      `vol_20`          DOUBLE        DEFAULT NULL,
      `vol_60`          DOUBLE        DEFAULT NULL,
      `ma5`             DOUBLE        DEFAULT NULL,
      `ma10`            DOUBLE        DEFAULT NULL,
      `ma20`            DOUBLE        DEFAULT NULL,
      `ma60`            DOUBLE        DEFAULT NULL,
      `ma5_dev`         DOUBLE        DEFAULT NULL,
      `ma20_dev`        DOUBLE        DEFAULT NULL,
      `volume_ma5`      DOUBLE        DEFAULT NULL,
      `volume_ma20`     DOUBLE        DEFAULT NULL,
      `vol_surge`       DOUBLE        DEFAULT NULL,
      `price_vol_corr`  DOUBLE        DEFAULT NULL,
      `mkt_ret_1`       DOUBLE        DEFAULT NULL,
      `mkt_ret_5`       DOUBLE        DEFAULT NULL,
      `mkt_ret_20`      DOUBLE        DEFAULT NULL,
      `mkt_vol_20`      DOUBLE        DEFAULT NULL,
      `mkt_drawdown_60` DOUBLE        DEFAULT NULL,
      `industry_l3`     VARCHAR(100)  DEFAULT NULL,
      `created_at`      TIMESTAMP     DEFAULT CURRENT_TIMESTAMP,
      `updated_at`      TIMESTAMP     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
      PRIMARY KEY (`id`),
      UNIQUE KEY `uq_stock_date` (`stock_code`, `trade_date`),
      KEY `idx_stock_code` (`stock_code`),
      KEY `idx_trade_date` (`trade_date`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """
    with conn.cursor() as cur:
        cur.execute(ddl)
    conn.commit()
    log.info("model_input_features 表已就绪")


def get_all_stock_codes(conn) -> list[str]:
    with conn.cursor() as cur:
        cur.execute(
            "SELECT stockCode FROM company_profile "
            "WHERE status = 'L' ORDER BY stockCode"
        )
        return [row["stockCode"] for row in cur.fetchall()]


def _query_df(conn, sql: str, params: tuple = ()) -> pd.DataFrame:
    """用游标执行 SQL，返回 DataFrame（兼容 pymysql 原生连接）。"""
    with conn.cursor() as cur:
        cur.execute(sql, params)
        rows = cur.fetchall()
        if not rows:
            return pd.DataFrame()
        return pd.DataFrame(rows)


def read_daily_data(conn, stock_code: str, days: int = 150) -> pd.DataFrame:
    """
    读取最近 `days` 个日历日的日频数据。
    days 取 150 以保证计算 60 日指标时有足够历史数据。
    """
    sql = """
        SELECT
            trade_date,
            stock_code,
            pe              AS pe_ttm,
            pb              AS pb_mrq,
            pct_chg,
            ev              AS total_mv,
            mkt_cap_float   AS float_mv,
            total_shares,
            share_issuing_mkt AS float_shares,
            maxup           AS limit_up,
            maxdown         AS limit_down,
            chg,
            vwap            AS avg_price,
            volume,
            amt             AS amount,
            turn            AS turnover,
            vol_ratio       AS volume_ratio,
            high,
            low,
            `open`          AS open_price,
            close,
            pre_close       AS prev_close,
            adjfactor       AS adj_factor
        FROM daily_market_data
        WHERE stock_code = %s
          AND trade_date >= DATE_SUB(CURDATE(), INTERVAL %s DAY)
        ORDER BY trade_date ASC
    """
    df = _query_df(conn, sql, (stock_code, days))
    if df.empty:
        return df
    df["trade_date"] = pd.to_datetime(df["trade_date"])
    num_cols = [c for c in df.columns if c not in ("trade_date", "stock_code")]
    for col in num_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def read_market_data(conn, days: int = 200) -> pd.DataFrame:
    """读取 kcb_close_daily 最近 days 个日历日的数据。"""
    sql = """
        SELECT trade_date,
               close_arithmetic,
               close_float_weighted,
               close_total_weighted
        FROM kcb_close_daily
        WHERE trade_date >= DATE_SUB(CURDATE(), INTERVAL %s DAY)
        ORDER BY trade_date ASC
    """
    df = _query_df(conn, sql, (days,))
    if df.empty:
        return df
    df["trade_date"] = pd.to_datetime(df["trade_date"])
    for col in ["close_arithmetic", "close_float_weighted", "close_total_weighted"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def load_industry_map() -> pd.DataFrame:
    """从 Excel 读取行业分类，返回 {stock_code, industry_l3}。"""
    try:
        raw = pd.read_excel(INDUSTRY_EXCEL)
        raw.columns = [str(c).strip() for c in raw.columns]

        # 自动识别股票代码列和行业列
        stock_col = None
        ind_col   = None
        for col in raw.columns:
            cl = col.lower()
            if stock_col is None and ("code" in cl or "代码" in col or "证券" in col):
                stock_col = col
            if ind_col is None and ("industry" in cl or "行业" in col):
                ind_col = col

        if stock_col is None:
            stock_col = raw.columns[0]
        if ind_col is None:
            # 取最后一个文本列
            for col in reversed(raw.columns.tolist()):
                if raw[col].dtype == object:
                    ind_col = col
                    break
            if ind_col is None:
                ind_col = raw.columns[-1]

        result = raw[[stock_col, ind_col]].copy()
        result.columns = ["stock_code", "industry_l3"]
        result["stock_code"]  = result["stock_code"].astype(str).str.strip()
        result["industry_l3"] = result["industry_l3"].astype(str).str.strip()
        result = result.dropna().drop_duplicates(subset=["stock_code"])
        log.info("行业分类加载完成，共 %d 条", len(result))
        return result
    except Exception as exc:
        log.warning("行业分类 Excel 读取失败：%s，industry_l3 将为 NULL", exc)
        return pd.DataFrame(columns=["stock_code", "industry_l3"])


# ──────────────────────────────────────────────────────────────────────────────
# 写入 model_input_features
# ──────────────────────────────────────────────────────────────────────────────
_FEATURE_COLS = [
    # 原始日频
    "pe_ttm", "pb_mrq", "pct_chg", "total_mv", "float_mv",
    "total_shares", "float_shares", "limit_up", "limit_down",
    "chg", "avg_price", "volume", "amount", "turnover", "volume_ratio",
    "high", "low", "open_price", "close", "prev_close", "adj_factor",
    # 技术指标
    "ret_1_calc", "ret_5", "ret_20", "ret_60",
    "rsi_6", "rsi_14",
    "macd", "macd_signal", "macd_hist",
    "bb_mid", "bb_std", "bb_upper", "bb_lower", "bb_width", "bb_pos",
    "tr", "atr_14", "atr_pct",
    "vol_20", "vol_60",
    "ma5", "ma10", "ma20", "ma60", "ma5_dev", "ma20_dev",
    "volume_ma5", "volume_ma20", "vol_surge", "price_vol_corr",
    # 市场特征
    "mkt_ret_1", "mkt_ret_5", "mkt_ret_20", "mkt_vol_20", "mkt_drawdown_60",
    # 行业
    "industry_l3",
]

_INSERT_COLS = ["stock_code", "trade_date"] + _FEATURE_COLS
_PLACEHOLDERS = ", ".join(["%s"] * len(_INSERT_COLS))
_UPDATE_SET = ", ".join(
    f"`{c}` = VALUES(`{c}`)"
    for c in _FEATURE_COLS
)
_INSERT_SQL = (
    f"INSERT INTO model_input_features "
    f"({', '.join(f'`{c}`' for c in _INSERT_COLS)}) "
    f"VALUES ({_PLACEHOLDERS}) "
    f"ON DUPLICATE KEY UPDATE {_UPDATE_SET}"
)


def _safe_float(val):
    """将值转为 float，NaN/None → None。"""
    if val is None:
        return None
    try:
        v = float(val)
        return None if (v != v) else v   # NaN check
    except (TypeError, ValueError):
        return None


def upsert_features(conn, df: pd.DataFrame) -> int:
    """批量 upsert 到 model_input_features，返回写入行数。"""
    if df.empty:
        return 0

    rows = []
    for _, row in df.iterrows():
        td = row["trade_date"]
        date_val = td.date() if hasattr(td, "date") else td
        values = [row.get("stock_code", ""), date_val]
        for col in _FEATURE_COLS:
            val = row.get(col)
            if col == "industry_l3":
                values.append(str(val) if (val is not None and str(val) != "nan") else None)
            else:
                values.append(_safe_float(val))
        rows.append(tuple(values))

    with conn.cursor() as cur:
        cur.executemany(_INSERT_SQL, rows)
    conn.commit()
    return len(rows)


# ══════════════════════════════════════════════════════════════════════════════
# 单只股票特征构建
# ══════════════════════════════════════════════════════════════════════════════
def build_features_for_stock(
    conn,
    stock_code: str,
    market_df: pd.DataFrame,
    industry_map: pd.DataFrame,
) -> int:
    """
    为单只股票构建并保存特征，返回写入的行数。
    读取 150 天原始数据以保证滚动窗口足够，最终只写最近 90 个交易日。
    """
    df = read_daily_data(conn, stock_code, days=150)
    if df.empty or len(df) < 5:
        log.debug("  %s：日频数据不足（%d 行），跳过", stock_code, len(df))
        return 0

    # 计算技术指标
    df = compute_technical_indicators(df)

    # 合并市场特征
    df = df.merge(market_df, on="trade_date", how="left")

    # 合并行业分类
    if not industry_map.empty:
        ind_row = industry_map[industry_map["stock_code"] == stock_code]
        df["industry_l3"] = ind_row.iloc[0]["industry_l3"] if not ind_row.empty else None
    else:
        df["industry_l3"] = None

    # 只保留最近 90 个交易日写入
    df = df.tail(90).copy()
    df["stock_code"] = stock_code

    return upsert_features(conn, df)


# ══════════════════════════════════════════════════════════════════════════════
# 主程序入口
# ══════════════════════════════════════════════════════════════════════════════
def main() -> None:
    parser = argparse.ArgumentParser(description="构建 model_input_features 特征表")
    parser.add_argument("--stock", type=str, default=None,
                        help="只处理指定股票代码，如 688001.SH")
    args = parser.parse_args()

    log.info("连接数据库...")
    conn = get_connection()

    try:
        # 1. 加载科创板市场指数
        log.info("加载科创板收盘价数据（kcb_close_daily）...")
        raw_mkt = read_market_data(conn, days=200)
        if raw_mkt.empty:
            log.warning("kcb_close_daily 无数据，市场特征将全为 NULL")
            market_df = pd.DataFrame(columns=["trade_date", "mkt_ret_1", "mkt_ret_5",
                                               "mkt_ret_20", "mkt_vol_20", "mkt_drawdown_60"])
        else:
            market_df = compute_market_features(raw_mkt)
            log.info("  市场数据：%d 行", len(market_df))

        # 2. 加载行业分类
        log.info("加载行业分类（21公司行业分类.xlsx）...")
        industry_map = load_industry_map()

        # 3. 确定股票列表
        if args.stock:
            stocks = [args.stock.strip()]
        else:
            stocks = get_all_stock_codes(conn)

        log.info("开始处理 %d 只股票...", len(stocks))
        total_rows = 0
        for i, code in enumerate(stocks, 1):
            try:
                n = build_features_for_stock(conn, code, market_df, industry_map)
                total_rows += n
                if i % 20 == 0 or i == len(stocks):
                    log.info("  进度：%d / %d，累计写入 %d 行", i, len(stocks), total_rows)
            except Exception as exc:
                log.error("  %s 处理失败：%s", code, exc)

        log.info("全部完成，共写入 %d 行到 model_input_features。", total_rows)

    finally:
        conn.close()


if __name__ == "__main__":
    main()
