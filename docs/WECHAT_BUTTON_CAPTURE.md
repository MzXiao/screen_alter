# 微信按钮截取指南 / WeChat Button Capture Guide

## 问题 Problem

应用无法识别微信通话按钮，错误信息：
```
ImageNotFoundException: Could not locate the image (highest confidence = 0.365)
```

## 原因 Cause

不同操作系统、微信版本、显示缩放比例下，按钮外观可能不同。

## 解决方案 Solution

### 方法1：使用截图工具 Method 1: Use Capture Tool (推荐 Recommended)

1. **打开微信，找到通话按钮**
   - 打开任意聊天窗口
   - 确保通话按钮可见（视频通话或语音通话按钮）

2. **运行截图工具**
   ```bash
   python capture_button.py
   ```

3. **按照提示操作**
   - 点击 OK 开始
   - 屏幕会冻结
   - 拖动鼠标选择按钮区域
   - 释放鼠标完成截取

4. **文件自动保存到**
   - Windows: `resources/wechat/call_button_win.png`
   - Mac: `resources/wechat/call_button_mac.png`

5. **重新运行应用测试**

### 方法2：手动截图 Method 2: Manual Screenshot

1. **打开微信并定位按钮**
   - 找到通话按钮（视频/语音通话图标）

2. **使用截图工具截取按钮**
   - Windows: Win + Shift + S (Snipping Tool)
   - Mac: Cmd + Shift + 4

3. **裁剪到合适大小**
   - 只包含按钮图标
   - 建议尺寸：30x30 到 100x100 像素
   - 避免包含过多背景

4. **保存图片**
   ```
   resources/wechat/call_button_win.png  (Windows)
   resources/wechat/call_button_mac.png  (Mac)
   resources/wechat/call_button.png      (通用 Generic)
   ```

5. **可以保存多个版本**
   - `call_button.png` - 默认版本
   - `call_button_win.png` - Windows 专用
   - `call_button_mac.png` - Mac 专用
   - `call_button_alt.png` - 备用版本
   
   应用会依次尝试所有图片！

## 应用行为 Application Behavior

### 多图片支持 Multiple Images Support

应用现在支持多个按钮图片：
- 自动检测可用的图片文件
- 按顺序尝试所有图片
- 使用多个置信度级别：0.8 → 0.7 → 0.6
- 第一个匹配成功的图片将被使用

### 日志输出 Log Output

```
✅ Found button using call_button_win.png (confidence: 0.7)
   Location: Box(left=100, top=200, width=50, height=50)
   Clicking at center: Point(x=125, y=225)
```

或者失败时：
```
❌ Button not found. Best match: 0.453 (required: 0.6+)

💡 Tips:
  1. Make sure WeChat window is visible
  2. Navigate to a chat with call button visible
  3. Capture button screenshot and save as:
     • resources/wechat/call_button_win.png (Windows)
     • resources/wechat/call_button_mac.png (Mac)
  4. Try different display scaling (100% recommended)
```

## 最佳实践 Best Practices

### 1. 图片质量 Image Quality
- ✅ 清晰、高对比度
- ✅ 准确裁剪，只包含按钮
- ✅ 原始分辨率（不要缩放）
- ❌ 模糊、压缩过度
- ❌ 包含太多背景

### 2. 显示设置 Display Settings
- 推荐显示缩放：100%
- 如果使用 125%/150% 缩放，需要重新截取对应的按钮

### 3. 微信窗口 WeChat Window
- 确保窗口可见（不要最小化）
- 确保按钮在屏幕上显示
- 应用会自动尝试激活和居中窗口

### 4. 多版本支持 Multiple Versions
- 为不同场景准备多个图片
- 不同微信版本的按钮可能不同
- 深色/浅色主题的按钮可能不同

## 故障排查 Troubleshooting

### 问题1：置信度太低 Low Confidence
**症状**: `Best match: 0.365 (required: 0.6+)`

**解决**:
1. 重新截取按钮图片
2. 确保图片清晰且准确
3. 检查显示缩放设置
4. 尝试在不同场景下截取（深色/浅色背景）

### 问题2：找不到微信窗口 WeChat Window Not Found
**症状**: `Could not activate WeChat`

**解决**:
1. 确保微信正在运行
2. 检查配置文件中的微信路径
3. 手动打开微信窗口

### 问题3：按钮位置不对 Wrong Button Location
**症状**: 点击了错误的位置

**解决**:
1. 重新截取更精确的按钮区域
2. 确保只截取按钮本身，不包含周围元素
3. 尝试调整置信度阈值

## 技术细节 Technical Details

### 图像识别流程 Image Recognition Flow
```
1. 加载所有可用的按钮图片
   Load all available button images

2. 激活并居中微信窗口
   Activate and center WeChat window

3. 对每个置信度级别 (0.8, 0.7, 0.6):
   For each confidence level:
   
   a. 尝试每个按钮图片
      Try each button image
      
   b. 在屏幕上搜索匹配
      Search for match on screen
      
   c. 如果找到，点击并返回成功
      If found, click and return success
      
4. 如果都失败，记录最佳匹配度并提示用户
   If all fail, log best confidence and show tips
```

### 支持的图片格式 Supported Image Formats
- PNG (推荐 Recommended)
- JPG/JPEG
- BMP

### 图片命名约定 Image Naming Convention
```
resources/wechat/
├── call_button.png          # 默认 Default (required)
├── call_button_win.png      # Windows 专用 Windows-specific
├── call_button_mac.png      # Mac 专用 Mac-specific
└── call_button_alt.png      # 备用 Alternative
```

## 示例 Examples

### 好的按钮图片 Good Button Image ✅
```
尺寸 Size: 40x40 px
清晰度 Clarity: 高清 High
背景 Background: 最小 Minimal
对比度 Contrast: 高 High
```

### 不好的按钮图片 Bad Button Image ❌
```
尺寸 Size: 200x200 px (too large)
清晰度 Clarity: 模糊 Blurry
背景 Background: 包含其他元素 Includes other elements
对比度 Contrast: 低 Low
```

## 参考 References

- PyAutoGUI 文档: https://pyautogui.readthedocs.io/
- 图像识别最佳实践: 使用清晰、高对比度的小图片
- 置信度阈值: 0.6-0.8 之间通常效果最好

## 联系支持 Support

如果问题仍然存在，请提供：
1. 日志文件 `logs/app.log`
2. 截取的按钮图片
3. 微信版本和操作系统信息
4. 显示缩放设置

---

**更新日期 Last Updated**: 2026-01-06
