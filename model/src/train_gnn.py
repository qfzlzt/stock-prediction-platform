from __future__ import annotations

from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
import torch
from torch import nn

from .evaluate import best_binary_threshold, cls_metrics


def normalized_adj(adj: np.ndarray) -> np.ndarray:
    a = adj + np.eye(adj.shape[0])
    d = np.sum(a, axis=1)
    d_inv_sqrt = np.diag(1.0 / np.sqrt(np.maximum(d, 1e-12)))
    return d_inv_sqrt @ a @ d_inv_sqrt


def build_adj_from_industry(stocks: List[str], industry_map: pd.DataFrame) -> np.ndarray:
    n = len(stocks)
    adj = np.zeros((n, n), dtype=np.float32)
    d = industry_map.set_index("stock")["industry_l3"].to_dict()
    for i, si in enumerate(stocks):
        for j, sj in enumerate(stocks):
            if i != j and d.get(si) == d.get(sj):
                adj[i, j] = 1.0
    return adj


def build_corr_adj(df_train: pd.DataFrame, stocks: List[str], window: int, threshold: float) -> np.ndarray:
    ret = df_train.pivot(index="date", columns="stock", values="fwd_ret").sort_index().tail(window)
    corr = ret.corr().fillna(0.0)
    n = len(stocks)
    adj = np.zeros((n, n), dtype=np.float32)
    for i, si in enumerate(stocks):
        for j, sj in enumerate(stocks):
            if i != j and si in corr.index and sj in corr.columns and corr.loc[si, sj] >= threshold:
                adj[i, j] = 1.0
    return adj


def build_volume_sync_adj(df_train: pd.DataFrame, stocks: List[str], window: int, threshold: float) -> np.ndarray:
    vol = df_train.pivot(index="date", columns="stock", values="volume").sort_index().ffill().pct_change().tail(window)
    corr = vol.corr().fillna(0.0)
    n = len(stocks)
    adj = np.zeros((n, n), dtype=np.float32)
    for i, si in enumerate(stocks):
        for j, sj in enumerate(stocks):
            if i != j and si in corr.index and sj in corr.columns and corr.loc[si, sj] >= threshold:
                adj[i, j] = 1.0
    return adj


def build_valuation_sim_adj(df_train: pd.DataFrame, stocks: List[str], threshold: float) -> np.ndarray:
    latest = df_train.sort_values("date").groupby("stock").tail(1).set_index("stock")
    pe = latest.get("pe_ttm", pd.Series(index=latest.index, data=np.nan)).replace([np.inf, -np.inf], np.nan)
    pb = latest.get("pb_mrq", pd.Series(index=latest.index, data=np.nan)).replace([np.inf, -np.inf], np.nan)
    pe = (pe - pe.mean()) / (pe.std() if pe.std() and pe.std() > 0 else 1.0)
    pb = (pb - pb.mean()) / (pb.std() if pb.std() and pb.std() > 0 else 1.0)

    n = len(stocks)
    adj = np.zeros((n, n), dtype=np.float32)
    for i, si in enumerate(stocks):
        for j, sj in enumerate(stocks):
            if i == j:
                continue
            vi = np.array([pe.get(si, 0.0), pb.get(si, 0.0)], dtype=float)
            vj = np.array([pe.get(sj, 0.0), pb.get(sj, 0.0)], dtype=float)
            dist = float(np.linalg.norm(np.nan_to_num(vi) - np.nan_to_num(vj)))
            sim = np.exp(-dist)
            if sim >= threshold:
                adj[i, j] = 1.0
    return adj


