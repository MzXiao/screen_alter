#!/usr/bin/env python3
"""
诊断微信窗口激活问题
Diagnose WeChat Window Activation Issues

在打包后的应用中运行，查看详细的调试信息
Run in packaged app to see detailed debug information
"""

import sys
import os
import logging
from pathlib import Path

# Setup logging to both console and file
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('wechat_diagnosis.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def test_ctypes():
    """Test if ctypes is available and working."""
    logger.info("=" * 60)
    logger.info("Testing ctypes availability...")
    logger.info("=" * 60)
    
    try:
        import ctypes
        from ctypes import wintypes
        logger.info("✅ ctypes imported successfully")
        logger.info(f"   ctypes location: {ctypes.__file__}")
        
        # Test windll
        try:
            user32 = ctypes.windll.user32
            logger.info("✅ user32 loaded successfully")
            
            # Test a simple API call
            foreground = user32.GetForegroundWindow()
            logger.info(f"✅ GetForegroundWindow() returned: {foreground}")
            
            return True
        except Exception as e:
            logger.error(f"❌ Failed to load user32: {e}")
            return False
            
    except ImportError as e:
        logger.error(f"❌ Failed to import ctypes: {e}")
        return False


def list_all_windows():
    """List all visible windows."""
    logger.info("=" * 60)
    logger.info("Listing all visible windows...")
    logger.info("=" * 60)
    
    try:
        import ctypes
        from ctypes import wintypes
        
        user32 = ctypes.windll.user32
        windows = []
        
        def enum_callback(hwnd, _):
            if user32.IsWindowVisible(hwnd):
                length = user32.GetWindowTextLengthW(hwnd)
                if length > 0:
                    buff = ctypes.create_unicode_buffer(length + 1)
                    user32.GetWindowTextW(hwnd, buff, length + 1)
                    title = buff.value
                    if title:  # Skip empty titles
                        windows.append({
                            'hwnd': hwnd,
                            'title': title,
                            'minimized': bool(user32.IsIconic(hwnd))
                        })
            return True
        
        EnumWindowsProc = ctypes.WINFUNCTYPE(
            wintypes.BOOL,
            wintypes.HWND,
            wintypes.LPARAM
        )
        
        user32.EnumWindows(EnumWindowsProc(enum_callback), 0)
        
        logger.info(f"Found {len(windows)} visible windows:")
        
        # Find WeChat windows
        wechat_windows = []
        for win in windows:
            if '微信' in win['title'] or 'WeChat' in win['title']:
                wechat_windows.append(win)
                logger.info(f"  ✅ WeChat: {win['title']}")
                logger.info(f"     Handle: {win['hwnd']}, Minimized: {win['minimized']}")
        
        if not wechat_windows:
            logger.warning("⚠️  No WeChat windows found!")
            logger.info("\nAll windows (first 20):")
            for i, win in enumerate(windows[:20]):
                logger.info(f"  {i+1}. {win['title']}")
        
        return len(wechat_windows) > 0
        
    except Exception as e:
        logger.error(f"❌ Failed to list windows: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


def test_activation():
    """Test WeChat activation."""
    logger.info("=" * 60)
    logger.info("Testing WeChat activation...")
    logger.info("=" * 60)
    
    try:
        # Import our activation code
        sys.path.insert(0, str(Path(__file__).parent / "src"))
        
        from alert.gui_alert import GUIAlert
        
        resource_dir = Path(__file__).parent / "resources"
        alert = GUIAlert(resource_dir)
        
        logger.info("Attempting to activate WeChat...")
        success = alert.activate_wechat()
        
        if success:
            logger.info("✅ Activation reported success")
        else:
            logger.warning("⚠️  Activation reported failure")
        
        return success
        
    except Exception as e:
        logger.error(f"❌ Activation test failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


def check_environment():
    """Check runtime environment."""
    logger.info("=" * 60)
    logger.info("Checking runtime environment...")
    logger.info("=" * 60)
    
    logger.info(f"Python executable: {sys.executable}")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Current directory: {os.getcwd()}")
    logger.info(f"Script location: {__file__}")
    
    # Check if frozen (PyInstaller)
    if getattr(sys, 'frozen', False):
        logger.info("✅ Running in FROZEN mode (PyInstaller)")
        logger.info(f"   Bundle dir: {sys._MEIPASS}")
    else:
        logger.info("⚠️  Running in NORMAL mode (not packaged)")
    
    # Check paths
    logger.info("\nPython path:")
    for p in sys.path[:5]:
        logger.info(f"  - {p}")


def main():
    """Run all diagnostic tests."""
    print("=" * 60)
    print("微信窗口激活诊断工具")
    print("WeChat Window Activation Diagnostic Tool")
    print("=" * 60)
    print()
    print("日志将保存到: wechat_diagnosis.log")
    print("Logs will be saved to: wechat_diagnosis.log")
    print()
    
    results = {}
    
    # Test 1: Environment
    logger.info("\n\n")
    check_environment()
    
    # Test 2: ctypes
    logger.info("\n\n")
    results['ctypes'] = test_ctypes()
    
    # Test 3: List windows
    logger.info("\n\n")
    results['windows'] = list_all_windows()
    
    # Test 4: Activation
    logger.info("\n\n")
    results['activation'] = test_activation()
    
    # Summary
    logger.info("\n\n")
    logger.info("=" * 60)
    logger.info("诊断总结 DIAGNOSTIC SUMMARY")
    logger.info("=" * 60)
    
    for test, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{test:20s}: {status}")
    
    logger.info("\n详细日志已保存到: wechat_diagnosis.log")
    logger.info("Detailed logs saved to: wechat_diagnosis.log")
    
    # Keep window open
    input("\n按回车键退出... Press Enter to exit...")


if __name__ == "__main__":
    main()
