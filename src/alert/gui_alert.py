"""
GUI-based alert system using pyautogui.
Handles automatic interaction with the WeChat interface.
"""

import pyautogui
import os
import platform
import subprocess
import time
from pathlib import Path
import traceback
from utils.logger import get_logger

logger = get_logger(__name__)

class GUIAlert:
    """Manages GUI-based alerts using pyautogui."""
    
    def __init__(self, resource_dir: Path):
        """
        Initialize GUI alert.
        
        Args:
            resource_dir: Directory containing reference images for buttons
        """
        self.resource_dir = resource_dir
        self.call_button_img = self.resource_dir / "wechat" / "call_button.png"
        
        # Configure pyautogui
        pyautogui.PAUSE = 0.5  # Add delay between actions
        pyautogui.FAILSAFE = True  # Move mouse to corner to abort
        
        logger.info(f"GUIAlert initialized with resource dir: {resource_dir}")
    
    def trigger_wechat_call(self) -> bool:
        """
        Locate and click the WeChat call button.
        
        Returns:
            True if successful, False otherwise
        """
        if not self.call_button_img.exists():
            logger.error(f"WeChat call button image not found: {self.call_button_img}")
            return False
        
        try:
            # 1. Activate/Focus WeChat
            if not self.activate_wechat():
                logger.warning("Could not activate WeChat, continuing with best effort...")
            
            # 2. Center and resize WeChat for consistent identification
            # Try centering with retries as window might take a moment to appear
            centered = False
            for i in range(3):
                if self.center_window():
                    centered = True
                    break
                time.sleep(1.0)
            
            if not centered:
                logger.warning("Failed to center window after retries.")
            
            # Wait a moment for window to stabilize
            time.sleep(1.0)
            
            logger.info("Searching for WeChat call button on screen...")
            # Try to find the button
            location = pyautogui.locateOnScreen(str(self.call_button_img), confidence=0.8)
            
            success = False
            if location:
                center = pyautogui.center(location)
                logger.info(f"Found call button at: {center}. Clicking...")
                
                # Perform safe click with Retina handling
                self._safe_click(center)
                success = True
            else:
                logger.warning("WeChat call button not found on screen.")
            
            # 3. Minimize WeChat removed to keep window open for user
            # time.sleep(0.5)
            # self.minimize_window()
            
            return success
                
        except Exception as e:
            logger.error(f"Error triggering WeChat call: {repr(e)}")
            logger.error(traceback.format_exc())
            return False

    def _safe_click(self, point):
        """
        Perform a robust click, handling macOS Retina scaling issues.
        
        Args:
            point: The point to click (from locateOnScreen)
        """
        x, y = point
        screen_w, screen_h = pyautogui.size()
        
        logger.info(f"Screen size: {screen_w}x{screen_h}, Target: {x}, {y}")
        
        # Check for Retina scaling issue on macOS
        # If target is outside screen bounds, it's likely a retina coordinate (2x)
        if platform.system() == "Darwin" and (x > screen_w or y > screen_h):
            logger.info("Detected Retina coordinate mismatch. Adjusting by 0.5x...")
            x = x / 2
            y = y / 2
            logger.info(f"Adjusted Target: {x}, {y}")
            
        # Move first, then click
        try:
            pyautogui.moveTo(x, y)
            time.sleep(0.2) # Short pause to ensure move completes
            pyautogui.click()
            logger.info("Click sent.")
        except Exception as e:
            logger.error(f"Failed to click: {e}")

    def activate_wechat(self) -> bool:
        """
        Activate the WeChat application across different platforms.
        
        Returns:
            True if successful, False otherwise
        """
        system = platform.system()
        logger.info(f"Activating WeChat on {system}...")
        
        try:
            if system == "Darwin":  # macOS
                # Use 'open' command which is robust for launching/activating
                try:
                    subprocess.run(["open", "-a", "WeChat"], check=True, stderr=subprocess.PIPE)
                except subprocess.CalledProcessError:
                    logger.warning("WeChat not found by name, trying bundle ID...")
                    # Try common bundle IDs
                    try:
                        subprocess.run(["open", "-b", "com.tencent.xinWeChat"], check=True)
                    except subprocess.CalledProcessError:
                        logger.error("Could not activate WeChat: Application not found via name or bundle ID.")
                        return False
                
                # Wait for app to be frontmost
                time.sleep(1.0)
                
                # Optional: Ensure it's active via AppleScript if open doesn't focus
                try:
                    script = 'tell application "WeChat" to activate'
                    subprocess.run(["osascript", "-e", script], check=True, stderr=subprocess.PIPE)
                except:
                    pass
                return True
            elif system == "Windows":
                # Using start command
                subprocess.run(["cmd", "/c", "start", "wechat"], shell=True, check=True)
                return True
            elif system == "Linux":
                subprocess.run(["wmctrl", "-a", "WeChat"], check=True)
                return True
            else:
                logger.warning(f"Activation not implemented for OS: {system}")
                return False
        except Exception as e:
            logger.error(f"Failed to activate WeChat: {e}")
            return False

    def center_window(self) -> bool:
        """
        Center and resize the WeChat window on the screen.
        """
        system = platform.system()
        logger.info(f"Centering WeChat window on {system}...")
        
        try:
            if system == "Darwin":  # macOS
                # Use System Events which is more reliable for window manipulation
                script = """
                tell application "Finder"
                    set screen_bounds to bounds of window of desktop
                    set {screen_x, screen_y, screen_w, screen_h} to screen_bounds
                end tell
                
                tell application "System Events"
                    tell process "WeChat"
                        set frontmost to true
                        -- Check if any windows exist
                        if (count of windows) > 0 then
                            set window_w to 1000
                            set window_h to 800
                            set pos_x to ((screen_w - window_w) / 2) as integer
                            set pos_y to ((screen_h - window_h) / 2) as integer
                            
                            try
                                set position of window 1 to {pos_x, pos_y}
                                set size of window 1 to {window_w, window_h}
                            on error
                                -- Fallback: sometimes setting size fails if window is not resizable
                                set position of window 1 to {pos_x, pos_y}
                            end try
                        else
                            return "NO_WINDOW"
                        end if
                    end tell
                end tell
                """
                # Run script and capture output to check for "NO_WINDOW"
                result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True, check=True)
                if "NO_WINDOW" in result.stdout:
                    logger.warning("WeChat process found but no windows available.")
                    return False
                return True
            elif system == "Windows":
                # Windows centering is harder without extra libs like pygetwindow
                # Best effort: just ensure it's not minimized
                return True
            elif system == "Linux":
                # Use wmctrl to center
                subprocess.run(["wmctrl", "-r", "WeChat", "-e", "0,-1,-1,1000,800"], check=True)
                return True
        except subprocess.CalledProcessError as e:
            if "(-1719)" in str(e) or "(-10006)" in str(e):
                 logger.warning(f"Window manipulation failed due to permissions or lack of support. Please grant Accessibility permissions to Terminal/Python.")
            else:
                 logger.warning(f"Failed to center WeChat window: {e}")
        except Exception as e:
            logger.warning(f"Failed to center WeChat window: {e}")
        return False

    def minimize_window(self) -> bool:
        """
        Minimize/Hide the WeChat window to avoid interfering with screen monitoring.
        """
        system = platform.system()
        logger.info(f"Minimizing WeChat window on {system}...")
        
        try:
            if system == "Darwin":  # macOS
                # Use System Events to minimize
                try:
                    # Try setting attribute first (cleaner)
                    script = """
                    tell application "System Events"
                        tell process "WeChat"
                            set value of attribute "AXMinimized" of window 1 to true
                        end tell
                    end tell
                    """
                    subprocess.run(["osascript", "-e", script], check=True)
                except subprocess.CalledProcessError:
                    # Fallback to Command+M
                    logger.info("AXMinimized failed, trying Command+M...")
                    script = """
                    tell application "System Events"
                        tell process "WeChat"
                            set frontmost to true
                            keystroke "m" using command down
                        end tell
                    end tell
                    """
                    subprocess.run(["osascript", "-e", script], check=True)
                return True
            elif system == "Windows":
                # PowerShell to minimize all windows of a process
                # Using a generic minimize for now
                subprocess.run(["powershell", "-command", "(Get-Process WeChat).MainWindowHandle | foreach { (New-Object -ComObject Shell.Application).MinimizeAll() }"], shell=True)
                return True
            elif system == "Linux":
                subprocess.run(["wmctrl", "-r", "WeChat", "-b", "add,iconified"], check=True)
                return True
        except Exception as e:
            logger.warning(f"Failed to minimize WeChat window: {e}")
        return False

    def get_system_info(self):
        """Get system information for platform-specific adjustments."""
        return {
            "os": platform.system(),
            "version": platform.version(),
            "machine": platform.machine()
        }
