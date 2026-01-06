# 配置文件说明

## 📁 配置文件位置

- **主配置**：`config/config.json`
- **示例配置**：`config/config.example.json`

---

## 📝 配置项说明

### 基础监控配置

```json
{
  "monitor_interval": 60,
  "ocr_engine": "paddleocr",
  "ocr_language": "chi_sim+eng",
  "similarity_threshold": 0.85,
  "screenshot_retention_days": 7,
  "screenshot_limit": 100,
  "capture_region": null,
  "keywords": [],
  "reference_images": [],
  "auto_start_monitoring": false
}
```

#### monitor_interval
- **说明**：监控间隔（秒）
- **类型**：整数
- **默认值**：60
- **可选值**：
  - `1` - 1 秒（仅测试用）
  - `5` - 5 秒
  - `30` - 30 秒
  - `60` - 1 分钟（推荐）
  - `300` - 5 分钟
- **示例**：`"monitor_interval": 60`

#### ocr_engine
- **说明**：OCR 识别引擎
- **类型**：字符串
- **默认值**：`"paddleocr"`
- **可选值**：
  - `"paddleocr"` - PaddleOCR（高准确率，需要服务）
  - `"pytesseract"` - Tesseract（轻量级，需要安装）
- **示例**：`"ocr_engine": "paddleocr"`

#### ocr_language
- **说明**：OCR 识别语言
- **类型**：字符串
- **默认值**：`"chi_sim+eng"`
- **格式**：语言代码，多个语言用 `+` 连接
- **常用值**：
  - `"chi_sim"` - 简体中文
  - `"chi_tra"` - 繁体中文
  - `"eng"` - 英文
  - `"chi_sim+eng"` - 中英文混合
- **示例**：`"ocr_language": "chi_sim+eng"`

#### similarity_threshold
- **说明**：图像相似度阈值（0-1）
- **类型**：浮点数
- **默认值**：0.85
- **范围**：0.0 - 1.0
- **说明**：
  - 数值越高，匹配越严格
  - 0.85 表示 85% 相似度
- **示例**：`"similarity_threshold": 0.85`

#### screenshot_retention_days
- **说明**：截图保留天数
- **类型**：整数
- **默认值**：7
- **说明**：自动删除超过指定天数的截图
- **示例**：`"screenshot_retention_days": 7`

#### screenshot_limit
- **说明**：截图数量限制
- **类型**：整数
- **默认值**：100
- **说明**：超过限制后删除最旧的截图
- **示例**：`"screenshot_limit": 100`

#### capture_region
- **说明**：截图区域（像素坐标）
- **类型**：数组或 null
- **默认值**：null（全屏）
- **格式**：`[left, top, width, height]`
- **示例**：
  ```json
  "capture_region": [100, 100, 800, 600]  // 指定区域
  "capture_region": null                   // 全屏
  ```

#### keywords
- **说明**：要检测的关键词列表
- **类型**：字符串数组
- **默认值**：`[]`
- **示例**：
  ```json
  "keywords": ["违规", "敏感词", "警告"]
  ```

#### reference_images
- **说明**：参考图片路径列表
- **类型**：字符串数组
- **默认值**：`[]`
- **说明**：用于图像相似度对比
- **示例**：
  ```json
  "reference_images": [
    "screenshots/reference1.png",
    "screenshots/reference2.png"
  ]
  ```

#### auto_start_monitoring
- **说明**：启动时自动开始监控
- **类型**：布尔值
- **默认值**：false
- **示例**：`"auto_start_monitoring": false`

---

### 后端服务配置

```json
{
  "backend_url": "http://localhost:8000"
}
```

#### backend_url
- **说明**：后端 API 服务地址
- **类型**：字符串
- **默认值**：`"http://localhost:8000"`
- **格式**：完整的 URL（包含协议）
- **示例**：
  ```json
  "backend_url": "http://localhost:8000"        // 本地
  "backend_url": "http://192.168.1.100:8000"   // 局域网
  "backend_url": "https://api.example.com"     // 远程
  ```

---

### PaddleOCR 服务配置

```json
{
  "paddleocr_service_url": "http://localhost:5000"
}
```

#### paddleocr_service_url
- **说明**：PaddleOCR HTTP 服务地址 ⭐
- **类型**：字符串
- **默认值**：`"http://localhost:5000"`
- **格式**：完整的 URL（包含协议和端口）
- **使用场景**：
  - 本地服务：`http://localhost:5000`
  - 远程服务：`http://192.168.1.100:5000`
  - 不同端口：`http://localhost:8888`
- **示例**：
  ```json
  "paddleocr_service_url": "http://localhost:5000"        // 本地默认
  "paddleocr_service_url": "http://192.168.1.100:5000"   // 远程服务器
  "paddleocr_service_url": "http://localhost:8888"       // 自定义端口
  ```
- **注意**：
  - 需要先启动 PaddleOCR 服务
  - 验证：访问 `{url}/docs` 查看 API 文档
  - 修改端口后需要同步修改服务端配置

---

### 微信功能配置

```json
{
  "wechat_enabled": false,
  "wechat_path": ""
}
```

#### wechat_enabled
- **说明**：是否启用微信报警功能
- **类型**：布尔值
- **默认值**：false
- **示例**：
  ```json
  "wechat_enabled": true   // 启用微信功能
  "wechat_enabled": false  // 禁用微信功能
  ```

#### wechat_path
- **说明**：微信程序完整路径
- **类型**：字符串
- **默认值**：`""`（空字符串表示自动查找）
- **格式**：
  - Windows：使用双反斜杠 `\\` 或正斜杠 `/`
  - 路径必须指向 WeChat.exe
