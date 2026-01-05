@echo off
echo Building Screen Alter for Windows...

:: Install dependencies
pip install -r requirements.txt

:: Build with PyInstaller
pyinstaller --noconsole --onedir ^
    --name "ScreenAlter" ^
    --add-data "src/resources;resources" ^
    --add-data "src/config;config" ^
    --icon "src/resources/app_icon.ico" ^
    src/main.py

echo Build complete. Check the dist/ScreenAlter directory.
pause
