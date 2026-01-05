# 🚀 开始使用 PaddleOCR 独立服务

## 这是什么？

这是一个**独立的 PaddleOCR HTTP API 服务**，可以让你的主应用体积从 500MB 缩减到 50MB！

## 快速开始（3 步）

### 步骤 1：安装依赖

```bash
pip install -r requirements.txt
```

### 步骤 2：启动服务

```bash
python server.py
```

你会看到：
```
Starting PaddleOCR Service...
Service will be available at: http://localhost:5000
```

### 步骤 3：运行主应用

主应用会自动连接到这个服务！

---

## 打包为可执行文件

如果想分发给用户：

```bash
build_service.bat
```

会生成：`dist\PaddleOCRService.exe` (约 500MB)

---

## 测试服务

### 浏览器

打开：http://localhost:5000/docs

会看到完整的 API 文档。

### 命令行

```bash
curl http://localhost:5000/health
```

应该返回：
```json
{"status": "healthy", "ocr_ready": true}
```

---

## 配置

### 修改端口

编辑 `server.py` 第 147 行：

```python
port=5000,  # 改为其他端口
```

### 启用 GPU

编辑 `server.py` 第 32 行：

```python
use_gpu=True,  # 需要 CUDA 支持
```

---

## 为什么要这样做？

### 原方案
```
主应用 + PaddleOCR = 500MB
```

### 新方案
```
主应用 = 50MB
PaddleOCR 服务 = 500MB (可选安装)
```

**优势**：
- ✅ 主应用小 90%
- ✅ 用户可以选择不安装 PaddleOCR（改用 Tesseract）
- ✅ PaddleOCR 可以独立更新
- ✅ 多个应用可以共享一个服务
- ✅ 可以部署到远程服务器

---

## 需要帮助？

- 详细文档：[PADDLEOCR_STANDALONE_DEPLOYMENT.md](../docs/PADDLEOCR_STANDALONE_DEPLOYMENT.md)
- 快速开始：[QUICK_START_STANDALONE.md](../QUICK_START_STANDALONE.md)
- API 文档：启动服务后访问 http://localhost:5000/docs

---

## 常见问题

**Q: 服务启动失败？**
A: 检查端口 5000 是否被占用。可以修改为其他端口。

**Q: 首次运行很慢？**
A: PaddleOCR 首次运行会下载模型文件（约 20MB），需要等待。

**Q: 主应用连接不上？**
A: 确保服务已启动，检查防火墙设置。

**Q: 可以远程访问吗？**
A: 可以！修改 `server.py` 中的 `host="0.0.0.0"`，但注意安全问题。

---

就这么简单！🎉
