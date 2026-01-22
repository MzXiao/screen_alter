"""
System tray integration.
Provides system tray icon and menu for background operation.
"""

from typing import Optional, Callable
from PIL import Image, ImageDraw
import pystray
from pystray import MenuItem as item

from utils.logger import get_logger

logger = get_logger(__name__)


class SystemTray:
    """System tray manager."""
    
    def __init__(
        self,
        app_name: str = "星联助手",
        icon_path: Optional[str] = None
    ):
        """
        Initialize system tray.
        
        Args:
            app_name: Application name
            icon_path: Optional path to icon image
        """
        self.app_name = app_name
        self.icon = None
        self.is_monitoring = False
        
        # Callbacks
        self.on_open_dashboard: Optional[Callable] = None
        self.on_toggle_monitoring: Optional[Callable] = None
        self.on_settings: Optional[Callable] = None
        self.on_view_logs: Optional[Callable] = None
        self.on_exit: Optional[Callable] = None
        
        # Create icon
        if icon_path:
            try:
                self.icon_image = Image.open(icon_path)
            except Exception as e:
                logger.warning(f"Failed to load icon: {e}, using default")
                self.icon_image = self._create_default_icon()
        else:
            self.icon_image = self._create_default_icon()
    
    def _create_default_icon(self) -> Image.Image:
        """
        Create a default icon.
        
        Returns:
            PIL Image for icon
        """
        # Create a simple colored circle as default icon
        size = 64
        image = Image.new('RGB', (size, size), color='white')
        draw = ImageDraw.Draw(image)
        
        # Draw a circle
        margin = 8
        draw.ellipse(
            [margin, margin, size - margin, size - margin],
            fill='#4A90E2',
            outline='#2E5C8A'
        )
        
        return image
    
    def _create_menu(self) -> pystray.Menu:
        """
        Create system tray menu.
        
        Returns:
            pystray Menu object
        """
        status_text = "监控中" if self.is_monitoring else "已停止"
        toggle_text = "停止监控" if self.is_monitoring else "开始监控"
        
        return pystray.Menu(
            item(
                f"状态: {status_text}",
                lambda: None,
                enabled=False
            ),
            item(
                "打开控制面板",
                self._handle_open_dashboard
            ),
            item(
                toggle_text,
                self._handle_toggle_monitoring
            ),
            pystray.Menu.SEPARATOR,
            item(
                "设置",
                self._handle_settings
            ),
            item(
                "查看日志",
                self._handle_view_logs
            ),
            pystray.Menu.SEPARATOR,
            item(
                "退出",
                self._handle_exit
            )
        )
    
    def _handle_open_dashboard(self, icon, item):
        """Handle open dashboard menu item."""
        if self.on_open_dashboard:
            self.on_open_dashboard()
    
    def _handle_toggle_monitoring(self, icon, item):
        """Handle toggle monitoring menu item."""
        if self.on_toggle_monitoring:
            self.on_toggle_monitoring()
    
    def _handle_settings(self, icon, item):
        """Handle settings menu item."""
        if self.on_settings:
            self.on_settings()
    
    def _handle_view_logs(self, icon, item):
        """Handle view logs menu item."""
        if self.on_view_logs:
            self.on_view_logs()
    
    def _handle_exit(self, icon, item):
        """Handle exit menu item."""
        if self.on_exit:
            self.on_exit()
        self.stop()
    
    def set_monitoring_status(self, is_monitoring: bool):
        """
        Update monitoring status.
        
        Args:
            is_monitoring: Whether monitoring is active
        """
        self.is_monitoring = is_monitoring
        
        # Update menu
        if self.icon:
            self.icon.menu = self._create_menu()
    
    def show_notification(self, title: str, message: str):
        """
        Show system notification.
        
        Args:
            title: Notification title
            message: Notification message
        """
        if self.icon:
            try:
                self.icon.notify(message, title)
            except Exception as e:
                logger.error(f"Failed to show notification: {e}")
    
    def run(self):
        """Run system tray (blocking)."""
        self.icon = pystray.Icon(
            self.app_name,
            self.icon_image,
            self.app_name,
            menu=self._create_menu()
        )
        
        logger.info("Starting system tray")
        self.icon.run()
    
    def run_detached(self):
        """Run system tray in detached mode (non-blocking)."""
        self.icon = pystray.Icon(
            self.app_name,
            self.icon_image,
            self.app_name,
            menu=self._create_menu()
        )
        
        logger.info("Starting system tray (detached)")
        self.icon.run_detached()
    
    def stop(self):
        """Stop system tray."""
        if self.icon:
            logger.info("Stopping system tray")
            self.icon.stop()
            self.icon = None
