"""
Main application window.
Provides the primary user interface for monitoring configuration and control.
"""

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem, QComboBox,
    QListWidget, QFileDialog, QMessageBox, QGroupBox, QLineEdit,
    QHeaderView, QAbstractItemView, QDialog
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QPixmap, QIcon
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List

from database.db_manager import DatabaseManager
from monitor.screen_capture import ScreenCapture
from monitor.ocr_detector import OCRDetector
from monitor.image_detector import ImageDetector
from alert.gui_alert import GUIAlert
from config import config
from utils.logger import get_logger

logger = get_logger(__name__)


class MainWindow(QMainWindow):
    """Main application window."""
    
    monitoring_started = pyqtSignal()
    monitoring_stopped = pyqtSignal()
    
    def __init__(
        self,
        db_manager: DatabaseManager,
        user_id: int,
        username: str,
        parent=None
    ):
        """
        Initialize main window.
        
        Args:
            db_manager: Database manager
            user_id: Current user ID
            username: Current username
            parent: Parent widget
        """
        super().__init__(parent)
        logger.info("MainWindow: Starting initialization...")
        self.db = db_manager
        self.user_id = user_id
        self.username = username
        
        logger.info("MainWindow: Initializing screen capture...")
        # Initialize components
        self.screen_capture = ScreenCapture(
            config.screenshots_dir,
            config.get("screenshot_retention_days", 7)
        )
        logger.info("MainWindow: Screen capture initialized")
        
        self.ocr_detector = None
        self.image_detector = ImageDetector(config.get("similarity_threshold", 0.85))
        self.gui_alert = GUIAlert(config.root_dir / "resources")
        logger.info("MainWindow: Detectors initialized")
        
        # Monitoring state
        self.is_monitoring = False
        self.monitor_timer = QTimer()
        self.monitor_timer.timeout.connect(self.perform_monitoring_check)
        
        # Load user config
        logger.info("MainWindow: Loading user config...")
        self.user_config = self.db.get_config(user_id) or {}
        logger.info("MainWindow: User config loaded")
        
        logger.info("MainWindow: Setting up UI...")
        self.setup_ui()
        logger.info("MainWindow: UI setup complete")
        
        logger.info("MainWindow: Loading config to UI...")
        self.load_config_to_ui()
        logger.info("MainWindow: Initialization complete")
    
    def setup_ui(self):
        """Set up the user interface."""
        self.setWindowTitle("Screen Monitor - 控制面板")
        self.setMinimumSize(900, 700)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Top section - User info and status
        layout.addWidget(self.create_header())
        
        # Status card
        layout.addWidget(self.create_status_card())
        
        # Configuration panel
        layout.addWidget(self.create_config_panel())
        
        # Alert log table
        layout.addWidget(self.create_alert_log())
        
        # Control buttons
        layout.addWidget(self.create_control_buttons())
        
        central_widget.setLayout(layout)
        
        # Apply stylesheet
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #ddd;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
    
    def create_header(self) -> QWidget:
        """Create header with user info."""
        header = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # User info
        user_label = QLabel(f"👤 {self.username}")
        user_label.setFont(QFont("Arial", 12))
        layout.addWidget(user_label)
        
        layout.addStretch()
        
        # Settings button
        settings_btn = QPushButton("⚙️ 设置")
        settings_btn.setStyleSheet("""
            QPushButton {
                padding: 8px 15px;
                background-color: #f0f0f0;
                border: 1px solid #ddd;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        layout.addWidget(settings_btn)
        
        header.setLayout(layout)
        return header
    
    def create_status_card(self) -> QWidget:
        """Create monitoring status card."""
        card = QGroupBox("监控状态")
        layout = QHBoxLayout()
        
        # Status indicator
        self.status_indicator = QLabel("●")
        self.status_indicator.setFont(QFont("Arial", 24))
        self.status_indicator.setStyleSheet("color: #dc3545;")  # Red
        layout.addWidget(self.status_indicator)
        
        # Status text
        self.status_text = QLabel("已停止")
        self.status_text.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(self.status_text)
        
        layout.addStretch()
        
        card.setLayout(layout)
        return card
    
    def create_config_panel(self) -> QWidget:
        """Create configuration panel."""
        panel = QGroupBox("配置")
        layout = QVBoxLayout()
        
        # Monitor interval and OCR Engine
        settings_row = QHBoxLayout()
        settings_row.addWidget(QLabel("监控间隔:"))
        
        self.interval_combo = QComboBox()
        self.interval_combo.addItems(["30秒", "1分钟", "5分钟", "10分钟"])
        self.interval_combo.currentIndexChanged.connect(self.save_config)
        settings_row.addWidget(self.interval_combo)
        
        settings_row.addSpacing(20)
        settings_row.addWidget(QLabel("OCR 引擎:"))
        self.ocr_engine_combo = QComboBox()
        self.ocr_engine_combo.addItems(["pytesseract", "easyocr"])
        self.ocr_engine_combo.currentIndexChanged.connect(self.save_config)
        settings_row.addWidget(self.ocr_engine_combo)
        
        settings_row.addStretch()
        layout.addLayout(settings_row)

        
        # Keywords
        keywords_label = QLabel("关键词列表:")
        keywords_label.setFont(QFont("Arial", 10, QFont.Bold))
        layout.addWidget(keywords_label)
        
        keywords_layout = QHBoxLayout()
        
        self.keywords_list = QListWidget()
        self.keywords_list.setMaximumHeight(100)
        keywords_layout.addWidget(self.keywords_list)
        
        keywords_buttons = QVBoxLayout()
        add_keyword_btn = QPushButton("添加")
        add_keyword_btn.clicked.connect(self.add_keyword)
        keywords_buttons.addWidget(add_keyword_btn)
        
        remove_keyword_btn = QPushButton("删除")
        remove_keyword_btn.clicked.connect(self.remove_keyword)
        keywords_buttons.addWidget(remove_keyword_btn)
        keywords_buttons.addStretch()
        
        keywords_layout.addLayout(keywords_buttons)
        layout.addLayout(keywords_layout)
        
        # Reference images
        ref_images_label = QLabel("参考图片:")
        ref_images_label.setFont(QFont("Arial", 10, QFont.Bold))
        layout.addWidget(ref_images_label)
        
        ref_images_layout = QHBoxLayout()
        
        self.ref_images_list = QListWidget()
        self.ref_images_list.setMaximumHeight(100)
        ref_images_layout.addWidget(self.ref_images_list)
        
        ref_buttons = QVBoxLayout()
        add_ref_btn = QPushButton("上传")
        add_ref_btn.clicked.connect(self.add_reference_image)
        ref_buttons.addWidget(add_ref_btn)
        
        remove_ref_btn = QPushButton("删除")
        remove_ref_btn.clicked.connect(self.remove_reference_image)
        ref_buttons.addWidget(remove_ref_btn)
        ref_buttons.addStretch()
        
        ref_images_layout.addLayout(ref_buttons)
        layout.addLayout(ref_images_layout)
        
        # Region configuration
        region_layout = QHBoxLayout()
        region_layout.addWidget(QLabel("监控区域:"))
        
        self.region_label = QLabel("全屏")
        self.region_label.setStyleSheet("color: #666; font-style: italic;")
        region_layout.addWidget(self.region_label)
        
        self.select_region_btn = QPushButton("选择区域")
        self.select_region_btn.clicked.connect(self.select_capture_region)
        region_layout.addWidget(self.select_region_btn)
        
        self.reset_region_btn = QPushButton("重置全屏")
        self.reset_region_btn.clicked.connect(self.reset_capture_region)
        region_layout.addWidget(self.reset_region_btn)
        
        region_layout.addStretch()
        layout.addLayout(region_layout)
        
        panel.setLayout(layout)
        return panel
    
    def create_alert_log(self) -> QWidget:
        """Create alert log table."""
        group = QGroupBox("最近报警记录")
        layout = QVBoxLayout()
        
        self.alert_table = QTableWidget()
        self.alert_table.setColumnCount(4)
        self.alert_table.setHorizontalHeaderLabels(["时间", "关键词", "检测方式", "状态"])
        self.alert_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.alert_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.alert_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.alert_table.setMaximumHeight(200)
        
        layout.addWidget(self.alert_table)
        
        # Refresh and History buttons
        buttons_layout = QHBoxLayout()
        refresh_btn = QPushButton("刷新报警")
        refresh_btn.clicked.connect(self.load_alert_log)
        buttons_layout.addWidget(refresh_btn)
        
        history_btn = QPushButton("查看监控历史")
        history_btn.clicked.connect(self.view_monitoring_history)
        buttons_layout.addWidget(history_btn)
        
        layout.addLayout(buttons_layout)
        
        group.setLayout(layout)
        return group


    
    def create_control_buttons(self) -> QWidget:
        """Create control buttons."""
        widget = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Start button
        self.start_btn = QPushButton("▶ 开始监控")
        self.start_btn.setFont(QFont("Arial", 12, QFont.Bold))
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                padding: 12px 30px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:disabled {
                background-color: #6c757d;
            }
        """)
        self.start_btn.clicked.connect(self.start_monitoring)
        layout.addWidget(self.start_btn)
        
        # Stop button
        self.stop_btn = QPushButton("⏸ 停止监控")
        self.stop_btn.setFont(QFont("Arial", 12, QFont.Bold))
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                padding: 12px 30px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
            QPushButton:disabled {
                background-color: #6c757d;
            }
        """)
        self.stop_btn.clicked.connect(self.stop_monitoring)
        self.stop_btn.setEnabled(False)
        layout.addWidget(self.stop_btn)
        
        layout.addStretch()
        
        widget.setLayout(layout)
        return widget
    
    def load_config_to_ui(self):
        """Load configuration to UI elements."""
        # OCR Engine
        current_engine = self.user_config.get("ocr_engine", "pytesseract")
        engine_idx = 0 if current_engine == "pytesseract" else 1
        self.ocr_engine_combo.setCurrentIndex(engine_idx)
        
        # Monitor interval
        
        # Keywords
        keywords = self.user_config.get("keywords", [])
        for keyword in keywords:
            self.keywords_list.addItem(keyword)
        
        # Reference images
        ref_images = self.user_config.get("reference_images", [])
        for img_path in ref_images:
            self.ref_images_list.addItem(Path(img_path).name)
        
        # Capture region
        region = self.user_config.get("capture_region")
        if region:
            self.region_label.setText(f"{region[0]}, {region[1]}, {region[2]}x{region[3]}")
        else:
            self.region_label.setText("全屏")
        
        # Load alert log
        self.load_alert_log()
    
    def save_config(self):
        """Save current configuration."""
        # Get interval and engine
        interval_map = {0: 30, 1: 60, 2: 300, 3: 600}
        interval = interval_map.get(self.interval_combo.currentIndex(), 60)
        ocr_engine = self.ocr_engine_combo.currentText()
        
        # Get keywords
        keywords = [self.keywords_list.item(i).text() 
                   for i in range(self.keywords_list.count())]
        
        # Get reference images (stored as full paths in user_config)
        ref_images = self.user_config.get("reference_images", [])
        
        # Get region
        capture_region = self.user_config.get("capture_region")
        
        # Save to database
        self.db.create_or_update_config(
            self.user_id,
            monitor_interval=interval,
            ocr_engine=ocr_engine,
            keywords=keywords,
            capture_region=capture_region,
            reference_images=ref_images
        )
        
        # Reload config
        self.user_config = self.db.get_config(self.user_id) or {}

    def select_capture_region(self):
        """Allow user to select a capture region."""
        from gui.region_selector import RegionSelector
        
        self.selector = RegionSelector()
        self.selector.region_selected.connect(self.on_region_selected)
        self.selector.show()

    def on_region_selected(self, region):
        """Handle region selected event."""
        self.user_config["capture_region"] = region
        self.region_label.setText(f"{region[0]}, {region[1]}, {region[2]}x{region[3]}")
        self.save_config()
        QMessageBox.information(self, "成功", f"监控区域已设置为: {region}")

    def reset_capture_region(self):
        """Reset capture region to full screen."""
        self.user_config["capture_region"] = None
        self.region_label.setText("全屏")
        self.save_config()
        QMessageBox.information(self, "成功", "已重置为全屏监控")
    
    def add_keyword(self):
        """Add a new keyword."""
        from PyQt5.QtWidgets import QInputDialog
        
        keyword, ok = QInputDialog.getText(self, "添加关键词", "请输入关键词:")
        if ok and keyword.strip():
            self.keywords_list.addItem(keyword.strip())
            self.save_config()
    
    def remove_keyword(self):
        """Remove selected keyword."""
        current_row = self.keywords_list.currentRow()
        if current_row >= 0:
            self.keywords_list.takeItem(current_row)
            self.save_config()
    
    def update_screenshot_preview(self, pixmap: QPixmap):
        """Update screenshot preview."""
        self.screenshot_label.setPixmap(pixmap.scaled(
            self.screenshot_label.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        ))

    def view_monitoring_history(self):
        """Open monitoring history dialog."""
        dialog = MonitoringHistoryDialog(self.db, self.user_id, self)
        dialog.exec_()
    
    def add_reference_image(self):
        """Add a reference image."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择参考图片",
            "",
            "图片文件 (*.png *.jpg *.jpeg *.bmp)"
        )
        
        if file_path:
            # Validate image
            is_valid, error_msg = self.image_detector.validate_reference_image(file_path)
            if not is_valid:
                QMessageBox.warning(self, "错误", error_msg)
                return
            
            # Add to list
            ref_images = self.user_config.get("reference_images", [])
            if file_path not in ref_images:
                ref_images.append(file_path)
                self.ref_images_list.addItem(Path(file_path).name)
                self.user_config["reference_images"] = ref_images
                self.save_config()
    
    def remove_reference_image(self):
        """Remove selected reference image."""
        current_row = self.ref_images_list.currentRow()
        if current_row >= 0:
            ref_images = self.user_config.get("reference_images", [])
            if current_row < len(ref_images):
                ref_images.pop(current_row)
                self.ref_images_list.takeItem(current_row)
                self.user_config["reference_images"] = ref_images
                self.save_config()
    
    def load_alert_log(self):
        """Load alert log from database."""
        alerts = self.db.get_recent_alerts(self.user_id, limit=20)
        
        self.alert_table.setRowCount(len(alerts))
        
        for i, alert in enumerate(alerts):
            # Time
            created_at = alert.get("created_at", "")
            self.alert_table.setItem(i, 0, QTableWidgetItem(str(created_at)))
            
            # Keyword
            keyword = alert.get("detected_keyword", "N/A")
            self.alert_table.setItem(i, 1, QTableWidgetItem(keyword))
            
            # Detection method
            method = alert.get("detection_method", "")
            method_text = "OCR" if method == "ocr" else "图像相似度"
            self.alert_table.setItem(i, 2, QTableWidgetItem(method_text))
            
            # Status
            alert_sent = alert.get("alert_sent", 0)
            status = "已发送" if alert_sent else "未发送"
            self.alert_table.setItem(i, 3, QTableWidgetItem(status))
    
    def start_monitoring(self):
        """Start monitoring."""
        # Validate configuration
        keywords = [self.keywords_list.item(i).text() 
                   for i in range(self.keywords_list.count())]
        ref_images = self.user_config.get("reference_images", [])
        
        if not keywords and not ref_images:
            QMessageBox.warning(
                self,
                "配置错误",
                "请至少添加一个关键词或参考图片"
            )
            return
        
        # Initialize OCR detector if needed
        if keywords:
            try:
                ocr_engine = self.user_config.get("ocr_engine", "pytesseract")
                ocr_language = self.user_config.get("ocr_language", "chi_sim+eng")
                logger.info(f"Initializing OCR detector with engine: {ocr_engine}")
                self.ocr_detector = OCRDetector(ocr_engine, ocr_language)

            except Exception as e:
                QMessageBox.critical(
                    self,
                    "OCR初始化失败",
                    f"无法初始化OCR引擎: {str(e)}\n\n请确保已安装Tesseract OCR或EasyOCR"
                )
                return
        
        # Start monitoring
        self.is_monitoring = True
        interval = self.user_config.get("monitor_interval", 60)
        self.monitor_timer.start(interval * 1000)  # Convert to milliseconds
        
        # Update UI
        self.status_indicator.setStyleSheet("color: #28a745;")  # Green
        self.status_text.setText("监控中")
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        
        # Emit signal
        self.monitoring_started.emit()
        
        logger.info("Monitoring started")
        QMessageBox.information(self, "成功", "监控已启动")
    
    def stop_monitoring(self):
        """Stop monitoring."""
        self.is_monitoring = False
        self.monitor_timer.stop()
        
        # Update UI
        self.status_indicator.setStyleSheet("color: #dc3545;")  # Red
        self.status_text.setText("已停止")
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        
        # Emit signal
        self.monitoring_stopped.emit()
        
        logger.info("Monitoring stopped")
    
    def perform_monitoring_check(self):
        """Perform a monitoring check."""
        try:
            # Get configuration
            keywords = [self.keywords_list.item(i).text() 
                       for i in range(self.keywords_list.count())]
            ref_images = self.user_config.get("reference_images", [])
            engine = self.ocr_detector.engine if self.ocr_detector else "None"
            region = self.user_config.get("capture_region")
            
            logger.info("--- Monitoring Check Started ---")
            logger.info(f"Target: {region if region else 'Full Screen'}")
            logger.info(f"OCR Engine: {engine}")
            logger.info(f"Keywords: {keywords}")
            logger.info(f"Ref Images: {[Path(p).name for p in ref_images]}")
            logger.info("--------------------------------")
            
            # Capture screenshot
            result = self.screen_capture.capture_and_save(region=region)
            if not result:
                logger.error("Failed to capture screenshot")
                return
            
            screenshot, screenshot_path = result

            
            detected = False
            detected_keyword = None
            detection_method = None
            similarity_score = None
            
            # OCR detection
            if keywords and self.ocr_detector:
                logger.info(f"Checking keywords using {self.ocr_detector.engine}...")
                ocr_result = self.ocr_detector.detect_keywords(screenshot, keywords)
                
                # Log a snippet of the extracted text to show what OCR sees
                text_snippet = ocr_result["extracted_text"][:100].replace('\n', ' ')
                logger.info(f"OCR Extracted: {text_snippet}...")
                
                if ocr_result["detected"]:
                    detected = True
                    detected_keyword = ", ".join(ocr_result["matched_keywords"])
                    detection_method = "ocr"
                    logger.info(f"OCR detection: {detected_keyword}")

            
            # Image similarity detection
            if ref_images and not detected:
                img_result = self.image_detector.compare_with_references(screenshot, ref_images)
                if img_result["detected"]:
                    detected = True
                    best_match = img_result["best_match"]
                    detected_keyword = Path(best_match["path"]).name
                    detection_method = "image_similarity"
                    similarity_score = best_match["similarity"]
                    logger.info(f"Image detection: {detected_keyword} ({similarity_score:.2f})")
            
            # If detected, create alert and send notification
            if detected:
                # Record alert
                alert_id = self.db.create_alert(
                    self.user_id,
                    detected_keyword=detected_keyword,
                    screenshot_path=screenshot_path,
                    detection_method=detection_method,
                    similarity_score=similarity_score,
                    alert_sent=False
                )
                
                # Record check log
                self.db.create_check_log(
                    self.user_id,
                    "DETECTED",
                    f"Detected {detection_method}: {detected_keyword}",
                    screenshot_path
                )
                
                # Trigger GUI Alert (WeChat Call)
                logger.info("Triggering GUI Alert (WeChat Call)...")
                success = self.gui_alert.trigger_wechat_call()
                
                if success and alert_id:
                    self.db.update_alert_sent_status(alert_id, True)
                elif not success:
                    logger.error("Failed to trigger GUI Alert")

                # Refresh alert log
                self.load_alert_log()
                
                # Pause monitoring after detection as requested
                logger.info("Monitoring paused due to detection.")
                self.stop_monitoring()
                QMessageBox.information(self, "监控暂停", "检测到目标，监控已自动暂停。\n微信窗口已保留在屏幕上。")
            else:
                logger.info("Check complete: No keywords or patterns detected.")
                self.db.create_check_log(
                    self.user_id,
                    "SUCCESS",
                    "No keywords or patterns detected",
                    screenshot_path
                )

            # Cleanup old screenshots
            self.screen_capture.cleanup_old_screenshots()
            
        except Exception as e:
            logger.error(f"Monitoring check failed: {e}")
            self.db.create_check_log(
                self.user_id,
                "FAILED",
                str(e)
            )

    def closeEvent(self, event):
        """Handle window close event."""
        if self.is_monitoring:
            reply = QMessageBox.question(
                self,
                "确认退出",
                "监控正在运行，确定要退出吗？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.stop_monitoring()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()


class MonitoringHistoryDialog(QDialog):
    """Dialog to show monitoring check history."""
    
    def __init__(self, db_manager, user_id, parent=None):
        super().__init__(parent)
        self.db = db_manager
        self.user_id = user_id
        self.setup_ui()
        self.load_history()
        
    def setup_ui(self):
        self.setWindowTitle("监控历史记录")
        self.setMinimumSize(800, 500)
        layout = QVBoxLayout()
        
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["时间", "状态", "详情", "截图"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
        layout.addWidget(self.table)
        
        refresh_btn = QPushButton("刷新")
        refresh_btn.clicked.connect(self.load_history)
        layout.addWidget(refresh_btn)
        
        self.setLayout(layout)
        
    def load_history(self):
        logs = self.db.get_recent_check_logs(self.user_id)
        self.table.setRowCount(len(logs))
        
        for i, log in enumerate(logs):
            self.table.setItem(i, 0, QTableWidgetItem(log['check_time']))
            
            status_item = QTableWidgetItem(log['result_status'])
            if log['result_status'] == 'DETECTED':
                status_item.setForeground(QColor("#dc3545"))
            elif log['result_status'] == 'FAILED':
                status_item.setForeground(QColor("#ffc107"))
            else:
                status_item.setForeground(QColor("#28a745"))
            self.table.setItem(i, 1, status_item)
            
            self.table.setItem(i, 2, QTableWidgetItem(log['details']))
            
            has_img = "有" if log['screenshot_path'] else "无"
            self.table.setItem(i, 3, QTableWidgetItem(has_img))

