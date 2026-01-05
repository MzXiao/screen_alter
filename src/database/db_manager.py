"""
Local Database Manager using SQLite.
"""

import sqlite3
import json
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple
from pathlib import Path
from config import config
from database.models import ALL_SCHEMA_STATEMENTS

logger = logging.getLogger(__name__)

class DatabaseManager:
    """
    Manager for local SQLite database interactions.
    """
    
    def __init__(self, db_path=None, auth_manager=None):
        """
        Initialize Database manager.
        
        Args:
            db_path: Path to SQLite database file.
            auth_manager: AuthManager instance (kept for interface compatibility).
        """
        self.db_path = db_path or config.db_path
        self._init_db()
        self.auth_manager = auth_manager
    
    def set_auth_manager(self, auth_manager):
        """Set auth manager after initialization if needed."""
        self.auth_manager = auth_manager

    def _get_connection(self):
        """Get SQLite database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        """Initialize database schema."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                for statement in ALL_SCHEMA_STATEMENTS:
                    cursor.execute(statement)
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise

    # ==================== User Operations ====================
    
    def ensure_user_exists(self, user_id: int, username: str) -> bool:
        """
        Ensure user exists in local database (sync from backend).
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                # Check if user exists
                cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
                if cursor.fetchone():
                    # Update existing
                    cursor.execute(
                        "UPDATE users SET username = ?, last_login = CURRENT_TIMESTAMP WHERE id = ?",
                        (username, user_id)
                    )
                else:
                    # Insert new
                    cursor.execute(
                        "INSERT INTO users (id, username, password_hash, last_login) VALUES (?, ?, 'synced_from_backend', CURRENT_TIMESTAMP)",
                        (user_id, username)
                    )
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Failed to sync user to local DB: {e}")
            return False
            
    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user by username from local DB."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
                row = cursor.fetchone()
                if row:
                    return dict(row)
        except Exception as e:
            logger.error(f"Failed to get user: {e}")
        return None
    
    def update_last_login(self, user_id: int):
        """Update last login timestamp."""
        try:
            with self._get_connection() as conn:
                conn.execute(
                    "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?",
                    (user_id,)
                )
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to update last login: {e}")

    # ==================== Config Operations ====================
    
    def create_or_update_config(
        self,
        user_id: int,
        monitor_interval: int = 60,
        ocr_engine: str = 'paddleocr',
        keywords: List[str] = None,
        capture_region: Tuple[int, int, int, int] = None,
        reference_images: List[str] = None
    ) -> bool:
        """Update configuration locally."""
        try:
            keywords_json = json.dumps(keywords or [])
            region_json = json.dumps(capture_region) if capture_region else None
            ref_imgs_json = json.dumps(reference_images or [])
            
            with self._get_connection() as conn:
                cursor = conn.cursor()
                # Check if config exists
                cursor.execute("SELECT id FROM config WHERE user_id = ?", (user_id,))
                if cursor.fetchone():
                    cursor.execute("""
                        UPDATE config 
                        SET monitor_interval=?, ocr_engine=?, keywords=?, 
                            capture_region=?, reference_images=?, updated_at=CURRENT_TIMESTAMP
                        WHERE user_id=?
                    """, (monitor_interval, ocr_engine, keywords_json, region_json, ref_imgs_json, user_id))
                else:
                    cursor.execute("""
                        INSERT INTO config (user_id, monitor_interval, ocr_engine, keywords, capture_region, reference_images)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (user_id, monitor_interval, ocr_engine, keywords_json, region_json, ref_imgs_json))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
            return False
    
    def get_config(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get configuration from local DB."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM config WHERE user_id = ?", (user_id,))
                row = cursor.fetchone()
                if row:
                    data = dict(row)
                    # Parse JSON fields
                    data['keywords'] = json.loads(data['keywords']) if data['keywords'] else []
                    data['capture_region'] = json.loads(data['capture_region']) if data['capture_region'] else None
                    data['reference_images'] = json.loads(data['reference_images']) if data['reference_images'] else []
                    return data
        except Exception as e:
            logger.error(f"Failed to get config: {e}")
        return None
    
    # ==================== Alert Operations ====================
    
    def create_alert(
        self,
        user_id: int,
        detected_keyword: str,
        screenshot_path: str,
        detection_method: str = "ocr",
        similarity_score: float = None,
        alert_sent: bool = False
    ) -> Optional[int]:
        """Create alert locally."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO alerts (user_id, detected_keyword, screenshot_path, detection_method, similarity_score, alert_sent)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (user_id, detected_keyword, screenshot_path, detection_method, similarity_score, alert_sent and 1 or 0))
                conn.commit()
                return cursor.lastrowid
        except Exception as e:
            logger.error(f"Failed to create alert: {e}")
            return None

    def create_check_log(
        self,
        user_id: int,
        result_status: str,
        details: str,
        screenshot_path: str = None
    ) -> Optional[int]:
        """Create check log locally."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO check_logs (user_id, result_status, details, screenshot_path)
                    VALUES (?, ?, ?, ?)
                """, (user_id, result_status, details, screenshot_path))
                conn.commit()
                return cursor.lastrowid
        except Exception as e:
            logger.error(f"Failed to create log: {e}")
            return None
    
    def get_recent_alerts(self, user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent alerts."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM alerts 
                    WHERE user_id = ? 
                    ORDER BY created_at DESC 
                    LIMIT ?
                """, (user_id, limit))
                rows = cursor.fetchall()
                results = []
                for row in rows:
                    r = dict(row)
                    r['alert_sent'] = bool(r['alert_sent'])
                    results.append(r)
                return results
        except Exception as e:
            logger.error(f"Failed to get alerts: {e}")
            return []
    
    def get_alert_stats(self, user_id: int, days: int = 7) -> Dict[str, Any]:
        """Get alert statistics."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT 
                        COUNT(id) as total_alerts,
                        SUM(CASE WHEN alert_sent = 1 THEN 1 ELSE 0 END) as alerts_sent
                    FROM alerts 
                    WHERE user_id = ? 
                    AND created_at >= datetime('now', ?)
                """, (user_id, f'-{days} days'))
                row = cursor.fetchone()
                return {
                    'total_alerts': row[0] or 0,
                    'alerts_sent': row[1] or 0,
                    'period_days': days
                }
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {'total_alerts': 0, 'alerts_sent': 0, 'period_days': days}
    
    def get_recent_check_logs(self, user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent check logs."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM check_logs 
                    WHERE user_id = ? 
                    ORDER BY check_time DESC 
                    LIMIT ?
                """, (user_id, limit))
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Failed to get logs: {e}")
            return []

    def update_alert_sent_status(self, alert_id: int, sent: bool = True):
        """Update alert sent status."""
        try:
            with self._get_connection() as conn:
                conn.execute(
                    "UPDATE alerts SET alert_sent = ? WHERE id = ?",
                    (sent and 1 or 0, alert_id)
                )
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to update alert status: {e}")
