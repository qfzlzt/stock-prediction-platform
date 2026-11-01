-- Schema only. Import into an empty stock database. No source records included.
SET FOREIGN_KEY_CHECKS=0;

CREATE TABLE `analysis_report_library` (
  `reportId` varchar(50) NOT NULL COMMENT '报告ID',
  `stockCode` varchar(20) NOT NULL COMMENT 'A股代码',
  `reportTitle` varchar(200) NOT NULL COMMENT '报告标题',
  `reportType` varchar(50) NOT NULL COMMENT '报告类型',
  `reportAbstract` text NOT NULL COMMENT '报告摘要',
  `reportContent` text NOT NULL COMMENT '报告正文',
  `reportAuthor` varchar(100) NOT NULL COMMENT '报告作者',
  `reportGenerateTime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '报告生成时间',
  `reportStatus` varchar(20) NOT NULL COMMENT '报告状态',
  `createdAt` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updatedAt` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`reportId`),
  KEY `idx_stockCode` (`stockCode`),
  KEY `idx_reportType` (`reportType`),
  CONSTRAINT `fk_analysis_report_stock` FOREIGN KEY (`stockCode`) REFERENCES `company_profile` (`stockCode`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='分析报告数据库表';

CREATE TABLE `company_profile` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `stockCode` varchar(20) NOT NULL COMMENT '证券代码',
  `stockName` varchar(50) DEFAULT NULL COMMENT '证券简称',
  `englishName` varchar(200) DEFAULT NULL COMMENT '股票英文简称',
  `marketType` varchar(20) DEFAULT NULL COMMENT '上市版',
  `stockCategory` varchar(30) DEFAULT NULL COMMENT '股票类别',
  `listingDate` date DEFAULT NULL COMMENT '上市日期',
  `status` enum('L','S','D','T') DEFAULT 'L' COMMENT '交易状态(L-正常交易,S-停牌,D-退市整理期,T-已退市)',
  `industryLevel` varchar(100) DEFAULT NULL COMMENT '所属行业名称',
  `legalRepresentative` varchar(100) DEFAULT NULL COMMENT '法定代表人',
  `registeredCapital` decimal(20,2) DEFAULT NULL COMMENT '注册资本(元)',
  `registrationTime` date DEFAULT NULL COMMENT '成立日期',
  `registrationProvince` varchar(50) DEFAULT NULL COMMENT '省份',
  `employeeCount` int(11) DEFAULT NULL COMMENT '员工总数',
  `independentDirectors` varchar(500) DEFAULT NULL COMMENT '公司独立董事(历任)',
  `companyIntro` text COMMENT '公司简介',
  `businessScope` text COMMENT '经营范围',
  `createdAt` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updatedAt` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_stockCode` (`stockCode`)
) ENGINE=InnoDB AUTO_INCREMENT=25 DEFAULT CHARSET=utf8mb4 COMMENT='公司概况表';

