# 故障排查指南

## 🔍 常见错误及解决方案

### 0. Windows 找不到文件 wechat

**快速解决**：
- ✅ **已修复**：最新版本自动查找微信路径
- ✅ **可选功能**：微信报警是可选的，不影响核心功能
- ✅ **详细说明**：查看 **[微信故障排查指南](WECHAT_TROUBLESHOOTING.md)**

**如果仍有问题**：
1. 更新到最新代码：`git pull`
2. 查看详细文档：[WECHAT_TROUBLESHOOTING.md](WECHAT_TROUBLESHOOTING.md)
3. 或禁用微信功能，使用其他报警方式

---

### 1. HTTP 400 错误 - 关键词检测失败

**错误日志**：
```
monitor.paddle_ocr_client - ERROR - Keyword detection failed with status 400: No keywords provided
```

**可能原因**：
1. 关键词列表为空
2. 关键词参数传输失败（FastAPI Form 参数问题）
3. 客户端和服务端版本不匹配

**解决方案**：

#### 方案 1：更新到最新版本（推荐）

确保服务端使用了 `Form(...)` 声明：

```bash
# 更新代码
git pull

# 重启服务
cd paddleocr_service
# 停止旧服务 (Ctrl+C)
python server.py
```

**关键修复**：服务端 `server.py` 应包含：
```python
from fastapi import Form

@app.post("/api/detect_keywords")
async def detect_keywords(
    file: UploadFile = File(...),
    keywords: str = Form("")  # 注意这里使用 Form(...)
):
```

#### 方案 2：运行测试脚本

```bash
# 测试服务是否正常
python test_paddleocr_service.py
```

应该看到：
```
✅ 关键词检测: 通过
```

#### 方案 3：检查关键词配置

在主应用界面检查：
1. 确保已添加至少一个关键词
2. 关键词不能为空字符串

#### 方案 4：查看详细日志

客户端日志 `logs/app.log`：
```
DEBUG - Detecting keywords: ['违规通知']
DEBUG - Sending keywords string: '违规通知'
```

服务端日志：
```
DEBUG - Received keywords parameter: '违规通知' (type: <class 'str'>)
DEBUG - Keywords to detect: ['违规通知']
```

如果服务端日志显示 `keywords param: ''`，说明参数传输失败，需要更新服务端代码。

---

### 2. 无法连接到 PaddleOCR 服务

**错误日志**：
```
Cannot connect to PaddleOCR service at http://localhost:5000
```

**原因**：
- PaddleOCR 服务未启动
- 端口被占用
- 防火墙阻止

**解决方案**：

#### 方案 1：启动服务

```bash
# 方式 1：Python 脚本
cd paddleocr_service
python server.py

# 方式 2：可执行文件
PaddleOCRService.exe
```

#### 方案 2：检查端口

```bash
# Windows
netstat -ano | findstr :5000

# 如果端口被占用，修改配置
```

编辑 `paddleocr_service/server.py`：
```python
uvicorn.run(app, host="127.0.0.1", port=5001)  # 改为其他端口
```

同时修改主应用配置：
```json
{
  "paddleocr_service_url": "http://localhost:5001"
}
```

#### 方案 3：检查防火墙

临时关闭防火墙测试，或添加允许规则。

#### 方案 4：验证服务

浏览器访问：http://localhost:5000
- 应该看到：`{"service":"PaddleOCR API","version":"1.0.0","status":"running"}`

访问 API 文档：http://localhost:5000/docs

---

### 3. 服务启动失败

**错误信息**：
```
ModuleNotFoundError: No module named 'paddleocr'
```

**解决方案**：

#### 方案 1：安装依赖

```bash
cd paddleocr_service
pip install -r requirements.txt
```

#### 方案 2：检查虚拟环境

确保在正确的虚拟环境中：
```bash
# Windows
venv\Scripts\activate

# 重新安装
pip install -r requirements.txt
```

#### 方案 3：检查 Python 版本

```bash
python --version
# 需要 Python 3.11+
```

---

### 4. OCR 识别结果为空

**症状**：
- 服务正常运行
- 请求成功 (200)
- 但返回空文字

**原因**：
- 图片中没有文字
- 图片质量太低
- PaddleOCR 模型未下载完整

**解决方案**：

#### 方案 1：检查图片

确保图片：
- 包含清晰文字
- 分辨率足够（建议 > 300x300）
- 格式正确（PNG, JPG, BMP）

#### 方案 2：查看服务端日志

日志应该显示：
```
INFO - OCR completed: text_length=0, lines=0
```

如果是这样，说明 OCR 确实没识别到文字。

#### 方案 3：手动测试

使用 curl 或浏览器测试：
```bash
curl -X POST http://localhost:5000/api/ocr \
  -F "file=@test_image.png"
```

或访问：http://localhost:5000/docs 使用 Swagger UI 测试

#### 方案 4：检查模型

首次运行 PaddleOCR 会下载模型到：
```
C:\Users\<用户名>\.paddleocr\
```

如果下载失败，删除这个文件夹重新下载。

---

### 5. 首次运行非常慢

**症状**：
- 启动服务或首次 OCR 请求等待很久
- 服务端显示 "Downloading..."

**原因**：
PaddleOCR 首次运行需要下载模型文件（约 20MB）

**解决方案**：

#### 方案 1：等待下载

耐心等待 1-2 分钟，模型会自动下载到：
```
C:\Users\<用户名>\.paddleocr\whl\
```

#### 方案 2：手动下载

如果自动下载失败，可以手动下载模型：
1. 访问：https://github.com/PaddlePaddle/PaddleOCR
2. 下载预训练模型
3. 放置到正确位置

