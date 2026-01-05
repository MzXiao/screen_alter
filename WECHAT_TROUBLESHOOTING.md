# 微信功能故障排查

## 🐛 常见问题

### 问题 1：windows 找不到文件 wechat

**错误信息**：
```
subprocess.CalledProcessError: Command '['cmd', '/c', 'start', 'wechat']' returned non-zero exit status 1
```

或者日志中显示：
```
Could not activate WeChat via start command
```

#### 原因

Windows 没有 `wechat` 这个命令，需要使用完整的微信程序路径。

#### 解决方案

**✅ 已修复**：最新版本会自动尝试以下方法（按顺序）：

1. **配置文件优先**：从 `config/config.json` 读取 `wechat_path`
2. **常见路径查找**：自动扫描以下位置
   - `C:\Program Files\Tencent\WeChat\WeChat.exe`
   - `C:\Program Files (x86)\Tencent\WeChat\WeChat.exe`
   - `%LocalAppData%\Tencent\WeChat\WeChat.exe`
   - `%AppData%\Tencent\WeChat\WeChat.exe`

**简洁高效**：只使用最常用的两种方法，快速准确。

**🔧 快速修复工具**（推荐）：

```bash
python find_wechat.py
```

这个工具会：
- ✅ 自动查找所有可能的微信安装位置
- ✅ 显示找到的所有路径
- ✅ 让你选择要使用的路径
- ✅ 自动保存到配置文件

**预期输出**：
```
============================================================
微信路径查找工具
============================================================

[1] 从配置文件查找...
  ⚠️ 配置文件中未设置微信路径

[2] 从常见安装路径查找...
  ✅ 找到: C:\Program Files\Tencent\WeChat\WeChat.exe

============================================================
查找结果
============================================================

找到 1 个微信安装：
  [1] C:\Program Files\Tencent\WeChat\WeChat.exe

使用找到的路径: C:\Program Files\Tencent\WeChat\WeChat.exe

✅ 配置已保存到: config/config.json
✅ 完成！现在可以在应用中使用微信功能了
```

#### 手动配置

如果自动查找工具无法找到微信，可以手动配置：

**方法 1：查找微信位置**

```cmd
# 在开始菜单搜索
Win+S → 搜索 "微信" → 右键 → 打开文件位置 → 记下路径
```

**方法 2：手动编辑配置文件**

编辑 `config/config.json`，添加或修改：

```json
{
  "wechat_enabled": true,
  "wechat_path": "C:\\Program Files\\Tencent\\WeChat\\WeChat.exe"
}
```

**注意**：
- 路径中的反斜杠 `\` 需要写成 `\\`
- 或者使用正斜杠 `/`：`"C:/Program Files/Tencent/WeChat/WeChat.exe"`

**方法 3：禁用微信功能**

如果不需要微信功能，编辑 `config/config.json`：

```json
{
  "wechat_enabled": false
}
```

这样程序不会尝试启动微信。

---

### 问题 2：找不到 wechat 资源文件

**错误日志**：
```
WeChat call button image not found: E:\work\screen_alter\resources\wechat\call_button.png
```

#### 原因

打包后资源文件路径错误，或资源文件缺失。

#### 解决方案

**方法 1：验证资源文件**

开发环境：
```bash
# 检查文件是否存在
dir resources\wechat\call_button.png
```

打包后：
```bash
# 检查打包后的资源
dir dist\ScreenAlter\resources\wechat\call_button.png
```

**方法 2：重新打包**

```bash
# 清理旧构建
rmdir /s /q build dist

# 重新打包
scripts\build_windows.bat

