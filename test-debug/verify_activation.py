import sys
import os
import platform
from pathlib import Path

# Add src to path
root_dir = Path("/")
src_dir = root_dir / "src"
sys.path.append(str(src_dir))

# Mock logger to avoid issues if not fully set up
import logging
logging.basicConfig(level=logging.INFO)

from alert.gui_alert import GUIAlert

def verify():
    resource_dir = root_dir / "resources"
    alert = GUIAlert(resource_dir)
    
    print(f"Current System: {platform.system()}")
    print("Attempting to activate WeChat...")
    
    # We test activate_wechat specifically
    success = alert.activate_wechat()
    
    if success:
        print("✅ WeChat activation command sent successfully.")
    else:
        print("❌ WeChat activation failed.")

if __name__ == "__main__":
    verify()
