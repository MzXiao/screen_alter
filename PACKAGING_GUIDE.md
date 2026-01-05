# Windows 打包指南（C/S 架构）

## 架构说明

本应用采用 **C/S 架构**，主应用和 PaddleOCR 服务分离：

```
┌──────────────────┐          ┌─────────────────────┐
│  ScreenAlter.exe │  ←────→  │ PaddleOCRService    │
│  主应用 (50MB)    │  HTTP   │ OCR 服务 (500MB)    │
└──────────────────┘          └─────────────────────┘
```

**优势**：
- ✅ 主应用体积减少 90%（500MB → 50MB）
- ✅ 用户可选择安装 PaddleOCR 或 Tesseract
- ✅ OCR 服务可独立更新
- ✅ 多个应用可共享一个 OCR 服务

## 解决方案

### 1. 工作目录修复

**修改文件**: `src/main.py`

添加了动态路径配置，使程序无论从哪个目录运行都能找到模块：

```python
# Add src directory to Python path to support imports from any working directory
current_file = Path(__file__).resolve()
src_dir = current_file.parent
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))
```

### 2. PaddleOCR C/S 架构

**完全移除本地 PaddleOCR**：
- 删除 `src/monitor/paddle_ocr_detector.py`（本地调用）
- 只保留 `src/monitor/paddle_ocr_client.py`（HTTP 客户端）
- 从 `requirements.txt` 移除 paddleocr 依赖
- 从 `ScreenAlter.spec` 移除所有 PaddleOCR 打包配置

**新增独立服务**：
- `paddleocr_service/server.py` - FastAPI 服务
- `paddleocr_service/build_service.bat` - 服务打包脚本

## 打包步骤

### 第一步：打包主应用

#### 方法 1：使用批处理脚本（推荐）

```bash
scripts\build_windows.bat
```

#### 方法 2：手动打包

```bash
# 1. 激活虚拟环境
venv\Scripts\activate

# 2. 安装依赖
pip install -r requirements.txt
pip install pyinstaller

# 3. 清理旧的构建
rmdir /s /q build dist

# 4. 使用 spec 文件打包
pyinstaller ScreenAlter.spec
```

**生成文件**：
- `dist\ScreenAlter\ScreenAlter.exe` (约 50MB)

### 第二步：打包 PaddleOCR 服务（可选）

如果用户需要使用 PaddleOCR：

```bash
cd paddleocr_service
build_service.bat
```

**生成文件**：
- `paddleocr_service\dist\PaddleOCRService.exe` (约 500MB)

### 第三步：准备分发包

创建发布目录：

```
Release_v1.0/
├── ScreenAlter/
│   └── ScreenAlter.exe          # 主应用 (50MB) - 必需
├── PaddleOCRService.exe         # OCR 服务 (500MB) - 可选
├── start_service.bat            # 服务启动脚本
├── README.txt                   # 使用说明
└── 安装说明.txt                  # 中文说明
```

## 运行测试

### 测试打包后的程序

```bash
# 运行打包后的程序
dist\ScreenAlter\ScreenAlter.exe
```

## OCR 引擎选择

程序支持两种 OCR 引擎，**都需要单独安装或部署**：

### 选项 A：PaddleOCR 服务（推荐 - 高准确率）

**特点**：
- ✅ 高准确率（特别是中文）
- ✅ 支持倾斜、旋转文字
- ✅ 独立服务，可远程部署
- ❌ 服务体积大（500MB）

**安装**：
1. 打包服务：`cd paddleocr_service && build_service.bat`
2. 启动服务：`PaddleOCRService.exe`
3. 主应用会自动连接（默认 http://localhost:5000）

**或者开发模式**：
```bash
cd paddleocr_service
python server.py
```

### 选项 B：Tesseract OCR（轻量级）

**特点**：
- ✅ 轻量级、速度快
- ✅ 成熟稳定
- ❌ 需要用户单独安装
- ❌ 准确率略低于 PaddleOCR

