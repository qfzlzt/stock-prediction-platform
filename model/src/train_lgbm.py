from __future__ import annotations

from typing import Dict, List

import lightgbm as lgb
import numpy as np
import pandas as pd
from sklearn.utils.class_weight import compute_class_weight

from .evaluate import attach_pred_columns, best_binary_threshold, cls_metrics


def train_predict_lgbm(df: pd.DataFrame, feature_cols: List[str], model_cfg: Dict, n_classes: int) -> tuple[pd.DataFrame, Dict]:
    train = df[df["split"] == "train"].dropna(subset=["label"])
    valid = df[df["split"] == "valid"].dropna(subset=["label"])
    test = df[df["split"] == "test"].dropna(subset=["label"])

    X_train = train[feature_cols].values
    y_train = train["label"].astype(int).values

    classes = np.unique(y_train)
    cw = compute_class_weight(class_weight="balanced", classes=classes, y=y_train)
    cw_map = {int(c): float(w) for c, w in zip(classes, cw)}
    sample_weight = np.array([cw_map[int(y)] for y in y_train])

    clf = lgb.LGBMClassifier(
        objective="multiclass",
        num_class=n_classes,
        random_state=model_cfg.get("random_state", 42),
        n_estimators=model_cfg["lgbm"].get("n_estimators", 500),
        learning_rate=model_cfg["lgbm"].get("learning_rate", 0.03),
        num_leaves=model_cfg["lgbm"].get("num_leaves", 31),
        min_child_samples=model_cfg["lgbm"].get("min_child_samples", 60),
        subsample=model_cfg["lgbm"].get("subsample", 0.8),
        colsample_bytree=model_cfg["lgbm"].get("colsample_bytree", 0.8),
        verbosity=-1,
    )
    clf.fit(X_train, y_train, sample_weight=sample_weight)

    prob = clf.predict_proba(test[feature_cols])
    pred_df = attach_pred_columns(test[["date", "stock", "fwd_ret", "fwd_ret_1d", "label"]].copy(), prob)
    if n_classes == 2 and len(valid):
        t_cfg = model_cfg.get("binary_threshold")
        if t_cfg is None:
            valid_prob = clf.predict_proba(valid[feature_cols])[:, 1]
            t = best_binary_threshold(valid["label"].astype(int).values, valid_prob)
        else:
            t = float(t_cfg)
        pred_df["pred_label"] = (pred_df["proba_1"].values >= t).astype(int)

    metrics = cls_metrics(test["label"].astype(int).values, pred_df["pred_label"].values)
    return pred_df, metrics
