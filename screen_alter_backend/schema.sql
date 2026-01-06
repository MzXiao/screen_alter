-- Database Schema for Screen Alter Backend (MySQL)

CREATE DATABASE IF NOT EXISTS screen_alter;
USE screen_alter;

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Configuration table
CREATE TABLE IF NOT EXISTS configs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT UNIQUE NOT NULL,
    monitor_interval INT DEFAULT 60,
    ocr_engine VARCHAR(50) DEFAULT 'paddleocr',
    keywords TEXT, -- JSON string
    capture_region TEXT, -- JSON string
    reference_images TEXT, -- JSON string
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Alerts table
CREATE TABLE IF NOT EXISTS alerts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    detected_keyword VARCHAR(255),
    screenshot_path VARCHAR(255),
    detection_method VARCHAR(50),
    similarity_score FLOAT,
    alert_sent BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_created (user_id, created_at),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Monitoring logs table (for statistics)
CREATE TABLE IF NOT EXISTS monitoring_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    result_status VARCHAR(50), -- SUCCESS, DETECTED, FAILED
    details TEXT,
    screenshot_path VARCHAR(255),
    check_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_time (user_id, check_time),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


insert into screen_alter.users (id, username, password_hash, created_at, last_login)
values  (1, 'admin', '$2b$12$uy2GVBPsoMwW0JjObM882OGDFe/wXy1nm7oZm3piT5HXebihRv272', '2026-01-05 13:15:20', null);