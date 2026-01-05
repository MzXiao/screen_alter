"""
API Manager for backend synchronization.
Replaces the local DatabaseManager to interact with the screen_alter backend.
"""

import requests
import json
from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple
from utils.logger import get_logger
from config import config

logger = get_logger(__name__)


class DatabaseManager:
    """
    Manager for backend API interactions.
    Maintains the same interface as the old local DatabaseManager for compatibility.
    """
    
    def __init__(self, db_path=None, auth_manager=None):
        """
        Initialize API manager.
        
        Args:
            db_path: Deprecated, kept for interface compatibility.
            auth_manager: AuthManager instance to get tokens.
        """
        self.backend_url = config.BACKEND_URL
        self.auth_manager = auth_manager
    
    def set_auth_manager(self, auth_manager):
        """Set auth manager after initialization if needed."""
        self.auth_manager = auth_manager

    def _get_headers(self):
        """Get headers with authentication token."""
        if self.auth_manager and self.auth_manager.access_token:
            return {"Authorization": f"Bearer {self.auth_manager.access_token}"}
        return {}

    def _request(self, method: str, endpoint: str, data: dict = None, params: dict = None) -> Optional[Any]:
        """Helper to make API requests."""
        url = f"{self.backend_url}{endpoint}"
        try:
            response = requests.request(
                method, url, json=data, params=params, 
                headers=self._get_headers(), timeout=10
            )
            if response.status_code in [200, 201]:
                return response.json()
            else:
                logger.error(f"API request to {endpoint} failed with {response.status_code}: {response.text}")
                return None
        except Exception as e:
            logger.error(f"API request to {endpoint} failed: {e}")
            return None

    # ==================== User Operations ====================
    
    def create_user(self, username: str, password_hash: str) -> Optional[int]:
        """Registration is disabled on client side."""
        logger.warning("create_user called on client side - Registration is disabled")
        return None
    
    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Deprecated: Use AuthManager.login directly."""
        return None
    
    def update_last_login(self, user_id: int):
        """Managed by backend during login."""
        pass
    
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
        """Update configuration on backend."""
        data = {
            "monitor_interval": monitor_interval,
            "ocr_engine": ocr_engine,
            "keywords": keywords or [],
            "capture_region": capture_region,
            "reference_images": reference_images or []
        }
        result = self._request("POST", "/config", data=data)
        return result is not None
    
    def get_config(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get configuration from backend."""
        return self._request("GET", "/config")
    
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
        """Create alert on backend."""
        data = {
            "detected_keyword": detected_keyword,
            "screenshot_path": screenshot_path,
            "detection_method": detection_method,
            "similarity_score": similarity_score,
            "alert_sent": alert_sent
        }
        result = self._request("POST", "/alerts", data=data)
        return result.get("id") if result else None

    def create_check_log(
        self,
        user_id: int,
        result_status: str,
        details: str,
        screenshot_path: str = None
    ) -> Optional[int]:
        """Create monitor log on backend."""
        data = {
            "result_status": result_status,
            "details": details,
            "screenshot_path": screenshot_path
        }
        result = self._request("POST", "/logs", data=data)
        return result.get("id") if result else None
    
    def get_recent_alerts(self, user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """Get alerts from backend."""
        result = self._request("GET", "/alerts", params={"limit": limit})
        return result if result is not None else []
    
    def get_alert_stats(self, user_id: int, days: int = 7) -> Dict[str, Any]:
        """Get stats from backend."""
        result = self._request("GET", "/stats", params={"days": days})
        return result if result is not None else {'total_alerts': 0, 'alerts_sent': 0, 'period_days': days}
    
    def get_recent_check_logs(self, user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """Placeholder: Backend may need a specific endpoint for logs history."""
        # For now, return empty as the UI prioritizes alerts
        return []

    def update_alert_sent_status(self, alert_id: int, sent: bool = True):
        """Managed by backend or simplified API call."""
        # Could implement a PATCH /alerts/{id} if needed
        pass
