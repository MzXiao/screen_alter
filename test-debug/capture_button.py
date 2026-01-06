#!/usr/bin/env python3
"""
Helper script to capture WeChat button image.
帮助脚本：截取微信按钮图片

Usage 使用方法:
  1. Open WeChat and navigate to a chat with the call button visible
     打开微信，导航到有通话按钮的聊天窗口
  2. Run this script: python capture_button.py
     运行此脚本
  3. Press SPACE to freeze screen, then drag to select the call button
     按空格键冻结屏幕，然后拖动鼠标选择通话按钮
  4. The image will be saved to resources/wechat/
     图片将保存到 resources/wechat/
"""

import sys
import time
from pathlib import Path
import tkinter as tk
from tkinter import messagebox
from PIL import ImageGrab, Image
import pyautogui

# Detect OS
import platform
IS_WINDOWS = platform.system() == 'Windows'
IS_MAC = platform.system() == 'Darwin'


class ButtonCapture:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()  # Hide main window
        
        self.canvas = None
        self.start_x = None
        self.start_y = None
        self.rect = None
        self.screenshot = None
        
    def show_instructions(self):
        """Show instructions to user."""
        msg = (
            "📸 截取微信按钮工具 / WeChat Button Capture Tool\n\n"
            "步骤 Steps:\n"
            "1️⃣ 打开微信并找到通话按钮\n"
            "   Open WeChat and find the call button\n\n"
            "2️⃣ 点击 OK，屏幕将被冻结\n"
            "   Click OK, screen will freeze\n\n"
            "3️⃣ 拖动鼠标选择按钮区域\n"
            "   Drag mouse to select button area\n\n"
            "4️⃣ 释放鼠标完成截取\n"
            "   Release mouse to capture\n\n"
            "准备好了吗？Ready?"
        )
        
        result = messagebox.askokcancel("准备截图 Ready to Capture", msg)
        if not result:
            sys.exit(0)
    
    def capture_screen(self):
        """Capture full screen."""
        print("📸 Capturing screen...")
        time.sleep(0.5)  # Give user time to see the message
        
        # Capture screenshot
        screenshot = ImageGrab.grab()
        return screenshot
    
    def on_mouse_down(self, event):
        """Handle mouse button press."""
        self.start_x = event.x
        self.start_y = event.y
        self.rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y,
            outline='red', width=3
        )
    
    def on_mouse_move(self, event):
        """Handle mouse movement."""
        if self.rect:
            self.canvas.coords(self.rect, self.start_x, self.start_y, event.x, event.y)
    
    def on_mouse_up(self, event):
        """Handle mouse button release."""
        end_x, end_y = event.x, event.y
        
        # Ensure start is top-left, end is bottom-right
        x1 = min(self.start_x, end_x)
        y1 = min(self.start_y, end_y)
        x2 = max(self.start_x, end_x)
        y2 = max(self.start_y, end_y)
        
        # Close selection window
        self.root.quit()
        
        # Crop and save
        self.save_selection(x1, y1, x2, y2)
    
    def select_region(self, screenshot):
        """Show screenshot and let user select region."""
        self.screenshot = screenshot
        
        # Create fullscreen window
        self.root.deiconify()
        self.root.attributes('-fullscreen', True)
        self.root.attributes('-topmost', True)
        
        # Create canvas with screenshot
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        self.canvas = tk.Canvas(
            self.root,
            width=screen_width,
            height=screen_height,
            cursor='cross',
            highlightthickness=0
        )
        self.canvas.pack()
        
        # Display screenshot
        # Convert PIL image to PhotoImage
        from PIL import ImageTk
        photo = ImageTk.PhotoImage(screenshot)
        self.canvas.create_image(0, 0, image=photo, anchor=tk.NW)
        self.canvas.image = photo  # Keep reference
        
        # Add instruction text
        self.canvas.create_text(
            screen_width // 2, 30,
            text="拖动鼠标选择按钮区域 Drag to select button area",
            fill='red',
            font=('Arial', 16, 'bold')
        )
        
        # Bind mouse events
        self.canvas.bind('<ButtonPress-1>', self.on_mouse_down)
        self.canvas.bind('<B1-Motion>', self.on_mouse_move)
        self.canvas.bind('<ButtonRelease-1>', self.on_mouse_up)
        
        # Bind ESC to cancel
        self.root.bind('<Escape>', lambda e: sys.exit(0))
        
        self.root.mainloop()
    
    def save_selection(self, x1, y1, x2, y2):
        """Save selected region."""
        # Crop image
        button_img = self.screenshot.crop((x1, y1, x2, y2))
        
        # Determine output path based on OS
        if IS_WINDOWS:
            filename = "call_button_win.png"
        elif IS_MAC:
            filename = "call_button_mac.png"
        else:
            filename = "call_button.png"
        
        # Save to resources directory
        resources_dir = Path(__file__).parent / "resources" / "wechat"
        resources_dir.mkdir(parents=True, exist_ok=True)
        
        output_path = resources_dir / filename
        button_img.save(output_path)
        
        print(f"\n✅ Button image saved to: {output_path}")
        print(f"   Size: {button_img.width} x {button_img.height} pixels")
        
        # Also save a backup with timestamp
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = resources_dir / f"call_button_{timestamp}.png"
        button_img.save(backup_path)
        print(f"   Backup: {backup_path}")
        
        # Show success message
        self.root.withdraw()
        messagebox.showinfo(
            "成功 Success",
            f"✅ 按钮图片已保存 Button image saved:\n\n"
            f"{output_path}\n\n"
            f"图片尺寸 Size: {button_img.width} x {button_img.height} px"
        )
        
        # Show preview
        self.show_preview(button_img)
    
    def show_preview(self, image):
        """Show preview of captured image."""
        preview = tk.Toplevel(self.root)
        preview.title("预览 Preview")
        
        from PIL import ImageTk
        
        # Scale up for better visibility (4x)
        scaled = image.resize((image.width * 4, image.height * 4), Image.NEAREST)
        photo = ImageTk.PhotoImage(scaled)
        
        label = tk.Label(preview, image=photo)
        label.image = photo
        label.pack(padx=10, pady=10)
        
        info_text = (
            f"原始尺寸 Original size: {image.width} x {image.height} px\n"
            f"显示尺寸 Display size: 4x zoom"
        )
        info_label = tk.Label(preview, text=info_text, font=('Arial', 10))
        info_label.pack(pady=5)
        
        close_btn = tk.Button(preview, text="关闭 Close", command=preview.destroy)
        close_btn.pack(pady=10)
        
        preview.mainloop()
    
    def run(self):
        """Run the capture process."""
        try:
            # Show instructions
            self.show_instructions()
            
            # Capture screen
            screenshot = self.capture_screen()
            
            # Let user select region
            self.select_region(screenshot)
            
        except Exception as e:
            messagebox.showerror("错误 Error", f"Error: {e}")
            raise


def main():
    print("=" * 60)
    print("WeChat Button Capture Tool")
    print("微信按钮截取工具")
    print("=" * 60)
    print()
    
    # Check dependencies
    try:
        import PIL
        import pyautogui
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please install: pip install pillow pyautogui")
        sys.exit(1)
    
    # Run capture
    capture = ButtonCapture()
    capture.run()
    
    print()
    print("=" * 60)
    print("✅ 完成 Done!")
    print("=" * 60)


if __name__ == "__main__":
    main()