**安装**：
1. 下载安装：https://github.com/UB-Mannheim/tesseract/wiki
2. 安装时勾选"Chinese (Simplified)"语言包
3. 添加到系统 PATH
4. 在程序中选择 OCR 引擎为 "pytesseract"

### 用户选择方案

分发时可以让用户选择：

```
请选择 OCR 引擎：
[ ] PaddleOCR（推荐）- 高准确率，需要 500MB
[ ] Tesseract - 轻量级，需要单独安装
[ ] 不使用 OCR - 仅图像检测
```

详细对比：**[OCR 引擎选择指南](docs/OCR_ENGINE_GUIDE.md)**

## 调试模式

当前 `ScreenAlter.spec` 中 `console=True`，这样可以看到详细的错误信息。

**发布版本前记得改为**：

```python
console=False,  # 无控制台窗口
```

## 从不同目录运行

现在支持以下运行方式：

```bash
# 从项目根目录
python src/main.py

# 从 src 目录
cd src
python main.py

# 打包后的程序
dist\ScreenAlter\ScreenAlter.exe
```

## 已知问题

### PaddleOCR 打包体积大

- PaddleOCR 包含大量模型文件，打包后体积会很大（可能超过 500MB）
- 如果对体积敏感，建议使用 pytesseract

### 首次运行慢

- PaddleOCR 首次初始化时需要下载模型文件
- 建议首次运行时保持网络连接

## 常见错误处理

### FileNotFoundError: paddleocr\tools\__init__.py

**已修复**：通过延迟导入和完整的包收集解决

### WARNING: No module named 'apted'

**说明**：这是 PaddleOCR 表格识别功能的依赖，但本应用只需要文字识别，不需要表格识别。

**已处理**：在 `ScreenAlter.spec` 中已排除表格相关模块，可以忽略此警告。

**如果需要表格识别**：
```bash
pip install apted attrdict openpyxl
```
然后从 `ScreenAlter.spec` 的 `excludes` 列表中移除 `'paddleocr.ppstructure'` 和 `'apted'`。

### ERROR: No module named 'scipy._cyutility'

**原因**：PaddleOCR 需要完整的 scipy 库，包括内部子模块。

**已修复**：
- 移除了 spec 文件中对 scipy 子模块的排除
- 添加了必要的 scipy hiddenimports

**解决方案**：重新打包即可。

```bash
rmdir /s /q build dist
scripts\build_windows.bat
```

### ModuleNotFoundError: No module named 'xxx'

**解决方案**：
1. 检查 `ScreenAlter.spec` 的 `hiddenimports` 列表
2. 添加缺失的模块名
3. 重新打包

### ImportError in packed executable

**解决方案**：
1. 使用 `console=True` 查看完整错误信息
2. 检查是否有动态导入的模块没有被包含
3. 在 spec 文件中使用 `collect_all()` 收集整个包

## 优化建议

### 减小打包体积

1. 排除不需要的包（已在 spec 中配置）：
```python
excludes=[
    'paddleocr.ppstructure',  # 表格识别（不需要）
    'paddleocr.ppstructure.table',
    'apted',  # 表格识别依赖
    'matplotlib',  # 图表库（不需要）
    'scipy.stats',  # 统计库（不需要）
    'scipy.ndimage',
]
```

2. 使用 UPX 压缩（已启用）：
```python
upx=True
```

3. 移除开发工具：
```python
excludes=['pytest', 'coverage', 'sphinx']
```

### 加快启动速度

1. 使用单文件模式（可选）：
```bash
pyinstaller --onefile ScreenAlter.spec
```

2. 预编译 Python 模块

## 参考资源

- [PyInstaller 文档](https://pyinstaller.org/en/stable/)
- [PaddleOCR 文档](https://github.com/PaddlePaddle/PaddleOCR)
- [Tesseract OCR 下载](https://github.com/UB-Mannheim/tesseract/wiki)
