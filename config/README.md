# 配置目录说明

## 📁 文件说明

- `config.json` - 主配置文件（自动生成或用户编辑）
- `config.example.json` - 配置示例文件（参考用）

---

## ⚡ 快速配置

### 方法 1：自动配置（推荐）

应用首次运行会自动创建默认配置。

### 方法 2：从示例复制

```bash
copy config.example.json config.json
```

然后编辑 `config.json` 修改你需要的值。

### 方法 3：手动创建

创建 `config.json`，最小配置：

```json
{
  "paddleocr_service_url": "http://localhost:5000"
}
```

其他配置会使用默认值。

---

## 🔧 关键配置项

### 必须配置

```json
{
  "paddleocr_service_url": "http://localhost:5000"
}
```

如果使用 PaddleOCR，必须配置服务地址。

### 微信按钮配置 WeChat Button Configuration

应用需要识别微信通话按钮。请确保：

1. **按钮图片已准备**
   ```
   resources/wechat/
   ├── call_button.png          # 默认（必需）
   ├── call_button_win.png      # Windows 版本（推荐）
   └── call_button_mac.png      # Mac 版本（推荐）
   ```

2. **如何获取按钮图片**
   - 运行 `python capture_button.py` 自动截取
   - 或手动截图保存到上述路径
   - 详见：`WECHAT_BUTTON_QUICK_FIX.md`

3. **应用会自动**
   - 检测所有可用的按钮图片
   - 依次尝试匹配（支持多个版本）
   - 使用多个置信度级别（0.8/0.7/0.6）

### 推荐配置

```json
{
  "ocr_engine": "paddleocr",
  "paddleocr_service_url": "http://localhost:5000",
  "wechat_enabled": false
}
```

### 完整配置

参考 `config.example.json` 或查看 [配置指南](../CONFIG_GUIDE.md)。

---

## ✅ 配置检查清单

### 基础配置
- [ ] `config.json` 文件存在
- [ ] JSON 格式正确（无语法错误）
- [ ] `ocr_engine` 已设置（paddleocr 或 pytesseract）

### PaddleOCR 配置
- [ ] `paddleocr_service_url` 已配置
- [ ] 服务地址格式正确（包含 http:// 和端口）
- [ ] 服务已启动（访问 {url}/docs 验证）

### 微信配置（可选）
- [ ] `wechat_enabled` 已设置（true/false）
- [ ] 如果启用，`wechat_path` 已配置
- [ ] 路径使用正确格式（双反斜杠或正斜杠）
- [ ] 路径指向的文件存在

---

## 🔍 验证配置

### 1. 检查 JSON 格式

```bash
python -m json.tool config.json
```

无错误表示格式正确。

### 2. 测试 OCR 服务连接

```bash
# 运行测试
python test_paddleocr_service.py

# 或浏览器访问
http://localhost:5000/docs
```

### 3. 查看应用日志

```bash
# 启动应用
python src/main.py

# 查看日志
type logs\app.log
```

---

## 🐛 常见问题

### 配置不生效？

1. 确保修改的是 `config.json`（不是 `config.example.json`）
2. 重启应用（配置在启动时加载）
3. 检查日志是否有错误

### JSON 格式错误？

常见错误：
- 最后一项多了逗号
- 路径使用单反斜杠
- 引号不匹配

使用工具验证：
```bash
python -m json.tool config.json
```

### 找不到配置文件？

应用会在以下位置查找：
1. `config/config.json`（项目目录）
2. 如果不存在，使用默认配置

---

## 📚 详细文档

完整的配置说明请查看：**[CONFIG_GUIDE.md](../CONFIG_GUIDE.md)**

包含：
- 📝 所有配置项详细说明
- 💡 配置示例
- 🔧 高级配置技巧
- ⚠️ 常见错误和解决方案

---

## 💬 需要帮助？

1. 查看 [CONFIG_GUIDE.md](../CONFIG_GUIDE.md)
2. 查看 [QUICK_FIX_GUIDE.md](../QUICK_FIX_GUIDE.md)
3. 查看日志：`logs/app.log`
4. 提交 Issue

---

**提示**：修改配置后记得重启应用！
