from __future__ import annotations

import pandas as pd


def add_time_split(df: pd.DataFrame, train_end: str, valid_end: str, test_end: str) -> pd.DataFrame:
    out = df.copy()
    train_end_ts = pd.Timestamp(train_end)
    valid_end_ts = pd.Timestamp(valid_end)
    test_end_ts = pd.Timestamp(test_end)

    out["split"] = "drop"
    out.loc[out["date"] <= train_end_ts, "split"] = "train"
    out.loc[(out["date"] > train_end_ts) & (out["date"] <= valid_end_ts), "split"] = "valid"
    out.loc[(out["date"] > valid_end_ts) & (out["date"] <= test_end_ts), "split"] = "test"
    return out
