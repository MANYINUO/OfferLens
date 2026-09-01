-- OfferLens V002: 面试复盘记录表
-- 每次面试后记录被问了什么、答得怎么样，用于反哺面试题预测

CREATE TABLE IF NOT EXISTS interview_note (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  user_id BIGINT NOT NULL,
  application_id BIGINT NOT NULL,
  content TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_user (user_id),
  INDEX idx_application (application_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
