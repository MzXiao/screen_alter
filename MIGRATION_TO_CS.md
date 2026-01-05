# 迁移指南：嵌入式 → C/S 架构

## 🎯 变更说明

本项目已从**嵌入式架构**完全迁移到 **C/S（客户端/服务器）架构**。

## 📊 核心变化

### Before（嵌入式）

```
ScreenAlter.exe (500MB)
├── 主应用
└── PaddleOCR (嵌入)
```

### After（C/S）

```
ScreenAlter.exe (50MB)          PaddleOCRService.exe (500MB)
├── 主应用                       ├── PaddleOCR
└── HTTP 客户端 ←────────────→  └── FastAPI 服务
```

---

## 🔄 迁移步骤

### 对于开发者

#### 1. 更新代码仓库

```bash
git pull origin main
```

#### 2. 重新安装依赖

```bash
# 主应用依赖（不再包含 PaddleOCR）
pip install -r requirements.txt

# OCR 服务依赖（新增）
cd paddleocr_service
pip install -r requirements.txt
cd ..
```

#### 3. 启动服务

```bash
# 终端 1：OCR 服务
cd paddleocr_service
python server.py

# 终端 2：主应用
python src/main.py
```

### 对于打包者

#### 1. 清理旧构建

```bash
rmdir /s /q build dist
cd paddleocr_service
rmdir /s /q build dist
cd ..
```

#### 2. 打包主应用

```bash
scripts\build_windows.bat
```

生成：`dist\ScreenAlter\ScreenAlter.exe` (50MB)

#### 3. 打包 OCR 服务

```bash
cd paddleocr_service
build_service.bat
```

生成：`paddleocr_service\dist\PaddleOCRService.exe` (500MB)

### 对于用户

#### 如果已安装旧版本

1. **卸载旧版本**
   - 删除 ScreenAlter.exe (500MB)

2. **安装新版本**
   - 主应用：ScreenAlter.exe (50MB)
   - OCR 服务：PaddleOCRService.exe (500MB，可选)

3. **首次运行**
   - 先启动 PaddleOCRService.exe
   - 再启动 ScreenAlter.exe

#### 如果是新用户

直接按照新的安装指南操作。

---

## 💡 代码变化

### 删除的文件

```
❌ src/monitor/paddle_ocr_detector.py  # 本地调用模式
```

### 新增的文件

```
✅ paddleocr_service/server.py                # OCR 服务
✅ paddleocr_service/requirements.txt         # 服务依赖
✅ paddleocr_service/build_service.bat        # 服务打包
✅ paddleocr_service/README.md                # 服务文档
✅ src/monitor/paddle_ocr_client.py           # HTTP 客户端
```

### 修改的文件

#### `src/gui/main_window.py`

```python
# Before
from monitor.paddle_ocr_detector import PaddleOCRDetector
self.ocr_detector = PaddleOCRDetector()

# After
from monitor.paddle_ocr_client import PaddleOCRClient
self.ocr_detector = PaddleOCRClient("http://localhost:5000")
```

#### `requirements.txt`

```diff
- paddlepaddle==2.6.2
- paddleocr==2.9.1
+ # PaddleOCR 已移至独立服务
+ requests==2.31.0  # For HTTP client
```

#### `ScreenAlter.spec`

```diff
- from PyInstaller.utils.hooks import collect_all
- paddleocr_datas, paddleocr_binaries, _ = collect_all('paddleocr')
+ # No PaddleOCR packaging
+ excludes=['paddleocr', 'paddle', 'scipy']
```

#### `src/config_mod.py`

```diff
- "paddleocr_use_service": True,  # 本地/服务模式切换
+ # 只支持服务模式
+ "paddleocr_service_url": "http://localhost:5000"
```

---

## 🎮 使用变化

### 启动流程

#### Before

```bash
# 一步
ScreenAlter.exe
```

#### After

```bash
# 两步
1. PaddleOCRService.exe  # 启动服务
2. ScreenAlter.exe        # 启动应用
```

### 配置变化

