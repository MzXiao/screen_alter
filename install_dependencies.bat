@echo off
REM 安装依赖包 - 修复编码问题
REM Install Dependencies - Fix Encoding Issues

echo ============================================================
echo 安装 Python 依赖包
echo Installing Python Dependencies
echo ============================================================
echo.

REM 设置代码页为 UTF-8
echo [1/4] 设置编码为 UTF-8...
chcp 65001 > nul
echo ✅ 编码设置完成
echo.

REM 激活虚拟环境
echo [2/4] 激活虚拟环境...
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
    echo ✅ 虚拟环境已激活
) else (
    echo ⚠️  虚拟环境不存在，将使用全局 Python
)
echo.

REM 升级 pip
echo [3/4] 升级 pip...
python -m pip install --upgrade pip
echo.

REM 安装依赖
echo [4/4] 安装依赖包...
echo.

REM 设置环境变量强制使用 UTF-8
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8

REM 安装
pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo ============================================================
    echo ❌ 安装失败！
    echo ❌ Installation failed!
    echo ============================================================
    echo.
    echo 如果仍然有编码错误，请尝试：
    echo If still getting encoding errors, try:
    echo.
    echo 方法 1: 逐个安装
    echo Method 1: Install one by one
    echo    pip install PyQt5==5.15.11
    echo    pip install Pillow==10.4.0
    echo    ... (etc)
    echo.
    echo 方法 2: 使用清理后的 requirements.txt
    echo Method 2: Use cleaned requirements.txt
    echo    记事本打开 requirements.txt
    echo    另存为，编码选择 UTF-8 (不要选 UTF-8 BOM)
    echo.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo ✅ 安装成功！
echo ✅ Installation successful!
echo ============================================================
echo.
pause
