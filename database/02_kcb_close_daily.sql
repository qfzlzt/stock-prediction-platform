-- 科创板收盘价日频数据表
CREATE TABLE IF NOT EXISTS `kcb_close_daily` (
  `id`                   bigint(20)     NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `trade_date`           date           NOT NULL                COMMENT '交易日期',
  `close_arithmetic`     decimal(12,4)  DEFAULT NULL            COMMENT '收盘价（算术平均）元',
  `close_float_weighted` decimal(12,4)  DEFAULT NULL            COMMENT '收盘价（流通股本加权平均）元',
  `close_total_weighted` decimal(12,4)  DEFAULT NULL            COMMENT '收盘价（总股本加权平均）元',
  `stock_count`          int(11)        DEFAULT NULL            COMMENT '参与计算的股票数量',
  `created_at`           datetime       DEFAULT CURRENT_TIMESTAMP,
  `updated_at`           datetime       DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_trade_date` (`trade_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='科创板收盘价日频数据（三种加权方式）';