def date_snapshots(
    df: pd.DataFrame,
    stocks: List[str],
    feat_cols: List[str],
    regime_cols: List[str],
) -> List[Tuple[pd.Timestamp, np.ndarray, np.ndarray, np.ndarray, np.ndarray]]:
    snaps = []
    all_dates = sorted(df["date"].unique())
    idx = pd.MultiIndex.from_product([all_dates, stocks], names=["date", "stock"])
    temp = df.set_index(["date", "stock"]).reindex(idx).reset_index().copy()

    for dt, g in temp.groupby("date"):
        g = g.sort_values("stock")
        x = g[feat_cols].fillna(0.0).values.astype(np.float32)
        y = g["label"].values
        mask = ~np.isnan(y)
        if mask.sum() == 0:
            continue
        # Regime is date-level context; use cross-stock mean for robustness.
        regime = g[regime_cols].replace([np.inf, -np.inf], np.nan).fillna(0.0).mean().values.astype(np.float32)
        snaps.append((pd.Timestamp(dt), x, y.astype(np.float32), mask.astype(bool), regime))
    return snaps


class MultiRelGraphLayer(nn.Module):
    def __init__(self, in_dim: int, out_dim: int, n_rel: int, dropout: float):
        super().__init__()
        self.self_lin = nn.Linear(in_dim, out_dim)
        self.rel_lins = nn.ModuleList([nn.Linear(in_dim, out_dim) for _ in range(n_rel)])
        self.norm = nn.LayerNorm(out_dim)
        self.drop = nn.Dropout(dropout)

    def forward(self, x: torch.Tensor, adjs: torch.Tensor, rel_w: torch.Tensor) -> torch.Tensor:
        # x: [N, F], adjs: [R, N, N], rel_w: [R]
        h_self = self.self_lin(x)
        h_rel = []
        for r in range(adjs.shape[0]):
            h_rel.append(self.rel_lins[r](adjs[r] @ x))
        h_rel = torch.stack(h_rel, dim=0)  # [R, N, D]
        h = h_self + torch.sum(rel_w[:, None, None] * h_rel, dim=0)
        # Residual skip connection (only when in_dim == out_dim, e.g. hidden→hidden)
        if x.shape[-1] == h.shape[-1]:
            h = h + x
        h = self.norm(h)
        h = torch.relu(h)
        return self.drop(h)


