# Screen Monitor - 屏幕监控报警应用

一个跨平台的桌面屏幕监控应用，能够周期性地检测屏幕内容中的违规关键词，并通过微信进行实时报警。

## 功能特性

- ✅ **用户认证系统**: 基于SQLite的本地登录认证
- ✅ **跨平台支持**: Windows和macOS桌面应用
- ✅ **智能屏幕监控**: 周期性截屏并进行OCR文字识别
- ✅ **关键词检测**: 支持OCR文字识别和图像相似度对比
- ✅ **微信报警**: 检测到违规内容后通过微信消息提醒
- ✅ **系统托盘集成**: 后台运行，不干扰正常工作

## 系统要求

### 基础要求
- Python 3.13
- macOS 11.0+ 或 Windows 10/11

### OCR引擎 (二选一)
- **Tesseract OCR** (推荐): 需要单独安装
  - macOS: `brew install tesseract tesseract-lang`
  - Windows: 下载安装 [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki)
- **EasyOCR**: 通过pip自动安装，但速度较慢

## 安装步骤

### 1. 克隆项目

```bash
cd /Users/xiao/work/partner/screen_alter
```

### 2. 创建虚拟环境

```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# 或
venv\Scripts\activate  # Windows
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 安装Tesseract OCR (推荐)

**macOS:**
```bash
brew install tesseract tesseract-lang
```

**Windows:**
1. 下载安装程序: https://github.com/UB-Mannheim/tesseract/wiki
2. 安装时选择包含中文语言包
3. 将Tesseract添加到系统PATH

### 5. 运行应用

```bash
# 方式1: 从项目根目录运行（推荐）
python src/main.py

# 方式2: 从src目录运行
cd src
python main.py
```

### 5.1 测试 PaddleOCR 服务（可选）

如果使用 PaddleOCR，可以先测试服务是否正常：

```bash
# 确保服务已启动
cd paddleocr_service
python server.py

# 新开终端，运行测试
python test_paddleocr_service.py
```

应该看到所有测试通过：
```
✅ 健康检查: 通过
✅ OCR 识别: 通过
✅ 关键词检测: 通过
✅ 空关键词验证: 通过
```

### 6. 选择 OCR 引擎

本应用支持两种 OCR 引擎，需要单独安装：

#### 选项 A：PaddleOCR 服务（推荐 - 高准确率）

```bash
# 启动 PaddleOCR 服务
cd paddleocr_service
pip install -r requirements.txt
python server.py
```

详见：[PaddleOCR 独立服务快速开始](docs-read/QUICK_START_STANDALONE.md)

#### 选项 B：Tesseract OCR（轻量级）

下载安装：https://github.com/UB-Mannheim/tesseract/wiki
- 安装时勾选"Chinese (Simplified)"语言包
- 添加到系统 PATH

详见：[OCR 引擎对比指南](docs/OCR_ENGINE_GUIDE.md)

## 使用指南

### 首次使用

1. **注册账号**
   - 启动应用后，点击"注册新账号"
   - 输入用户名和密码（密码长度至少6个字符）
   - 注册成功后使用新账号登录

2. **配置监控**
   - 设置监控间隔（30秒、1分钟、5分钟等）
   - 添加要检测的关键词（如"直播间违规"）
   - 可选：上传参考图片进行图像相似度检测
   - 输入微信接收人（用户名或备注名）

3. **启动监控**
   - 点击"开始监控"按钮
   - 应用将按设定间隔截屏并检测
   - 检测到关键词或相似图片时自动报警

### 微信报警设置

> **注意**: 微信自动化功能可能不稳定，使用前请了解相关风险。

1. 首次使用需要扫码登录微信
2. 输入接收报警的微信好友用户名或备注名
3. 检测到违规内容时会自动发送消息和截图

### 系统托盘功能

应用最小化后会在系统托盘运行，右键托盘图标可以:
- 查看监控状态
- 打开控制面板
- 启动/停止监控
- 查看日志
- 退出应用

## 配置说明

### 配置文件位置

- **主配置**：`config/config.json`
- **配置说明**：查看 **[配置文件指南](docs-read/CONFIG_GUIDE.md)** 📝

### 主要配置项

```json
{
  "ocr_engine": "paddleocr",                    // OCR 引擎
  "paddleocr_service_url": "http://localhost:5000",  // PaddleOCR 服务地址 ⭐
  "wechat_enabled": false,                      // 是否启用微信
  "wechat_path": ""                             // 微信程序路径
}
```

**详细说明**：[CONFIG_GUIDE.md](docs-read/CONFIG_GUIDE.md)

### 数据存储位置

应用数据存储在项目根目录:

- `config/` - 配置文件
- `screen_monitor.db` - 数据库文件
- `screenshots/` - 截图存储目录
- `logs/` - 应用日志

## 常见问题

### 🚨 快速修复

遇到问题？查看 **[快速修复指南](docs-read/QUICK_FIX_GUIDE.md)** ⭐

### 无法连接 PaddleOCR 服务

1. 确保服务已启动：`cd paddleocr_service && python server.py`
2. 检查端口 5000 是否被占用
3. 浏览器访问 http://localhost:5000 验证服务

### OCR 识别不准确

1. **PaddleOCR**：准确率高，但需要启动服务
2. **Tesseract**：需要单独安装，轻量级
3. 调整屏幕分辨率或文字大小
4. 查看 [OCR 引擎对比](docs/OCR_ENGINE_GUIDE.md)

### HTTP 400 错误

```bash
# 测试服务
python test_paddleocr_service.py
```

详细说明：[FIX_HTTP_400.md](docs-read/FIX_HTTP_400.md)

### windows 找不到微信

```bash
# 自动查找并配置（简洁高效）
python find_wechat.py
```

工具会按顺序查找：
1. 配置文件（优先）
2. 常见安装路径

或禁用微信：`"wechat_enabled": false`

详细说明：[WECHAT_TROUBLESHOOTING.md](docs-read/WECHAT_TROUBLESHOOTING.md)

### 更多问题

- **[快速修复指南](docs-read/QUICK_FIX_GUIDE.md)** - 最常见问题 ⭐
- **[完整故障排查](docs-read/TROUBLESHOOTING.md)** - 所有已知问题

## 开发相关

### 项目结构

```
screen_alter/
├── src/
│   ├── auth/           # 认证模块
│   ├── database/       # 数据库模块
│   ├── monitor/        # 监控模块
│   ├── alert/          # 报警模块
│   ├── gui/            # 图形界面
│   ├── utils/          # 工具函数
│   ├── config.py       # 配置管理
│   └── main.py         # 应用入口
├── tests/              # 单元测试
├── docs/               # 文档
├── requirements.txt    # 依赖列表
└── README.md          # 本文件
```

### 运行测试

```bash
pytest tests/ -v
```

### 打包应用

**macOS:**
```bash
python setup.py py2app
```

**Windows:**
```bash
pyinstaller --onefile --windowed src/main.py
```

## 许可证

本项目仅供学习和个人使用。

## 免责声明

- 本应用使用的微信自动化功能可能违反微信服务条款
- 使用OCR和屏幕监控功能请遵守当地法律法规
- 作者不对使用本应用造成的任何后果负责

## 技术支持

如有问题，请查看:
- 产品文档: `docs/product_documentation.md`
- 实现计划: `docs/implementation_plan.md`
- 应用日志: `~/Library/Application Support/ScreenMonitor/logs/`
