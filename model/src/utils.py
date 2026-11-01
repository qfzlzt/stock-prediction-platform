from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict, List

import numpy as np
import pandas as pd
import yaml


def load_config(path: str | Path) -> Dict:
    cfg_path = Path(path).resolve()
    with open(cfg_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    data_cfg = cfg.get("data")
    if isinstance(data_cfg, dict) and data_cfg.get("base_dir"):
        base_dir = Path(str(data_cfg["base_dir"]))
        if not base_dir.is_absolute():
            data_cfg["base_dir"] = str((cfg_path.parent / base_dir).resolve())
    return cfg


def save_json(path: str | Path, obj: Dict) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def clean_col(name: str) -> str:
    # Keep the semantic prefix before metadata blocks like [交易日期]
    base = str(name).split("\n")[0].strip()
    base = re.sub(r"\s+", "_", base)
    mapping = {
        "日期": "date",
        "trade_date": "date",
        "时间": "date",
        "收盘价": "close",
        "开盘价": "open",
        "最高价": "high",
        "最低价": "low",
        "涨跌幅": "pct_chg",
        "涨跌": "chg",
        "成交量": "volume",
        "成交额": "amount",
        "换手率": "turnover",
        "量比": "volume_ratio",
        "市盈率PE(TTM)": "pe_ttm",
        "市净率PB(MRQ)": "pb_mrq",
        "总市值1": "total_mv",
        "流通市值": "float_mv",
        "总股本": "total_shares",
        "流通股本(含限售股)": "float_shares",
        "前收盘价": "prev_close",
        "复权因子": "adj_factor",
        "均价": "avg_price",
        "涨停价": "limit_up",
        "跌停价": "limit_down",
        # Market-level fields (STAR board daily aggregates)
        "挂牌数": "mkt_listed_count",
        "市价总值": "mkt_total_mv",
        "流通市值": "float_mv",
        "成交金额": "mkt_amount",
        "平均市盈率": "mkt_pe_mean",
        "流通换手率": "mkt_float_turnover",
    }
    if base in mapping:
        return mapping[base]

    # Market file columns
    if "收盘价（算术平均" in base:
        return "star_close_mean"
    if "收盘价（流通股本加权平均" in base:
        return "star_close_float_w"
    if "收盘价（总股本加权平均" in base:
        return "star_close_total_w"

    return re.sub(r"[^0-9a-zA-Z_\u4e00-\u9fa5]", "", base)


def ensure_datetime(df: pd.DataFrame, col: str = "date") -> pd.DataFrame:
    df[col] = pd.to_datetime(df[col], errors="coerce")
    return df.dropna(subset=[col]).copy()


def infer_numeric_cols(df: pd.DataFrame, exclude: List[str]) -> List[str]:
    cols: List[str] = []
    for c in df.columns:
        if c in exclude:
            continue
        if pd.api.types.is_numeric_dtype(df[c]) and not pd.api.types.is_bool_dtype(df[c]):
            cols.append(c)
    return cols


def winsorize_series(s: pd.Series, low: float = 0.01, high: float = 0.99) -> pd.Series:
    if s.isna().all():
        return s
    lo, hi = s.quantile(low), s.quantile(high)
    return s.clip(lo, hi)


def zscore_with_train_stats(train: pd.DataFrame, test: pd.DataFrame, cols: List[str]) -> tuple[pd.DataFrame, pd.DataFrame]:
    mu = train[cols].mean()
    sigma = train[cols].std().replace(0, np.nan)
    train_scaled = train.copy()
    test_scaled = test.copy()
    train_scaled[cols] = (train[cols] - mu) / sigma
    test_scaled[cols] = (test[cols] - mu) / sigma
    train_scaled[cols] = train_scaled[cols].replace([np.inf, -np.inf], np.nan).fillna(0.0)
    test_scaled[cols] = test_scaled[cols].replace([np.inf, -np.inf], np.nan).fillna(0.0)
    return train_scaled, test_scaled
