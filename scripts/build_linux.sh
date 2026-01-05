#!/bin/bash

# Linux Build Script for Screen Alter
echo "Building Screen Alter for Linux..."

# Install dependencies
pip install -r requirements.txt

# Build with PyInstaller
pyinstaller --noconsole --onedir \
    --name "ScreenAlter" \
    --add-data "src/resources:resources" \
    --add-data "src/config:config" \
    src/main.py

echo "Build complete. Check the dist/ScreenAlter directory."
echo "Note: On Linux, users may need to install libgl1-mesa-glx for PaddleOCR."
