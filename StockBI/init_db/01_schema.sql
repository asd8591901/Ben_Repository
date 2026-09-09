-- StockBI 数据库初始化（MySQL 8）
-- 由 docker-entrypoint-initdb.d 在数据卷首次创建时自动执行。

CREATE DATABASE IF NOT EXISTS stockbi
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;

USE stockbi;

-- 股票基本信息
-- market: 'A' = A股, 'US' = 美股
CREATE TABLE IF NOT EXISTS stock_info (
  id       INT AUTO_INCREMENT PRIMARY KEY,
  market   VARCHAR(2)  NOT NULL COMMENT 'A=A股, US=美股',
  code     VARCHAR(20) NOT NULL COMMENT 'A:600519 / US:AAPL',
  name     VARCHAR(64) NOT NULL COMMENT 'A:中文名 / US:公司英文名',
  exchange VARCHAR(10) NULL COMMENT 'A:SH/SZ / US:NASDAQ/NYSE',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uq_market_code (market, code)
) ENGINE=InnoDB COMMENT='股票基本信息';

-- 日线行情（数据量最大的表）
CREATE TABLE IF NOT EXISTS daily_quote (
  id         BIGINT AUTO_INCREMENT PRIMARY KEY,
  market     VARCHAR(2)   NOT NULL,
  code       VARCHAR(20)  NOT NULL,
  trade_date DATE         NOT NULL,
  open       DOUBLE       NOT NULL,
  high       DOUBLE       NOT NULL,
  low        DOUBLE       NOT NULL,
  close      DOUBLE       NOT NULL,
  volume     BIGINT       NULL COMMENT 'A:手 / US:股',
  amount     DOUBLE       NULL COMMENT '成交额(元)，美股可能为空',
  UNIQUE KEY uq_quote (market, code, trade_date),  -- 天然去重，配合 ON DUPLICATE KEY UPDATE
  KEY idx_code_date (code, trade_date),
  KEY idx_market_date (market, trade_date)
) ENGINE=InnoDB COMMENT='日线行情';

-- 自选股（V1 预留）
CREATE TABLE IF NOT EXISTS watchlist (
  id         INT AUTO_INCREMENT PRIMARY KEY,
  market     VARCHAR(2)   NOT NULL,
  code       VARCHAR(20)  NOT NULL,
  note       VARCHAR(255) NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uq_watch (market, code)
) ENGINE=InnoDB COMMENT='自选股';
