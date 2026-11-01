from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from src.backtest import BacktestConfig, run_backtest
from src.data_loader import load_industry_map, load_market_index, load_stock_panel
from src.evaluate import cls_metrics
from src.features import add_industry_features, add_relative_features, add_stock_features, preprocess_features
from src.labels import add_labels
from src.split import add_time_split
from src.utils import load_config, save_json, zscore_with_train_stats


def build_base_dataset(cfg: dict) -> tuple[pd.DataFrame, pd.DataFrame, list[str]]:
    data_cfg = cfg["data"]
    label_cfg = cfg["label"]

    panel = load_stock_panel(data_cfg["base_dir"], data_cfg["stock_glob"])
    industry = load_industry_map(data_cfg["base_dir"], data_cfg["industry_file"])
    market = load_market_index(data_cfg["base_dir"], data_cfg["market_file"])

    df = panel.merge(industry, on="stock", how="left")
    df = df.merge(market, on="date", how="left")

    df = add_labels(
        df,
        horizon=int(label_cfg["horizon"]),
        quantile_window=int(label_cfg["quantile_window"]),
        n_classes=int(label_cfg["n_classes"]),
        neutral_ret_band=label_cfg.get("neutral_ret_band"),
    )
    df = add_industry_features(df)
    df = add_stock_features(df)
    df = add_relative_features(df)

    df, feature_cols = preprocess_features(df)
    df = df.dropna(subset=["label"]).copy()
    df["label"] = df["label"].astype(int)
    return df, industry, feature_cols


def run_model_on_windows(
    base_df: pd.DataFrame,
    industry: pd.DataFrame,
    feature_cols: list[str],
    cfg: dict,
    model_name: str,
) -> tuple[pd.DataFrame, dict]:
    n_classes = int(cfg["label"]["n_classes"])
    windows = cfg["walk_forward"]["windows"]

    all_preds = []
    by_window = []

    for i, w in enumerate(windows, start=1):
        df_w = add_time_split(
            base_df,
            train_end=w["train_end"],
            valid_end=w["valid_end"],
            test_end=w["test_end"],
        )
        df_w = df_w[df_w["split"].isin(["train", "valid", "test"])].copy()

        # Optional neutral-band filtering for training data only (keep test untouched).
        lbl_cfg = cfg.get("label", {})
        if bool(lbl_cfg.get("neutral_filter_train", False)) and "is_neutral" in df_w.columns:
            neutral_splits = lbl_cfg.get("neutral_filter_splits", ["train"])
            if isinstance(neutral_splits, str):
                neutral_splits = [neutral_splits]
            neutral_splits = [str(s) for s in neutral_splits]
            drop_mask = df_w["split"].isin(neutral_splits) & df_w["is_neutral"].fillna(False)
            if drop_mask.any():
                df_w = df_w.loc[~drop_mask].copy()

        if model_name in {"lstm", "gnn"}:
            tr_mask = df_w["split"] == "train"
            te_mask = ~tr_mask
            train_scaled, other_scaled = zscore_with_train_stats(df_w.loc[tr_mask], df_w.loc[te_mask], feature_cols)
            df_w = pd.concat([train_scaled, other_scaled], ignore_index=True).sort_values(["stock", "date"]).reset_index(drop=True)

        if df_w[df_w["split"] == "test"].empty:
            continue

        if model_name == "lgbm":
            from src.train_lgbm import train_predict_lgbm

            pred_df, cls = train_predict_lgbm(df_w, feature_cols, cfg["model"], n_classes=n_classes)
        elif model_name == "lstm":
            from src.train_lstm import train_predict_lstm

            pred_df, cls = train_predict_lstm(df_w, feature_cols, cfg["model"], n_classes=n_classes)
        else:
            from src.train_gnn import train_predict_gnn

            pred_df, cls = train_predict_gnn(df_w, feature_cols, industry, cfg["model"], n_classes=n_classes)

        pred_df = pred_df.copy()
        pred_df["wf_window"] = i
        pred_df["wf_train_end"] = w["train_end"]
        pred_df["wf_valid_end"] = w["valid_end"]
        pred_df["wf_test_end"] = w["test_end"]

        all_preds.append(pred_df)
        by_window.append({"window": i, "classification": cls, "n_rows": int(len(pred_df))})

    if not all_preds:
        raise ValueError("No walk-forward predictions generated. Check window ranges.")

    pred_all = pd.concat(all_preds, ignore_index=True)
    pred_all = pred_all.sort_values(["date", "stock", "wf_window"]).drop_duplicates(
        subset=["date", "stock"], keep="last"
    )
    pred_all = pred_all.sort_values(["stock", "date"]).reset_index(drop=True)

    overall_cls = cls_metrics(pred_all["label"].astype(int).values, pred_all["pred_label"].astype(int).values)
    cls_payload = {
        "overall": overall_cls,
        "by_window": by_window,
    }
    return pred_all, cls_payload


