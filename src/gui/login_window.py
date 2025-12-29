"""
Login window implementation.
Provides user authentication interface.
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QCheckBox, QMessageBox, QWidget
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QPalette, QColor, QLinearGradient

from auth.auth_manager import AuthManager
from utils.logger import get_logger

logger = get_logger(__name__)


class LoginWindow(QDialog):
    """Login window for user authentication."""
    
    login_successful = pyqtSignal(dict)  # Emits user data on successful login
    
    def __init__(self, auth_manager: AuthManager, parent=None):
        """
        Initialize login window.
        
        Args:
            auth_manager: Authentication manager instance
            parent: Parent widget
        """
        super().__init__(parent)
        self.auth_manager = auth_manager
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the user interface."""
        self.setWindowTitle("Screen Monitor - 登录")
        self.setFixedSize(400, 500)
        self.setModal(True)
        
        # Set gradient background
        self.set_gradient_background()
        
        # Main layout
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        # Add stretch at top to center content
        layout.addStretch()
        
        # Title
        title = QLabel("Screen Monitor")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Arial", 24, QFont.Bold))
        title.setStyleSheet("color: white;")
        layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel("登录以继续")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setFont(QFont("Arial", 12))
        subtitle.setStyleSheet("color: rgba(255, 255, 255, 0.8);")
        layout.addWidget(subtitle)
        
        layout.addSpacing(30)
        
        # Login card
        card = self.create_login_card()
        layout.addWidget(card)
        
        # Add stretch at bottom
        layout.addStretch()
        
        # Footer
        footer = QLabel("Powered by AI Detection")
        footer.setAlignment(Qt.AlignCenter)
        footer.setFont(QFont("Arial", 9))
        footer.setStyleSheet("color: rgba(255, 255, 255, 0.6);")
        layout.addWidget(footer)
        
        self.setLayout(layout)
    
    def set_gradient_background(self):
        """Set gradient background."""
        # Use stylesheet for better cross-platform compatibility
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4A90E2,
                    stop:1 #6A5ACD
                );
            }
        """)
    
    def create_login_card(self) -> QWidget:
        """
        Create login card widget.
        
        Returns:
            Login card widget
        """
        card = QWidget()
        card.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 10px;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)
        
        # Username input
        username_label = QLabel("用户名")
        username_label.setFont(QFont("Arial", 10))
        layout.addWidget(username_label)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("请输入用户名")
        self.username_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 5px;
                font-size: 12px;
            }
            QLineEdit:focus {
                border: 2px solid #4A90E2;
            }
        """)
        layout.addWidget(self.username_input)
        
        # Password input
        password_label = QLabel("密码")
        password_label.setFont(QFont("Arial", 10))
        layout.addWidget(password_label)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("请输入密码")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 5px;
                font-size: 12px;
            }
            QLineEdit:focus {
                border: 2px solid #4A90E2;
            }
        """)
        self.password_input.returnPressed.connect(self.handle_login)
        layout.addWidget(self.password_input)
        
        # Remember me checkbox
        self.remember_checkbox = QCheckBox("记住用户名")
        self.remember_checkbox.setFont(QFont("Arial", 9))
        layout.addWidget(self.remember_checkbox)
        
        layout.addSpacing(10)
        
        # Login button
        self.login_button = QPushButton("登录")
        self.login_button.setFont(QFont("Arial", 12, QFont.Bold))
        self.login_button.setStyleSheet("""
            QPushButton {
                background-color: #4A90E2;
                color: white;
                padding: 12px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #357ABD;
            }
            QPushButton:pressed {
                background-color: #2E5C8A;
            }
        """)
        self.login_button.clicked.connect(self.handle_login)
        layout.addWidget(self.login_button)
        
        # Register button
        self.register_button = QPushButton("注册新账号")
        self.register_button.setFont(QFont("Arial", 10))
        self.register_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #4A90E2;
                padding: 8px;
                border: 1px solid #4A90E2;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: rgba(74, 144, 226, 0.1);
            }
        """)
        self.register_button.clicked.connect(self.handle_register)
        layout.addWidget(self.register_button)
        
        card.setLayout(layout)
        return card
    
    def handle_login(self):
        """Handle login button click."""
        username = self.username_input.text().strip()
        password = self.password_input.text()
        
        if not username or not password:
            QMessageBox.warning(self, "错误", "请输入用户名和密码")
            return
        
        # Attempt login
        success, message = self.auth_manager.login(username, password)
        
        if success:
            # Save username if remember me is checked
            if self.remember_checkbox.isChecked():
                from config import config
                config.set("remember_username", username)
            
            # Emit signal and close
            user = self.auth_manager.get_current_user()
            self.login_successful.emit(user)
            self.accept()
        else:
            QMessageBox.warning(self, "登录失败", message)
    
    def handle_register(self):
        """Handle register button click."""
        username = self.username_input.text().strip()
        password = self.password_input.text()
        
        if not username or not password:
            QMessageBox.warning(self, "错误", "请输入用户名和密码")
            return
        
        # Attempt registration
        success, message = self.auth_manager.register(username, password)
        
        if success:
            QMessageBox.information(self, "注册成功", f"{message}\n请使用新账号登录")
            # Clear password field
            self.password_input.clear()
        else:
            QMessageBox.warning(self, "注册失败", message)
    
    def showEvent(self, event):
        """Override show event to load remembered username."""
        super().showEvent(event)
        
        # Load remembered username
        from config import config
        remembered_username = config.get("remember_username", "")
        if remembered_username:
            self.username_input.setText(remembered_username)
            self.remember_checkbox.setChecked(True)
            self.password_input.setFocus()
