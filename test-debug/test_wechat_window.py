#!/usr/bin/env python3
"""
测试微信窗口激活和居中功能
Test WeChat window activation and centering
"""

import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from alert.gui_alert import GUIAlert


def main():
    print("=" * 60)
    print("测试微信窗口激活 Testing WeChat Window Activation")
    print("=" * 60)
    print()
    
    # Setup
    resource_dir = Path(__file__).parent / "resources"
    alert = GUIAlert(resource_dir)
    
    print("步骤 Step 1: 激活微信 Activate WeChat")
    print("-" * 60)
    success = alert.activate_wechat()
    if success:
        print("✅ 激活成功 Activation successful")
    else:
        print("❌ 激活失败 Activation failed")
        return
    
    print()
    time.sleep(2)
    
    print("步骤 Step 2: 居中微信窗口 Center WeChat Window")
    print("-" * 60)
    success = alert.center_window()
    if success:
        print("✅ 居中成功 Centering successful")
    else:
        print("⚠️  居中失败 Centering failed")
    
    print()
    time.sleep(2)
    
    print("步骤 Step 3: 尝试查找通话按钮 Try to find call button")
    print("-" * 60)
    print("请确保微信窗口中有通话按钮可见 Make sure call button is visible")
    print("等待 5 秒... Waiting 5 seconds...")
    time.sleep(5)
    
    success = alert.trigger_wechat_call()
    if success:
        print("✅ 找到并点击按钮 Button found and clicked")
    else:
        print("❌ 未找到按钮 Button not found")
    
    print()
    print("=" * 60)
    print("测试完成 Test complete")
    print("=" * 60)


if __name__ == "__main__":
    main()