#### 方案 3：使用代理

如果网络受限，配置代理：
```bash
set http_proxy=http://your-proxy:port
set https_proxy=http://your-proxy:port
python server.py
```

---

### 6. 内存占用过高

**症状**：
- PaddleOCRService 占用 500MB+ 内存
- 系统响应变慢

**原因**：
PaddleOCR 是深度学习模型，需要较大内存。

**解决方案**：

#### 方案 1：使用后关闭服务

不使用时关闭 PaddleOCRService.exe。

#### 方案 2：切换到 Tesseract

在主应用中：
- OCR 引擎 → 选择 `pytesseract`
- Tesseract 内存占用约 50-100MB

安装 Tesseract：https://github.com/UB-Mannheim/tesseract/wiki

#### 方案 3：优化服务器配置

如果是服务器部署，可以：
- 增加内存
- 使用轻量级模型
- 配置内存限制

---

### 7. 打包后主应用仍然很大

**症状**：
- 打包后 ScreenAlter.exe 仍然 > 100MB
- 预期应该是 50MB 左右

**原因**：
- 旧的打包配置
- 没有排除 PaddleOCR
- 包含了不必要的依赖

**解决方案**：

#### 方案 1：清理并重新打包

```bash
# 清理所有旧构建
rmdir /s /q build dist
rmdir /s /q src\__pycache__
rmdir /s /q src\*\__pycache__

# 确保使用最新配置
git pull

# 重新打包
scripts\build_windows.bat
```

#### 方案 2：检查 spec 文件

确保 `ScreenAlter.spec` 中有：
```python
excludes=[
    'paddleocr',
    'paddle',
    'paddlepaddle',
    'matplotlib',
    'scipy',
]
```

#### 方案 3：检查 requirements.txt

确保已移除：
```
# 不应该包含这些
paddlepaddle
paddleocr
```

---

### 8. "Previous check still in progress"

**日志**：
```
gui.main_window - DEBUG - Previous check still in progress, skipping...
```

**原因**：
上一次 OCR 检测还未完成，新的检测被跳过。这是**正常行为**。

**说明**：
- OCR 处理需要 1-2 秒
- 如果监控间隔太短（如 1 秒），可能会出现这个日志
- 这是为了防止请求堆积

**解决方案**（如果频繁出现）：

#### 方案 1：增加监控间隔

在主应用中：
- 监控间隔 → 选择 5 秒或更长

#### 方案 2：优化图片大小

- 减小截图区域
- 降低分辨率

#### 方案 3：使用 GPU 加速

编辑 `paddleocr_service/server.py`：
```python
ocr_instance = PaddleOCR(
    use_gpu=True,  # 启用 GPU
    ...
)
```

---

### 9. 跨域 (CORS) 错误

**症状**（如果从浏览器调用）：
```
Access to XMLHttpRequest blocked by CORS policy
```

**解决方案**：

编辑 `paddleocr_service/server.py`：
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

### 10. 远程连接失败

**症状**：
- 客户端配置了远程地址：http://192.168.1.100:5000
- 无法连接

**解决方案**：

#### 方案 1：修改服务器监听地址

编辑服务器上的 `server.py`：
```python
uvicorn.run(
    app,
    host="0.0.0.0",  # 允许远程访问
    port=5000
)
```

#### 方案 2：检查防火墙

服务器端：
```bash
# Windows 防火墙规则
netsh advfirewall firewall add rule name="PaddleOCR" dir=in action=allow protocol=TCP localport=5000
```

#### 方案 3：检查网络

```bash
# 客户端测试连通性
ping 192.168.1.100
telnet 192.168.1.100 5000
curl http://192.168.1.100:5000/health
```

---

## 🛠️ 调试技巧

### 1. 启用详细日志

主应用的日志文件：
```
logs/app.log
```

服务端运行时会显示详细日志。

### 2. 使用 API 文档测试

启动服务后访问：
```
http://localhost:5000/docs
```

可以直接测试 API，无需主应用。

### 3. 检查网络请求

使用工具查看 HTTP 请求：
- Fiddler
- Wireshark
- Chrome DevTools (如果是 Web 界面)

### 4. 查看进程

```bash
# Windows
tasklist | findstr -i "paddle\|screen"

# 检查端口占用
netstat -ano | findstr :5000
```

---

## 📞 获取帮助

如果以上方法都无法解决问题：

1. **收集信息**：
   - 错误日志（`logs/app.log`）
   - 服务端日志
   - 系统环境（OS, Python 版本）
   - 操作步骤

2. **检查文档**：
   - [架构说明](ARCHITECTURE_CS_MODE.md)
   - [快速开始](QUICK_START_STANDALONE.md)
   - [OCR 引擎指南](../docs/OCR_ENGINE_GUIDE.md)

3. **提交 Issue**：
   - 描述问题
   - 附上日志
   - 说明环境

---

## 📝 常用命令参考

### 服务管理

```bash
# 启动服务
cd paddleocr_service
python server.py

# 检查服务
curl http://localhost:5000/health

# 停止服务
Ctrl+C
```

### 主应用

```bash
# 开发模式
python src/main.py

# 打包
scripts\build_windows.bat

# 运行打包版本
dist\ScreenAlter\ScreenAlter.exe
```

### 清理

```bash
# 清理构建
rmdir /s /q build dist

# 清理 Python 缓存
rmdir /s /q src\__pycache__
find . -name "*.pyc" -delete
```

---

希望这份指南能帮助你快速解决问题！🚀
