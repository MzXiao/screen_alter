@echo off
echo ========================================
echo Building PaddleOCR Service...
echo ========================================
echo.

:: Create virtual environment
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

:: Activate virtual environment
call venv\Scripts\activate

:: Install dependencies
echo.
echo Installing dependencies...
pip install -r requirements.txt
pip install pyinstaller

:: Clean previous builds
echo.
echo Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

:: Build with PyInstaller
echo.
echo Building executable...
pyinstaller --name PaddleOCRService ^
    --onefile ^
    --console ^
    --hidden-import=paddleocr ^
    --hidden-import=paddle ^
    --hidden-import=fastapi ^
    --hidden-import=uvicorn ^
    --collect-all paddleocr ^
    --collect-all paddle ^
    server.py

echo.
echo ========================================
echo Build complete!
echo Executable: dist\PaddleOCRService.exe
echo Size: ~500MB (includes PaddleOCR models)
echo ========================================
echo.
echo To run the service:
echo   dist\PaddleOCRService.exe
echo.
echo Service will be available at:
echo   http://localhost:5000
echo.
pause
