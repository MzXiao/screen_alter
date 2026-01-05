# HTTP 400 错误修复说明

## 🐛 问题描述

### 症状

即使客户端发送了关键词，服务端仍然返回 HTTP 400 错误：

```
monitor.paddle_ocr_client - DEBUG - Detecting keywords: ['违规通知']
urllib3.connectionpool - DEBUG - http://localhost:5000 "POST /api/detect_keywords HTTP/1.1" 400 85
monitor.paddle_ocr_client - ERROR - Keyword detection failed with status 400: No keywords provided
```

### 根本原因

FastAPI 在处理 `multipart/form-data` 请求时，需要显式声明 Form 参数。

**错误的代码**：
```python
@app.post("/api/detect_keywords")
async def detect_keywords(
    file: UploadFile = File(...),
    keywords: str = ""  # ❌ 这样无法接收 form-data 中的 keywords
):
```

**正确的代码**：
```python
from fastapi import Form

@app.post("/api/detect_keywords")
async def detect_keywords(
    file: UploadFile = File(...),
    keywords: str = Form("")  # ✅ 使用 Form() 声明
):
```

---

## ✅ 修复内容

### 1. 服务端修复（`paddleocr_service/server.py`）

#### 修复 1.1：导入 Form

```python
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
```

#### 修复 1.2：使用 Form 声明参数

```python
@app.post("/api/detect_keywords")
async def detect_keywords(
    file: UploadFile = File(...),
    keywords: str = Form("")  # 使用 Form() 声明
):
    """
    关键词检测接口
    
    参数:
        file: 图片文件
        keywords: 逗号分隔的关键词字符串（如 "关键词1,关键词2,关键词3"）
    """
    logger.debug(f"Received keywords parameter: '{keywords}' (type: {type(keywords)})")
    # ... 其余代码
```

#### 修复 1.3：增强日志

```python
logger.debug(f"Received keyword detection request for file: {file.filename}")
logger.debug(f"Keywords to detect: {keyword_list}")
logger.info(
    f"Keyword detection completed: "
    f"detected={len(matched_keywords) > 0}, "
    f"matched={matched_keywords}, "
    f"text_length={len(full_text)}"
)
```

### 2. 客户端增强（`src/monitor/paddle_ocr_client.py`）

#### 增强 2.1：详细日志

```python
keywords_str = ','.join(keywords)
files = {'file': ('image.png', img_byte_arr, 'image/png')}
data = {'keywords': keywords_str}

logger.debug(f"Detecting keywords: {keywords}")
logger.debug(f"Sending keywords string: '{keywords_str}'")
```

#### 增强 2.2：错误信息

```python
# 记录详细错误信息
error_detail = ""
try:
    error_response = response.json()
    error_detail = error_response.get("detail", "")
except:
    error_detail = response.text

logger.error(
    f"Keyword detection failed with status {response.status_code}: {error_detail}"
)
```

### 3. 测试脚本（`test_paddleocr_service.py`）

创建了完整的测试脚本，包含：
- ✅ 健康检查测试
- ✅ OCR 识别测试
- ✅ 关键词检测测试
- ✅ 空关键词验证测试

---

## 🧪 验证修复

### 步骤 1：更新代码

```bash
git pull
```

### 步骤 2：重启服务

```bash
cd paddleocr_service
# 停止旧服务 (Ctrl+C 或关闭窗口)
python server.py
```

你应该看到：
```
Starting PaddleOCR Service...
Service will be available at: http://localhost:5000
```

### 步骤 3：运行测试

```bash
python test_paddleocr_service.py
```

**预期输出**：
```
=== 测试 1: 健康检查 ===
状态码: 200
响应: {'status': 'healthy', 'ocr_ready': True}

=== 测试 2: OCR 识别 ===
状态码: 200
识别成功: True
识别文字: 违规通知测试
行数: 1

=== 测试 3: 关键词检测 ===
关键词: 违规通知,测试
发送数据: files=['file'], data={'keywords': '违规通知,测试'}
状态码: 200
检测成功: True
是否检测到: True
匹配的关键词: ['违规通知', '测试']
识别文字: 违规通知测试

=== 测试 4: 空关键词（预期失败）===
状态码: 400
✅ 正确返回 400: {'detail': 'No keywords provided. Please provide keywords as comma-separated string.'}

============================================================
测试结果汇总
============================================================
健康检查: ✅ 通过
OCR 识别: ✅ 通过
关键词检测: ✅ 通过
空关键词验证: ✅ 通过

总计: 4/4 通过

🎉 所有测试通过！
```

### 步骤 4：测试主应用

```bash
# 运行主应用
python src/main.py

# 或运行打包后的版本
dist\ScreenAlter\ScreenAlter.exe
```

在主应用中：
1. 添加关键词："违规通知"
2. 点击"开始监控"
3. 应该正常工作，不再有 HTTP 400 错误

---

## 📊 日志对比

### Before（修复前）

**客户端**：
```
DEBUG - Detecting keywords: ['违规通知']
ERROR - Keyword detection failed with status 400: No keywords provided
```

**服务端**：
```
WARNING - No keywords provided in request. keywords param: ''
```
❌ 参数丢失

### After（修复后）

**客户端**：
```
DEBUG - Detecting keywords: ['违规通知']
DEBUG - Sending keywords string: '违规通知'
```

**服务端**：
```
DEBUG - Received keywords parameter: '违规通知' (type: <class 'str'>)
DEBUG - Keywords to detect: ['违规通知']
INFO - Keyword detection completed: detected=True, matched=['违规通知'], text_length=6
```
✅ 参数正确接收

---

## 🔍 技术细节

### FastAPI Form 参数

在 FastAPI 中，处理 `multipart/form-data` 有两种方式：

#### 方式 1：自动推断（不推荐）

```python
async def endpoint(file: UploadFile = File(...), param: str = ""):
```

这种方式在某些情况下可能无法正确接收 form field。

#### 方式 2：显式声明（推荐）

```python
from fastapi import Form

async def endpoint(file: UploadFile = File(...), param: str = Form("")):
```

使用 `Form()` 明确告诉 FastAPI 这是一个 form field。

### Requests 发送 multipart/form-data

```python
files = {'file': ('image.png', data, 'image/png')}
data = {'keywords': 'keyword1,keyword2'}

response = requests.post(url, files=files, data=data)
```

当同时使用 `files` 和 `data` 参数时：
- `Content-Type` 自动设置为 `multipart/form-data`
- `files` 中的内容作为文件字段
- `data` 中的内容作为普通表单字段

---

## 📚 相关文档

- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - 完整故障排查指南
- [FastAPI Form Data](https://fastapi.tiangolo.com/tutorial/request-forms/) - 官方文档
- [Requests Multipart](https://requests.readthedocs.io/en/latest/user/quickstart/#post-a-multipart-encoded-file) - 官方文档

---

## ✨ 总结

这次修复解决了 FastAPI 接收 multipart/form-data 参数的问题：

1. **核心修复**：使用 `Form()` 显式声明参数
2. **日志增强**：添加详细的调试信息
3. **测试完善**：创建自动化测试脚本

现在关键词可以正确传输，不再有 HTTP 400 错误！🎉

---

## 🚀 下一步

1. **重启服务**：`cd paddleocr_service && python server.py`
2. **运行测试**：`python test_paddleocr_service.py`
3. **使用应用**：`python src/main.py`

如有问题，查看 [TROUBLESHOOTING.md](TROUBLESHOOTING.md)。
