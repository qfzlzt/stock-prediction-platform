from __future__ import annotations

from typing import Dict

import numpy as np
import pandas as pd


def _labels_union(y_true: np.ndarray, y_pred: np.ndarray) -> np.ndarray:
    return np.unique(np.concatenate([np.asarray(y_true), np.asarray(y_pred)]))


def _per_class_stats(y_true: np.ndarray, y_pred: np.ndarray, labels: np.ndarray) -> tuple[dict[str, float], dict[str, float]]:
    recalls: dict[str, float] = {}
    f1s: dict[str, float] = {}
    for c in labels:
        t = y_true == c
        p = y_pred == c
        tp = float(np.sum(t & p))
        fn = float(np.sum(t & (~p)))
        fp = float(np.sum((~t) & p))
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        f1 = (2.0 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0
        recalls[str(int(c)) if np.issubdtype(type(c), np.integer) else str(c)] = float(recall)
        f1s[str(int(c)) if np.issubdtype(type(c), np.integer) else str(c)] = float(f1)
    return recalls, f1s


def _accuracy(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    if y_true.size == 0:
        return 0.0
    return float(np.mean(y_true == y_pred))


def _balanced_accuracy(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    labels = _labels_union(y_true, y_pred)
    recalls, _ = _per_class_stats(np.asarray(y_true), np.asarray(y_pred), labels)
    if not recalls:
        return 0.0
    return float(np.mean(list(recalls.values())))


def _macro_f1(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    labels = _labels_union(y_true, y_pred)
    _, f1s = _per_class_stats(np.asarray(y_true), np.asarray(y_pred), labels)
    if not f1s:
        return 0.0
    return float(np.mean(list(f1s.values())))


def cls_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict:
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    labels = _labels_union(y_true, y_pred)
    per_class_recall, _ = _per_class_stats(y_true, y_pred, labels)
    out = {
        "accuracy": _accuracy(y_true, y_pred),
        "balanced_accuracy": _balanced_accuracy(y_true, y_pred),
        "macro_f1": _macro_f1(y_true, y_pred),
        "per_class_recall": per_class_recall,
    }
    return out


def attach_pred_columns(df: pd.DataFrame, prob: np.ndarray) -> pd.DataFrame:
    out = df.copy()
    for i in range(prob.shape[1]):
        out[f"proba_{i}"] = prob[:, i]
    out["pred_label"] = prob.argmax(axis=1)
    return out


def best_binary_threshold(y_true: np.ndarray, proba_pos: np.ndarray, objective: str = "balanced") -> float:
    y = np.asarray(y_true).astype(int)
    p = np.asarray(proba_pos).astype(float)
    best_t = 0.5
    best_s = -1.0
    for t in np.linspace(0.1, 0.9, 161):
        pred = (p >= t).astype(int)
        bal = _balanced_accuracy(y, pred)
        mf1 = _macro_f1(y, pred)
        if objective == "macro_f1":
            s = mf1
        elif objective == "combo":
            s = 0.5 * bal + 0.5 * mf1
        else:
            s = bal
        if s > best_s + 1e-12:
            best_s = s
            best_t = float(t)
    return best_t
