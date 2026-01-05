@echo off
echo ========================================
echo Building Screen Alter for Windows
echo (Without PaddleOCR - C/S Architecture)
echo ========================================
echo.

:: Activate virtual environment if it exists
if exist venv\Scripts\activate.bat (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
)

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

:: Build with PyInstaller using spec file
echo.
echo Building with PyInstaller...
echo (PaddleOCR excluded - using C/S mode)
pyinstaller ScreenAlter.spec

echo.
echo ========================================
echo Build complete!
echo ========================================
echo.
echo Main Application:
echo   Location: dist\ScreenAlter\ScreenAlter.exe
echo   Size: ~50MB (without PaddleOCR)
echo.
echo PaddleOCR Service (Optional):
echo   Build separately: paddleocr_service\build_service.bat
echo   Size: ~500MB
echo.
echo To use PaddleOCR:
echo   1. Run: paddleocr_service\server.py
echo   2. Or: paddleocr_service\dist\PaddleOCRService.exe
echo.
echo To use Tesseract:
echo   1. Install Tesseract OCR
echo   2. Select "pytesseract" in app settings
echo.
pause
