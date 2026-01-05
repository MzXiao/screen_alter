"""
Application configuration management.
Handles application directories, default settings, and configuration persistence.
"""

import os
import json
from pathlib import Path
from typing import Dict, Any


class Config:
    """Application configuration manager."""
    
    # Application metadata
    APP_NAME = "ScreenMonitor"
    APP_VERSION = "1.0.0"
    
    # Backend configuration
    # Backend configuration
    # BACKEND_URL is now loaded from config.json

    
    # Default settings
    DEFAULT_MONITOR_INTERVAL = 60  # seconds
    DEFAULT_OCR_ENGINE = "paddleocr"  # or "pytesseract"
    DEFAULT_OCR_LANGUAGE = "chi_sim+eng"  # Chinese simplified + English
    DEFAULT_SIMILARITY_THRESHOLD = 0.85  # for image similarity (0-1)
    DEFAULT_SCREENSHOT_RETENTION_DAYS = 7
    
    def __init__(self):
        """Initialize configuration."""
        self.root_dir = Path(__file__).parent.parent.absolute()
        self.app_dir = self.root_dir  # Store everything in project root
        
        self.config_dir = self.root_dir / "config"
        self.config_file = self.config_dir / "config.json"
        self.db_path = self.root_dir / "screen_monitor.db"
        self.screenshots_dir = self.root_dir / "screenshots"
        self.logs_dir = self.root_dir / "logs"
        
        # Create directories if they don't exist
        self._ensure_directories()
        
        # Load or create configuration
        self.settings = self._load_config()
    
    def _get_app_directory(self) -> Path:
        """Deprecated: Return root directory."""
        return self.root_dir
    
    def _ensure_directories(self):
        """Create application directories if they don't exist."""
        for directory in [self.app_dir, self.config_dir, self.screenshots_dir, self.logs_dir]:
            directory.mkdir(parents=True, exist_ok=True)
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading config: {e}. Using defaults.")
                return self._get_default_config()
        else:
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            "monitor_interval": self.DEFAULT_MONITOR_INTERVAL,
            "ocr_engine": self.DEFAULT_OCR_ENGINE,
            "ocr_language": self.DEFAULT_OCR_LANGUAGE,
            "similarity_threshold": self.DEFAULT_SIMILARITY_THRESHOLD,
            "screenshot_retention_days": self.DEFAULT_SCREENSHOT_RETENTION_DAYS,
            "screenshot_limit": 100,
            "capture_region": None,  # (left, top, width, height) or None for full screen
            "keywords": [],
            "reference_images": [],
            "auto_start_monitoring": False,
            "backend_url": "http://localhost:8000",
        }
    
    def save(self):
        """Save current configuration to file."""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get(self, key: str, default=None):
        """Get configuration value."""
        return self.settings.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set configuration value."""
        self.settings[key] = value
        self.save()
    
    def update(self, settings: Dict[str, Any]):
        """Update multiple configuration values."""
        self.settings.update(settings)
        self.save()


# Global configuration instance
config = Config()
