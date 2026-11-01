from __future__ import annotations

import argparse
import pickle
from pathlib import Path

import lightgbm as lgb
import numpy as np
import pandas as pd
import torch
from sklearn.utils.class_weight import compute_class_weight

from run_pipeline import build_base_dataset
from src.evaluate import best_binary_threshold
from src.split import add_time_split
from src.train_gnn import (
    HeteroRegimeGNN,
    build_adj_from_industry,
    build_corr_adj,
    build_volume_sync_adj,
    build_valuation_sim_adj,
    date_snapshots,
    normalized_adj,
)
from src.train_lstm import LSTMClassifier, SeqDataset, build_sequences
from src.utils import load_config


def latest_window(cfg: dict) -> dict:
    ws = cfg["walk_forward"]["windows"]
    if not ws:
        raise ValueError("walk_forward.windows is empty")
    return ws[-1]


def split_latest(df: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    w = latest_window(cfg)
    out = add_time_split(df, train_end=w["train_end"], valid_end=w["valid_end"], test_end=w["test_end"])
    return out[out["split"].isin(["train", "valid", "test"])].copy()


def export_lgbm(df: pd.DataFrame, feature_cols: list[str], cfg: dict, out_dir: Path) -> Path:
    n_classes = int(cfg["label"]["n_classes"])
    mcfg = cfg["model"]

    train = df[df["split"] == "train"].dropna(subset=["label"])
    valid = df[df["split"] == "valid"].dropna(subset=["label"])
    trv = pd.concat([train, valid], ignore_index=True)

    X = trv[feature_cols].values
    y = trv["label"].astype(int).values
    classes = np.unique(y)
    cw = compute_class_weight(class_weight="balanced", classes=classes, y=y)
    cw_map = {int(c): float(w) for c, w in zip(classes, cw)}
    sw = np.array([cw_map[int(v)] for v in y])

    clf = lgb.LGBMClassifier(
        objective="multiclass",
        num_class=n_classes,
        random_state=mcfg.get("random_state", 42),
        n_estimators=mcfg["lgbm"].get("n_estimators", 700),
        learning_rate=mcfg["lgbm"].get("learning_rate", 0.03),
        num_leaves=mcfg["lgbm"].get("num_leaves", 63),
        min_child_samples=mcfg["lgbm"].get("min_child_samples", 80),
        subsample=mcfg["lgbm"].get("subsample", 0.8),
        colsample_bytree=mcfg["lgbm"].get("colsample_bytree", 0.8),
        verbosity=-1,
    )
    clf.fit(X, y, sample_weight=sw)

    threshold = None
    if n_classes == 2:
        threshold = mcfg.get("binary_threshold")
        if threshold is None and len(valid):
            vp = clf.predict_proba(valid[feature_cols])[:, 1]
            threshold = best_binary_threshold(valid["label"].astype(int).values, vp)

    bundle = {
        "model_type": "lgbm",
        "n_classes": n_classes,
        "feature_cols": feature_cols,
        "threshold": threshold,
        "label_horizon": int(cfg["label"]["horizon"]),
        "model": clf,
    }
    p = out_dir / "lgbm_prod.pkl"
    with open(p, "wb") as f:
        pickle.dump(bundle, f)
    return p


def export_lstm(df: pd.DataFrame, feature_cols: list[str], cfg: dict, out_dir: Path) -> tuple[Path, Path]:
    n_classes = int(cfg["label"]["n_classes"])
    mcfg = cfg["model"]
    lcfg = mcfg["lstm"]
    lookback = int(lcfg.get("lookback", 20))

    train = df[df["split"] == "train"].dropna(subset=["label"])
    valid = df[df["split"] == "valid"].dropna(subset=["label"])
    trv = pd.concat([train, valid], ignore_index=True)

    X, y, _ = build_sequences(trv, feature_cols, lookback)
    if len(y) == 0:
        raise ValueError("No LSTM train data for export")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = LSTMClassifier(
        in_dim=len(feature_cols),
        hidden=int(lcfg.get("hidden_size", 64)),
        num_layers=int(lcfg.get("num_layers", 2)),
        dropout=float(lcfg.get("dropout", 0.2)),
        num_classes=n_classes,
    ).to(device)

    loader = torch.utils.data.DataLoader(SeqDataset(X, y), batch_size=int(lcfg.get("batch_size", 128)), shuffle=True)
    opt = torch.optim.Adam(model.parameters(), lr=float(lcfg.get("lr", 1e-3)))
    criterion = torch.nn.CrossEntropyLoss()

    model.train()
    for _ in range(max(5, int(lcfg.get("epochs", 25)) // 2)):
        for xb, yb in loader:
            xb, yb = xb.to(device), yb.to(device)
            opt.zero_grad()
            loss = criterion(model(xb), yb)
            loss.backward()
            opt.step()

    pt_path = out_dir / "lstm_prod.pt"
    torch.save(model.state_dict(), pt_path)

    meta = {
        "model_type": "lstm",
        "n_classes": n_classes,
        "feature_cols": feature_cols,
        "lookback": lookback,
        "hidden_size": int(lcfg.get("hidden_size", 64)),
        "num_layers": int(lcfg.get("num_layers", 2)),
        "dropout": float(lcfg.get("dropout", 0.2)),
        "threshold": mcfg.get("binary_threshold"),
        "label_horizon": int(cfg["label"]["horizon"]),
        "weights_path": str(pt_path),
    }
    pkl_path = out_dir / "lstm_prod_meta.pkl"
    with open(pkl_path, "wb") as f:
        pickle.dump(meta, f)
    return pt_path, pkl_path


def export_gnn(df: pd.DataFrame, industry: pd.DataFrame, feature_cols: list[str], cfg: dict, out_dir: Path) -> tuple[Path, Path]:
    n_classes = int(cfg["label"]["n_classes"])
    mcfg = cfg["model"]
    gcfg = mcfg["gnn"]

    train = df[df["split"] == "train"].dropna(subset=["label"])
    valid = df[df["split"] == "valid"].dropna(subset=["label"])
    trv = pd.concat([train, valid], ignore_index=True)

    stocks = sorted(df["stock"].dropna().unique().tolist())
    ind_adj = build_adj_from_industry(stocks, industry)
    corr_adj = build_corr_adj(train, stocks, int(gcfg.get("corr_window", 60)), float(gcfg.get("corr_threshold", 0.2)))
    vol_adj = build_volume_sync_adj(train, stocks, int(gcfg.get("vol_window", 60)), float(gcfg.get("vol_threshold", 0.2)))
    val_adj = build_valuation_sim_adj(train, stocks, float(gcfg.get("valuation_threshold", 0.6)))
    all_relation_names = ["industry", "corr", "volume_sync", "valuation_sim"]
    all_rel_adjs = np.stack([
        normalized_adj(ind_adj),
        normalized_adj(corr_adj),
        normalized_adj(vol_adj),
        normalized_adj(val_adj),
    ], axis=0).astype(np.float32)
    use_relations = gcfg.get("use_relations")
    if use_relations is None:
        relation_names = all_relation_names
        rel_adjs = all_rel_adjs
    else:
        picked = [str(x) for x in use_relations]
        idx_map = {n: i for i, n in enumerate(all_relation_names)}
        keep_idx = [idx_map[n] for n in picked if n in idx_map]
        if not keep_idx:
            raise ValueError("gnn.use_relations is set but no valid relation name found")
        relation_names = [all_relation_names[i] for i in keep_idx]
        rel_adjs = all_rel_adjs[keep_idx]

    regime_cols = [c for c in ["mkt_ret_1", "mkt_ret_5", "mkt_vol_20", "mkt_drawdown_60"] if c in df.columns]
    if not regime_cols:
        regime_cols = [feature_cols[0]]

    snaps = date_snapshots(trv, stocks, feature_cols, regime_cols)
    if not snaps:
        raise ValueError("No GNN train snapshots for export")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    adjs_t = torch.tensor(rel_adjs, dtype=torch.float32, device=device)

    # Build fixed_rel_w when use_gate=False
    use_gate_flag = bool(gcfg.get("use_gate", True))
    fixed_rel_w = None
    if not use_gate_flag:
        rw_cfg = gcfg.get("relation_weights")
        if rw_cfg is not None:
            arr = np.asarray(rw_cfg, dtype=np.float32).reshape(-1)
            if arr.shape[0] == len(relation_names):
                s = float(arr.sum())
                fixed_rel_w = (arr / s).astype(np.float32) if s > 0 else arr

    model = HeteroRegimeGNN(
        in_dim=len(feature_cols),
        hidden=int(gcfg.get("hidden_size", 128)),
        n_rel=rel_adjs.shape[0],
        regime_dim=len(regime_cols),
        dropout=float(gcfg.get("dropout", 0.25)),
        num_classes=n_classes,
        use_gate=use_gate_flag,
        fixed_rel_w=fixed_rel_w,
        mlp_layers=int(gcfg.get("mlp_layers", 0)),
        mlp_hidden=int(gcfg.get("mlp_hidden", gcfg.get("hidden_size", 128))),
    ).to(device)

    class_counts = trv["label"].value_counts().reindex(range(n_classes), fill_value=0).astype(float).values
    class_counts = np.maximum(class_counts, 1.0)
    class_weights = class_counts.sum() / (n_classes * class_counts)
    criterion = torch.nn.CrossEntropyLoss(weight=torch.tensor(class_weights, dtype=torch.float32, device=device))
    opt = torch.optim.Adam(model.parameters(), lr=float(gcfg.get("lr", 8e-4)), weight_decay=float(gcfg.get("weight_decay", 1e-4)))

    model.train()
    for _ in range(max(10, int(gcfg.get("epochs", 80)) // 2)):
        for _, x_np, y_np, mask_np, regime_np in snaps:
            x = torch.tensor(x_np, dtype=torch.float32, device=device)
            y_all = torch.tensor(y_np, dtype=torch.long, device=device)
            mask = torch.tensor(mask_np, dtype=torch.bool, device=device)
            regime = torch.tensor(regime_np, dtype=torch.float32, device=device)
            opt.zero_grad()
            logits, _ = model(x, adjs_t, regime)
            loss = criterion(logits[mask], y_all[mask])
            loss.backward()
            opt.step()

    pt_path = out_dir / "gnn_prod.pt"
    torch.save(model.state_dict(), pt_path)

    meta = {
        "model_type": "gnn_v2_hetero_regime",
        "n_classes": n_classes,
        "feature_cols": feature_cols,
        "regime_cols": regime_cols,
        "stocks": stocks,
        "relation_names": relation_names,
        "adj_matrices": rel_adjs,
        "use_gate": use_gate_flag,
        "fixed_rel_w": fixed_rel_w,
        "hidden_size": int(gcfg.get("hidden_size", 128)),
        "mlp_layers": int(gcfg.get("mlp_layers", 0)),
        "mlp_hidden": int(gcfg.get("mlp_hidden", gcfg.get("hidden_size", 128))),
        "dropout": float(gcfg.get("dropout", 0.25)),
        "threshold": gcfg.get("binary_threshold", mcfg.get("binary_threshold")),
        "label_horizon": int(cfg["label"]["horizon"]),
        "weights_path": str(pt_path),
    }
    pkl_path = out_dir / "gnn_prod_meta.pkl"
    with open(pkl_path, "wb") as f:
        pickle.dump(meta, f)
    return pt_path, pkl_path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config_prod.yaml")
    parser.add_argument("--model", choices=["lgbm", "lstm", "gnn", "all"], default="all")
    parser.add_argument("--out-dir", default="outputs/artifacts")
    args = parser.parse_args()

    cfg = load_config(args.config)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    base_df, industry, feature_cols = build_base_dataset(cfg)
    df = split_latest(base_df, cfg)

    if args.model in {"lgbm", "all"}:
        p = export_lgbm(df, feature_cols, cfg, out_dir)
        print("lgbm artifact:", p)

    if args.model in {"lstm", "all"}:
        pt, meta = export_lstm(df, feature_cols, cfg, out_dir)
        print("lstm artifact:", pt, meta)

    if args.model in {"gnn", "all"}:
        pt, meta = export_gnn(df, industry, feature_cols, cfg, out_dir)
        print("gnn artifact:", pt, meta)


if __name__ == "__main__":
    np.random.seed(42)
    torch.manual_seed(42)
    main()
