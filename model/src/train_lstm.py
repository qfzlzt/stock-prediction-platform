from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
import torch
from torch import nn
from torch.utils.data import DataLoader, Dataset

from .evaluate import attach_pred_columns, best_binary_threshold, cls_metrics


class SeqDataset(Dataset):
    def __init__(self, X: np.ndarray, y: np.ndarray):
        self.X = torch.tensor(X, dtype=torch.float32)
        self.y = torch.tensor(y, dtype=torch.long)

    def __len__(self) -> int:
        return len(self.y)

    def __getitem__(self, idx: int):
        return self.X[idx], self.y[idx]


class LSTMClassifier(nn.Module):
    def __init__(self, in_dim: int, hidden: int, num_layers: int, dropout: float, num_classes: int):
        super().__init__()
        self.lstm = nn.LSTM(
            input_size=in_dim,
            hidden_size=hidden,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0.0,
        )
        self.head = nn.Sequential(
            nn.Dropout(dropout),
            nn.Linear(hidden, num_classes),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        out, _ = self.lstm(x)
        last = out[:, -1, :]
        return self.head(last)


def build_sequences(df: pd.DataFrame, feature_cols: List[str], lookback: int) -> Tuple[np.ndarray, np.ndarray, pd.DataFrame]:
    xs, ys, rows = [], [], []
    for _, g in df.groupby("stock"):
        g = g.sort_values("date").reset_index(drop=True)
        vals = g[feature_cols].values
        lbl = g["label"].values
        for i in range(lookback, len(g)):
            if np.isnan(lbl[i]):
                continue
            xs.append(vals[i - lookback : i])
            ys.append(int(lbl[i]))
            rows.append(g.loc[i, ["date", "stock", "fwd_ret", "fwd_ret_1d", "label"]])
    if not xs:
        return np.empty((0, lookback, len(feature_cols))), np.array([]), pd.DataFrame(columns=["date", "stock", "fwd_ret", "fwd_ret_1d", "label"])
    meta = pd.DataFrame(rows)
    return np.array(xs, dtype=np.float32), np.array(ys, dtype=np.int64), meta


def train_predict_lstm(df: pd.DataFrame, feature_cols: List[str], model_cfg: Dict, n_classes: int) -> tuple[pd.DataFrame, Dict]:
    cfg = model_cfg["lstm"]
    lookback = int(cfg.get("lookback", 20))

    train = df[df["split"] == "train"].dropna(subset=["label"])
    valid = df[df["split"] == "valid"].dropna(subset=["label"])
    test = df[df["split"] == "test"].dropna(subset=["label"])

    X_train, y_train, _ = build_sequences(train, feature_cols, lookback)
    X_valid, y_valid, _ = build_sequences(valid, feature_cols, lookback)
    X_test, y_test, test_meta = build_sequences(test, feature_cols, lookback)

    if len(y_train) == 0 or len(y_test) == 0:
        raise ValueError("LSTM sequence data is empty. Check split range and lookback.")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = LSTMClassifier(
        in_dim=len(feature_cols),
        hidden=int(cfg.get("hidden_size", 64)),
        num_layers=int(cfg.get("num_layers", 2)),
        dropout=float(cfg.get("dropout", 0.2)),
        num_classes=n_classes,
    ).to(device)

    optimizer = torch.optim.Adam(model.parameters(), lr=float(cfg.get("lr", 1e-3)))
    criterion = nn.CrossEntropyLoss()

    train_loader = DataLoader(SeqDataset(X_train, y_train), batch_size=int(cfg.get("batch_size", 128)), shuffle=True)
    valid_loader = DataLoader(SeqDataset(X_valid, y_valid), batch_size=256, shuffle=False) if len(y_valid) else None

    best_state = None
    best_val = float("inf")
    patience = int(cfg.get("patience", 5))
    bad = 0

    for _ in range(int(cfg.get("epochs", 30))):
        model.train()
        for xb, yb in train_loader:
            xb, yb = xb.to(device), yb.to(device)
            optimizer.zero_grad()
            loss = criterion(model(xb), yb)
            loss.backward()
            optimizer.step()

        val_loss = 0.0
        if valid_loader is not None:
            model.eval()
            n = 0
            with torch.no_grad():
                for xb, yb in valid_loader:
                    xb, yb = xb.to(device), yb.to(device)
                    logits = model(xb)
                    l = criterion(logits, yb).item()
                    val_loss += l * len(yb)
                    n += len(yb)
            val_loss = val_loss / max(n, 1)
        else:
            val_loss = 0.0

        if val_loss < best_val:
            best_val = val_loss
            best_state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}
            bad = 0
        else:
            bad += 1
            if bad >= patience:
                break

    if best_state is not None:
        model.load_state_dict(best_state)

    model.eval()
    t = 0.5
    if n_classes == 2:
        t_cfg = model_cfg.get("binary_threshold")
        if t_cfg is not None:
            t = float(t_cfg)
        elif len(y_valid):
            with torch.no_grad():
                valid_logits = model(torch.tensor(X_valid, dtype=torch.float32, device=device)).cpu().numpy()
            valid_prob = torch.softmax(torch.tensor(valid_logits), dim=1).numpy()[:, 1]
            t = best_binary_threshold(y_valid, valid_prob)

    with torch.no_grad():
        logits = model(torch.tensor(X_test, dtype=torch.float32, device=device)).cpu().numpy()
    prob = torch.softmax(torch.tensor(logits), dim=1).numpy()

    pred_df = attach_pred_columns(test_meta.copy(), prob)
    if n_classes == 2:
        pred_df["pred_label"] = (pred_df["proba_1"].values >= t).astype(int)
    metrics = cls_metrics(y_test, pred_df["pred_label"].values)
    return pred_df, metrics
