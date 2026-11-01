"""
app.py  —— AI 预测微服务（Flask）
────────────────────────────────
默认监听 http://localhost:8083

接口列表：
  GET  /api/ml/health
      健康检查

  GET  /api/ml/predict?stockCode=688001.SH&model=lgbm
      参数：
        stockCode  股票代码（必填）
        model      lgbm | lstm | gnn  （默认 lgbm）
      返回：{ code:200, data: { pred_label, label_name, confidence, ... } }

  POST /api/ml/build-features
      触发特征构建（可选 body: {"stockCode":"688001.SH"}）
      若不传 stockCode 则处理所有正常交易股票（耗时较长）

运行方式：
  cd predict_service
  python app.py
"""
from __future__ import annotations

from settings import MODEL_SRC_DIR, ARTIFACTS_DIR, INDUSTRY_EXCEL, database_config


import logging
import sys
from pathlib import Path

import pandas as pd
import pymysql
import pymysql.cursors
from flask import Flask, jsonify, request
from flask_cors import CORS

# ─── 将模型源码目录加入 sys.path ──────────────────────────────

if str(MODEL_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(MODEL_SRC_DIR))

from build_features import (
    DB_CONFIG,
    build_features_for_stock,
    compute_market_features,
    ensure_table,
    get_all_stock_codes,
    load_industry_map,
    read_market_data,
)
from predictor import predict_gnn, predict_lgbm, predict_lstm
from sentiment import analyze_stock_sentiment

# ─── 日志 ─────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    stream=sys.stdout,
)
log = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)    # 允许前端跨域调用


# ══════════════════════════════════════════════════════════════
# 数据库辅助
# ══════════════════════════════════════════════════════════════
def _get_conn():
    return pymysql.connect(**DB_CONFIG)


# ── 启动时自动建表 ────────────────────────────────────────────
def _init_db() -> None:
    try:
        conn = _get_conn()
        ensure_table(conn)
        conn.close()
    except Exception as exc:
        log.warning("启动时建表失败（数据库可能未就绪）：%s", exc)


_init_db()


def _query_df(conn, sql: str, params: tuple = ()) -> pd.DataFrame:
    """用游标执行 SQL，返回 DataFrame（兼容 pymysql 原生连接）。"""
    with conn.cursor() as cur:
        cur.execute(sql, params)
        rows = cur.fetchall()
        if not rows:
            return pd.DataFrame()
        cols = [d[0] for d in cur.description]
        return pd.DataFrame(rows, columns=cols)


def _get_stock_features(conn, stock_code: str) -> pd.DataFrame:
    """从 model_input_features 读取单只股票的全部历史特征。"""
    sql = """
        SELECT * FROM model_input_features
        WHERE stock_code = %s
        ORDER BY trade_date ASC
    """
    df = _query_df(conn, sql, (stock_code,))
    if not df.empty:
        df["trade_date"] = pd.to_datetime(df["trade_date"])
    return df


def _get_all_latest_features(conn) -> pd.DataFrame:
    """读取所有股票最新一行特征（供 GNN 使用）。"""
    sql = """
        SELECT m.*
        FROM model_input_features m
        INNER JOIN (
            SELECT stock_code, MAX(trade_date) AS max_date
            FROM model_input_features
            GROUP BY stock_code
        ) t ON m.stock_code = t.stock_code
             AND m.trade_date = t.max_date
    """
    df = _query_df(conn, sql)
    if not df.empty:
        df["trade_date"] = pd.to_datetime(df["trade_date"])
    return df


