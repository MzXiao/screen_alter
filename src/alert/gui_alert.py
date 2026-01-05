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
        
        # Support multiple button images for different OS/versions
        wechat_dir = self.resource_dir / "wechat"
        self.call_button_images = [
            wechat_dir / "call_button.png",          # 默认
            wechat_dir / "call_button_win.png",      # Windows 版本
            wechat_dir / "call_button_mac.png",      # Mac 版本
            wechat_dir / "call_button_alt.png",      # 备用版本
        ]
        
        # Configure pyautogui
        pyautogui.PAUSE = 0.5  # Add delay between actions
        pyautogui.FAILSAFE = True  # Move mouse to corner to abort
        
        logger.info(f"GUIAlert initialized with resource dir: {resource_dir}")
        
        # Check available button images
        available_images = [img for img in self.call_button_images if img.exists()]
        if available_images:
            logger.info(f"Found {len(available_images)} WeChat button image(s):")
            for img in available_images:
                logger.info(f"  - {img.name}")
        else:
            logger.warning(
                f"No WeChat call button images found in: {wechat_dir}\n"
                f"Expected files: call_button.png, call_button_win.png, call_button_mac.png\n"
                f"WeChat call functionality will not work."
            )
    
    def trigger_wechat_call(self) -> bool:
        """
        Locate and click the WeChat call button.
        Tries multiple button images for different OS/versions.
        
        Returns:
            True if successful, False otherwise
        """
        # Check if any button images exist
        available_images = [img for img in self.call_button_images if img.exists()]
        if not available_images:
            logger.error(f"No WeChat call button images found in: {self.resource_dir / 'wechat'}")
            logger.error("Please add button images: call_button.png, call_button_win.png, or call_button_mac.png")
            return False
        
        try:
            # 1. Activate/Focus WeChat
            if not self.activate_wechat():
                logger.warning("Could not activate WeChat, continuing with best effort...")
            
            # 2. Center and resize WeChat for consistent identification
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
            
            logger.info(f"Searching for WeChat call button (trying {len(available_images)} image(s))...")
            
            # Try to find the button using each available image
            location = None
            matched_image = None
            best_confidence = 0.0
            
            # Try different confidence levels (from strict to loose)
            confidence_levels = [0.8, 0.7, 0.6]
            
            for confidence in confidence_levels:
                for button_img in available_images:
                    try:
                        logger.debug(f"Trying {button_img.name} with confidence {confidence}...")
                        location = pyautogui.locateOnScreen(str(button_img), confidence=confidence)
                        
                        if location:
                            matched_image = button_img
                            logger.info(f"✅ Found button using {button_img.name} (confidence: {confidence})")
                            logger.info(f"   Location: {location}")
                            break
                    except Exception as e:
                        # Try to extract confidence from error message
                        error_msg = str(e)
                        if 'highest confidence' in error_msg.lower():
                            try:
                                import re
                                match = re.search(r'confidence = ([\d.]+)', error_msg)
                                if match:
                                    conf = float(match.group(1))
                                    if conf > best_confidence:
                                        best_confidence = conf
                            except:
                                pass
                        logger.debug(f"   {button_img.name}: Not found")
                        continue
                
                if location:
                    break  # Found with this confidence level
            
            # Log helpful info if no match found
            if not location:
                if best_confidence > 0:
                    logger.warning(
                        f"❌ Button not found. Best match: {best_confidence:.3f} (required: 0.6+)"
                    )
                else:
                    logger.warning("❌ Button not found on screen.")
                
                logger.info(
                    "\n💡 Tips:\n"
                    "  1. Make sure WeChat window is visible\n"
                    "  2. Navigate to a chat with call button visible\n"
                    "  3. Capture button screenshot and save as:\n"
                    f"     • {self.resource_dir / 'wechat' / 'call_button_win.png'} (Windows)\n"
                    f"     • {self.resource_dir / 'wechat' / 'call_button_mac.png'} (Mac)\n"
                    "  4. Try different display scaling (100% recommended)"
                )
                return False
            
            # Click the found button
            center = pyautogui.center(location)
            logger.info(f"Clicking at center: {center}")
            self._safe_click(center)
            return True
                
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
                # Try to activate WeChat on Windows
                import os
                
                # First, try to find and activate existing window
                wechat_activated = self._activate_wechat_window_windows()
                if wechat_activated:
                    logger.info("WeChat window activated successfully")
                    return True
                
                # If no window found, try to start WeChat
                logger.info("No active WeChat window found, attempting to start WeChat...")
                
                # Method 1: Try user-configured path (from config)
                wechat_started = False
                try:
                    from config_mod import config
                    wechat_path = config.get("wechat_path", "")
                    if wechat_path and os.path.exists(wechat_path):
                        logger.info(f"Using configured WeChat path: {wechat_path}")
                        subprocess.Popen([wechat_path])
                        wechat_started = True
                except Exception as e:
                    logger.debug(f"Could not use configured path: {e}")
                
                # Method 2: Try common installation paths
                if not wechat_started:
                    common_paths = [
                        os.path.expandvars(r"%ProgramFiles%\Tencent\WeChat\WeChat.exe"),
                        os.path.expandvars(r"%ProgramFiles(x86)%\Tencent\WeChat\WeChat.exe"),
                        os.path.expandvars(r"%LocalAppData%\Tencent\WeChat\WeChat.exe"),
                        os.path.expandvars(r"%AppData%\Tencent\WeChat\WeChat.exe"),
                        r"C:\Program Files\Tencent\WeChat\WeChat.exe",
                        r"C:\Program Files (x86)\Tencent\WeChat\WeChat.exe",
                    ]
                    
                    for wechat_path in common_paths:
                        try:
                            if os.path.exists(wechat_path):
                                logger.info(f"Found WeChat at: {wechat_path}")
                                subprocess.Popen([wechat_path])
                                wechat_started = True
                                break
                        except Exception as e:
                            logger.debug(f"Failed to start from {wechat_path}: {e}")
                
                if wechat_started:
                    # Wait for window to appear and try to activate
                    logger.info("Waiting for WeChat window to appear...")
                    time.sleep(2)
                    
                    # Try to activate the window
                    for attempt in range(5):
                        if self._activate_wechat_window_windows():
                            logger.info("WeChat window activated after startup")
                            return True
                        time.sleep(0.5)
                    
                    logger.warning("WeChat started but window could not be activated")
                    return True  # At least it's running
                
                # All methods failed
                logger.warning(
                    "WeChat not found. Please either:\n"
                    "  1. Install WeChat from https://weixin.qq.com/\n"
                    "  2. Run 'python find_wechat.py' to configure path\n"
                    "  3. Disable WeChat in config.json: 'wechat_enabled': false"
                )
                return False
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
                # Windows: Find and center WeChat window
                logger.info("Centering WeChat window on Windows...")
                return self._center_wechat_window_windows()
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

    def _activate_wechat_window_windows(self) -> bool:
        """
        Find and activate WeChat window on Windows.
        
        Returns:
            True if window found and activated, False otherwise
        """
        try:
            import ctypes
            from ctypes import wintypes
            
            # Define Windows API functions
            user32 = ctypes.windll.user32
            
            # Find window by class name or title
            # WeChat window titles usually contain "微信" or "WeChat"
            hwnd = None
            
            # Callback function for EnumWindows
            def enum_windows_callback(window_hwnd, _):
                nonlocal hwnd
                if user32.IsWindowVisible(window_hwnd):
                    length = user32.GetWindowTextLengthW(window_hwnd)
                    if length > 0:
                        buff = ctypes.create_unicode_buffer(length + 1)
                        user32.GetWindowTextW(window_hwnd, buff, length + 1)
                        title = buff.value
                        
                        # Check if this is a WeChat window
                        if '微信' in title or 'WeChat' in title:
                            # Skip minimized or hidden windows
                            if not user32.IsIconic(window_hwnd):
                                hwnd = window_hwnd
                                return False  # Stop enumeration
                return True  # Continue enumeration
            
            # Enumerate all windows
            EnumWindowsProc = ctypes.WINFUNCTYPE(
                wintypes.BOOL,
                wintypes.HWND,
                wintypes.LPARAM
            )
            user32.EnumWindows(EnumWindowsProc(enum_windows_callback), 0)
            
            if hwnd:
                logger.debug(f"Found WeChat window handle: {hwnd}")
                
                # Restore if minimized
                if user32.IsIconic(hwnd):
                    user32.ShowWindow(hwnd, 9)  # SW_RESTORE = 9
                    time.sleep(0.3)
                
                # Bring to foreground
                # Sometimes SetForegroundWindow fails, need to work around
                try:
                    # Get current foreground window
                    current_hwnd = user32.GetForegroundWindow()
                    
                    # Get thread IDs
                    current_thread = user32.GetWindowThreadProcessId(current_hwnd, None)
                    target_thread = user32.GetWindowThreadProcessId(hwnd, None)
                    
                    # Attach input to allow SetForegroundWindow to work
                    if current_thread != target_thread:
                        user32.AttachThreadInput(current_thread, target_thread, True)
                    
                    # Set foreground
                    user32.SetForegroundWindow(hwnd)
                    user32.BringWindowToTop(hwnd)
                    user32.ShowWindow(hwnd, 5)  # SW_SHOW = 5
                    
                    # Detach input
                    if current_thread != target_thread:
                        user32.AttachThreadInput(current_thread, target_thread, False)
                    
                    logger.info("✅ WeChat window activated and brought to foreground")
                    return True
                except Exception as e:
                    logger.warning(f"Failed to bring window to foreground: {e}")
                    # Still try ShowWindow as fallback
                    user32.ShowWindow(hwnd, 5)  # SW_SHOW = 5
                    return True
            else:
                logger.debug("No WeChat window found")
                return False
                
        except Exception as e:
            logger.error(f"Error activating WeChat window on Windows: {e}")
            logger.error(traceback.format_exc())
            return False
    
    def _center_wechat_window_windows(self) -> bool:
        """
        Center WeChat window on Windows.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            import ctypes
            from ctypes import wintypes
            
            user32 = ctypes.windll.user32
            
            # Find WeChat window
            hwnd = None
            
            def enum_windows_callback(window_hwnd, _):
                nonlocal hwnd
                if user32.IsWindowVisible(window_hwnd):
                    length = user32.GetWindowTextLengthW(window_hwnd)
                    if length > 0:
                        buff = ctypes.create_unicode_buffer(length + 1)
                        user32.GetWindowTextW(window_hwnd, buff, length + 1)
                        title = buff.value
                        
                        if '微信' in title or 'WeChat' in title:
                            if not user32.IsIconic(window_hwnd):
                                hwnd = window_hwnd
                                return False
                return True
            
            EnumWindowsProc = ctypes.WINFUNCTYPE(
                wintypes.BOOL,
                wintypes.HWND,
                wintypes.LPARAM
            )
            user32.EnumWindows(EnumWindowsProc(enum_windows_callback), 0)
            
            if hwnd:
                # Get screen size
                screen_width = user32.GetSystemMetrics(0)  # SM_CXSCREEN
                screen_height = user32.GetSystemMetrics(1)  # SM_CYSCREEN
                
                # Desired window size
                window_width = 1000
                window_height = 800
                
                # Calculate centered position
                x = (screen_width - window_width) // 2
                y = (screen_height - window_height) // 2
                
                # Move and resize window
                # SetWindowPos(hwnd, HWND_TOP, x, y, width, height, SWP_SHOWWINDOW)
                SWP_SHOWWINDOW = 0x0040
                HWND_TOP = 0
                
                result = user32.SetWindowPos(
                    hwnd, HWND_TOP,
                    x, y,
                    window_width, window_height,
                    SWP_SHOWWINDOW
                )
                
                if result:
                    logger.info(f"✅ Window centered at ({x}, {y}) with size {window_width}x{window_height}")
                    return True
                else:
                    logger.warning("SetWindowPos returned False, but window might still be positioned")
                    return True
            else:
                logger.warning("Could not find WeChat window to center")
                return False
                
        except Exception as e:
            logger.error(f"Error centering WeChat window on Windows: {e}")
            logger.error(traceback.format_exc())
            return False

    def get_system_info(self):
        """Get system information for platform-specific adjustments."""
        return {
            "os": platform.system(),
            "version": platform.version(),
            "machine": platform.machine()
        }
