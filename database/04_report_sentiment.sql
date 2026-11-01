-- Cache schema required by prediction-service/sentiment.py.
CREATE TABLE IF NOT EXISTS report_sentiment (
  id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  stockCode VARCHAR(20) NOT NULL,
  reportId VARCHAR(50) NOT NULL,
  reportTitle VARCHAR(200),
  proba_pos DOUBLE,
  proba_neu DOUBLE,
  proba_neg DOUBLE,
  sentiment VARCHAR(20),
  analyzedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uk_reportId (reportId),
  KEY idx_stockCode (stockCode)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
