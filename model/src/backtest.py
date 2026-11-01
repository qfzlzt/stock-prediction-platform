from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass
class BacktestConfig:
    buy_threshold: float = 0.55
    sell_threshold: float = 0.55
    fee_rate: float = 0.0005
    slippage: float = 0.0005


def probability_to_signal(df: pd.DataFrame, buy_threshold: float, sell_threshold: float) -> pd.Series:
    proba_cols = sorted([c for c in df.columns if c.startswith("proba_")], key=lambda x: int(x.split("_")[1]))
    n_classes = len(proba_cols)
    if n_classes < 2:
        raise ValueError("Prediction DataFrame must contain probability columns: proba_0 ... proba_k")

    if n_classes == 2:
        score_long = df["proba_1"]
        score_short = df["proba_0"]
        top_cls = 1
        second_cls = None
    elif n_classes == 3:
        score_long = df["proba_2"]
        score_short = df["proba_0"]
        top_cls = 2
        second_cls = 1
    else:
        score_long = df["proba_4"] + 0.5 * df["proba_3"]
        score_short = df["proba_0"] + 0.5 * df["proba_1"]
        top_cls = 4
        second_cls = 3

    sig = pd.Series(0.0, index=df.index)
    sig[score_long >= buy_threshold] = 1.0

    # confidence sizing
    very_conf = score_long >= (buy_threshold + 0.2)
    med_conf = score_long >= (buy_threshold + 0.1)
    sig[med_conf] = 0.6
    sig[very_conf] = 1.0

    # Fallback from hard class to avoid all-cash behavior.
    if "pred_label" in df.columns:
        sig[(sig == 0.0) & (df["pred_label"] == top_cls)] = 1.0
        if second_cls is not None:
            sig[(sig == 0.0) & (df["pred_label"] == second_cls)] = 0.6

    # Short confidence is treated as reducing long exposure to flat.
    sig[score_short >= sell_threshold] = 0.0
    return sig


def run_backtest(pred_df: pd.DataFrame, cfg: BacktestConfig) -> tuple[pd.DataFrame, dict]:
    df = pred_df.sort_values("date").copy()
    df["position"] = probability_to_signal(df, cfg.buy_threshold, cfg.sell_threshold)
    df["position_prev"] = df["position"].shift(1).fillna(0.0)

    realized_col = "fwd_ret_1d" if "fwd_ret_1d" in df.columns else "fwd_ret"
    df["gross_ret"] = df["position_prev"] * df[realized_col]
    turnover = (df["position"] - df["position_prev"]).abs()
    df["cost"] = turnover * (cfg.fee_rate + cfg.slippage)
    df["net_ret"] = df["gross_ret"] - df["cost"]

    df["equity"] = (1.0 + df["net_ret"].fillna(0.0)).cumprod()

    total_ret = float(df["equity"].iloc[-1] - 1.0) if len(df) else 0.0
    ann_ret = float((1.0 + total_ret) ** (252 / max(len(df), 1)) - 1.0)
    vol = float(df["net_ret"].std() * np.sqrt(252)) if len(df) else 0.0
    sharpe = float(ann_ret / vol) if vol > 1e-12 else 0.0
    rolling_max = df["equity"].cummax() if len(df) else pd.Series([1.0])
    drawdown = df["equity"] / rolling_max - 1.0 if len(df) else pd.Series([0.0])
    mdd = float(drawdown.min()) if len(df) else 0.0

    metrics = {
        "total_return": total_ret,
        "annualized_return": ann_ret,
        "annualized_vol": vol,
        "sharpe": sharpe,
        "max_drawdown": mdd,
        "win_rate": float((df["net_ret"] > 0).mean()) if len(df) else 0.0,
        "avg_turnover": float(turnover.mean()) if len(df) else 0.0,
        "n_days": int(len(df)),
    }
    return df, metrics
