from __future__ import annotations

from typing import List

import numpy as np
import pandas as pd

from .utils import infer_numeric_cols, winsorize_series


BASE_DROP = {"date", "stock", "industry_l3", "label", "fwd_ret", "fwd_ret_1d", "split"}


def add_industry_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["ret_1_raw"] = out.groupby("stock")["close"].pct_change(1)

    ind_daily = (
        out.groupby(["date", "industry_l3"], dropna=False)["ret_1_raw"]
        .agg(ind_ret_mean="mean", ind_ret_std="std")
        .reset_index()
    )
    out = out.merge(ind_daily, on=["date", "industry_l3"], how="left")

    dummies = pd.get_dummies(out["industry_l3"], prefix="ind", dummy_na=True).astype(float)
    out = pd.concat([out, dummies], axis=1)
    return out


def add_stock_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    stock_dummies = pd.get_dummies(out["stock"], prefix="stock", dummy_na=False).astype(float)
    out = pd.concat([out, stock_dummies], axis=1)
    return out


def add_relative_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    if "ret_1_calc" in out.columns:
        out["ret_1_raw"] = out["ret_1_calc"] / 100.0
    else:
        out["ret_1_raw"] = out.groupby("stock")["close"].pct_change(1)

    def _to_decimal(s: pd.Series) -> pd.Series:
        # Dataset ret_* columns are in percent unit.
        return s / 100.0

    out["alpha_1"] = out["ret_1_raw"] - out["mkt_ret_1"]
    if "ret_5" in out.columns:
        out["alpha_5"] = _to_decimal(out["ret_5"]) - out["mkt_ret_5"]
    else:
        out["alpha_5"] = out.groupby("stock")["close"].pct_change(5) - out["mkt_ret_5"]

    if "ret_20" in out.columns:
        out["alpha_20"] = _to_decimal(out["ret_20"]) - out["mkt_ret_20"]
    else:
        out["alpha_20"] = out.groupby("stock")["close"].pct_change(20) - out["mkt_ret_20"]

    return out


def shift_leakage_prone_features(df: pd.DataFrame, feature_cols: List[str]) -> pd.DataFrame:
    out = df.copy()
    # Use only info available at end of day t to predict t+1.
    out[feature_cols] = out.groupby("stock")[feature_cols].shift(1)
    return out


def preprocess_features(df: pd.DataFrame) -> tuple[pd.DataFrame, List[str]]:
    out = df.copy()

    num_cols = infer_numeric_cols(out, exclude=["label"])
    for c in num_cols:
        out[c] = pd.to_numeric(out[c], errors="coerce")
        out[c] = out.groupby("stock")[c].transform(lambda s: s.ffill())
        out[c] = out.groupby("stock")[c].transform(lambda s: s.bfill())
        out[c] = winsorize_series(out[c])

    feature_cols = [c for c in num_cols if c not in BASE_DROP]
    out = shift_leakage_prone_features(out, feature_cols)
    out[feature_cols] = out[feature_cols].replace([np.inf, -np.inf], np.nan).fillna(0.0)
    return out, feature_cols