def run_backtest_all_stocks(pred_df: pd.DataFrame, bt_cfg: BacktestConfig) -> tuple[pd.DataFrame, pd.DataFrame]:
    summaries = []
    equities = []

    for stock, g in pred_df.groupby("stock"):
        g = g.sort_values("date").reset_index(drop=True)
        if g.empty:
            continue

        eq_df, m = run_backtest(g, bt_cfg)
        eq_df = eq_df.copy()
        eq_df["stock"] = stock
        equities.append(eq_df)

        rec = {"stock": stock}
        rec.update(m)
        summaries.append(rec)

    summary_df = pd.DataFrame(summaries).sort_values("stock").reset_index(drop=True)
    equity_all = pd.concat(equities, ignore_index=True) if equities else pd.DataFrame()
    return summary_df, equity_all


def run_single_model(cfg: dict, model_name: str) -> dict:
    base_df, industry, feature_cols = build_base_dataset(cfg)
    pred_df, cls_payload = run_model_on_windows(base_df, industry, feature_cols, cfg, model_name)

    bt_cfg = BacktestConfig(
        buy_threshold=float(cfg["strategy"]["buy_threshold"]),
        sell_threshold=float(cfg["strategy"]["sell_threshold"]),
        fee_rate=float(cfg["strategy"]["fee_rate"]),
        slippage=float(cfg["strategy"]["slippage"]),
    )

    summary_df, equity_all = run_backtest_all_stocks(pred_df, bt_cfg)

    out_dir = Path("outputs")
    out_dir.mkdir(parents=True, exist_ok=True)

    pred_all_path = out_dir / f"{model_name}_all_predictions.csv"
    eq_all_path = out_dir / f"{model_name}_all_equity_curve.csv"
    bt_all_path = out_dir / f"{model_name}_all_backtest_summary.csv"
    metrics_all_path = out_dir / f"{model_name}_all_metrics.json"

    pred_df.to_csv(pred_all_path, index=False)
    equity_all.to_csv(eq_all_path, index=False)
    summary_df.to_csv(bt_all_path, index=False)

    payload = {
        "classification": cls_payload,
        "n_stocks_in_test": int(pred_df["stock"].nunique()),
        "backtest_summary_mean": summary_df.mean(numeric_only=True).to_dict() if not summary_df.empty else {},
    }
    save_json(metrics_all_path, payload)

    return {
        "model": model_name,
        "pred_path": str(pred_all_path),
        "equity_path": str(eq_all_path),
        "summary_path": str(bt_all_path),
        "metrics_path": str(metrics_all_path),
        "payload": payload,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config.yaml")
    parser.add_argument("--model", choices=["lgbm", "lstm", "gnn"], default="lgbm")
    parser.add_argument("--all-models", action="store_true", help="Run lgbm/lstm/gnn and export comparison table")
    args = parser.parse_args()

    cfg = load_config(args.config)

    model_list = ["lgbm", "lstm", "gnn"] if args.all_models else [args.model]
    results = []
    for m in model_list:
        res = run_single_model(cfg, m)
        results.append(res)
        print(f"[{m}] done -> {res['metrics_path']}")

    if len(results) > 1:
        rows = []
        for r in results:
            b = r["payload"]["backtest_summary_mean"]
            c = r["payload"]["classification"]["overall"]
            rows.append(
                {
                    "model": r["model"],
                    "macro_f1": c.get("macro_f1", np.nan),
                    "balanced_accuracy": c.get("balanced_accuracy", np.nan),
                    "total_return_mean": b.get("total_return", np.nan),
                    "annualized_return_mean": b.get("annualized_return", np.nan),
                    "sharpe_mean": b.get("sharpe", np.nan),
                    "max_drawdown_mean": b.get("max_drawdown", np.nan),
                }
            )
        comp = pd.DataFrame(rows).sort_values("sharpe_mean", ascending=False)
        comp_path = Path("outputs") / "model_comparison.csv"
        comp.to_csv(comp_path, index=False)
        print(f"Comparison: {comp_path}")


if __name__ == "__main__":
    np.random.seed(42)
    main()
