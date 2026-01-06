"""
Setup script for packaging the application.
Supports both py2app (macOS) and PyInstaller (Windows/macOS).
"""

from setuptools import setup

APP = ['src/main.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': False,
    'packages': [
        'PyQt5',
        'PIL',
        'mss',
        'pytesseract',
        'imagehash',
        'itchat',
        'pystray',
        'bcrypt',
    ],
    'iconfile': 'resources/icons/app.icns',  # Create this icon file
    'plist': {
        'CFBundleName': 'Screen Monitor',
        'CFBundleDisplayName': 'Screen Monitor',
        'CFBundleGetInfoString': "Screen monitoring and alert application",
        'CFBundleIdentifier': "com.screenmonitor.app",
        'CFBundleVersion': "1.0.0",
        'CFBundleShortVersionString': "1.0.0",
        'NSHumanReadableCopyright': "Copyright © 2024",
        'NSHighResolutionCapable': True,
    }
}

setup(
    name='ScreenMonitor',
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
