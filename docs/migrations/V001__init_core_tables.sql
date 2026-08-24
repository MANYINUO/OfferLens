-- OfferLens V001: 初始化 4 张核心表
-- 执行方式：在 MySQL 中 source 本文件，或通过数据库客户端执行
-- 后续新增表请新建 V002__xxx.sql，不要修改本文件

CREATE DATABASE IF NOT EXISTS offerlens DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
USE offerlens;

-- 用户表
CREATE TABLE IF NOT EXISTS user (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  username VARCHAR(64) NOT NULL UNIQUE,
  password_hash VARCHAR(128) NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 简历表（多版本）
CREATE TABLE IF NOT EXISTS resume (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  user_id BIGINT NOT NULL,
  version_name VARCHAR(64) NOT NULL,
  content TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_user (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- JD 收藏库
CREATE TABLE IF NOT EXISTS job_description (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  user_id BIGINT NOT NULL,
  company VARCHAR(128),
  position VARCHAR(128),
  content TEXT,
  content_hash VARCHAR(64),
  channel VARCHAR(32),
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uk_hash (user_id, content_hash)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 投递记录表（含七阶段状态机）
CREATE TABLE IF NOT EXISTS application (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  user_id BIGINT NOT NULL,
  jd_id BIGINT,
  resume_id BIGINT,
  company VARCHAR(128),
  position VARCHAR(128),
  channel VARCHAR(32),
  job_type VARCHAR(32),
  match_score INT,
  status VARCHAR(16) DEFAULT 'applied',
  applied_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  last_followup_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  notes TEXT,
  INDEX idx_user_status (user_id, status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