class HeteroRegimeGNN(nn.Module):
    def __init__(
        self,
        in_dim: int,
        hidden: int,
        n_rel: int,
        regime_dim: int,
        dropout: float,
        num_classes: int,
        use_gate: bool = True,
        fixed_rel_w: np.ndarray | None = None,
        mlp_layers: int = 0,
        mlp_hidden: int | None = None,
    ):
        super().__init__()
        self.use_gate = use_gate
        self.fixed_rel_w = None if fixed_rel_w is None else torch.tensor(fixed_rel_w, dtype=torch.float32)
        if use_gate:
            self.gate = nn.Sequential(
                nn.Linear(regime_dim, hidden),
                nn.ReLU(),
                nn.Linear(hidden, n_rel),
            )
        self.g1 = MultiRelGraphLayer(in_dim, hidden, n_rel=n_rel, dropout=dropout)
        self.g2 = MultiRelGraphLayer(hidden, hidden, n_rel=n_rel, dropout=dropout)
        self.use_mlp_head = int(mlp_layers) > 0
        if self.use_mlp_head:
            h2 = int(mlp_hidden or hidden)
            layers: list[nn.Module] = []
            in_d = hidden
            for _ in range(int(mlp_layers)):
                layers.extend([nn.Linear(in_d, h2), nn.ReLU(), nn.Dropout(dropout)])
                in_d = h2
            self.head = nn.Sequential(*layers)
            self.cls = nn.Linear(in_d, num_classes)
        else:
            self.head = nn.Identity()
            self.cls = nn.Linear(hidden, num_classes)

    def forward(self, x: torch.Tensor, adjs: torch.Tensor, regime: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        if self.use_gate:
            rel_logits = self.gate(regime)
            rel_w = torch.softmax(rel_logits, dim=-1)
        else:
            if self.fixed_rel_w is not None and self.fixed_rel_w.numel() == adjs.shape[0]:
                rel_w = self.fixed_rel_w.to(device=x.device, dtype=x.dtype)
            else:
                rel_w = torch.full((adjs.shape[0],), 1.0 / max(adjs.shape[0], 1), dtype=x.dtype, device=x.device)
        h = self.g1(x, adjs, rel_w)
        h = self.g2(h, adjs, rel_w)
        h = self.head(h)
        return self.cls(h), rel_w


def ranking_loss_binary(
    prob_pos: torch.Tensor,
    y: torch.Tensor,
    margin: float = 0.02,
    mode: str = "mean_margin",
) -> torch.Tensor:
    pos = prob_pos[y == 1]
    neg = prob_pos[y == 0]
    if len(pos) == 0 or len(neg) == 0:
        return torch.tensor(0.0, device=prob_pos.device)
    if mode == "pairwise_logistic":
        # Encourage all positive samples to have higher score than negatives.
        diff = pos[:, None] - neg[None, :]
        return torch.nn.functional.softplus(-diff).mean()
    score = pos.mean() - neg.mean()
    return torch.relu(margin - score)


def train_predict_gnn(df: pd.DataFrame, feature_cols: List[str], industry_map: pd.DataFrame, model_cfg: Dict, n_classes: int) -> tuple[pd.DataFrame, Dict]:
    cfg = model_cfg["gnn"]
    seed = int(model_cfg.get("random_state", 42))
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    stocks = sorted(df["stock"].dropna().unique().tolist())

    train = df[df["split"] == "train"].dropna(subset=["label"])
    valid = df[df["split"] == "valid"].dropna(subset=["label"])
    test = df[df["split"] == "test"].dropna(subset=["label"])

    # Multi-relation graph
    ind_adj = build_adj_from_industry(stocks, industry_map)
    corr_adj = build_corr_adj(train, stocks, int(cfg.get("corr_window", 60)), float(cfg.get("corr_threshold", 0.2)))
    vol_adj = build_volume_sync_adj(train, stocks, int(cfg.get("vol_window", 60)), float(cfg.get("vol_threshold", 0.2)))
    val_adj = build_valuation_sim_adj(train, stocks, float(cfg.get("valuation_threshold", 0.6)))

    all_relation_names = ["industry", "corr", "volume_sync", "valuation_sim"]
    all_rel_adjs = np.stack([
        normalized_adj(ind_adj),
        normalized_adj(corr_adj),
        normalized_adj(vol_adj),
        normalized_adj(val_adj),
    ], axis=0).astype(np.float32)
    use_relations = cfg.get("use_relations")
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

    train_snaps = date_snapshots(train, stocks, feature_cols, regime_cols)
    valid_snaps = date_snapshots(valid, stocks, feature_cols, regime_cols)
    test_snaps = date_snapshots(test, stocks, feature_cols, regime_cols)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    adjs_t = torch.tensor(rel_adjs, dtype=torch.float32, device=device)

    fixed_rel_w = None
    if not bool(cfg.get("use_gate", True)):
        rw_cfg = cfg.get("relation_weights")
        if rw_cfg is not None:
            arr = np.asarray(rw_cfg, dtype=np.float32).reshape(-1)
            if arr.shape[0] == len(relation_names):
                s = float(arr.sum())
                if s > 0:
                    fixed_rel_w = (arr / s).astype(np.float32)

    model = HeteroRegimeGNN(
        in_dim=len(feature_cols),
        hidden=int(cfg.get("hidden_size", 128)),
        n_rel=rel_adjs.shape[0],
        regime_dim=len(regime_cols),
        dropout=float(cfg.get("dropout", 0.25)),
        num_classes=n_classes,
        use_gate=bool(cfg.get("use_gate", True)),
        fixed_rel_w=fixed_rel_w,
        mlp_layers=int(cfg.get("mlp_layers", 0)),
        mlp_hidden=int(cfg.get("mlp_hidden", cfg.get("hidden_size", 128))),
    ).to(device)

    lr = float(cfg.get("lr", 8e-4))
    wd = float(cfg.get("weight_decay", 1e-4))
    rank_lambda = float(cfg.get("rank_lambda", 0.4))
    rank_margin = float(cfg.get("rank_margin", 0.02))
    rank_mode = str(cfg.get("rank_mode", "mean_margin"))
    optim = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=wd)

    class_counts = train["label"].value_counts().reindex(range(n_classes), fill_value=0).astype(float).values
    class_counts = np.maximum(class_counts, 1.0)
    class_weights = class_counts.sum() / (n_classes * class_counts)
    w_tensor = torch.tensor(class_weights, dtype=torch.float32, device=device)
    ce = nn.CrossEntropyLoss(weight=w_tensor)

    best_val = float("inf")
    best_state = None
    best_relw = None
    patience = int(cfg.get("patience", 8))
    bad = 0

    for _ in range(int(cfg.get("epochs", 80))):
        model.train()
        for _, x_np, y_np, mask_np, regime_np in train_snaps:
            x = torch.tensor(x_np, dtype=torch.float32, device=device)
            y_all = torch.tensor(y_np, dtype=torch.long, device=device)
            mask = torch.tensor(mask_np, dtype=torch.bool, device=device)
            regime = torch.tensor(regime_np, dtype=torch.float32, device=device)

            optim.zero_grad()
            logits, rel_w = model(x, adjs_t, regime)
            y = y_all[mask]
            logit_m = logits[mask]
            loss = ce(logit_m, y)
            if n_classes == 2:
                p1 = torch.softmax(logit_m, dim=1)[:, 1]
                loss = loss + rank_lambda * ranking_loss_binary(p1, y, margin=rank_margin, mode=rank_mode)
            loss.backward()
            optim.step()

        model.eval()
        val_loss, n = 0.0, 0
        relw_acc = torch.zeros(rel_adjs.shape[0], device=device)
        with torch.no_grad():
            for _, x_np, y_np, mask_np, regime_np in valid_snaps:
                x = torch.tensor(x_np, dtype=torch.float32, device=device)
                y_all = torch.tensor(y_np, dtype=torch.long, device=device)
                mask = torch.tensor(mask_np, dtype=torch.bool, device=device)
                regime = torch.tensor(regime_np, dtype=torch.float32, device=device)
                logits, rel_w = model(x, adjs_t, regime)
                l = ce(logits[mask], y_all[mask]).item()
                val_loss += l * int(mask_np.sum())
                n += int(mask_np.sum())
                relw_acc += rel_w
        val_loss = val_loss / max(n, 1)

        if val_loss < best_val:
            best_val = val_loss
            best_state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}
            if len(valid_snaps):
                best_relw = (relw_acc / max(len(valid_snaps), 1)).detach().cpu().numpy().tolist()
            bad = 0
        else:
            bad += 1
            if bad >= patience:
                break

    if best_state is not None:
        model.load_state_dict(best_state)

    # Validation probabilities for calibration / dynamic threshold
    yv, pv = [], []
    if n_classes == 2 and valid_snaps:
        model.eval()
        with torch.no_grad():
            for _, x_np, y_np, mask_np, regime_np in valid_snaps:
                x = torch.tensor(x_np, dtype=torch.float32, device=device)
                regime = torch.tensor(regime_np, dtype=torch.float32, device=device)
                logits, _ = model(x, adjs_t, regime)
                prob = torch.softmax(logits, dim=1).cpu().numpy()
                yv.extend(y_np[mask_np].astype(int).tolist())
                pv.extend(prob[mask_np, 1].tolist())
    yv_np = np.asarray(yv, dtype=int)
    pv_np = np.asarray(pv, dtype=float)

    # Probability calibration on validation set
    calib_method = str(cfg.get("calibration", "none")).lower()
    calibrator = None
    if n_classes == 2 and len(yv_np) > 0 and np.unique(yv_np).shape[0] == 2:
        if calib_method == "isotonic":
            from sklearn.isotonic import IsotonicRegression

            ir = IsotonicRegression(out_of_bounds="clip")
            ir.fit(pv_np, yv_np)
            calibrator = ("isotonic", ir)
        elif calib_method in {"platt", "sigmoid"}:
            from sklearn.linear_model import LogisticRegression

            lr_cal = LogisticRegression(solver="lbfgs", max_iter=200)
            lr_cal.fit(pv_np.reshape(-1, 1), yv_np)
            calibrator = ("platt", lr_cal)

    # Threshold selection for binary
    t = 0.5
    if n_classes == 2:
        use_dynamic_threshold = bool(cfg.get("dynamic_threshold", False))
        t_cfg = cfg.get("binary_threshold", model_cfg.get("binary_threshold"))
        if (not use_dynamic_threshold) and (t_cfg is not None):
            t = float(t_cfg)
        elif len(yv_np) > 0:
            t_obj = str(cfg.get("threshold_objective", model_cfg.get("threshold_objective", "combo")))
            p_for_t = pv_np.copy()
            if calibrator is not None:
                if calibrator[0] == "isotonic":
                    p_for_t = calibrator[1].predict(p_for_t)
                else:
                    p_for_t = calibrator[1].predict_proba(p_for_t.reshape(-1, 1))[:, 1]
            t = best_binary_threshold(yv_np, p_for_t, objective=t_obj)

    # Test prediction
    rows = []
    model.eval()
    with torch.no_grad():
        for dt, x_np, y_np, mask_np, regime_np in test_snaps:
            x = torch.tensor(x_np, dtype=torch.float32, device=device)
            regime = torch.tensor(regime_np, dtype=torch.float32, device=device)
            logits, rel_w = model(x, adjs_t, regime)
            prob = torch.softmax(logits, dim=1).cpu().numpy()
            if n_classes == 2 and calibrator is not None:
                p1 = prob[:, 1]
                if calibrator[0] == "isotonic":
                    p1c = calibrator[1].predict(p1)
                else:
                    p1c = calibrator[1].predict_proba(p1.reshape(-1, 1))[:, 1]
                p1c = np.clip(p1c, 1e-6, 1.0 - 1e-6)
                prob[:, 1] = p1c
                prob[:, 0] = 1.0 - p1c

            for i, s in enumerate(stocks):
                if not mask_np[i]:
                    continue
                row = {
                    "date": dt,
                    "stock": s,
                    "fwd_ret": float(test[(test["date"] == dt) & (test["stock"] == s)]["fwd_ret"].iloc[0]),
                    "fwd_ret_1d": float(test[(test["date"] == dt) & (test["stock"] == s)]["fwd_ret_1d"].iloc[0]),
                    "label": int(y_np[i]),
                    "pred_label": int(prob[i].argmax()),
                }
                for k in range(n_classes):
                    row[f"proba_{k}"] = float(prob[i, k])
                for r_i, r_name in enumerate(relation_names):
                    row[f"relw_{r_name}"] = float(rel_w[r_i].cpu().item())
                rows.append(row)

    pred_df = pd.DataFrame(rows).sort_values(["date", "stock"]).reset_index(drop=True)
    if n_classes == 2 and not pred_df.empty:
        pred_df["pred_label"] = (pred_df["proba_1"].values >= t).astype(int)

    metrics = cls_metrics(pred_df["label"].values, pred_df["pred_label"].values)
    if best_relw is not None:
        metrics["avg_relation_weights_valid"] = {r_name: float(best_relw[i]) for i, r_name in enumerate(relation_names)}
    metrics["relation_names"] = relation_names
    metrics["use_gate"] = bool(cfg.get("use_gate", True))
    metrics["mlp_layers"] = int(cfg.get("mlp_layers", 0))
    metrics["mlp_hidden"] = int(cfg.get("mlp_hidden", cfg.get("hidden_size", 128)))
    metrics["rank_mode"] = rank_mode
    metrics["rank_lambda"] = rank_lambda
    metrics["rank_margin"] = rank_margin
    metrics["calibration"] = calib_method
    metrics["dynamic_threshold"] = bool(cfg.get("dynamic_threshold", False))
    if fixed_rel_w is not None:
        metrics["relation_weights_used"] = {r_name: float(fixed_rel_w[i]) for i, r_name in enumerate(relation_names)}
    metrics["threshold"] = float(t)
    return pred_df, metrics
