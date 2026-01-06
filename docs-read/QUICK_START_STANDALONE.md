# PaddleOCR 独立服务 - 快速开始

## 🎯 概述

通过独立服务方式使用 PaddleOCR，主应用体积从 **500MB 减少到 50MB**！

## 📦 架构

```
主应用 (ScreenAlter.exe)  ←→  PaddleOCR 服务 (PaddleOCRService.exe)
     50MB                          500MB (可选安装)
```

## 🚀 快速开始

### 方案一：启动服务（开发/测试）

#### 1. 启动 PaddleOCR 服务

```bash
# 进入服务目录
cd paddleocr_service

# 安装依赖（首次）
pip install -r requirements.txt

# 启动服务
python server.py
```

服务启动后会显示：
```
Starting PaddleOCR Service...
Service will be available at: http://localhost:5000
API documentation: http://localhost:5000/docs
```

#### 2. 运行主应用

```bash
# 开发模式
python src/main.py

# 或打包后运行
dist\ScreenAlter\ScreenAlter.exe
```

主应用会自动连接到服务。

---

### 方案二：打包服务（生产环境）

#### 1. 打包 PaddleOCR 服务

```bash
cd paddleocr_service
build_service.bat
```

生成：`paddleocr_service\dist\PaddleOCRService.exe`

#### 2. 打包主应用

```bash
# 回到项目根目录
cd ..

# 确保 requirements.txt 中没有 paddleocr
# （或者在 spec 文件中排除）

# 打包主应用
scripts\build_windows.bat
```

生成：`dist\ScreenAlter\ScreenAlter.exe`

#### 3. 分发给用户

创建发布包：
```
MyApp_v1.0/
├── ScreenAlter/
│   └── ScreenAlter.exe          # 主应用 (50MB)
├── PaddleOCRService.exe         # OCR 服务 (500MB, 可选)
├── start_service.bat            # 启动服务脚本
└── README.txt                   # 使用说明
```

**start_service.bat** 内容：
```batch
@echo off
echo Starting PaddleOCR Service...
start PaddleOCRService.exe
echo.
echo Service is starting...
echo Please wait for a few seconds, then run ScreenAlter.exe
pause
```

---

## ⚙️ 配置

### 主应用配置

主应用的配置在 `config/config.json` 或数据库中：

```json
{
  "ocr_engine": "paddleocr",
  "paddleocr_use_service": true,
  "paddleocr_service_url": "http://localhost:5000"
}
```

**配置说明**：
- `paddleocr_use_service: true` - 使用服务模式（推荐）
- `paddleocr_use_service: false` - 使用本地模式（需要打包 PaddleOCR）
- `paddleocr_service_url` - 服务地址

### 修改服务端口

编辑 `paddleocr_service/server.py`：

```python
uvicorn.run(
    app,
    host="127.0.0.1",
    port=5000,  # 改为其他端口，如 8888
    log_level="info"
)
```

同时修改主应用配置中的 `paddleocr_service_url`。

---

## 🎮 使用场景

### 场景 1：单机使用

用户在同一台电脑上运行服务和主应用：

1. 启动 `PaddleOCRService.exe`
2. 启动 `ScreenAlter.exe`
3. 开始监控

### 场景 2：远程服务

将服务部署在服务器，多台电脑共享：

**服务器端**：
```python
# 修改 server.py
uvicorn.run(
    app,
    host="0.0.0.0",  # 允许远程访问
    port=5000
)
```

**客户端配置**：
```json
{
  "paddleocr_service_url": "http://192.168.1.100:5000"
}
```

### 场景 3：用户选择

让用户选择安装哪个 OCR 引擎：

```
安装选项：
[ ] PaddleOCR 服务（高准确率，500MB）
[ ] Tesseract（轻量级，需单独安装）
```

---

## 📊 体积对比

### 原方案（打包 PaddleOCR）

```
ScreenAlter.exe: 500MB
总体积: 500MB
```

### 新方案（独立服务）

```
ScreenAlter.exe: 50MB
PaddleOCRService.exe: 500MB (可选)
```

**优势**：
- ✅ 主应用小 90%
- ✅ 用户可选择不安装 PaddleOCR
- ✅ 可以使用 Tesseract 替代
- ✅ 服务可以独立更新

---

## 🔍 验证服务

### 浏览器访问

打开浏览器访问：`http://localhost:5000/docs`

你会看到完整的 API 文档（Swagger UI）。

### 命令行测试

```bash
# 健康检查
curl http://localhost:5000/health

# OCR 识别
curl -X POST http://localhost:5000/api/ocr -F "file=@test.png"
```

### Python 测试

```python
import requests

# 检查服务
response = requests.get("http://localhost:5000/health")
print(response.json())
# 输出: {"status": "healthy", "ocr_ready": true}
```

---

## 🐛 故障排除

### 问题 1：无法连接到服务

**症状**：主应用提示"无法连接到 PaddleOCR 服务"

**解决**：
1. 确认服务已启动：浏览器访问 `http://localhost:5000`
2. 检查端口是否被占用：`netstat -ano | findstr :5000`
3. 检查防火墙设置

### 问题 2：服务启动失败

**症状**：运行 `PaddleOCRService.exe` 后立即退出

**解决**：
1. 以命令行方式运行查看错误信息：
   ```bash
   cd paddleocr_service\dist
   PaddleOCRService.exe
   ```
2. 检查依赖是否安装：`pip install -r requirements.txt`
3. 检查 Python 版本：需要 Python 3.11+

### 问题 3：首次运行很慢

**症状**：第一次调用 OCR 等待很久

**原因**：PaddleOCR 首次运行需要下载模型文件（约 20MB）

**解决**：等待下载完成，后续会很快。模型保存在：
```
C:\Users\<用户名>\.paddleocr\
```

### 问题 4：想切换到本地模式

**操作**：在主应用界面中，或修改配置：

```json
{
  "paddleocr_use_service": false
}
```

注意：本地模式需要重新打包主应用，包含 PaddleOCR。

---

## 📝 更新日志

### v1.0.0
- ✅ 支持 HTTP API 服务模式
- ✅ 主应用可选择服务模式或本地模式
- ✅ 服务可独立打包和分发
- ✅ 自动服务健康检查
- ✅ 完整的 API 文档

---

## 📚 相关文档

- 详细实现：[docs/PADDLEOCR_STANDALONE_DEPLOYMENT.md](../docs/PADDLEOCR_STANDALONE_DEPLOYMENT.md)
- 服务 API：[paddleocr_service/README.md](../paddleocr_service/README.md)
- OCR 引擎对比：[docs/OCR_ENGINE_GUIDE.md](../docs/OCR_ENGINE_GUIDE.md)
- 打包指南：[PACKAGING_GUIDE.md](PACKAGING_GUIDE.md)

---

## 💡 最佳实践

1. **开发阶段**：使用 `python server.py` 启动服务，方便调试
2. **测试阶段**：打包服务和主应用，测试分发流程
3. **生产环境**：提供服务和主应用两个独立可执行文件
4. **用户选择**：让用户选择安装 PaddleOCR 或 Tesseract

---

## ✨ 总结

这个方案完美解决了打包体积问题：

- ✅ **灵活**：用户可以选择是否安装 PaddleOCR
- ✅ **轻量**：主应用只有 50MB
- ✅ **高效**：HTTP 开销可忽略（< 10ms）
- ✅ **可扩展**：可以远程部署、负载均衡
- ✅ **易维护**：服务和应用独立更新

试试看吧！ 🚀
