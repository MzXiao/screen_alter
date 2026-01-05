# 微信按钮识别失败快速修复 / WeChat Button Recognition Quick Fix

## 🚨 问题 Problem
```
ImageNotFoundException: Could not locate the image (highest confidence = 0.365)
```

## ✅ 解决方案 Solution

### 快速步骤 Quick Steps (5分钟)

1. **运行截图工具**
   ```bash
   python capture_button.py
   ```

2. **按提示操作**
   - 点击 OK
   - 拖动选择微信通话按钮
   - 释放鼠标完成

3. **完成！重新运行应用**

---

## 📝 手动方法 Manual Method

### Windows:
1. 打开微信，找到通话按钮
2. 按 `Win + Shift + S` 截图
3. 只选择按钮图标（不要包含太多背景）
4. 保存为：`resources/wechat/call_button_win.png`

### Mac:
1. 打开微信，找到通话按钮
2. 按 `Cmd + Shift + 4` 截图
3. 只选择按钮图标
4. 保存为：`resources/wechat/call_button_mac.png`

---

## 💡 提示 Tips

### ✅ 好的按钮图片
- 清晰、高对比度
- 只包含按钮本身
- 30x30 到 60x60 像素
- PNG 格式

### ❌ 避免
- 模糊的图片
- 包含大量背景
- 过大或过小
- 压缩过度的 JPG

---

## 📂 支持的文件名 Supported Filenames

应用会按顺序尝试这些文件：
```
resources/wechat/
├── call_button.png          # 1. 默认版本
├── call_button_win.png      # 2. Windows 版本
├── call_button_mac.png      # 3. Mac 版本
└── call_button_alt.png      # 4. 备用版本
```

**可以添加多个！应用会自动尝试所有图片。**

---

## 🔧 显示设置 Display Settings

- **推荐显示缩放**: 100%
- 如果使用 125%/150% 缩放，需要重新截取

---

## 📖 详细文档 Full Documentation

查看完整指南：`docs/WECHAT_BUTTON_CAPTURE.md`

---

## ❓ 仍然有问题？ Still Having Issues?

检查日志：`logs/app.log`

查看错误信息中的 "Best match confidence"：
- < 0.3: 图片差异很大，需要重新截取
- 0.3-0.5: 图片相似但不够，可能需要调整截取区域
- > 0.5: 很接近了！尝试稍微调整图片或降低对比度要求

---

**更新**: 2026-01-06
