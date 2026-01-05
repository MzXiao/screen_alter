@echo off
echo Building Screen Alter for Windows...

:: Activate virtual environment if it exists
if exist venv\Scripts\activate.bat (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
)

:: Install dependencies
echo Installing dependencies...
pip install -r requirements.txt
pip install pyinstaller

:: Clean previous builds
echo Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

:: Build with PyInstaller using spec file
echo Building with PyInstaller...
pyinstaller ScreenAlter.spec

echo.
echo ========================================
echo Build complete!
echo Executable location: dist\ScreenAlter\ScreenAlter.exe
echo ========================================
echo.
pause
