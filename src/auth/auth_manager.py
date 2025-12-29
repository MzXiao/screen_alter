"""
Authentication manager.
Handles user registration, login, and session management.
"""

import __main__
import bcrypt
from typing import Optional, Dict, Any

from database.db_manager import DatabaseManager
from utils.logger import get_logger

logger = get_logger(__name__)


class AuthManager:
    """Manages user authentication and sessions."""
    
    MIN_PASSWORD_LENGTH = 6
    
    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize authentication manager.
        
        Args:
            db_manager: Database manager instance
        """
        self.db = db_manager
        self.current_user: Optional[Dict[str, Any]] = None
    
    def _hash_password(self, password: str) -> str:
        """
        Hash a password using bcrypt.
        
        Args:
            password: Plain text password
        
        Returns:
            Hashed password
        """
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def _verify_password(self, password: str, password_hash: str) -> bool:
        """
        Verify a password against its hash.
        
        Args:
            password: Plain text password
            password_hash: Hashed password
        
        Returns:
            True if password matches
        """
        try:
            return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
        except Exception as e:
            logger.error(f"Password verification error: {e}")
            return False
    
    def validate_password(self, password: str) -> tuple[bool, str]:
        """
        Validate password strength.
        
        Args:
            password: Password to validate
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if len(password) < self.MIN_PASSWORD_LENGTH:
            return False, f"密码长度至少为 {self.MIN_PASSWORD_LENGTH} 个字符"
        
        # Add more validation rules as needed
        # For now, just check length
        
        return True, ""
    
    def register(self, username: str, password: str) -> tuple[bool, str]:
        """
        Register a new user.
        
        Args:
            username: Username
            password: Password
        
        Returns:
            Tuple of (success, message)
        """
        # Validate username
        if not username or len(username) < 3:
            return False, "用户名长度至少为 3 个字符"
        
        # Validate password
        is_valid, error_msg = self.validate_password(password)
        if not is_valid:
            return False, error_msg
        
        # Check if user already exists
        existing_user = self.db.get_user_by_username(username)
        if existing_user:
            return False, "用户名已存在"
        
        # Hash password and create user
        password_hash = self._hash_password(password)
        user_id = self.db.create_user(username, password_hash)
        
        if user_id:
            logger.info(f"User '{username}' registered successfully")
            
            # Create default config for the user
            self.db.create_or_update_config(user_id)
            
            return True, "注册成功"
        else:
            return False, "注册失败，请重试"
    
    def login(self, username: str, password: str) -> tuple[bool, str]:
        """
        Authenticate a user.
        
        Args:
            username: Username
            password: Password
        
        Returns:
            Tuple of (success, message)
        """
        # Get user from database
        user = self.db.get_user_by_username(username)
        
        if not user:
            return False, "用户名或密码错误"
        
        # Verify password
        if not self._verify_password(password, user['password_hash']):
            return False, "用户名或密码错误"
        
        # Update last login
        self.db.update_last_login(user['id'])
        
        # Set current user (remove password hash from session)
        self.current_user = {
            'id': user['id'],
            'username': user['username'],
            'created_at': user['created_at'],
            'last_login': user['last_login']
        }
        
        logger.info(f"User '{username}' logged in successfully")
        return True, "登录成功"
    
    def logout(self):
        """Logout current user."""
        if self.current_user:
            logger.info(f"User '{self.current_user['username']}' logged out")
            self.current_user = None
    
    def is_authenticated(self) -> bool:
        """
        Check if a user is currently authenticated.
        
        Returns:
            True if user is logged in
        """
        return self.current_user is not None
    
    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """
        Get current authenticated user.
        
        Returns:
            User data or None
        """
        return self.current_user
    
    def get_current_user_id(self) -> Optional[int]:
        """
        Get current user ID.
        
        Returns:
            User ID or None
        """
        return self.current_user['id'] if self.current_user else None

if __name__ == "__main__":
    # Add parent directory to path for direct execution
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    
    from database.db_manager import DatabaseManager
    from config import config
    
    print(f"Database path: {config.db_path}")
    db_manager = DatabaseManager(config.db_path)
    auth_manager = AuthManager(db_manager)
    
    # Test registration
    success, message = auth_manager.register("test", "123456")
    print(f"Registration: {success} - {message}")
    
    # Test login
    if success:
        success, message = auth_manager.login("test", "123456")
        print(f"Login: {success} - {message}")
        
        if success:
            user = auth_manager.get_current_user()
            print(f"Current user: {user}")