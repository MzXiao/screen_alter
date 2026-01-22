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
    --name "星联助手" \
    --add-data "resources:resources" \
    --add-data "config:config" \
    --add-data "docs:docs" \
    --icon "resources/icons/app.ico" \
    --hidden-import "PyQt5.QtCore" \
    --hidden-import "PyQt5.QtGui" \
    --hidden-import "PyQt5.QtWidgets" \
    src/main.py

echo "Build complete. Check the dist/星联助手 directory."
