#!/usr/bin/env python3
"""
Simple Windows build script without Chinese characters
"""

import subprocess
import sys
import os
import platform
from pathlib import Path

def main():
    """Main function"""
    print("=== Building Windows executable ===")
    
    # Check if running on Windows (for GitHub Actions)
    print(f"Current OS: {platform.system()}")
    
    # PyInstaller command for Windows
    cmd = [
        'pyinstaller',
        '--onefile',
        '--windowed',
        '--name=VintedInventoryManager',
        '--distpath=dist',
        '--workpath=build',
        '--specpath=.',
        '--add-data=resources;resources',
        '--hidden-import=tkinter',
        '--hidden-import=selenium',
        '--hidden-import=requests',
        '--hidden-import=beautifulsoup4',
        '--hidden-import=urllib3',
        '--hidden-import=certifi',
        'src/main.py'
    ]
    
    try:
        print("Starting build process...")
        result = subprocess.run(cmd, check=True)
        print("Build successful!")
        
        # Check if exe file was created
        exe_path = Path('dist/VintedInventoryManager.exe')
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"Generated file: {exe_path}")
            print(f"File size: {size_mb:.1f} MB")

            # Rename to Chinese name for distribution
            chinese_name = Path('dist/Vinted 库存宝.exe')
            try:
                exe_path.rename(chinese_name)
                print(f"Renamed to: {chinese_name}")
                return True
            except Exception as e:
                print(f"Warning: Could not rename to Chinese name: {e}")
                print("Using English name instead")
                return True
        else:
            print("ERROR: .exe file not found")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"Build failed with exit code: {e.returncode}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
