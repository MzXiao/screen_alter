"""
Region Selector component.
Allows users to select a specific rectangular area of the screen for monitoring.
"""

from PyQt5.QtWidgets import QWidget, QRubberBand
from PyQt5.QtCore import Qt, QRect, QSize, pyqtSignal, QPoint
from PyQt5.QtGui import QColor, QPalette

class RegionSelector(QWidget):
    """A transparent overlay for selecting a screen region."""
    
    region_selected = pyqtSignal(tuple)
    
    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.FramelessWindowHint | 
            Qt.WindowStaysOnTopHint | 
            Qt.Tool |
            Qt.X11BypassWindowManagerHint
        )
        self.setWindowOpacity(0.3)
        self.setStyleSheet("background-color: black;")
        
        # Make it full screen
        from PyQt5.QtWidgets import QApplication
        screen = QApplication.primaryScreen()
        self.setGeometry(screen.geometry())
        
        self.origin = QPoint()
        self.rubber_band = QRubberBand(QRubberBand.Rectangle, self)
        
        # Set cursor
        self.setCursor(Qt.CrossCursor)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.origin = event.pos()
            self.rubber_band.setGeometry(QRect(self.origin, QSize()))
            self.rubber_band.show()
            
    def mouseMoveEvent(self, event):
        if not self.rubber_band.isHidden():
            self.rubber_band.setGeometry(QRect(self.origin, event.pos()).normalized())
            
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            rect = self.rubber_band.geometry()
            self.rubber_band.hide()
            self.close()
            
            # Emit the selected region (left, top, width, height)
            # Need to adjust for screen coordinates if necessary, but here we are full screen
            self.region_selected.emit((rect.x(), rect.y(), rect.width(), rect.height()))
            
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
