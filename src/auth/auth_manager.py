"""
Authentication manager.
Handles user login and session management via backend API.
"""

import requests
from typing import Optional, Dict, Any
from config_mod import config
from utils.logger import get_logger

logger = get_logger(__name__)


class AuthManager:
    """Manages user authentication and sessions via Backend API."""
    
    def __init__(self, db_manager=None):
        """
        Initialize authentication manager.
        
        Args:
            db_manager: Database manager instance
        """
        self.backend_url = config.get("backend_url")
        self.db_manager = db_manager
        self.current_user: Optional[Dict[str, Any]] = None
        self.access_token: Optional[str] = None
    
    def login(self, username: str, password: str) -> tuple[bool, str]:
        """
        Authenticate a user via backend API.
        
        Args:
            username: Username
            password: Password
        
        Returns:
            Tuple of (success, message)
        """
        try:
            from utils.hwid import get_hwid
            hwid = get_hwid()
            
            url = f"{self.backend_url}/login"
            data = {
                "username": username,
                "password": password
            }
            # Add hwid as query param since OAuth2PasswordRequestForm takes from body, 
            # but FastAPI allows query params too or we could use custom form
            params = {"hwid": hwid}
            
            response = requests.post(url, data=data, params=params, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                self.access_token = result.get("access_token")
                user_id = result.get("user_id")
                username_val = result.get("username")
                
                self.current_user = {
                    'id': user_id,
                    'username': username_val,
                }
                
                # Sync user to local database
                if self.db_manager:
                    try:
                        self.db_manager.ensure_user_exists(user_id, username_val)
                    except Exception as e:
                        logger.error(f"Failed to sync user to local DB: {e}")
                
                logger.info(f"User '{username}' logged in successfully via API")
                return True, "登录成功"
            elif response.status_code == 401:
                return False, "用户名或密码错误"
            elif response.status_code == 403:
                detail = response.json().get("detail", "权限错误")
                if "expired" in detail.lower():
                    return False, "账号已到期，请联系管理员续费"
                if "device" in detail.lower():
                    return False, "该账号已在其他设备登录，请联系管理员解绑"
                return False, detail
            else:
                logger.error(f"Login failed with status {response.status_code}: {response.text}")
                return False, f"登录服务器错误: {response.status_code}"
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Backend connection error during login: {e}")
            return False, "无法连接到服务器，请检查网络"

    def set_db_manager(self, db_manager):
        """Set database manager."""
        self.db_manager = db_manager
    
    def register(self, username: str, password: str) -> tuple[bool, str]:
        """
        Register a new user (Disabled as per requirements).
        """
        return False, "注册功能已禁用，请联系管理员"
    
    def logout(self):
        """Logout current user."""
        if self.current_user:
            logger.info(f"User '{self.current_user['username']}' logged out")
            self.current_user = None
            self.access_token = None
    
    def is_authenticated(self) -> bool:
        """Check if a user is currently authenticated."""
        return self.current_user is not None and self.access_token is not None
    
    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """Get current authenticated user."""
        return self.current_user
    
    def get_current_user_id(self) -> Optional[int]:
        """Get current user ID."""
        return self.current_user['id'] if self.current_user else None

    def get_auth_header(self) -> Dict[str, str]:
        """Get Authorization header for API calls."""
        if self.access_token:
            return {"Authorization": f"Bearer {self.access_token}"}
        return {}

    def validate_call_permission(self) -> tuple[bool, str]:
        """
        Check if user has permission to make a call via backend.
        
        Returns:
            Tuple of (success, message)
        """
        try:
            url = f"{self.backend_url}/validate_call"
            response = requests.get(url, headers=self.get_auth_header(), timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if result.get("valid"):
                    return True, "验证成功"
                else:
                    return False, result.get("reason", "验证不通过")
            else:
                return False, f"服务器验证失败 ({response.status_code})"
        except Exception as e:
            logger.error(f"Failed to validate call permission: {e}")
            return False, "网络连接错误，无法验证权限"