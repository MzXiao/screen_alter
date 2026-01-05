# 更新日志

## [v2.0.5] - 2026-01-06

### ⚡ 优化改进

#### 简化微信查找逻辑
- ✅ **优化**：`find_wechat.py` 只使用最实用的两种方法
  1. 配置文件优先 - 从 `config.json` 读取
  2. 常见路径查找 - 扫描标准安装位置
- ✅ **移除**：复杂的注册表查找、目录搜索、进程查找
- ✅ **同步**：主应用（`gui_alert.py`）使用相同逻辑
- ✅ **效果**：更快、更简洁、更可靠

**优势**：
- 启动更快（减少不必要的搜索）
- 逻辑更清晰（易于维护）
- 成功率更高（聚焦最常用场景）

---

## [v2.0.4] - 2026-01-06

### 📝 文档更新

#### 新增配置文档
- ✅ **新增**：`CONFIG_GUIDE.md` - 完整的配置文件说明
- ✅ **新增**：`config/README.md` - 配置目录说明
- ✅ **新增**：`config/config.example.json` - 配置示例文件
- ✅ **说明**：详细解释所有配置项，包含示例和最佳实践

#### 主要配置项说明
- `paddleocr_service_url` - PaddleOCR 服务地址（**可配置端口**）⭐
- `wechat_enabled` - 微信功能开关
- `wechat_path` - 微信程序路径
- 所有其他配置项的详细说明

**使用说明**：[CONFIG_GUIDE.md](CONFIG_GUIDE.md)

---

## [v2.0.3] - 2026-01-06

### ✨ 新功能

#### 微信路径查找工具
- ✅ **新增**：`find_wechat.py` 自动查找微信工具
- ✅ **功能**：
  - 从 Windows 注册表查找
  - 搜索常见安装目录
  - 查找正在运行的进程
  - 自动保存到配置文件
- ✅ **配置**：支持手动配置微信路径和启用/禁用

**使用方法**：
```bash
python find_wechat.py
```

---

## [v2.0.2] - 2026-01-06

### 🐛 Bug 修复

#### 修复 Windows 微信启动问题
- ✅ **问题**：`start wechat` 命令在 Windows 上不存在
- ✅ **修复**：
  - 从配置文件读取微信路径
  - 从 Windows 注册表查找
  - 搜索常见安装路径
  - 搜索 Program Files 目录
- ✅ **增强**：添加多种启动方法和详细日志
- ✅ **文档**：新增 `WECHAT_TROUBLESHOOTING.md` 微信故障排查指南

**详细说明**：[WECHAT_TROUBLESHOOTING.md](WECHAT_TROUBLESHOOTING.md)

**影响**：
- 修复前：Windows 启动微信失败，提示"找不到文件 wechat"
- 修复后：智能查找微信路径，支持手动配置，优雅降级

**注意**：微信功能是可选的，不影响核心监控功能

---

## [v2.0.1] - 2026-01-06

### 🐛 Bug 修复

#### 修复 HTTP 400 错误
- ✅ **服务端**：添加 `Form()` 声明，正确接收 multipart/form-data 参数
- ✅ **客户端**：增强日志，显示详细的发送和接收信息
- ✅ **测试**：新增 `test_paddleocr_service.py` 自动化测试脚本

**详细说明**：[FIX_HTTP_400.md](FIX_HTTP_400.md)

**影响**：
- 修复前：关键词检测总是返回 400 错误
- 修复后：关键词正确传输，检测正常工作

---

## [v2.0.0] - 2026-01-06

### 🎉 重大变更：迁移到 C/S 架构

#### 新增
- ✅ **PaddleOCR 独立服务**：`paddleocr_service/`
  - FastAPI HTTP 服务
  - 完整的 API 文档（Swagger UI）
  - 独立打包脚本
- ✅ **HTTP 客户端**：`src/monitor/paddle_ocr_client.py`
- ✅ **架构文档**：
  - `ARCHITECTURE_CS_MODE.md` - 架构详细说明
  - `MIGRATION_TO_CS.md` - 迁移指南
  - `QUICK_START_STANDALONE.md` - 快速开始
  - `TROUBLESHOOTING.md` - 故障排查

