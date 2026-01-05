#!/bin/bash

# macOS Build Script for Screen Alter
# Requires: pyinstaller

echo "Building Screen Alter for macOS..."

# Install dependencies
pip install -r requirements.txt

# (Optional) Obfuscate code with PyArmor
# pip install pyarmor
# pyarmor gen -O dist/obfuscated src/main.py

# Clean previous builds
rm -rf build dist

# Build with PyInstaller
# --noconsole/--windowed: Hide terminal (App bundle)
# --onedir: Directory based (easier for resources)
# --add-data: Include necessary resources
pyinstaller --noconsole --onedir --windowed \
    --name "ScreenAlter" \
    --add-data "src/resources:resources" \
    --add-data "src/config:config" \
    --icon "src/resources/app_icon.icns" \
    --hidden-import "PyQt5.QtCore" \
    --hidden-import "PyQt5.QtGui" \
    --hidden-import "PyQt5.QtWidgets" \
    --hidden-import "paddleocr" \
    src/main.py

# Ensure config directory exists in the bundle (optional explicit check)
# cp -r src/config dist/ScreenAlter.app/Contents/Resources/

echo "Build complete. Check the dist/ScreenAlter directory."
