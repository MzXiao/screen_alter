"""
Screen capture functionality.
Handles taking screenshots and managing screenshot storage.
"""

import mss
import mss.tools
from PIL import Image
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Tuple
import os

from utils.logger import get_logger

logger = get_logger(__name__)


class ScreenCapture:
    """Manages screen capture operations."""
    
    def __init__(self, screenshots_dir: Path, retention_days: int = 7):
        """
        Initialize screen capture.
        
        Args:
            screenshots_dir: Directory to save screenshots
            retention_days: Number of days to keep screenshots
        """
        self.screenshots_dir = screenshots_dir
        self.retention_days = retention_days
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)
    
    def capture_screen(self, region: Optional[Tuple[int, int, int, int]] = None) -> Optional[Image.Image]:
        """
        Capture screenshot of full screen or specific region.
        
        Args:
            region: Optional tuple of (left, top, width, height) for specific region
        
        Returns:
            PIL Image object or None if capture fails
        """
        try:
            with mss.mss() as sct:
                if region:
                    # Capture specific region
                    monitor = {
                        "left": region[0],
                        "top": region[1],
                        "width": region[2],
                        "height": region[3]
                    }
                else:
                    # Capture primary monitor
                    monitor = sct.monitors[1]
                
                # Capture screenshot
                sct_img = sct.grab(monitor)
                
                # Convert to PIL Image
                img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
                
                logger.debug(f"Screenshot captured: {img.size}")
                return img
                
        except Exception as e:
            logger.error(f"Failed to capture screenshot: {e}")
            return None
    
    def save_screenshot(self, image: Image.Image, prefix: str = "screenshot") -> Optional[str]:
        """
        Save screenshot to disk.
        
        Args:
            image: PIL Image to save
            prefix: Filename prefix
        
        Returns:
            Path to saved screenshot or None
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{prefix}_{timestamp}.png"
            filepath = self.screenshots_dir / filename
            
            image.save(filepath, "PNG")
            logger.info(f"Screenshot saved: {filepath}")
            
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Failed to save screenshot: {e}")
            return None
    
    def capture_and_save(self, region: Optional[Tuple[int, int, int, int]] = None) -> Optional[Tuple[Image.Image, str]]:
        """
        Capture screenshot and save to disk.
        
        Args:
            region: Optional region to capture
        
        Returns:
            Tuple of (Image, filepath) or None
        """
        image = self.capture_screen(region)
        if image:
            filepath = self.save_screenshot(image)
            if filepath:
                return image, filepath
        return None
    
    def cleanup_old_screenshots(self):
        """Delete screenshots older than retention period."""
        try:
            cutoff_date = datetime.now() - timedelta(days=self.retention_days)
            deleted_count = 0
            
            for filepath in self.screenshots_dir.glob("*.png"):
                # Get file modification time
                mtime = datetime.fromtimestamp(filepath.stat().st_mtime)
                
                if mtime < cutoff_date:
                    filepath.unlink()
                    deleted_count += 1
            
            if deleted_count > 0:
                logger.info(f"Cleaned up {deleted_count} old screenshots")
                
        except Exception as e:
            logger.error(f"Failed to cleanup screenshots: {e}")
    
    def get_screenshot_count(self) -> int:
        """
        Get number of screenshots in storage.
        
        Returns:
            Number of screenshot files
        """
        try:
            return len(list(self.screenshots_dir.glob("*.png")))
        except Exception as e:
            logger.error(f"Failed to count screenshots: {e}")
            return 0
    
    def get_storage_size(self) -> int:
        """
        Get total size of screenshot storage in bytes.
        
        Returns:
            Total size in bytes
        """
        try:
            total_size = 0
            for filepath in self.screenshots_dir.glob("*.png"):
                total_size += filepath.stat().st_size
            return total_size
        except Exception as e:
            logger.error(f"Failed to calculate storage size: {e}")
            return 0
