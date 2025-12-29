"""
Database manager for SQLite operations.
Handles all database interactions including CRUD operations.
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple
from contextlib import contextmanager

from database.models import ALL_SCHEMA_STATEMENTS, SCHEMA_VERSION
from utils.logger import get_logger

logger = get_logger(__name__)


class DatabaseManager:
    """Manages all database operations."""
    
    def __init__(self, db_path: Path):
        """
        Initialize database manager.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._ensure_database()
    
    @contextmanager
    def _get_connection(self):
        """Context manager for database connections."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            conn.close()
    
    def _ensure_database(self):
        """Create database and tables if they don't exist."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Create all tables
                for statement in ALL_SCHEMA_STATEMENTS:
                    cursor.execute(statement)
                
                # Check schema version
                cursor.execute("SELECT version FROM schema_version ORDER BY version DESC LIMIT 1")
                result = cursor.fetchone()
                
                if result is None:
                    # First time setup
                    cursor.execute(
                        "INSERT INTO schema_version (version) VALUES (?)",
                        (SCHEMA_VERSION,)
                    )
                    logger.info(f"Database initialized with schema version {SCHEMA_VERSION}")
                elif result[0] < SCHEMA_VERSION:
                    # Future: Handle migrations here
                    logger.warning(f"Schema version mismatch: {result[0]} vs {SCHEMA_VERSION}")
                
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    # ==================== User Operations ====================
    
    def create_user(self, username: str, password_hash: str) -> Optional[int]:
        """
        Create a new user.
        
        Args:
            username: Username
            password_hash: Hashed password
        
        Returns:
            User ID if successful, None otherwise
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                    (username, password_hash)
                )
                return cursor.lastrowid
        except sqlite3.IntegrityError:
            logger.warning(f"User '{username}' already exists")
            return None
        except Exception as e:
            logger.error(f"Failed to create user: {e}")
            return None
    
    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Get user by username.
        
        Args:
            username: Username to search for
        
        Returns:
            User data as dictionary or None
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id, username, password_hash, created_at, last_login FROM users WHERE username = ?",
                    (username,)
                )
                row = cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            logger.error(f"Failed to get user: {e}")
            return None
    
    def update_last_login(self, user_id: int):
        """
        Update user's last login timestamp.
        
        Args:
            user_id: User ID
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE users SET last_login = ? WHERE id = ?",
                    (datetime.now(), user_id)
                )
        except Exception as e:
            logger.error(f"Failed to update last login: {e}")
    
    # ==================== Config Operations ====================
    
    def create_or_update_config(
        self,
        user_id: int,
        monitor_interval: int = 60,
        keywords: List[str] = None,
        wechat_config: Dict[str, Any] = None,
        reference_images: List[str] = None
    ) -> bool:
        """
        Create or update user configuration.
        
        Args:
            user_id: User ID
            monitor_interval: Monitoring interval in seconds
            keywords: List of keywords to detect
            wechat_config: WeChat configuration
            reference_images: List of reference image paths
        
        Returns:
            True if successful
        """
        keywords = keywords or []
        wechat_config = wechat_config or {}
        reference_images = reference_images or []
        
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Check if config exists
                cursor.execute("SELECT id FROM config WHERE user_id = ?", (user_id,))
                exists = cursor.fetchone()
                
                if exists:
                    # Update
                    cursor.execute(
                        """UPDATE config 
                           SET monitor_interval = ?, keywords = ?, wechat_config = ?, 
                               reference_images = ?, updated_at = ?
                           WHERE user_id = ?""",
                        (
                            monitor_interval,
                            json.dumps(keywords, ensure_ascii=False),
                            json.dumps(wechat_config, ensure_ascii=False),
                            json.dumps(reference_images, ensure_ascii=False),
                            datetime.now(),
                            user_id
                        )
                    )
                else:
                    # Create
                    cursor.execute(
                        """INSERT INTO config (user_id, monitor_interval, keywords, wechat_config, reference_images)
                           VALUES (?, ?, ?, ?, ?)""",
                        (
                            user_id,
                            monitor_interval,
                            json.dumps(keywords, ensure_ascii=False),
                            json.dumps(wechat_config, ensure_ascii=False),
                            json.dumps(reference_images, ensure_ascii=False)
                        )
                    )
                return True
        except Exception as e:
            logger.error(f"Failed to create/update config: {e}")
            return False
    
    def get_config(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get user configuration.
        
        Args:
            user_id: User ID
        
        Returns:
            Configuration dictionary or None
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT * FROM config WHERE user_id = ?",
                    (user_id,)
                )
                row = cursor.fetchone()
                
                if row:
                    config = dict(row)
                    # Parse JSON fields
                    config['keywords'] = json.loads(config['keywords']) if config['keywords'] else []
                    config['wechat_config'] = json.loads(config['wechat_config']) if config['wechat_config'] else {}
                    config['reference_images'] = json.loads(config['reference_images']) if config['reference_images'] else []
                    return config
                return None
        except Exception as e:
            logger.error(f"Failed to get config: {e}")
            return None
    
    # ==================== Alert Operations ====================
    
    def create_alert(
        self,
        user_id: int,
        detected_keyword: Optional[str] = None,
        screenshot_path: Optional[str] = None,
        detection_method: str = "ocr",
        similarity_score: Optional[float] = None,
        alert_sent: bool = False
    ) -> Optional[int]:
        """
        Create a new alert record.
        
        Args:
            user_id: User ID
            detected_keyword: Detected keyword
            screenshot_path: Path to screenshot
            detection_method: Detection method ('ocr' or 'image_similarity')
            similarity_score: Similarity score (for image detection)
            alert_sent: Whether alert was sent successfully
        
        Returns:
            Alert ID if successful
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """INSERT INTO alerts 
                       (user_id, detected_keyword, screenshot_path, detection_method, similarity_score, alert_sent)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (user_id, detected_keyword, screenshot_path, detection_method, similarity_score, alert_sent)
                )
                return cursor.lastrowid
        except Exception as e:
            logger.error(f"Failed to create alert: {e}")
            return None
    
    def get_recent_alerts(self, user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get recent alerts for a user.
        
        Args:
            user_id: User ID
            limit: Maximum number of alerts to return
        
        Returns:
            List of alert dictionaries
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """SELECT * FROM alerts 
                       WHERE user_id = ? 
                       ORDER BY created_at DESC 
                       LIMIT ?""",
                    (user_id, limit)
                )
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Failed to get alerts: {e}")
            return []
    
    def get_alert_stats(self, user_id: int, days: int = 7) -> Dict[str, Any]:
        """
        Get alert statistics for a user.
        
        Args:
            user_id: User ID
            days: Number of days to look back
        
        Returns:
            Statistics dictionary
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Total alerts in period
                cursor.execute(
                    """SELECT COUNT(*) as total, 
                              SUM(CASE WHEN alert_sent = 1 THEN 1 ELSE 0 END) as sent
                       FROM alerts 
                       WHERE user_id = ? 
                       AND created_at >= datetime('now', '-' || ? || ' days')""",
                    (user_id, days)
                )
                row = cursor.fetchone()
                
                return {
                    'total_alerts': row['total'] if row else 0,
                    'alerts_sent': row['sent'] if row else 0,
                    'period_days': days
                }
        except Exception as e:
            logger.error(f"Failed to get alert stats: {e}")
            return {'total_alerts': 0, 'alerts_sent': 0, 'period_days': days}
    
    def update_alert_sent_status(self, alert_id: int, sent: bool = True):
        """
        Update alert sent status.
        
        Args:
            alert_id: Alert ID
            sent: Whether alert was sent
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE alerts SET alert_sent = ? WHERE id = ?",
                    (sent, alert_id)
                )
        except Exception as e:
            logger.error(f"Failed to update alert status: {e}")
