-- ============================================================
-- model_input_features 表
-- 存放三个 AI 模型（LGBM / LSTM / GNN）推理所需的全部特征
-- 包括：原始日频字段 + 计算指标 + 市场特征 + 行业分类
-- ============================================================

CREATE TABLE IF NOT EXISTS `model_input_features` (
  `id`              BIGINT        NOT NULL AUTO_INCREMENT COMMENT '主键',
  `stock_code`      VARCHAR(20)   NOT NULL                COMMENT '股票代码，如 688001.SH',
  `trade_date`      DATE          NOT NULL                COMMENT '交易日期',

  -- ── 原始日频字段（来自 daily_market_data）────────────────
  `pe_ttm`          DOUBLE        DEFAULT NULL            COMMENT '市盈率（TTM）',
  `pb_mrq`          DOUBLE        DEFAULT NULL            COMMENT '市净率（MRQ）',
  `pct_chg`         DOUBLE        DEFAULT NULL            COMMENT '涨跌幅（%）',
  `total_mv`        DOUBLE        DEFAULT NULL            COMMENT '总市值（元）',
  `float_mv`        DOUBLE        DEFAULT NULL            COMMENT '流通市值（元）',
  `total_shares`    DOUBLE        DEFAULT NULL            COMMENT '总股本（股）',
  `float_shares`    DOUBLE        DEFAULT NULL            COMMENT '流通股本（股）',
  `limit_up`        DOUBLE        DEFAULT NULL            COMMENT '涨停价（元）',
  `limit_down`      DOUBLE        DEFAULT NULL            COMMENT '跌停价（元）',
  `chg`             DOUBLE        DEFAULT NULL            COMMENT '涨跌额（元）',
  `avg_price`       DOUBLE        DEFAULT NULL            COMMENT '均价（元）',
  `volume`          DOUBLE        DEFAULT NULL            COMMENT '成交量',
  `amount`          DOUBLE        DEFAULT NULL            COMMENT '成交额（元）',
  `turnover`        DOUBLE        DEFAULT NULL            COMMENT '换手率（%）',
  `volume_ratio`    DOUBLE        DEFAULT NULL            COMMENT '量比',
  `high`            DOUBLE        DEFAULT NULL            COMMENT '最高价（元）',
  `low`             DOUBLE        DEFAULT NULL            COMMENT '最低价（元）',
  `open_price`      DOUBLE        DEFAULT NULL            COMMENT '开盘价（元）',
  `close`           DOUBLE        DEFAULT NULL            COMMENT '收盘价（元）',
  `prev_close`      DOUBLE        DEFAULT NULL            COMMENT '前收盘价（元）',
  `adj_factor`      DOUBLE        DEFAULT NULL            COMMENT '复权因子',

  -- ── 技术指标（由 build_features.py 计算）────────────────
  `ret_1_calc`      DOUBLE        DEFAULT NULL            COMMENT '日收益率',
  `ret_5`           DOUBLE        DEFAULT NULL            COMMENT '5日收益率',
  `ret_20`          DOUBLE        DEFAULT NULL            COMMENT '20日收益率',
  `ret_60`          DOUBLE        DEFAULT NULL            COMMENT '60日收益率',
  `rsi_6`           DOUBLE        DEFAULT NULL            COMMENT 'RSI（6日）',
  `rsi_14`          DOUBLE        DEFAULT NULL            COMMENT 'RSI（14日）',
  `macd`            DOUBLE        DEFAULT NULL            COMMENT 'MACD',
  `macd_signal`     DOUBLE        DEFAULT NULL            COMMENT 'MACD 信号线',
  `macd_hist`       DOUBLE        DEFAULT NULL            COMMENT 'MACD 柱状图',
  `bb_mid`          DOUBLE        DEFAULT NULL            COMMENT '布林中轨',
  `bb_std`          DOUBLE        DEFAULT NULL            COMMENT '布林标准差',
  `bb_upper`        DOUBLE        DEFAULT NULL            COMMENT '布林上轨',
  `bb_lower`        DOUBLE        DEFAULT NULL            COMMENT '布林下轨',
  `bb_width`        DOUBLE        DEFAULT NULL            COMMENT '布林带宽',
  `bb_pos`          DOUBLE        DEFAULT NULL            COMMENT '价格在布林带中的位置',
  `tr`              DOUBLE        DEFAULT NULL            COMMENT '真实波幅（TR）',
  `atr_14`          DOUBLE        DEFAULT NULL            COMMENT '平均真实波幅（ATR14）',
  `atr_pct`         DOUBLE        DEFAULT NULL            COMMENT 'ATR 占收盘价比例',
  `vol_20`          DOUBLE        DEFAULT NULL            COMMENT '20日收益率标准差',
  `vol_60`          DOUBLE        DEFAULT NULL            COMMENT '60日收益率标准差',
  `ma5`             DOUBLE        DEFAULT NULL            COMMENT '5日均线',
  `ma10`            DOUBLE        DEFAULT NULL            COMMENT '10日均线',
  `ma20`            DOUBLE        DEFAULT NULL            COMMENT '20日均线',
  `ma60`            DOUBLE        DEFAULT NULL            COMMENT '60日均线',
  `ma5_dev`         DOUBLE        DEFAULT NULL            COMMENT '价格偏离5日均线',
  `ma20_dev`        DOUBLE        DEFAULT NULL            COMMENT '价格偏离20日均线',
  `volume_ma5`      DOUBLE        DEFAULT NULL            COMMENT '5日成交量均线',
  `volume_ma20`     DOUBLE        DEFAULT NULL            COMMENT '20日成交量均线',
  `vol_surge`       DOUBLE        DEFAULT NULL            COMMENT '成交量相对20日均量倍数',
  `price_vol_corr`  DOUBLE        DEFAULT NULL            COMMENT '20日价量相关系数',

  -- ── 市场特征（来自 kcb_close_daily）────────────────────
  `mkt_ret_1`       DOUBLE        DEFAULT NULL            COMMENT '科创板指数日收益率',
  `mkt_ret_5`       DOUBLE        DEFAULT NULL            COMMENT '科创板指数5日收益率',
  `mkt_ret_20`      DOUBLE        DEFAULT NULL            COMMENT '科创板指数20日收益率',
  `mkt_vol_20`      DOUBLE        DEFAULT NULL            COMMENT '科创板指数20日波动率',
  `mkt_drawdown_60` DOUBLE        DEFAULT NULL            COMMENT '科创板指数60日最大回撤',

  -- ── 行业分类（来自 21公司行业分类.xlsx）──────────────────
  `industry_l3`     VARCHAR(100)  DEFAULT NULL            COMMENT '申万三级行业',

  -- ── 元数据 ────────────────────────────────────────────
  `created_at`      TIMESTAMP     DEFAULT CURRENT_TIMESTAMP,
  `updated_at`      TIMESTAMP     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_stock_date` (`stock_code`, `trade_date`),
  KEY `idx_stock_code`  (`stock_code`),
  KEY `idx_trade_date`  (`trade_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='AI 模型输入特征表（供 LGBM / LSTM / GNN 使用）';
