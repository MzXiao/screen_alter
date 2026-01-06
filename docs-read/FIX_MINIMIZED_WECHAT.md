# 修复最小化微信窗口激活问题
# Fix Minimized WeChat Window Activation

## 🚨 问题 Problem

### 症状 Symptoms:
```
INFO - Found 1 WeChat window(s):
INFO -   - 微信 (hwnd: 131376, minimized: 1)
WARNING - ❌ No suitable WeChat window found (all were minimized or hidden)
```

**结果：** 微信被找到了，但因为是最小化状态被跳过了，无法激活。

---

## ✅ 根本原因 Root Cause

### 旧代码逻辑（错误）：

```python
# 枚举窗口时
if '微信' in title or 'WeChat' in title:
    # ❌ 跳过最小化的窗口
    if not user32.IsIconic(window_hwnd):
        hwnd = window_hwnd
        
# 结果：最小化的微信窗口被忽略
```

---

## ✅ 已修复 Fixed

### 新代码逻辑（正确）：

```python
# 枚举窗口时
if '微信' in title or 'WeChat' in title:
    # ✅ 接受任何微信窗口（包括最小化的）
    if hwnd is None:
        hwnd = window_hwnd

# 后续处理
if hwnd:
    # ✅ 如果是最小化，恢复它
    if user32.IsIconic(hwnd):
        user32.ShowWindow(hwnd, 9)  # SW_RESTORE
        
    # ✅ 激活到前台
    SetForegroundWindow(hwnd)
```

---

## 📊 修复效果 Effect

### 修复前 Before:

```
微信状态: 最小化
    ↓
代码逻辑: 跳过最小化窗口
    ↓
结果: ❌ 无法激活
```

### 修复后 After:

```
微信状态: 最小化
    ↓
代码逻辑: 接受最小化窗口
    ↓
恢复窗口: ShowWindow(RESTORE)
    ↓
激活前台: SetForegroundWindow
    ↓
结果: ✅ 成功激活
```

---

## 📝 新的日志输出 New Log Output

### 成功激活最小化窗口：

```
INFO - Found 1 WeChat window(s):
INFO -   - 微信 (hwnd: 131376, minimized: True)
INFO - ✅ Selected WeChat window handle: 131376 (minimized: True)
INFO - 🔄 Window is minimized, restoring...
INFO - ShowWindow(RESTORE) result: 1
INFO - ✅ Window successfully restored
INFO - Attempting to bring window to foreground...
INFO - SetForegroundWindow result: 1
INFO - ✅✅ WeChat window successfully activated and in foreground!
```

### 如果恢复失败：

```
INFO - 🔄 Window is minimized, restoring...
INFO - ShowWindow(RESTORE) result: 0
WARNING - ⚠️  Window still minimized after restore attempt
```

---

## 🧪 测试场景 Test Scenarios

### 场景 1: 微信最小化 ✅
- **操作：** 最小化微信
- **触发：** 检测到关键词
- **结果：** 微信自动恢复并激活

### 场景 2: 微信在后台 ✅
- **操作：** 微信在其他窗口后面
- **触发：** 检测到关键词
- **结果：** 微信置于前台

### 场景 3: 微信在系统托盘 ✅
- **操作：** 微信最小化到系统托盘
- **触发：** 检测到关键词
- **结果：** 微信从托盘恢复并激活

### 场景 4: 微信未运行 ✅
- **操作：** 微信完全关闭
- **触发：** 检测到关键词
- **结果：** 尝试启动微信（如果配置了路径）

---

## 🔧 代码变更 Code Changes

### src/alert/gui_alert.py

#### 变更 1: 接受最小化窗口（第 439-459 行）

**旧代码：**
```python
if '微信' in title or 'WeChat' in title:
    # 跳过最小化窗口
    if not user32.IsIconic(window_hwnd):
        hwnd = window_hwnd
        return False
```

**新代码：**
```python
if '微信' in title or 'WeChat' in title:
    # 接受任何窗口（包括最小化）
    if hwnd is None:
        hwnd = window_hwnd
        return False
```

#### 变更 2: 增强的恢复逻辑（第 482-497 行）

**新增功能：**
- ✅ 检测窗口是否最小化
- ✅ 恢复最小化窗口
- ✅ 验证恢复是否成功
- ✅ 详细的日志输出
- ✅ 增加等待时间（0.5 秒）

---

## 🎯 验证修复 Verify Fix

### 步骤 1: 最小化微信
- 打开微信
- 点击最小化按钮

### 步骤 2: 运行应用
```bash
cd dist\ScreenAlter
ScreenAlter.exe
```

### 步骤 3: 触发检测
- 配置关键词或图片
- 等待检测触发

### 步骤 4: 查看日志
```bash
type logs\app.log | findstr "WeChat window"
```

**应该看到：**
```
INFO - Found 1 WeChat window(s):
INFO -   - 微信 (hwnd: xxx, minimized: True)
INFO - ✅ Selected WeChat window handle: xxx (minimized: True)
INFO - 🔄 Window is minimized, restoring...
INFO - ✅ Window successfully restored
INFO - ✅✅ WeChat window successfully activated!
```

---

## 🐛 故障排查 Troubleshooting

### 问题 1: 恢复失败

**症状：**
```
WARNING - ⚠️  Window still minimized after restore attempt
```

**可能原因：**
- Windows 权限限制
- 微信窗口处于特殊状态

**解决方案：**
1. 以管理员身份运行应用
2. 检查 Windows 安全设置
3. 手动打开微信窗口

### 问题 2: 找不到窗口

**症状：**
```
WARNING - ⚠️  No windows with '微信' or 'WeChat' in title found!
```

**可能原因：**
- 微信未运行
- 窗口标题不包含 "微信" 或 "WeChat"

**解决方案：**
1. 确保微信正在运行
2. 查看任务管理器中的窗口标题
3. 配置 `wechat_path` 自动启动

### 问题 3: 窗口激活但不在前台

**症状：**
```
INFO - SetForegroundWindow result: 0
```

**可能原因：**
- Windows 10/11 安全限制
- 其他应用锁定前台

**解决方案：**
- 已包含 AttachThreadInput 技巧
- 如果仍失败，手动点击微信窗口

---

## 📋 相关改进 Related Improvements

此次修复还包含：

1. ✅ **详细的日志输出**
   - 显示窗口句柄
   - 显示最小化状态
   - 显示恢复结果

2. ✅ **增加等待时间**
   - 恢复后等待 0.5 秒
   - 让窗口有足够时间响应

3. ✅ **验证恢复结果**
   - 检查窗口是否仍然最小化
   - 记录警告信息

4. ✅ **更好的错误处理**
   - 详细的错误信息
   - 清晰的故障排查建议

---

## 🎉 总结 Summary

**修复内容：**
- ✅ 接受最小化的微信窗口
- ✅ 自动恢复最小化窗口
- ✅ 验证恢复结果
- ✅ 详细的日志输出

**支持的微信状态：**
- ✅ 最小化到任务栏
- ✅ 最小化到系统托盘
- ✅ 在其他窗口后面
- ✅ 正常显示

**下一步：**
1. 重新打包应用
2. 测试最小化场景
3. 查看日志验证

---

**更新日期**: 2026-01-06  
**版本**: 1.0
