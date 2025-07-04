#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Windows build script - simplified version
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def clean_build_dirs():
    """Clean build directories"""
    dirs_to_clean = ['build', 'dist']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"Cleaned directory: {dir_name}")

def build_windows():
    """Build Windows .exe file"""
    print("=== Vinted Inventory Manager - Windows Build Script ===")

    clean_build_dirs()

    print("Starting Windows .exe build...")

    # Ensure icon exists
    if not Path('assets/icon.ico').exists():
        print("Warning: Icon file not found, using default icon")

    # Icon path
    icon_path = Path('assets/icon.ico')
    icon_arg = f'--icon={icon_path}' if icon_path.exists() else ''

    # PyInstaller command - simplified to avoid missing files
    cmd = [
        'pyinstaller',
        '--onefile',
        '--windowed',
        '--name=Vinted 库存宝',  # Keep Chinese name for the executable
        '--add-data=src;src',
        '--add-data=assets;assets',
        '--hidden-import=tkinter',
        '--hidden-import=customtkinter',
        '--hidden-import=darkdetect',
        '--hidden-import=PIL',
        '--hidden-import=selenium',
        '--hidden-import=requests',
        '--hidden-import=beautifulsoup4',
        '--hidden-import=lxml',
        '--distpath=dist',
        '--workpath=build',
        '--specpath=.',
        'src/main.py'
    ]

    # Add version file if it exists
    if Path('version_info.txt').exists():
        cmd.insert(-1, '--version-file=version_info.txt')

    # Add icon if exists
    if icon_arg:
        cmd.insert(-1, icon_arg)

    try:
        print("Executing build command...")
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("Build successful!")

        # Check generated file - avoid Chinese characters in print
        exe_path = Path('dist/Vinted 库存宝.exe')

        if exe_path.exists():
            # Calculate .exe file size
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print("Generated .exe file successfully")
            print(f"File size: {size_mb:.1f} MB")
        else:
            print("ERROR: .exe file not found")
            return False

    except subprocess.CalledProcessError as e:
        print("Build failed with PyInstaller error")
        if e.stderr:
            # Avoid printing stderr that might contain Chinese characters
            print("Error occurred during build process")
        return False
    except Exception as e:
        print("Build process error occurred")
        return False

    print("\nBuild completed!")
    print("Output file: dist/Vinted [Chinese name].exe")
    print("Ready to run")
    print("=== Build Success ===")
    return True

if __name__ == "__main__":
    success = build_windows()
    sys.exit(0 if success else 1)
