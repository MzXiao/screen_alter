# 截屏尺寸配置说明
# Screenshot Size Configuration Guide

## 🚨 问题 Problem

**旧版本问题：**
- ❌ 配置为全屏（`capture_region: null`），但实际截屏只有 500x500
- ❌ 无法捕获完整屏幕内容

## ✅ 已修复 Fixed

### 修复内容 What's Fixed:

1. **全屏捕获恢复正常**
   - `capture_region: null` → 捕获**完整屏幕**
   - 不再截取中心 500x500 区域

2. **添加截屏尺寸配置**（保留给未来功能）
   - 配置项：`screenshot_size`
   - 默认值：500
   - 用途：未来可能用于特定场景

---

## 📋 配置说明 Configuration

### config.json:

```json
{
  "capture_region": null,
  "screenshot_size": 500
}
```

### 配置选项 Options:

| 配置项 Config | 说明 Description | 默认值 Default | 示例 Example |
|-------------|----------------|--------------|--------------|
| `capture_region` | 截屏区域 | `null` (全屏) | `[100, 100, 800, 600]` |
| `screenshot_size` | 截屏尺寸（保留） | 500 | 800 |

---

## 🎯 使用场景 Use Cases

### 场景 1: 全屏监控 ⭐ 推荐

**配置：**
```json
{
  "capture_region": null
}
```

**效果：**
- ✅ 捕获整个主显示器
- ✅ 分辨率：1920x1080 / 2560x1440 等（根据实际屏幕）
- ✅ 适合：监控整个屏幕的内容变化

**优点：**
- 不会遗漏任何内容
- 适合不确定目标位置的情况

**缺点：**
- 截图文件较大
- OCR 处理较慢

---

### 场景 2: 自定义区域

**配置：**
```json
{
  "capture_region": [100, 100, 800, 600]
}
```

**格式：** `[left, top, width, height]`
- `left`: 区域左上角 X 坐标
- `top`: 区域左上角 Y 坐标
- `width`: 区域宽度
- `height`: 区域高度

**效果：**
- ✅ 只捕获指定区域
- ✅ 文件更小
- ✅ 处理更快

**如何设置：**
1. 在应用中点击 "选择监控区域"
2. 拖动鼠标选择区域
3. 自动保存到配置

---

## 🔍 验证截屏尺寸 Verify Screenshot Size

### 方法 1: 查看日志

```bash
type logs\app.log | findstr "Screenshot captured"
```

应该看到：
```
INFO - Screenshot captured: (1920, 1080) (region: full screen)
```

或自定义区域：
```
INFO - Screenshot captured: (800, 600) (region: custom)
```

### 方法 2: 查看截图文件

```bash
dir screenshots
```

然后用图片查看器打开最新的截图，查看尺寸。

---

## 📊 对比 Comparison

### 修复前 Before Fix:

```
配置: capture_region: null
↓
实际截屏: 500x500 (中心区域)
↓
问题: 只能看到屏幕中心，丢失边缘内容
```

### 修复后 After Fix:

```
配置: capture_region: null
↓
实际截屏: 1920x1080 (全屏，根据实际分辨率)
↓
效果: 捕获完整屏幕内容
```

---

## ⚙️ 性能优化建议 Performance Tips

### 如果 OCR 处理太慢：

**方案 1: 使用自定义区域**
```json
{
  "capture_region": [0, 0, 1280, 720]
}
```
缩小监控区域可以：
- ✅ 减少截图大小
- ✅ 加快 OCR 处理速度
- ✅ 降低 CPU 使用

**方案 2: 增加监控间隔**
```json
{
  "monitor_interval": 120
}
```
从 60 秒改为 120 秒（2 分钟）

**方案 3: 使用 PaddleOCR 服务**
- 比 Tesseract 更快
- 识别更准确
- 需要单独启动服务

---

## 🐛 故障排查 Troubleshooting

### 问题 1: 截图仍然是 500x500

**原因：** 可能还在使用旧版本代码

**解决：**
```bash
# 1. 拉取最新代码
git pull

# 2. 重新打包
pyinstaller ScreenAlter.spec

# 3. 运行新版本
cd dist\ScreenAlter
ScreenAlter.exe
```

### 问题 2: 截图太大，占用空间

**解决方案：**

**方法 1: 限制保存数量**
```json
{
  "screenshot_limit": 50
}
```
只保留最近 50 张截图

**方法 2: 缩短保留时间**
```json
{
  "screenshot_retention_days": 3
}
```
只保留 3 天内的截图

**方法 3: 使用自定义区域**
只监控需要的区域，不要全屏

---

## 📝 代码变更 Code Changes

### screen_capture.py:

**旧代码：**
```python
else:
    # 问题：总是捕获中心 500x500
    monitor = self._get_center_region(sct.monitors[1], size=500)
```

**新代码：**
```python
else:
    # 修复：捕获完整主显示器
    monitor = sct.monitors[1]
```

### 影响 Impact:

- ✅ `capture_region: null` → 完整屏幕
- ✅ `capture_region: [x, y, w, h]` → 自定义区域
- ✅ 日志显示实际截图尺寸

---

## 🎉 总结 Summary

**已修复：**
- ✅ 全屏配置现在真正捕获全屏
- ✅ 不再限制为 500x500
- ✅ 添加详细日志显示实际尺寸

**使用建议：**
- 📌 默认使用全屏（`capture_region: null`）
- 📌 如果性能不够，再使用自定义区域
- 📌 查看日志确认实际截图尺寸

**下一步：**
- 重新打包应用
- 测试全屏捕获
- 查看日志验证尺寸

---

**更新日期**: 2026-01-06  
**版本**: 1.0
