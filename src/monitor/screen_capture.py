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
    
    def __init__(self, screenshots_dir: Path, retention_days: int = 7, max_count: int = 100):
        """
        Initialize screen capture.
        
        Args:
            screenshots_dir: Directory to save screenshots
            retention_days: Number of days to keep screenshots
            max_count: Maximum number of screenshots to keep
        """
        self.screenshots_dir = screenshots_dir
        self.retention_days = retention_days
        self.max_count = max_count
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)
    
    def capture_screen(self, region: Optional[Tuple[int, int, int, int]] = None) -> Optional[Image.Image]:
        """
        Capture screenshot of full screen or specific region.
        
        Args:
            region: Optional tuple of (left, top, width, height) for specific region.
                    If None and config specifies, can be center square.
        
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
                    # Capture center square by default if no region provided
                    monitor = self._get_center_region(sct.monitors[1])
                
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

    def _get_center_region(self, monitor: dict, size: int = 500) -> dict:
        """Calculate a center square region."""
        width = monitor["width"]
        height = monitor["height"]
        
        # Ensure size doesn't exceed monitor bounds
        size = min(size, width, height)
        
        left = monitor["left"] + (width - size) // 2
        top = monitor["top"] + (height - size) // 2
        
        return {
            "left": left,
            "top": top,
            "width": size,
            "height": size
        }
    
    def cleanup_old_screenshots(self):
        """Delete screenshots older than retention period OR exceeding max_count."""
        try:
            # 1. Age-based cleanup
            cutoff_date = datetime.now() - timedelta(days=self.retention_days)
            
            files = sorted(
                self.screenshots_dir.glob("*.png"),
                key=lambda x: x.stat().st_mtime,
                reverse=True
            )
            
            deleted_count = 0
            
            # Keep track of files to delete
            to_delete = []
            
            for filepath in files:
                mtime = datetime.fromtimestamp(filepath.stat().st_mtime)
                if mtime < cutoff_date:
                    to_delete.append(filepath)
            
            # 2. Count-based cleanup (keep newest self.max_count)
            # Filter out files already marked for deletion
            remaining_files = [f for f in files if f not in to_delete]
            
            if len(remaining_files) > self.max_count:
                to_delete.extend(remaining_files[self.max_count:])
            
            for filepath in to_delete:
                filepath.unlink()
                deleted_count += 1
            
            if deleted_count > 0:
                logger.info(f"Cleaned up {deleted_count} screenshots (Age or Count limit)")
                
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
