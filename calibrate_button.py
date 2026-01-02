import sys
import os
import platform
import time
import subprocess
import pyautogui
from pathlib import Path

# Add src to path
root_dir = Path("/Users/xiao/work/partner/screen_alter")
src_dir = root_dir / "src"
sys.path.append(str(src_dir))

def activate_wechat():
    print("Activating WeChat...")
    system = platform.system()
    try:
        if system == "Darwin":
            subprocess.run(["open", "-a", "WeChat"], check=True)
            time.sleep(1) # Wait for open
        elif system == "Windows":
             subprocess.run(["cmd", "/c", "start", "wechat"], shell=True, check=True)
        elif system == "Linux":
             subprocess.run(["wmctrl", "-a", "WeChat"], check=True)
    except Exception as e:
        print(f"Failed to activate WeChat: {e}")

def capture_screen():
    print("Capturing screen for calibration...")
    # Wait for animation
    time.sleep(2)
    
    screenshot_path = root_dir / "resources" / "calibration_screen.png"
    pyautogui.screenshot(str(screenshot_path))
    
    print(f"\n✅ Screen captured to: {screenshot_path}")
    print("\n⚠️  INSTRUCTIONS:")
    print("1. Open the image above.")
    print("2. Crop the 'Call' (phone) button icon EXACTLY.")
    print("3. Save the cropped image as: resources/wechat/call_button.png")
    print("   (Overwrite the existing file)")
    print("4. Restart the screen monitor.")

if __name__ == "__main__":
    activate_wechat()
    capture_screen()
