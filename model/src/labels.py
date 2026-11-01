from __future__ import annotations

import numpy as np
import pandas as pd


CLASS_NAME = {
    0: "下跌",
    1: "上涨",
}


def add_labels(
    df: pd.DataFrame,
    horizon: int = 1,
    quantile_window: int = 252,
    n_classes: int = 3,
    neutral_ret_band: float | None = None,
) -> pd.DataFrame:
    out = df.copy()
    out = out.sort_values(["stock", "date"]).reset_index(drop=True)

    out["fwd_ret"] = out.groupby("stock")["close"].shift(-horizon) / out["close"] - 1.0
    out["fwd_ret_1d"] = out.groupby("stock")["close"].shift(-1) / out["close"] - 1.0

    if n_classes < 2:
        raise ValueError("n_classes must be >= 2")

    # Rolling quantile bins per stock using only historical forward returns (shifted).
    q_cols = []
    for k in range(1, n_classes):
        q_name = f"q_{k}"
        out[q_name] = out.groupby("stock")["fwd_ret"].transform(
            lambda s, q=k / n_classes: s.shift(1).rolling(quantile_window, min_periods=60).quantile(q)
        )
        q_cols.append(q_name)

    fwd = out["fwd_ret"].to_numpy()
    q_mat = out[q_cols].to_numpy()
    valid = (~np.isnan(fwd)) & (~np.isnan(q_mat).any(axis=1))

    labels = np.full(len(out), np.nan)
    labels[valid] = np.sum(fwd[valid, None] > q_mat[valid], axis=1)
    out["label"] = labels
    out = out.drop(columns=q_cols)

    band = None if neutral_ret_band is None else float(neutral_ret_band)
    if band is not None and band > 0:
        out["is_neutral"] = out["fwd_ret"].abs() <= band
    else:
        out["is_neutral"] = False

    return out
