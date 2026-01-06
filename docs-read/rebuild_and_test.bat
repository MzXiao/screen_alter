@echo off
REM 重新打包并测试微信激活功能
REM Rebuild and test WeChat activation

echo ============================================================
echo 重新打包并测试 WeChat 激活功能
echo Rebuild and Test WeChat Activation
echo ============================================================
echo.

REM 步骤 1: 清理旧文件
echo [1/6] 清理旧的打包文件...
echo [1/6] Cleaning old build files...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
echo ✅ 清理完成
echo.

REM 步骤 2: 重新打包
echo [2/6] 重新打包应用...
echo [2/6] Rebuilding application...
call venv\Scripts\activate.bat
pyinstaller ScreenAlter.spec
if errorlevel 1 (
    echo ❌ 打包失败！
    echo ❌ Build failed!
    pause
    exit /b 1
)
echo ✅ 打包完成
echo.

REM 步骤 3: 修复资源文件
echo [3/6] 修复资源文件...
echo [3/6] Fixing resources...
call fix_packaged_resources.bat
echo.

REM 步骤 3.5: 复制诊断工具
echo [3.5/6] 复制诊断工具...
echo [3.5/6] Copying diagnostic tool...
copy diagnose_wechat.py dist\ScreenAlter\
echo ✅ 复制完成
echo.

REM 步骤 4: 运行诊断
echo [4/6] 运行诊断工具...
echo [4/6] Running diagnostic tool...
cd dist\ScreenAlter
python diagnose_wechat.py
cd ..\..
echo.

REM 步骤 5: 显示诊断结果
echo [5/6] 诊断结果 Diagnostic Results:
echo ============================================================
type dist\ScreenAlter\wechat_diagnosis.log | findstr /C:"✅" /C:"❌" /C:"⚠️" /C:"SUMMARY"
echo ============================================================
echo.

REM 步骤 6: 询问是否运行应用
echo [6/6] 是否运行打包后的应用？
echo [6/6] Run packaged application?
echo.
choice /C YN /M "运行应用 (Y=是/Yes, N=否/No)"
if errorlevel 2 goto end
if errorlevel 1 goto run_app

:run_app
echo.
echo 启动应用...
echo Starting application...
cd dist\ScreenAlter
start ScreenAlter.exe
cd ..\..

:end
echo.
echo ============================================================
echo 完成！ Done!
echo.
echo 查看详细日志 View detailed logs:
echo   - dist\ScreenAlter\wechat_diagnosis.log (诊断日志)
echo   - dist\ScreenAlter\logs\app.log (应用日志)
echo ============================================================
pause
