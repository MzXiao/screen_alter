"""
Database schema definitions.
Defines the structure of all database tables.
"""

# SQL schema for the application database

SCHEMA_VERSION = 4

# Users table - stores user authentication information
CREATE_USERS_TABLE = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);
"""

# Config table - stores user-specific configuration
CREATE_CONFIG_TABLE = """
CREATE TABLE IF NOT EXISTS config (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    monitor_interval INTEGER DEFAULT 60,
    ocr_engine VARCHAR(20) DEFAULT 'pytesseract',
    keywords TEXT,
    capture_region TEXT,
    reference_images TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
"""

# Alerts table - stores detection and alert history
CREATE_ALERTS_TABLE = """
CREATE TABLE IF NOT EXISTS alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    detected_keyword VARCHAR(100),
    screenshot_path VARCHAR(500),
    detection_method VARCHAR(20),
    similarity_score FLOAT,
    alert_sent BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
"""

# Check logs table - records every monitoring check attempt
CREATE_CHECK_LOGS_TABLE = """
CREATE TABLE IF NOT EXISTS check_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    check_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    result_status VARCHAR(20),
    details TEXT,
    screenshot_path VARCHAR(500),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
"""

# Index for faster queries
CREATE_ALERTS_INDEX = """
CREATE INDEX IF NOT EXISTS idx_alerts_user_created 
ON alerts(user_id, created_at DESC);
"""

CREATE_CHECK_LOGS_INDEX = """
CREATE INDEX IF NOT EXISTS idx_check_logs_user_time
ON check_logs(user_id, check_time DESC);
"""

CREATE_ALERTS_KEYWORD_INDEX = """
CREATE INDEX IF NOT EXISTS idx_alerts_keyword 
ON alerts(detected_keyword);
"""

# Schema version table
CREATE_SCHEMA_VERSION_TABLE = """
CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER PRIMARY KEY,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

# All schema creation statements in order
ALL_SCHEMA_STATEMENTS = [
    CREATE_USERS_TABLE,
    CREATE_CONFIG_TABLE,
    CREATE_ALERTS_TABLE,
    CREATE_CHECK_LOGS_TABLE,
    CREATE_ALERTS_INDEX,
    CREATE_CHECK_LOGS_INDEX,
    CREATE_ALERTS_KEYWORD_INDEX,
    CREATE_SCHEMA_VERSION_TABLE,
]
