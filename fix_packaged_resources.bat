@echo off
REM 修复打包后缺失的资源文件
REM Fix missing resources in packaged application

echo ============================================================
echo 修复打包后的资源文件
echo Fix Packaged Resources
echo ============================================================
echo.

if not exist "dist\ScreenAlter" (
    echo ❌ 错误: dist\ScreenAlter 目录不存在
    echo ❌ Error: dist\ScreenAlter directory does not exist
    echo.
    echo 请先运行打包命令: pyinstaller ScreenAlter.spec
    echo Please run build first: pyinstaller ScreenAlter.spec
    pause
    exit /b 1
)

echo [1/3] 检查资源目录...
if not exist "dist\ScreenAlter\resources" (
    echo 创建 resources 目录...
    mkdir "dist\ScreenAlter\resources"
)

if not exist "dist\ScreenAlter\resources\wechat" (
    echo 创建 resources\wechat 目录...
    mkdir "dist\ScreenAlter\resources\wechat"
)

if not exist "dist\ScreenAlter\resources\icons" (
    echo 创建 resources\icons 目录...
    mkdir "dist\ScreenAlter\resources\icons"
)
echo ✅ 资源目录已准备
echo.

echo [2/3] 复制资源文件...
echo 复制微信按钮图片...
copy /Y "resources\wechat\*.png" "dist\ScreenAlter\resources\wechat\" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  微信按钮图片复制失败或不存在
) else (
    echo ✅ 微信按钮图片已复制
)

echo 复制应用图标...
copy /Y "resources\icons\*.ico" "dist\ScreenAlter\resources\icons\" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  应用图标复制失败或不存在
) else (
    echo ✅ 应用图标已复制
)
echo.

echo [3/3] 验证资源文件...
echo.
echo 微信按钮图片:
dir /b "dist\ScreenAlter\resources\wechat\*.png" 2>nul
if errorlevel 1 (
    echo   ❌ 无按钮图片
) else (
    echo   ✅ 已找到
)

echo.
echo 配置文件:
if exist "dist\ScreenAlter\config\config.json" (
    echo   ✅ config.json 存在
) else (
    echo   ⚠️  config.json 不存在
    if exist "config\config.json" (
        echo   正在复制...
        copy /Y "config\config.json" "dist\ScreenAlter\config\" >nul
        echo   ✅ 已复制
    )
)

echo.
echo ============================================================
echo ✅ 资源文件修复完成！
echo ✅ Resources fixed!
echo ============================================================
echo.
echo 现在可以运行应用: dist\ScreenAlter\ScreenAlter.exe
echo You can now run: dist\ScreenAlter\ScreenAlter.exe
echo.
pause
