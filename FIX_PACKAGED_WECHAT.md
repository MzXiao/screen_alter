# 打包后微信激活问题修复指南
# Fix Packaged WeChat Activation Issue

## 🚨 问题 Problem

打包后的应用无法激活微信窗口到前台。

## ✅ 解决步骤 Solution Steps

### 步骤 1: 重新打包 Rebuild Package

已更新的代码包含：
- ✅ 更详细的日志输出
- ✅ Windows API 调用的完整错误处理
- ✅ ctypes 和 wintypes 的显式导入

**重新打包：**

```bash
# 确保在项目根目录
cd e:\work\screen_alter

# 删除旧的打包文件
rmdir /s /q build dist

# 重新打包
pyinstaller ScreenAlter.spec
```

### 步骤 2: 运行诊断工具 Run Diagnostic Tool

在打包后的目录中运行诊断：

```bash
# 复制诊断脚本到打包目录
copy diagnose_wechat.py dist\ScreenAlter\

# 进入打包目录
cd dist\ScreenAlter

# 运行诊断
python diagnose_wechat.py
```

**或者直接在开发环境测试：**

```bash
python diagnose_wechat.py
```

### 步骤 3: 查看日志 Check Logs

诊断工具会生成 `wechat_diagnosis.log`，包含：
- ✅ ctypes 是否可用
- ✅ 所有可见窗口列表
- ✅ 微信窗口是否被找到
- ✅ 激活过程的详细步骤

**查看日志：**

```bash
type wechat_diagnosis.log
```

### 步骤 4: 运行打包的应用 Run Packaged App

```bash
cd dist\ScreenAlter
ScreenAlter.exe
```

触发关键词检测，然后查看日志：

```bash
type logs\app.log
```

## 🔍 诊断信息 Diagnostic Information

### 查找的关键日志 Key Logs to Look For:

#### ✅ 成功的日志：
```
INFO - 🔍 Searching for WeChat window...
INFO - Enumerating windows...
INFO - Found 1 WeChat window(s):
INFO -   - 微信 (hwnd: 123456, minimized: False)
INFO - ✅ Selected WeChat window handle: 123456
INFO - SetForegroundWindow result: 1
INFO - ✅✅ WeChat window successfully activated and in foreground!
```

#### ❌ 失败的日志：
```
INFO - 🔍 Searching for WeChat window...
INFO - Enumerating windows...
WARNING - ⚠️  No windows with '微信' or 'WeChat' in title found!
```

或者：

```
ERROR - ❌ Failed to import ctypes: ...
```

## 🛠️ 根据日志修复 Fix Based on Logs

### 情况 1: ctypes 导入失败

**症状：**
```
ERROR - ❌ Failed to import ctypes
```

**解决：**
- ctypes 应该是 Python 内置模块
- 检查 Python 安装是否完整
- 尝试重新安装 Python

### 情况 2: 找不到微信窗口

**症状：**
```
WARNING - ⚠️  No windows with '微信' or 'WeChat' in title found!
```

**解决：**
1. 确保微信正在运行
2. 检查微信窗口标题：
   - 打开任务管理器
   - 找到微信进程
   - 查看窗口标题是否包含 "微信" 或 "WeChat"
3. 如果标题不同，修改代码中的匹配条件

### 情况 3: SetForegroundWindow 失败

**症状：**
```
WARNING - ⚠️  Window activated but foreground is: 789 (expected: 123456)
```

**解决：**
1. 可能是 Windows 权限限制
2. 尝试以管理员身份运行
3. 查看 Windows 安全设置

### 情况 4: 窗口被找到但仍在后台

**症状：**
微信窗口被找到，API 调用成功，但窗口仍在后台

**解决：**
- 这可能是 Windows 10/11 的安全特性
- 备用方案：手动点击微信窗口激活后再触发检测

## 🔧 临时解决方案 Workaround

如果自动激活一直失败，可以：

### 方案 1: 手动保持微信在前台

1. 打开微信
2. 确保微信窗口在前台（不要最小化）
3. 运行应用进行监控
4. 触发关键词时，微信已经可见，按钮识别成功率更高

### 方案 2: 使用多显示器

1. 将微信放在第二显示器
2. 保持微信窗口可见
3. 主显示器用于其他工作
4. 应用仍然可以在主显示器找到第二显示器上的按钮

### 方案 3: 禁用窗口激活，只识别按钮

如果你确定微信一直开着，可以修改代码跳过激活步骤：

```python
# 在 src/alert/gui_alert.py 的 trigger_wechat_call() 中
# 注释掉激活和居中的代码：

# if not self.activate_wechat():
#     logger.warning("Could not activate WeChat, continuing with best effort...")

# centered = False
# for i in range(3):
#     if self.center_window():
#         centered = True
#         break
#     time.sleep(1.0)
```

## 📊 更新的 spec 文件 Updated spec File

确保 `ScreenAlter.spec` 包含：

```python
hiddenimports = [
    # ... 其他导入
    'ctypes',
    'ctypes.wintypes',
    'pyautogui',
]
```

## 🧪 完整测试流程 Complete Test Workflow

```bash
# 1. 清理旧文件
rmdir /s /q build dist

# 2. 重新打包
pyinstaller ScreenAlter.spec

# 3. 复制诊断工具
copy diagnose_wechat.py dist\ScreenAlter\

# 4. 测试诊断
cd dist\ScreenAlter
python diagnose_wechat.py

# 5. 查看诊断日志
type wechat_diagnosis.log

# 6. 如果诊断通过，运行主应用
ScreenAlter.exe

# 7. 触发关键词检测

# 8. 查看应用日志
type logs\app.log
```

## 📞 需要帮助？ Need Help?

如果问题仍然存在，请提供：

1. ✅ `wechat_diagnosis.log` 文件内容
2. ✅ `logs/app.log` 中的相关部分
3. ✅ Windows 版本信息
4. ✅ 微信版本信息
5. ✅ 是否以管理员身份运行

---

## 🎯 预期结果 Expected Result

成功后，应该看到：

```
2026-01-06 15:30:00 - alert.gui_alert - INFO - === Starting WeChat activation on Windows ===
2026-01-06 15:30:00 - alert.gui_alert - INFO - 🔍 Searching for WeChat window...
2026-01-06 15:30:00 - alert.gui_alert - INFO - Enumerating windows...
2026-01-06 15:30:00 - alert.gui_alert - INFO - Found 1 WeChat window(s):
2026-01-06 15:30:00 - alert.gui_alert - INFO -   - 微信 (hwnd: 395842, minimized: False)
2026-01-06 15:30:00 - alert.gui_alert - INFO - ✅ Selected WeChat window handle: 395842
2026-01-06 15:30:00 - alert.gui_alert - INFO - Attempting to bring window to foreground...
2026-01-06 15:30:00 - alert.gui_alert - INFO - SetForegroundWindow result: 1
2026-01-06 15:30:00 - alert.gui_alert - INFO - ✅✅ WeChat window successfully activated and in foreground!
2026-01-06 15:30:00 - alert.gui_alert - INFO - ✅ WeChat window activated successfully
```

---

**更新日期**: 2026-01-06