# 验证资源已包含
dir dist\ScreenAlter\resources\wechat\
```

**方法 3：手动复制资源**

如果打包后缺失资源：
```bash
# 复制资源到打包目录
mkdir dist\ScreenAlter\resources\wechat
copy resources\wechat\call_button.png dist\ScreenAlter\resources\wechat\
```

---

### 问题 3：微信窗口找不到按钮

**日志**：
```
WeChat call button not found on screen.
```

#### 原因

1. 微信窗口未打开
2. 微信界面与参考图片不匹配
3. 屏幕缩放导致图像识别失败

#### 解决方案

**方法 1：确保微信已登录**

1. 手动打开微信并登录
2. 切换到要发送消息的聊天窗口
3. 再运行监控功能

**方法 2：更新参考图片**

1. 截取当前微信的呼叫按钮图片
2. 替换 `resources/wechat/call_button.png`
3. 确保图片清晰，尺寸适中（建议 50x50 左右）

**方法 3：调整屏幕缩放**

Windows 显示设置：
- 右键桌面 → 显示设置
- 缩放与布局 → 改为 100%
- 重启应用

**方法 4：降低识别精度**

编辑 `src/alert/gui_alert.py`：
```python
location = pyautogui.locateOnScreen(str(self.call_button_img), confidence=0.7)  # 从 0.8 降到 0.7
```

---

### 问题 4：微信功能不工作（总体）

**症状**：
- 监控检测到关键词
- 但微信没有发送消息

#### 检查清单

1. **微信是否已安装？**
   ```cmd
   # 查找微信进程
   tasklist | findstr WeChat
   ```

2. **微信是否已登录？**
   - 打开微信
   - 确保已扫码登录

3. **是否有目标联系人？**
   - 打开要发送消息的聊天窗口
   - 确保联系人名称正确

4. **资源文件是否存在？**
   ```bash
   dir resources\wechat\call_button.png
   ```

5. **日志中的错误信息？**
   - 查看 `logs/app.log`
   - 搜索 "WeChat" 或 "wechat"

---

## 🔧 调试微信功能

### 启用详细日志

微信相关的日志会自动记录到 `logs/app.log`，查找：

```bash
# 搜索微信相关日志
findstr /i "wechat" logs\app.log
```

### 测试微信激活

创建测试脚本 `test_wechat.py`：

```python
"""测试微信功能"""
import sys
from pathlib import Path
from alert.gui_alert import GUIAlert

# 添加 src 到路径
sys.path.insert(0, str(Path(__file__).parent / 'src'))

# 测试
resource_dir = Path(__file__).parent / "resources"
alert = GUIAlert(resource_dir)

print("尝试激活微信...")
result = alert.activate_wechat()
print(f"结果: {'成功' if result else '失败'}")

print("\n尝试查找呼叫按钮...")
result = alert.trigger_wechat_call()
print(f"结果: {'成功' if result else '失败'}")
```

运行：
```bash
python test_wechat.py
```

---

## ⚙️ 配置选项

### 禁用微信功能

如果不需要微信报警，可以在主应用中：
- 不配置微信接收人
- 或在代码中跳过微信调用

### 使用其他报警方式

考虑以下替代方案：
- ✅ GUI 弹窗（已内置）
- ✅ 邮件通知
- ✅ 钉钉/企业微信 Webhook
- ✅ 自定义 HTTP 回调

---

## 📝 微信自动化限制

### 注意事项

1. **官方限制**：
   - 微信不鼓励自动化操作
   - 频繁使用可能被限制
   - 建议仅用于测试或个人使用

2. **技术限制**：
   - 需要微信窗口可见
   - 依赖图像识别（不够稳定）
   - 受屏幕缩放影响

3. **替代方案**：
   - **企业微信**：提供官方 API
   - **个人微信 Bot**：使用 itchat 等库（有风险）
   - **Server酱**：微信推送服务

---

## 🆘 仍然无法解决？

### 收集信息

1. **日志文件**：
   ```bash
   type logs\app.log | findstr /i "wechat"
   ```

2. **微信版本**：
   - 打开微信 → 设置 → 关于微信
   - 记录版本号

3. **安装路径**：
   ```cmd
   where WeChat.exe
   # 或手动查找
   ```

4. **错误截图**：
   - 捕获错误对话框
   - 包含日志输出

### 获取帮助

提交 Issue 时包含：
- 操作系统版本
- 微信版本
- 完整错误日志
- 已尝试的解决方案

---

## 📚 相关文档

- [主文档](README.md)
- [故障排查总览](TROUBLESHOOTING.md)
- [微信使用指南](WECHAT_GUIDE.md)

---

## 💡 最佳实践

1. **仅用于个人测试**
2. **不要频繁调用**
3. **保持微信窗口可见**
4. **定期更新参考图片**
5. **考虑使用官方 API**

---

**免责声明**：微信自动化功能可能违反服务条款，使用风险自负。
