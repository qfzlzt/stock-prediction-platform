"""
sentiment.py  —— 基于 FinBERT 的研报情绪分析
模型：yiyanghkust/finbert-tone-chinese
标签：Positive / Neutral / Negative
"""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Dict, List

import pymysql
import pymysql.cursors
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

log = logging.getLogger(__name__)

_MODEL_NAME = "yiyanghkust/finbert-tone-chinese"
_tok = None
_mdl = None


def _load_model():
    global _tok, _mdl
    if _tok is None:
        log.info("加载 FinBERT 模型：%s", _MODEL_NAME)
        _tok = AutoTokenizer.from_pretrained(_MODEL_NAME)
        _mdl = AutoModelForSequenceClassification.from_pretrained(_MODEL_NAME)
        _mdl.eval()
        log.info("FinBERT 加载完成，标签：%s", _mdl.config.id2label)


def _analyze_text(text: str) -> Dict[str, float]:
    """对单段文本运行 FinBERT，返回三类概率。"""
    _load_model()
    inputs = _tok(
        text,
        return_tensors="pt",
        truncation=True,
        max_length=512,
        padding=True,
    )
    with torch.no_grad():
        logits = _mdl(**inputs).logits
    proba = torch.softmax(logits, dim=1)[0].tolist()
    id2label = _mdl.config.id2label   # {0:'Neutral',1:'Positive',2:'Negative'}

    result = {}
    for idx, p in enumerate(proba):
        label = id2label[idx].lower()   # neutral / positive / negative
        result[label] = round(p, 4)
    return result


def analyze_stock_sentiment(conn, stock_code: str) -> Dict:
    """
    分析某只股票的所有研报情绪，返回汇总结果。
    先查缓存表 report_sentiment，未缓存的才跑模型。
    """
    # 1. 拉该股全部报告
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT reportId, reportTitle, reportAbstract
            FROM analysis_report_library
            WHERE stockCode = %s
            ORDER BY reportGenerateTime DESC
            """,
            (stock_code,),
        )
        reports = cur.fetchall()

    if not reports:
        return {
            "stock_code": stock_code,
            "report_count": 0,
            "msg": "暂无研报数据",
            "reports": [],
        }

    results: List[Dict] = []

    for rpt in reports:
        rid = rpt["reportId"]
        title = rpt["reportTitle"] or ""
        abstract = rpt["reportAbstract"] or ""

        # 先查缓存
        with conn.cursor() as cur:
            cur.execute(
                "SELECT proba_pos, proba_neu, proba_neg, sentiment FROM report_sentiment WHERE reportId=%s",
                (rid,),
            )
            cached = cur.fetchone()

        if cached:
            proba_pos = cached["proba_pos"]
            proba_neu = cached["proba_neu"]
            proba_neg = cached["proba_neg"]
            sentiment = cached["sentiment"]
        else:
            # 拼接标题+摘要作为输入
            text = title + "。" + abstract if abstract else title
            proba = _analyze_text(text)
            proba_pos = proba.get("positive", 0.0)
            proba_neu = proba.get("neutral", 0.0)
            proba_neg = proba.get("negative", 0.0)

            # 判断主情绪
            if proba_pos >= proba_neu and proba_pos >= proba_neg:
                sentiment = "Positive"
            elif proba_neg >= proba_pos and proba_neg >= proba_neu:
                sentiment = "Negative"
            else:
                sentiment = "Neutral"

            # 写缓存
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO report_sentiment
                        (stockCode, reportId, reportTitle, proba_pos, proba_neu, proba_neg, sentiment)
                    VALUES (%s,%s,%s,%s,%s,%s,%s)
                    ON DUPLICATE KEY UPDATE
                        proba_pos=VALUES(proba_pos),
                        proba_neu=VALUES(proba_neu),
                        proba_neg=VALUES(proba_neg),
                        sentiment=VALUES(sentiment),
                        analyzedAt=NOW()
                    """,
                    (stock_code, rid, title, proba_pos, proba_neu, proba_neg, sentiment),
                )
            conn.commit()
            log.info("  %s [%s] -> %s (pos=%.1f%%)", rid, title[:20], sentiment, proba_pos * 100)

        results.append(
            {
                "reportId": rid,
                "title": title,
                "proba_pos": round(proba_pos * 100, 1),
                "proba_neu": round(proba_neu * 100, 1),
                "proba_neg": round(proba_neg * 100, 1),
                "sentiment": sentiment,
            }
        )

    # 汇总：加权平均
    n = len(results)
    avg_pos = round(sum(r["proba_pos"] for r in results) / n, 1)
    avg_neu = round(sum(r["proba_neu"] for r in results) / n, 1)
    avg_neg = round(sum(r["proba_neg"] for r in results) / n, 1)

    if avg_pos >= avg_neu and avg_pos >= avg_neg:
        overall = "Positive"
        overall_cn = "看多"
        overall_color = "#67c23a"
    elif avg_neg >= avg_pos and avg_neg >= avg_neu:
        overall = "Negative"
        overall_cn = "看空"
        overall_color = "#f56c6c"
    else:
        overall = "Neutral"
        overall_cn = "中性"
        overall_color = "#909399"

    return {
        "stock_code": stock_code,
        "report_count": n,
        "overall_sentiment": overall,
        "overall_sentiment_cn": overall_cn,
        "overall_color": overall_color,
        "avg_pos": avg_pos,
        "avg_neu": avg_neu,
        "avg_neg": avg_neg,
        "reports": results,
    }
