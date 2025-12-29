"""
WeChat alert integration.
Handles WeChat login and sending alert messages.
"""

from typing import Optional, Callable
from pathlib import Path
import time

from utils.logger import get_logger

logger = get_logger(__name__)

# Try to import itchat
try:
    import itchat
    ITCHAT_AVAILABLE = True
except ImportError:
    ITCHAT_AVAILABLE = False
    logger.warning("itchat not available")


class WeChatAlert:
    """WeChat alert manager."""
    
    def __init__(self):
        """Initialize WeChat alert manager."""
        self.is_logged_in = False
        self.login_callback: Optional[Callable] = None
        
        if not ITCHAT_AVAILABLE:
            logger.error("itchat is not installed, WeChat alerts will not work")
    
    def set_login_callback(self, callback: Callable):
        """
        Set callback for login status updates.
        
        Args:
            callback: Function to call with login status
        """
        self.login_callback = callback
    
    def login(self, qr_callback: Optional[Callable[[str], None]] = None, timeout: int = 60) -> bool:
        """
        Login to WeChat.
        
        Args:
            qr_callback: Optional callback to receive QR code path
            timeout: Login timeout in seconds
        
        Returns:
            True if login successful
        """
        if not ITCHAT_AVAILABLE:
            logger.error("itchat not available")
            return False
        
        try:
            logger.info("Initiating WeChat login...")
            
            # Configure itchat
            itchat.auto_login(
                hotReload=True,  # Enable hot reload to save login state
                qrCallback=qr_callback,
                loginCallback=self._on_login_success,
                exitCallback=self._on_logout
            )
            
            return self.is_logged_in
            
        except Exception as e:
            logger.error(f"WeChat login failed: {e}")
            return False
    
    def _on_login_success(self):
        """Callback when login succeeds."""
        self.is_logged_in = True
        logger.info("WeChat login successful")
        
        if self.login_callback:
            self.login_callback(True)
    
    def _on_logout(self):
        """Callback when logout occurs."""
        self.is_logged_in = False
        logger.info("WeChat logged out")
        
        if self.login_callback:
            self.login_callback(False)
    
    def logout(self):
        """Logout from WeChat."""
        if ITCHAT_AVAILABLE and self.is_logged_in:
            try:
                itchat.logout()
                self.is_logged_in = False
                logger.info("WeChat logout successful")
            except Exception as e:
                logger.error(f"WeChat logout failed: {e}")
    
    def send_message(self, recipient: str, message: str) -> bool:
        """
        Send text message to a WeChat user.
        
        Args:
            recipient: Recipient username or remark name
            message: Message text
        
        Returns:
            True if sent successfully
        """
        if not ITCHAT_AVAILABLE:
            logger.error("itchat not available")
            return False
        
        if not self.is_logged_in:
            logger.error("Not logged in to WeChat")
            return False
        
        try:
            # Search for user
            users = itchat.search_friends(name=recipient)
            
            if not users:
                logger.error(f"User '{recipient}' not found")
                return False
            
            # Send message to first match
            user = users[0]
            itchat.send(message, toUserName=user['UserName'])
            
            logger.info(f"Message sent to {recipient}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            return False
    
    def send_image(self, recipient: str, image_path: str) -> bool:
        """
        Send image to a WeChat user.
        
        Args:
            recipient: Recipient username or remark name
            image_path: Path to image file
        
        Returns:
            True if sent successfully
        """
        if not ITCHAT_AVAILABLE:
            logger.error("itchat not available")
            return False
        
        if not self.is_logged_in:
            logger.error("Not logged in to WeChat")
            return False
        
        try:
            # Verify image exists
            if not Path(image_path).exists():
                logger.error(f"Image file not found: {image_path}")
                return False
            
            # Search for user
            users = itchat.search_friends(name=recipient)
            
            if not users:
                logger.error(f"User '{recipient}' not found")
                return False
            
            # Send image to first match
            user = users[0]
            itchat.send_image(image_path, toUserName=user['UserName'])
            
            logger.info(f"Image sent to {recipient}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send image: {e}")
            return False
    
    def send_alert(
        self,
        recipient: str,
        keyword: str,
        screenshot_path: Optional[str] = None
    ) -> bool:
        """
        Send alert message with optional screenshot.
        
        Args:
            recipient: Recipient username
            keyword: Detected keyword
            screenshot_path: Optional screenshot path
        
        Returns:
            True if sent successfully
        """
        # Format alert message
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        message = f"⚠️ 屏幕监控报警\n\n检测时间: {timestamp}\n检测到关键词: {keyword}\n\n请及时处理！"
        
        # Send text message
        if not self.send_message(recipient, message):
            return False
        
        # Send screenshot if provided
        if screenshot_path:
            time.sleep(1)  # Small delay between messages
            return self.send_image(recipient, screenshot_path)
        
        return True
    
    def get_friends_list(self) -> list:
        """
        Get list of WeChat friends.
        
        Returns:
            List of friend dictionaries
        """
        if not ITCHAT_AVAILABLE or not self.is_logged_in:
            return []
        
        try:
            friends = itchat.get_friends(update=True)
            return friends
        except Exception as e:
            logger.error(f"Failed to get friends list: {e}")
            return []
    
    @staticmethod
    def is_available() -> bool:
        """
        Check if WeChat integration is available.
        
        Returns:
            True if itchat is installed
        """
        return ITCHAT_AVAILABLE
