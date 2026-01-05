# PaddleOCR HTTP API Service

独立运行的 PaddleOCR 服务，通过 HTTP API 提供 OCR 功能。

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动服务

```bash
python server.py
```

服务将在 `http://localhost:5000` 启动

### 3. 访问 API 文档

浏览器打开：`http://localhost:5000/docs`

## 📦 打包为可执行文件

### Windows

```bash
build_service.bat
```

生成 `dist\PaddleOCRService.exe`

## 📋 API 接口

### 1. 健康检查

```bash
GET http://localhost:5000/health
```

### 2. OCR 识别

```bash
POST http://localhost:5000/api/ocr
Content-Type: multipart/form-data

file: <图片文件>
```

**响应示例**：
```json
{
  "success": true,
  "text": "识别的完整文字",
  "lines": [
    {
      "text": "第一行文字",
      "confidence": 0.98,
      "box": [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]
    }
  ],
  "total_lines": 1
}
```

### 3. 关键词检测

```bash
POST http://localhost:5000/api/detect_keywords
Content-Type: multipart/form-data

file: <图片文件>
keywords: "关键词1,关键词2,关键词3"
```

**响应示例**：
```json
{
  "success": true,
  "detected": true,
  "matched_keywords": ["关键词1"],
  "contexts": {
    "关键词1": "...上下文文字..."
  },
  "text": "完整识别文字"
}
```

## 🔧 配置

### 修改端口

编辑 `server.py`：

```python
uvicorn.run(
    app,
    host="127.0.0.1",
    port=5000,  # 修改端口
    log_level="info"
)
```

### 启用 GPU

编辑 `server.py`：

```python
ocr_instance = PaddleOCR(
    use_angle_cls=False,
    lang='ch',
    use_gpu=True,  # 改为 True
    show_log=False
)
```

### 远程访问

编辑 `server.py`：

```python
uvicorn.run(
    app,
    host="0.0.0.0",  # 允许远程访问
    port=5000
)
```

## 🎮 使用示例

### Python 客户端

```python
import requests

# 健康检查
response = requests.get("http://localhost:5000/health")
print(response.json())

# OCR 识别
with open("image.png", "rb") as f:
    files = {"file": f}
    response = requests.post("http://localhost:5000/api/ocr", files=files)
    print(response.json()["text"])

# 关键词检测
with open("image.png", "rb") as f:
    files = {"file": f}
    data = {"keywords": "违规,敏感"}
    response = requests.post(
        "http://localhost:5000/api/detect_keywords",
        files=files,
        data=data
    )
    result = response.json()
    if result["detected"]:
        print(f"检测到关键词: {result['matched_keywords']}")
```

### cURL

```bash
# 健康检查
curl http://localhost:5000/health

# OCR 识别
curl -X POST http://localhost:5000/api/ocr \
  -F "file=@image.png"

# 关键词检测
curl -X POST http://localhost:5000/api/detect_keywords \
  -F "file=@image.png" \
  -F "keywords=违规,敏感"
```

## 📊 性能

- 初始化时间：2-3 秒（首次）
- OCR 处理速度：1-2 秒/图片（CPU）
- 内存占用：约 500MB
- 并发支持：单进程可处理多个请求

## 🔍 监控

查看日志：

```bash
python server.py
```

日志包含：
- 服务启动信息
- 请求处理时间
- 错误信息

## 🛠️ 故障排除

### 端口被占用

修改端口或关闭占用端口的程序：

```bash
# Windows 查看端口占用
netstat -ano | findstr :5000

# 结束进程
taskkill /PID <进程ID> /F
```

### PaddleOCR 初始化失败

检查依赖是否正确安装：

```bash
pip install paddlepaddle paddleocr --upgrade
```

### 首次运行下载模型

首次运行时会自动下载模型文件（约 20MB），需要网络连接。

模型保存位置：`C:\Users\<用户名>\.paddleocr\`

## 📦 部署

### 生产环境

使用 Gunicorn (Linux) 或直接运行：

```bash
# 开发
python server.py

# 生产（Windows）
直接运行 PaddleOCRService.exe
```

### Docker 部署

```dockerfile
FROM python:3.11
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY server.py .
EXPOSE 5000
CMD ["python", "server.py"]
```

构建和运行：

```bash
docker build -t paddleocr-service .
docker run -p 5000:5000 paddleocr-service
```

## 📝 许可证

本服务基于 PaddleOCR 构建，遵循 Apache 2.0 许可证。