- **示例**：
  ```json
  // 留空自动查找
  "wechat_path": ""
  
  // Windows 路径（双反斜杠）
  "wechat_path": "C:\\Program Files\\Tencent\\WeChat\\WeChat.exe"
  
  // Windows 路径（正斜杠）
  "wechat_path": "C:/Program Files/Tencent/WeChat/WeChat.exe"
  
  // 你的实际路径
  "wechat_path": "D:\\software\\Weixin\\Weixin.exe"
  ```
- **如何获取**：
  1. 运行工具：`python find_wechat.py`
  2. 或手动查找：开始菜单 → 微信 → 右键 → 打开文件位置

---

## 🔧 完整配置示例

### 本地开发配置

```json
{
  "monitor_interval": 5,
  "ocr_engine": "paddleocr",
  "ocr_language": "chi_sim+eng",
  "similarity_threshold": 0.85,
  "screenshot_retention_days": 3,
  "screenshot_limit": 50,
  "capture_region": null,
  "keywords": ["测试", "违规"],
  "reference_images": [],
  "auto_start_monitoring": false,
  "backend_url": "http://localhost:8000",
  "paddleocr_service_url": "http://localhost:5000",
  "wechat_enabled": false,
  "wechat_path": ""
}
```

### 生产环境配置

```json
{
  "monitor_interval": 60,
  "ocr_engine": "paddleocr",
  "ocr_language": "chi_sim+eng",
  "similarity_threshold": 0.85,
  "screenshot_retention_days": 7,
  "screenshot_limit": 100,
  "capture_region": null,
  "keywords": ["违规通知", "敏感内容", "警告"],
  "reference_images": [
    "screenshots/ref1.png",
    "screenshots/ref2.png"
  ],
  "auto_start_monitoring": true,
  "backend_url": "http://localhost:8000",
  "paddleocr_service_url": "http://localhost:5000",
  "wechat_enabled": true,
  "wechat_path": "C:/Program Files/Tencent/WeChat/WeChat.exe"
}
```

### 远程服务配置

```json
{
  "monitor_interval": 60,
  "ocr_engine": "paddleocr",
  "ocr_language": "chi_sim+eng",
  "similarity_threshold": 0.85,
  "screenshot_retention_days": 7,
  "screenshot_limit": 100,
  "capture_region": null,
  "keywords": ["违规"],
  "reference_images": [],
  "auto_start_monitoring": false,
  "backend_url": "https://api.example.com",
  "paddleocr_service_url": "http://192.168.1.100:5000",
  "wechat_enabled": false,
  "wechat_path": ""
}
```

---

## 💡 配置技巧

### 1. 修改服务端口

如果 5000 端口被占用：

**步骤 1**：修改服务端（`paddleocr_service/server.py`）
```python
uvicorn.run(
    app,
    host="127.0.0.1",
    port=8888,  # 改为其他端口
    log_level="info"
)
```

**步骤 2**：修改客户端配置（`config/config.json`）
```json
{
  "paddleocr_service_url": "http://localhost:8888"
}
```

### 2. 使用远程 OCR 服务

**服务端**（服务器上）：
```python
# paddleocr_service/server.py
uvicorn.run(
    app,
    host="0.0.0.0",  # 允许远程访问
    port=5000
)
```

**客户端**（本地）：
```json
{
  "paddleocr_service_url": "http://192.168.1.100:5000"
}
```

### 3. 自动查找微信

```bash
python find_wechat.py
```

会自动更新配置文件。

### 4. 备份配置

```bash
# 备份当前配置
copy config\config.json config\config.backup.json

# 恢复配置
copy config\config.backup.json config\config.json
```

### 5. 重置配置

删除 `config/config.json`，应用会自动创建默认配置。

---

## 🔍 验证配置

### 检查配置格式

```bash
python -m json.tool config\config.json
```

如果配置正确，会输出格式化的 JSON。

### 测试 OCR 服务连接

```bash
# 测试服务
python test_paddleocr_service.py

# 或浏览器访问
http://localhost:5000/docs
```

### 测试微信路径

运行应用，查看日志：
```bash
# 日志文件
type logs\app.log | findstr /i "wechat"
```

---

## ⚠️ 常见错误

### 1. JSON 格式错误

```json
// ❌ 错误：最后一项有逗号
{
  "key": "value",
}

// ✅ 正确：最后一项无逗号
{
  "key": "value"
}
```

### 2. 路径格式错误

```json
// ❌ 错误：单反斜杠
"wechat_path": "C:\Program Files\WeChat\WeChat.exe"

// ✅ 正确：双反斜杠或正斜杠
"wechat_path": "C:\\Program Files\\WeChat\\WeChat.exe"
"wechat_path": "C:/Program Files/WeChat/WeChat.exe"
```

### 3. URL 格式错误

```json
// ❌ 错误：缺少协议
"paddleocr_service_url": "localhost:5000"

// ✅ 正确：包含协议
"paddleocr_service_url": "http://localhost:5000"
```

---

## 📚 相关文档

- [快速修复指南](QUICK_FIX_GUIDE.md) - 常见问题
- [微信故障排查](WECHAT_TROUBLESHOOTING.md) - 微信配置
- [PaddleOCR 服务](QUICK_START_STANDALONE.md) - 服务配置
- [完整示例](../config/config.example.json) - 配置模板

---

## 💬 需要帮助？

1. 查看示例配置：`config/config.example.json`
2. 运行自动配置工具：`python find_wechat.py`
3. 查看日志：`logs/app.log`
4. 提交 Issue 附上配置文件（隐藏敏感信息）

---

记住：
- ✅ 修改配置后需要**重启应用**
- ✅ 修改服务端口需要**同步修改客户端配置**
- ✅ 路径使用**双反斜杠或正斜杠**
- ✅ JSON 最后一项**不要逗号**

配置愉快！🚀