CREATE TABLE `daily_market_data` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `stockCode` varchar(20) NOT NULL COMMENT 'A股代码',
  `tradeDate` date NOT NULL COMMENT '交易日期',
  `peRatio` double DEFAULT NULL COMMENT '市盈率',
  `pbRatio` double DEFAULT NULL COMMENT '市净率',
  `priceChangeRate` double DEFAULT NULL COMMENT '涨跌幅(%)',
  `totalMarketCap` double DEFAULT NULL COMMENT '总市值(元)',
  `circulatingMarketCap` double DEFAULT NULL COMMENT '流通市值(元)',
  `totalShares` double DEFAULT NULL COMMENT '总股本(万股)',
  `circulatingShares` double DEFAULT NULL COMMENT '流通股本(万股)',
  `yesterdayReturn` double DEFAULT NULL COMMENT '昨日收益(%)',
  `upperLimitPrice` double DEFAULT NULL COMMENT '涨停价(元)',
  `lowerLimitPrice` double DEFAULT NULL COMMENT '跌停价(元)',
  `hs300ChangeRate` double DEFAULT NULL COMMENT '沪深300涨跌幅(%)',
  `industryChangeRate` double DEFAULT NULL COMMENT '行业指数涨跌幅(%)',
  `marketVolatility` double DEFAULT NULL COMMENT '市场波动率(%)',
  `createdAt` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updatedAt` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_stock_trade` (`stockCode`,`tradeDate`),
  KEY `idx_tradeDate` (`tradeDate`),
  CONSTRAINT `fk_daily_market_stock` FOREIGN KEY (`stockCode`) REFERENCES `company_profile` (`stockCode`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=25 DEFAULT CHARSET=utf8mb4 COMMENT='日频市场数据表';

CREATE TABLE `financial_report` (
  `stockCode` varchar(20) NOT NULL COMMENT 'A股代码',
  `reportPeriod` varchar(10) NOT NULL COMMENT '报告年份',
  `reportType` enum('Q1','Q2','S1','Q3','Q4','A') NOT NULL COMMENT '报告类型(Q1-一季报,Q2-二季报,S1-半年报,Q3-三季报,Q4-四季报,A-年报)',
  `basicEps` double DEFAULT NULL COMMENT '基本每股收益(元)',
  `netAssetsPerShare` double DEFAULT NULL COMMENT '每股净资产(元)',
  `capitalReservePerShare` double DEFAULT NULL COMMENT '资本公积金(元)',
  `undistributedProfitPerShare` double DEFAULT NULL COMMENT '每股未分配利润(元)',
  `operatingCashFlowPerShare` double DEFAULT NULL COMMENT '每股现金净额(元)',
  `totalOperatingRevenue` double DEFAULT NULL COMMENT '营业总收入(元)',
  `grossProfit` double DEFAULT NULL COMMENT '毛利润(元)',
  `netProfitAttributable` double DEFAULT NULL COMMENT '净利润(元)',
  `totalOperatingRevenueYoy` double DEFAULT NULL COMMENT '营业总收入同比增长(%)',
  `roe` double DEFAULT NULL COMMENT '净资产收益率(%)',
  `revenueGrowthRate` double DEFAULT NULL COMMENT '营收增速(%)',
  `grossMargin` double DEFAULT NULL COMMENT '毛利率(%)',
  `netProfitGrowthRate` double DEFAULT NULL COMMENT '净利润增速(%)',
  `createdAt` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updatedAt` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`stockCode`,`reportPeriod`,`reportType`),
  CONSTRAINT `fk_financial_report_stock` FOREIGN KEY (`stockCode`) REFERENCES `company_profile` (`stockCode`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='财务状况表';

CREATE TABLE `realtime_market_data` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `stockCode` varchar(20) NOT NULL COMMENT 'A股代码',
  `latestPrice` double DEFAULT NULL COMMENT '最新价(元)',
  `priceChange` double DEFAULT NULL COMMENT '涨跌(元)',
  `priceChangeRate` double DEFAULT NULL COMMENT '涨幅(%)',
  `averagePrice` double DEFAULT NULL COMMENT '均价(元)',
  `totalVolume` double DEFAULT NULL COMMENT '成交量(手)',
  `turnover` double DEFAULT NULL COMMENT '成交额(元)',
  `turnoverRate` double DEFAULT NULL COMMENT '换手率(%)',
  `volumeRatio` double DEFAULT NULL COMMENT '量比',
  `highestPrice` double DEFAULT NULL COMMENT '最高价(元)',
  `lowestPrice` double DEFAULT NULL COMMENT '最低价(元)',
  `openingPrice` double DEFAULT NULL COMMENT '开盘价(元)',
  `preClosePrice` double DEFAULT NULL COMMENT '前收盘价(元)',
  `closePrice` double DEFAULT NULL COMMENT '收盘价(元)',
  `adjFactor` double DEFAULT NULL COMMENT '复权因子',
  `dataTimestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '数据时间戳',
  `createdAt` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updatedAt` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `idx_stockCode` (`stockCode`),
  KEY `idx_dataTimestamp` (`dataTimestamp`),
  CONSTRAINT `fk_realtime_market_stock` FOREIGN KEY (`stockCode`) REFERENCES `company_profile` (`stockCode`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=25 DEFAULT CHARSET=utf8mb4 COMMENT='实时市场数据表';

CREATE TABLE `technical_indicator_library` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `stockCode` varchar(20) NOT NULL COMMENT 'A股代码',
  `tradeDate` date NOT NULL COMMENT '交易日期',
  `ma20` double DEFAULT NULL COMMENT '20日均线(元)',
  `ma60` double DEFAULT NULL COMMENT '60日均线(元)',
  `momentum20` double DEFAULT NULL COMMENT '20日动量(%)',
  `volatility20` double DEFAULT NULL COMMENT '20日波动率(%)',
  `relativeVolume` double DEFAULT NULL COMMENT '相对成交量',
  `predictionResult` varchar(100) DEFAULT NULL COMMENT '预测结果',
  `algorithmVersion` varchar(50) DEFAULT NULL COMMENT '算法版本',
  `calculatedAt` datetime DEFAULT NULL COMMENT '计算时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_stock_trade` (`stockCode`,`tradeDate`),
  CONSTRAINT `fk_technical_indicator_stock` FOREIGN KEY (`stockCode`) REFERENCES `company_profile` (`stockCode`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=25 DEFAULT CHARSET=utf8mb4 COMMENT='技术指标数据库表';

CREATE TABLE `user` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '用户ID',
  `username` varchar(50) NOT NULL COMMENT '用户名',
  `password` varchar(255) NOT NULL COMMENT '密码',
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

SET FOREIGN_KEY_CHECKS=1;
