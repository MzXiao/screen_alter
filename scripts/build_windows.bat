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
:: Added --noconfirm to avoid prompts
pyinstaller --noconfirm ScreenAlter.spec

echo Main Application:
echo   Location: dist\星联助手\星联助手.exe
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

:: Ensure config and resources are copied to dist directory
:: This acts as a fail-safe if PyInstaller's --add-data fails
echo.
echo Copying configuration and resource files...
if not exist dist\星联助手 mkdir dist\星联助手
xcopy /E /I /Y config dist\星联助手\config
xcopy /E /I /Y resources dist\星联助手\resources
xcopy /E /I /Y docs dist\星联助手\docs

:: Only pause if not running in CI
if "%GITHUB_ACTIONS%"=="" pause