#### Before

```json
{
  "ocr_engine": "paddleocr",
  "paddleocr_use_service": false  # 可选本地模式
}
```

#### After

```json
{
  "ocr_engine": "paddleocr",
  "paddleocr_service_url": "http://localhost:5000"  # 只支持服务模式
}
```

---

## ⚠️ 兼容性说明

### 向后不兼容

- ❌ 旧的配置项 `paddleocr_use_service` 已废弃
- ❌ 本地模式已完全移除
- ❌ 无法直接使用旧版 exe

### 数据兼容

- ✅ 数据库结构未变化
- ✅ 配置文件可自动迁移
- ✅ 用户数据完全兼容

---

## 📦 打包变化

### Before

```bash
pyinstaller ScreenAlter.spec
# 输出: 500MB
# 包含: 应用 + PaddleOCR
```

### After

```bash
# 主应用
pyinstaller ScreenAlter.spec
# 输出: 50MB
# 包含: 应用 + HTTP 客户端

# OCR 服务
cd paddleocr_service
pyinstaller server.py
# 输出: 500MB
# 包含: PaddleOCR + FastAPI
```

---

## 🐛 常见迁移问题

### Q1: 运行主应用提示"无法连接服务"？

**A**: 需要先启动 OCR 服务：

```bash
# 方式 1
PaddleOCRService.exe

# 方式 2
cd paddleocr_service
python server.py
```

### Q2: 旧版配置不工作？

**A**: 删除旧配置，使用新的默认配置：

```bash
del config\config.json
# 重启应用，会自动生成新配置
```

### Q3: 打包失败，提示找不到 PaddleOCR？

**A**: 确保使用最新的 spec 文件：

```bash
git pull
pyinstaller ScreenAlter.spec
```

### Q4: 想用回本地模式？

**A**: 本地模式已完全移除。如果不想使用服务，可以：
- 切换到 Tesseract OCR
- 或仅使用图像检测（不用文字识别）

### Q5: 服务占用内存太多？

**A**: PaddleOCR 需要约 500MB 内存，这是正常的。可以：
- 使用完毕后关闭服务
- 或切换到 Tesseract（内存占用小）

---

## 📈 优势总结

### 对开发者

- ✅ 代码更清晰（职责分离）
- ✅ 调试更容易（独立服务）
- ✅ 打包更快速（无需等待 PaddleOCR）

### 对用户

- ✅ 下载更快（主应用只有 50MB）
- ✅ 启动更快（不加载 PaddleOCR）
- ✅ 更灵活（可选择安装 OCR）

### 对维护者

- ✅ 更新更简单（独立部署）
- ✅ 扩展更容易（微服务架构）
- ✅ 监控更方便（独立日志）

---

## 🚀 下一步

1. **阅读文档**
   - [架构说明](ARCHITECTURE_CS_MODE.md)
   - [快速开始](QUICK_START_STANDALONE.md)
   - [打包指南](PACKAGING_GUIDE.md)

2. **尝试运行**
   ```bash
   # 启动服务
   cd paddleocr_service
   python server.py
   
   # 运行应用
   python src/main.py
   ```

3. **测试打包**
   ```bash
   scripts\build_windows.bat
   cd paddleocr_service
   build_service.bat
   ```

4. **反馈问题**
   - 如遇到问题，请查看日志
   - 或提交 Issue

---

## 📝 检查清单

迁移完成后，请确认：

- [ ] 主应用可以正常启动
- [ ] OCR 服务可以正常启动
- [ ] 主应用可以连接到服务
- [ ] OCR 识别功能正常
- [ ] 关键词检测功能正常
- [ ] 打包后的 exe 可以运行
- [ ] 文档已更新
- [ ] 旧文件已删除

---

## 💬 获取帮助

如有问题：

1. 查看文档：[docs/](docs/)
2. 查看日志：`logs/app.log`
3. 检查服务：http://localhost:5000/docs
4. 提交 Issue

---

迁移完成！🎉

现在享受更轻量、更灵活的新架构吧！
