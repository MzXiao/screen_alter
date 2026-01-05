#!/bin/bash

# macOS Build Script for Screen Alter
# Requires: pyinstaller

echo "Building Screen Alter for macOS..."

# Install dependencies
pip install -r requirements.txt

# (Optional) Obfuscate code with PyArmor
# pip install pyarmor
# pyarmor gen -O dist/obfuscated src/main.py

# Build with PyInstaller
# --noconsole: Hide terminal
# --onedir: Easier for debugging, --onefile: Single executable
# --add-data: Include necessary resources
pyinstaller --noconsole --onedir \
    --name "ScreenAlter" \
    --add-data "src/resources:resources" \
    --add-data "src/config:config" \
    --hidden-import "PyQt5.QtCore" \
    --hidden-import "PyQt5.QtGui" \
    --hidden-import "PyQt5.QtWidgets" \
    --hidden-import "paddleocr" \
    src/main.py

echo "Build complete. Check the dist/ScreenAlter directory."
