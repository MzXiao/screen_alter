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
cd /Users/xiao/work/partner/screen_alter/src
python main.py
```

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

## 配置文件位置

应用数据存储在以下位置:

- **macOS**: `~/Library/Application Support/ScreenMonitor/`
- **Windows**: `C:\Users\<用户名>\AppData\Local\ScreenMonitor\`

包含:
- `screen_monitor.db` - 数据库文件
- `screenshots/` - 截图存储目录
- `logs/` - 应用日志
- `config.json` - 配置文件

## 常见问题

### OCR识别不准确

1. 确保已安装Tesseract OCR及中文语言包
2. 尝试调整屏幕分辨率或文字大小
3. 考虑使用EasyOCR（更准确但更慢）

### 微信登录失败

1. 确保已安装itchat: `pip install itchat`
2. 检查网络连接
3. 尝试重新扫码登录
4. 注意：频繁使用可能导致账号被限制

### 截图功能不工作

1. 检查应用是否有屏幕录制权限（macOS）
2. 确保已安装mss库: `pip install mss`
3. 查看日志文件了解详细错误信息

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
