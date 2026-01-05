# Windows 微信窗口激活修复 / Windows WeChat Window Activation Fix

## 🐛 问题 Problem

### 症状 Symptoms:
- Windows 上微信窗口未被激活到前台
- 按钮识别失败，因为窗口不可见
- 日志显示 "Activating WeChat" 但窗口保持在后台

### 原因 Root Cause:
旧代码只是**启动**了微信进程，但没有：
1. ❌ 激活已存在的窗口
2. ❌ 将窗口置于前台
3. ❌ 居中窗口

```python
# 旧代码 Old Code - 只启动进程
subprocess.Popen([wechat_path])
time.sleep(1)
return True  # 但窗口可能在后台！
```

---

## ✅ 解决方案 Solution

### 新实现 New Implementation:

#### 1. **智能窗口查找和激活** - `_activate_wechat_window_windows()`

使用 Windows API 查找并激活微信窗口：

```python
# 枚举所有窗口
user32.EnumWindows(callback, 0)

# 查找标题包含 "微信" 或 "WeChat" 的窗口
if '微信' in title or 'WeChat' in title:
    # 恢复最小化窗口
    if user32.IsIconic(hwnd):
        user32.ShowWindow(hwnd, 9)  # SW_RESTORE
    
    # 线程输入附加技巧（绕过 Windows 限制）
    user32.AttachThreadInput(current_thread, target_thread, True)
    
    # 激活窗口
    user32.SetForegroundWindow(hwnd)
    user32.BringWindowToTop(hwnd)
```

#### 2. **窗口居中** - `_center_wechat_window_windows()`

使用 Windows API 居中和调整窗口大小：

```python
# 获取屏幕尺寸
screen_width = user32.GetSystemMetrics(0)
screen_height = user32.GetSystemMetrics(1)

# 计算居中位置
x = (screen_width - 1000) // 2
y = (screen_height - 800) // 2

# 移动和调整窗口
user32.SetWindowPos(hwnd, HWND_TOP, x, y, 1000, 800, SWP_SHOWWINDOW)
```

#### 3. **改进的激活流程**

```
1. 首先尝试激活已存在的窗口
   ├─ 查找微信窗口
   ├─ 恢复最小化状态
   └─ 置于前台

2. 如果没有窗口，启动微信
   ├─ 启动进程
   ├─ 等待窗口出现
   └─ 激活新窗口

3. 居中窗口
   ├─ 查找窗口句柄
   ├─ 计算居中位置
   └─ 调整大小和位置
```

---

## 🔧 技术细节 Technical Details

### Windows API 使用 Windows API Usage:

| API Function | 用途 Purpose |
|-------------|-------------|
| `EnumWindows` | 枚举所有窗口 |
| `GetWindowTextW` | 获取窗口标题 |
| `IsWindowVisible` | 检查窗口是否可见 |
| `IsIconic` | 检查窗口是否最小化 |
| `ShowWindow` | 显示/恢复窗口 |
| `GetForegroundWindow` | 获取前台窗口 |
| `SetForegroundWindow` | 设置前台窗口 |
| `BringWindowToTop` | 将窗口置顶 |
| `AttachThreadInput` | 附加线程输入（绕过限制）|
| `SetWindowPos` | 设置窗口位置和大小 |
| `GetSystemMetrics` | 获取系统指标（屏幕尺寸）|

### 为什么需要 AttachThreadInput?

Windows 有安全限制：进程不能随意将其他进程的窗口置于前台。`AttachThreadInput` 是一个合法的绕过方法：

```python
# 获取线程 ID
current_thread = user32.GetWindowThreadProcessId(current_hwnd, None)
target_thread = user32.GetWindowThreadProcessId(hwnd, None)

# 临时附加输入
user32.AttachThreadInput(current_thread, target_thread, True)

# 现在可以设置前台了
user32.SetForegroundWindow(hwnd)

# 分离输入
user32.AttachThreadInput(current_thread, target_thread, False)
```

---

## 📊 对比 Comparison

### 之前 Before:

