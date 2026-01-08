# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path

block_cipher = None

# Base directory
base_dir = Path('.')

# Collect all data files
# Include all files from config and resources directories
datas = [
    ('config', 'config'),
    ('resources', 'resources'),
    ('docs', 'docs'),
]

# Hidden imports to ensure all modules are included
hiddenimports = [
    'config',
    'PyQt5',
    'PyQt5.QtCore',
    'PyQt5.QtGui',
    'PyQt5.QtWidgets',
    'PIL',
    'PIL.Image',
    'mss',
    'pytesseract',
    'imagehash',
    'bcrypt',
    'requests',  # For PaddleOCR HTTP client
    'sqlite3',
    'json',
    'logging',
    'ctypes',  # For Windows API calls
    'ctypes.wintypes',  # Windows types
    'pyautogui',  # Window activation fallback
    # OpenCV dependencies
    'cv2',
    'numpy',
]

a = Analysis(
    ['src/main.py'],
    pathex=['src'],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude PaddleOCR (now using standalone service)
        'paddleocr',
        'paddle',
        'paddlepaddle',
        # Exclude heavy dependencies not needed
        'matplotlib',
        'scipy',
        'numpy.distutils',
        'tkinter',
        'test',
        'unittest',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='ScreenAlter',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # Set to False to hide the console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='resources/icons/app.ico' if Path('resources/icons/app.ico').exists() else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='ScreenAlter',
)