# ══════════════════════════════════════════════════════════════
# 路由
# ══════════════════════════════════════════════════════════════
@app.route("/api/ml/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "ml-prediction-service", "port": 8083})


@app.route("/api/ml/predict", methods=["GET"])
def predict():
    """
    GET /api/ml/predict?stockCode=688001.SH&model=lgbm

    返回格式：
    {
      "code": 200,
      "data": {
        "model":        "LightGBM",
        "stock_code":   "688001.SH",
        "trade_date":   "2026-03-25",
        "pred_label":   1,
        "label_name":   "看涨",
        "confidence":   68.5,
        "proba_up":     68.5,
        "proba_down":   31.5,
        "threshold_pct": 52.0,
        "horizon_days": 5,
        "desc":         "...",
        // GNN 额外字段
        "relation_weights": { "industry": 0.4, "corr": 0.3, "valuation_sim": 0.3 },
        "n_stocks_graph": 21,
        // LSTM 额外字段
        "sequence_len": 20
      }
    }
    """
    stock_code = request.args.get("stockCode", "").strip()
    model_name = request.args.get("model", "lgbm").strip().lower()

    if not stock_code:
        return jsonify({"code": 400, "msg": "参数 stockCode 不能为空"}), 400
    if model_name not in ("lgbm", "lstm", "gnn"):
        return jsonify({"code": 400, "msg": "model 参数必须为 lgbm / lstm / gnn"}), 400

    log.info("预测请求：stock=%s  model=%s", stock_code, model_name)

    try:
        conn = _get_conn()
        try:
            if model_name in ("lgbm", "lstm"):
                feature_df = _get_stock_features(conn, stock_code)
                if feature_df.empty:
                    return jsonify({
                        "code": 404,
                        "msg": (
                            f"未找到 {stock_code} 的特征数据，"
                            "请先执行 build_features.py 构建特征"
                        )
                    }), 404
                if model_name == "lgbm":
                    result = predict_lgbm(stock_code, feature_df)
                else:
                    result = predict_lstm(stock_code, feature_df)

            else:   # gnn
                all_df = _get_all_latest_features(conn)
                if all_df.empty:
                    return jsonify({
                        "code": 404,
                        "msg": "未找到任何特征数据，请先执行 build_features.py 构建特征"
                    }), 404
                result = predict_gnn(stock_code, all_df)

        finally:
            conn.close()

        if "error" in result:
            return jsonify({"code": 422, "msg": result["error"]}), 422

        log.info("预测完成：%s -> %s (%.1f%%)",
                 stock_code, result.get("label_name"), result.get("confidence", 0))
        return jsonify({"code": 200, "data": result})

    except BaseException as exc:
        log.exception("预测异常 stock=%s model=%s: %s", stock_code, model_name, exc)
        import traceback
        return jsonify({"code": 500, "msg": f"服务器内部错误：{type(exc).__name__}: {exc}",
                        "traceback": traceback.format_exc()}), 500


@app.route("/api/ml/sentiment", methods=["GET"])
def sentiment():
    """
    GET /api/ml/sentiment?stockCode=688001.SH
    返回该股票所有研报的 FinBERT 情绪分析结果（带缓存）。
    """
    stock_code = request.args.get("stockCode", "").strip()
    if not stock_code:
        return jsonify({"code": 400, "msg": "参数 stockCode 不能为空"}), 400

    log.info("情绪分析请求：stock=%s", stock_code)
    try:
        conn = _get_conn()
        try:
            result = analyze_stock_sentiment(conn, stock_code)
        finally:
            conn.close()
        return jsonify({"code": 200, "data": result})
    except Exception as exc:
        log.exception("情绪分析异常 stock=%s: %s", stock_code, exc)
        return jsonify({"code": 500, "msg": str(exc)}), 500


@app.route("/api/ml/build-features", methods=["POST"])
def build_features_endpoint():
    """
    POST /api/ml/build-features
    Body（可选）：{"stockCode": "688001.SH"}
    若不传 stockCode 则处理所有正常交易股票（耗时较长，建议单独脚本执行）。
    """
    body       = request.get_json(silent=True) or {}
    stock_code = body.get("stockCode", "").strip() or None

    log.info("特征构建请求：stock=%s", stock_code or "全部")

    try:
        conn = _get_conn()
        try:
            raw_mkt    = read_market_data(conn, days=200)
            market_df  = compute_market_features(raw_mkt) if not raw_mkt.empty else pd.DataFrame()
            industry_map = load_industry_map()

            if stock_code:
                n = build_features_for_stock(conn, stock_code, market_df, industry_map)
                msg = f"{stock_code} 特征构建完成，写入 {n} 行"
            else:
                stocks  = get_all_stock_codes(conn)
                total   = 0
                errors  = 0
                for code in stocks:
                    try:
                        total += build_features_for_stock(conn, code, market_df, industry_map)
                    except Exception as exc:
                        log.warning("  %s 跳过：%s", code, exc)
                        errors += 1
                msg = (f"全部股票特征构建完成：{len(stocks)} 只，"
                       f"写入 {total} 行，失败 {errors} 只")
        finally:
            conn.close()

        log.info(msg)
        return jsonify({"code": 200, "msg": msg})

    except Exception as exc:
        log.exception("特征构建异常：%s", exc)
        return jsonify({"code": 500, "msg": str(exc)}), 500


# ══════════════════════════════════════════════════════════════
# 启动
# ══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    log.info("AI 预测服务启动，监听 http://0.0.0.0:8083")
    app.run(host="0.0.0.0", port=8083, debug=False)