```
用户运行应用 → 检测到关键词
           ↓
启动微信进程 → 微信在后台运行
           ↓
尝试查找按钮 → ❌ 失败（窗口不可见）
           ↓
报错: Button not found
```

### 现在 Now:

```
用户运行应用 → 检测到关键词
           ↓
查找微信窗口 → 找到 → 激活并置于前台
           ↓          ↓
        未找到    居中窗口
           ↓          ↓
        启动微信 → 等待并激活
           ↓
查找按钮 → ✅ 成功！
```

---

## 🧪 测试 Testing

### 测试脚本 Test Script:

```bash
python test_wechat_window.py
```

### 测试场景 Test Scenarios:

1. **微信已运行且可见**
   - ✅ 应该立即激活并居中

2. **微信已运行但最小化**
   - ✅ 应该恢复并激活

3. **微信未运行**
   - ✅ 应该启动、等待、激活

4. **微信在后台**
   - ✅ 应该置于前台

### 预期日志 Expected Logs:

**成功场景:**
```
INFO - Activating WeChat on Windows...
DEBUG - Found WeChat window handle: 123456
INFO - ✅ WeChat window activated and brought to foreground
INFO - Centering WeChat window on Windows...
INFO - ✅ Window centered at (460, 140) with size 1000x800
```

**启动新实例场景:**
```
INFO - Activating WeChat on Windows...
DEBUG - No WeChat window found
INFO - No active WeChat window found, attempting to start WeChat...
INFO - Using configured WeChat path: D:\software\Weixin\Weixin.exe
INFO - Waiting for WeChat window to appear...
INFO - WeChat window activated after startup
INFO - Centering WeChat window on Windows...
INFO - ✅ Window centered at (460, 140) with size 1000x800
```

---

## 🔍 故障排查 Troubleshooting

### 问题1: 窗口仍然不激活

**可能原因:**
- Windows 安全策略限制
- 需要管理员权限
- 其他应用锁定前台

**解决方法:**
```python
# 检查日志中的错误信息
tail -f logs/app.log

# 手动激活测试
python test_wechat_window.py
```

### 问题2: 找不到窗口

**可能原因:**
- 微信窗口标题不包含 "微信" 或 "WeChat"
- 窗口被隐藏或在另一个桌面

**解决方法:**
- 检查微信窗口标题
- 确保微信在当前桌面运行
- 查看 DEBUG 日志中的窗口枚举信息

### 问题3: 无法居中

**可能原因:**
- 窗口不可调整大小
- 多显示器设置

**解决方法:**
- 窗口仍会被激活（主要功能）
- 手动调整窗口位置
- 检查多显示器配置

---

## 📝 代码变更 Code Changes

### 新增文件 New Files:
- `test_wechat_window.py` - 测试脚本

### 修改文件 Modified Files:
- `src/alert/gui_alert.py`
  - ✅ 新增 `_activate_wechat_window_windows()` 方法
  - ✅ 新增 `_center_wechat_window_windows()` 方法
  - ✅ 改进 `activate_wechat()` 中的 Windows 逻辑
  - ✅ 改进 `center_window()` 中的 Windows 逻辑

### 新增文档 New Documentation:
- `docs/WINDOWS_WINDOW_FIX.md` - 本文档

---

## 🎯 下一步 Next Steps

1. **测试修复**
   ```bash
   python test_wechat_window.py
   ```

2. **运行主应用**
   ```bash
   python src/main.py
   ```

3. **验证日志**
   - 检查 `logs/app.log`
   - 确认看到 "✅ WeChat window activated"
   - 确认看到 "✅ Window centered"

4. **测试按钮识别**
   - 触发关键词检测
   - 确认微信窗口出现在前台
   - 确认按钮被正确识别和点击

---

## 📚 参考资料 References

- [Windows API Documentation](https://docs.microsoft.com/en-us/windows/win32/api/)
- [SetForegroundWindow](https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-setforegroundwindow)
- [Python ctypes](https://docs.python.org/3/library/ctypes.html)

---

**更新日期 Last Updated**: 2026-01-06

**版本 Version**: 1.0
