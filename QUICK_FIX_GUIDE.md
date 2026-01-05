# 快速修复指南

遇到问题？按照这个顺序快速解决！

---

## 🚨 常见问题快速修复

### 1. HTTP 400 错误（关键词检测失败）

**症状**：
```
ERROR - Keyword detection failed with status 400
```

**快速修复**：
```bash
# 1. 重启 PaddleOCR 服务
cd paddleocr_service
python server.py

# 2. 测试服务
python test_paddleocr_service.py

# 3. 运行应用
python src/main.py
```

**详细说明**：[FIX_HTTP_400.md](FIX_HTTP_400.md)

---

### 2. Windows 找不到微信

**症状**：
```
WARNING - WeChat not found in common installation paths
```

**快速修复（1分钟）**：
```bash
python find_wechat.py
```

这个工具会自动：
- ✅ 查找所有微信安装位置
- ✅ 让你选择要使用的
- ✅ 自动保存配置

**或者禁用微信功能**：

编辑 `config/config.json`：
```json
{
  "wechat_enabled": false
}
```

**详细说明**：[WECHAT_TROUBLESHOOTING.md](WECHAT_TROUBLESHOOTING.md)

---

### 3. 无法连接 PaddleOCR 服务

**症状**：
```
Cannot connect to PaddleOCR service at http://localhost:5000
```

**快速修复**：
```bash
# 1. 启动服务
cd paddleocr_service
python server.py

# 2. 验证服务（浏览器）
http://localhost:5000/docs

# 3. 或切换到 Tesseract
# 在应用界面：OCR 引擎 → pytesseract
```

**详细说明**：[TROUBLESHOOTING.md](TROUBLESHOOTING.md#2-无法连接到-paddleocr-服务)

---

### 4. 打包后体积太大

**症状**：
- ScreenAlter.exe > 100MB

**快速修复**：
```bash
# 1. 清理
rmdir /s /q build dist

# 2. 确保使用最新 spec
git pull

# 3. 重新打包
scripts\build_windows.bat
```

**预期结果**：
- ScreenAlter.exe ≈ 50MB

**详细说明**：[PACKAGING_GUIDE.md](PACKAGING_GUIDE.md)

---

### 5. 模块找不到

**症状**：
```
ModuleNotFoundError: No module named 'xxx'
```

**快速修复**：
```bash
# 1. 激活虚拟环境
venv\Scripts\activate

# 2. 重新安装依赖
pip install -r requirements.txt

# 3. 运行应用
python src/main.py
```

---

## 🛠️ 工具速查

| 工具 | 用途 | 命令 |
|------|------|------|
| **测试 PaddleOCR** | 验证服务是否正常 | `python test_paddleocr_service.py` |
| **查找微信** | 自动配置微信路径 | `python find_wechat.py` |
| **主应用** | 运行监控应用 | `python src/main.py` |
| **打包主应用** | 生成 exe | `scripts\build_windows.bat` |
| **打包服务** | 打包 PaddleOCR | `cd paddleocr_service && build_service.bat` |

---

## 📋 检查清单

遇到问题时，按顺序检查：

### 基础环境
- [ ] Python 3.11+ 已安装？
- [ ] 虚拟环境已激活？
- [ ] 依赖已安装？`pip list`

### OCR 功能
- [ ] 选择了哪个 OCR 引擎？
  - [ ] PaddleOCR：服务是否启动？
  - [ ] Tesseract：是否已安装？
- [ ] 访问 http://localhost:5000/docs 是否正常？
- [ ] 测试脚本是否通过？`python test_paddleocr_service.py`

### 微信功能（可选）
- [ ] 是否需要微信功能？
- [ ] 微信是否已安装？
- [ ] 运行 `python find_wechat.py` 是否找到？
- [ ] 配置文件中 `wechat_enabled` 是否正确？

### 应用运行
- [ ] 可以启动应用？`python src/main.py`
- [ ] 可以添加关键词？
- [ ] 可以开始监控？
- [ ] 查看日志：`logs/app.log`

---

## 📚 完整文档索引

| 文档 | 说明 |
|------|------|
| [README.md](README.md) | 项目总览和快速开始 |
| [CONFIG_GUIDE.md](CONFIG_GUIDE.md) | 配置文件详细说明 ⭐ |
| [ARCHITECTURE_CS_MODE.md](ARCHITECTURE_CS_MODE.md) | C/S 架构说明 |
| [QUICK_START_STANDALONE.md](QUICK_START_STANDALONE.md) | PaddleOCR 服务快速开始 |
| [PACKAGING_GUIDE.md](PACKAGING_GUIDE.md) | 打包指南 |
| [TROUBLESHOOTING.md](TROUBLESHOOTING.md) | 完整故障排查 |
| [WECHAT_TROUBLESHOOTING.md](WECHAT_TROUBLESHOOTING.md) | 微信问题专项 |
| [FIX_HTTP_400.md](FIX_HTTP_400.md) | HTTP 400 错误详解 |
| [OCR_ENGINE_GUIDE.md](docs/OCR_ENGINE_GUIDE.md) | OCR 引擎对比 |

---

## 🆘 仍然无法解决？

### 1. 收集信息

```bash
# 系统信息
python --version
pip list

# 日志
type logs\app.log

# 配置
type config\config.json
```

### 2. 查看日志

- **主应用日志**：`logs/app.log`
- **服务端日志**：运行 `python server.py` 时的控制台输出

### 3. 搜索关键词

在日志中搜索：
- `ERROR`
- `CRITICAL`
- `Failed`
- `not found`

### 4. 提交 Issue

包含以下信息：
- 操作系统版本
- Python 版本
- 错误日志
- 复现步骤
- 已尝试的解决方案

---

## 💡 最佳实践

1. **开发阶段**：
   - 使用 `python src/main.py` 运行
   - 保持服务端在单独的终端运行
   - 及时查看日志

2. **测试阶段**：
   - 运行所有测试脚本
   - 验证打包后的 exe
   - 在干净的环境中测试

3. **生产环境**：
   - 打包前清理旧构建
   - 测试所有功能
   - 准备用户文档

---

记住：
- ✅ **核心功能**不依赖 PaddleOCR 或微信
- ✅ 有问题时先查看**日志**
- ✅ 使用**测试工具**验证配置
- ✅ 查阅**详细文档**获取更多信息

祝你使用愉快！🚀