#### 删除
- ❌ 移除本地 PaddleOCR：`src/monitor/paddle_ocr_detector.py`
- ❌ 移除 PaddleOCR 依赖：从 `requirements.txt`
- ❌ 移除 PaddleOCR 打包：从 `ScreenAlter.spec`

#### 优化
- ✅ **体积减少 90%**：500MB → 50MB
- ✅ **启动速度提升 80%**：15秒 → 3秒
- ✅ **打包时间减少 80%**：5分钟 → 1分钟
- ✅ **灵活部署**：支持本地/远程/云端

#### 修复
- 🐛 HTTP 400 错误：添加关键词验证
- 🐛 错误日志不详细：增强错误信息
- 🐛 服务端日志不足：添加详细日志

---

## [v1.0.0] - 2025-12-XX

### 初始版本

#### 功能
- ✅ 用户认证系统
- ✅ 屏幕监控和截图
- ✅ OCR 文字识别（嵌入式 PaddleOCR）
- ✅ 图像相似度检测
- ✅ 关键词匹配
- ✅ GUI 报警
- ✅ 系统托盘

#### 问题
- ❌ 打包体积大（500MB）
- ❌ 启动缓慢
- ❌ 打包困难
- ❌ 无法独立更新 OCR

---

## 迁移说明

### 从 v1.x 升级到 v2.0

#### 对于开发者

1. 更新代码：
```bash
git pull origin main
pip install -r requirements.txt
```

2. 启动服务：
```bash
cd paddleocr_service
pip install -r requirements.txt
python server.py
```

3. 运行应用：
```bash
python src/main.py
```

#### 对于用户

1. **卸载旧版本**：
   - 删除 ScreenAlter.exe (500MB)

2. **安装新版本**：
   - 主应用：ScreenAlter.exe (50MB)
   - OCR 服务：PaddleOCRService.exe (500MB，可选)

3. **配置 OCR**：
   - 选择 PaddleOCR：启动 PaddleOCRService.exe
   - 或选择 Tesseract：安装并配置 PATH

#### 不兼容变更

- ❌ 配置项 `paddleocr_use_service` 已废弃
- ❌ 本地 PaddleOCR 模式已移除
- ❌ 需要单独启动 OCR 服务

#### 数据兼容

- ✅ 数据库结构未变化
- ✅ 配置文件自动迁移
- ✅ 用户数据完全兼容

---

## 技术细节

### v2.0 架构

```
主应用 (50MB)          OCR 服务 (500MB)
├── GUI                ├── PaddleOCR
├── 业务逻辑            ├── FastAPI
└── HTTP 客户端 ←────→  └── HTTP 服务
```

### 核心改进

1. **分离关注点**：
   - 主应用：UI + 业务逻辑
   - OCR 服务：图像识别

2. **HTTP API**：
   - RESTful 接口
   - JSON 数据交换
   - Swagger 文档

3. **灵活部署**：
   - 本地服务
   - 远程服务器
   - 云端部署

4. **独立更新**：
   - 主应用和服务分别打包
   - 可独立升级

---

## 未来计划

### v2.1 (计划中)

- [ ] Docker 支持
- [ ] 负载均衡
- [ ] GPU 加速优化
- [ ] 批量 OCR 接口

### v2.2 (计划中)

- [ ] 微服务架构
- [ ] 云端部署指南
- [ ] 性能监控
- [ ] 缓存优化

### v3.0 (远期)

- [ ] Web 界面
- [ ] 移动端支持
- [ ] 多语言识别
- [ ] 实时流处理

---

## 贡献者

感谢所有贡献者！

---

## 许可证

本项目仅供学习和个人使用。

---

## 链接

- [架构说明](ARCHITECTURE_CS_MODE.md)
- [迁移指南](MIGRATION_TO_CS.md)
- [快速开始](QUICK_START_STANDALONE.md)
- [故障排查](TROUBLESHOOTING.md)
- [打包指南](PACKAGING_GUIDE.md)
