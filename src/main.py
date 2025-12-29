"""
Screen Monitor Application
Main entry point for the screen monitoring and alert application.
"""

import sys
from pathlib import Path
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import QThread

from config import config
from database.db_manager import DatabaseManager
from auth.auth_manager import AuthManager
from gui.login_window import LoginWindow
from gui.main_window import MainWindow
from utils.system_tray import SystemTray


from utils.logger import setup_logger, get_logger

# Set up logging
logger = setup_logger(
    "screen_monitor",
    log_file=config.logs_dir / "app.log"
)


class Application:
    """Main application class."""
    
    def __init__(self):
        """Initialize application."""
        self.app = QApplication(sys.argv)
        self.app.setApplicationName(config.APP_NAME)
        self.app.setApplicationVersion(config.APP_VERSION)
        
        # Initialize database
        self.db_manager = DatabaseManager(config.db_path)
        
        # Initialize auth manager
        self.auth_manager = AuthManager(self.db_manager)
        
        # Windows
        self.login_window = None
        self.main_window = None
        self.system_tray = None
        
        logger.info(f"Application initialized - {config.APP_NAME} v{config.APP_VERSION}")
    
    def run(self):
        """Run the application."""
        # Show login window
        self.show_login()
        
        # Start event loop
        return self.app.exec_()
    
    def show_login(self):
        """Show login window."""
        self.login_window = LoginWindow(self.auth_manager)
        self.login_window.login_successful.connect(self.on_login_success)
        self.login_window.show()
    
    def on_login_success(self, user_data):
        """
        Handle successful login.
        
        Args:
            user_data: User data dictionary
        """
        logger.info(f"User logged in: {user_data['username']}")
        
        # Hide login window
        if self.login_window:
            self.login_window.hide()


        
        # Show main window
        self.show_main_window(user_data)
        
        # Initialize system tray (disabled due to macOS compatibility issues)
        # Uncomment if needed, but may cause segfault on some macOS versions
        # self.setup_system_tray()
    
    def show_main_window(self, user_data):
        """
        Show main application window.
        
        Args:
            user_data: User data dictionary
        """
        logger.info("Creating main window...")
        try:
            self.main_window = MainWindow(
                self.db_manager,
                user_data['id'],
                user_data['username']
            )


            logger.info("Main window created successfully")
            
            # Connect signals
            self.main_window.monitoring_started.connect(self.on_monitoring_started)
            self.main_window.monitoring_stopped.connect(self.on_monitoring_stopped)
            logger.info("Signals connected")
            
            self.main_window.show()
            logger.info("Main window shown")
        except Exception as e:
            logger.error(f"Failed to create/show main window: {e}", exc_info=True)
    
    def setup_system_tray(self):
        """Set up system tray."""
        try:
            self.system_tray = SystemTray(config.APP_NAME)
            
            # Set callbacks
            self.system_tray.on_open_dashboard = self.on_tray_open_dashboard
            self.system_tray.on_toggle_monitoring = self.on_tray_toggle_monitoring
            self.system_tray.on_settings = self.on_tray_settings
            self.system_tray.on_view_logs = self.on_tray_view_logs
            self.system_tray.on_exit = self.on_tray_exit
            
            # Run in detached mode (non-blocking)
            self.system_tray.run_detached()
            
            logger.info("System tray initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize system tray: {e}")
            logger.warning("Application will continue without system tray support")
            self.system_tray = None
    
    def on_monitoring_started(self):
        """Handle monitoring started event."""
        if self.system_tray:
            self.system_tray.set_monitoring_status(True)
            self.system_tray.show_notification(
                "监控已启动",
                "屏幕监控正在运行"
            )
    
    def on_monitoring_stopped(self):
        """Handle monitoring stopped event."""
        if self.system_tray:
            self.system_tray.set_monitoring_status(False)
            self.system_tray.show_notification(
                "监控已停止",
                "屏幕监控已停止"
            )
    
    def on_tray_open_dashboard(self):
        """Handle open dashboard from tray."""
        if self.main_window:
            self.main_window.show()
            self.main_window.activateWindow()
    
    def on_tray_toggle_monitoring(self):
        """Handle toggle monitoring from tray."""
        if self.main_window:
            if self.main_window.is_monitoring:
                self.main_window.stop_monitoring()
            else:
                self.main_window.start_monitoring()
    
    def on_tray_settings(self):
        """Handle settings from tray."""
        self.on_tray_open_dashboard()
    
    def on_tray_view_logs(self):
        """Handle view logs from tray."""
        self.on_tray_open_dashboard()
        if self.main_window:
            self.main_window.load_alert_log()
    
    def on_tray_exit(self):
        """Handle exit from tray."""
        # Check if monitoring is running
        if self.main_window and self.main_window.is_monitoring:
            reply = QMessageBox.question(
                None,
                "确认退出",
                "监控正在运行，确定要退出吗？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.No:
                return
            
            self.main_window.stop_monitoring()
        
        # Cleanup
        logger.info("Application exiting")
        
        if self.auth_manager:
            self.auth_manager.logout()
        
        if self.system_tray:
            self.system_tray.stop()
        
        # Quit application
        self.app.quit()


def main():
    """Main entry point."""
    try:
        app = Application()
        sys.exit(app.run())
    except Exception as e:
        logger.critical(f"Application crashed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
