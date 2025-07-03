#!/usr/bin/env python3
"""
Docker内Windows构建脚本
在Linux容器中使用Wine构建Windows .exe文件
"""

import subprocess
import sys
import os
from pathlib import Path

def build_windows_exe():
    """在Docker容器中构建Windows .exe文件"""
    print("=== Docker Windows构建 ===")
    
    # PyInstaller命令 - Windows配置
    cmd = [
        'pyinstaller',
        '--onefile',
        '--windowed',
        '--name=VintedInventoryManager',
        '--distpath=dist',
        '--workpath=build',
        '--specpath=.',
        '--add-data=resources;resources',  # Windows路径分隔符
        '--hidden-import=tkinter',
        '--hidden-import=selenium',
        '--hidden-import=requests',
        '--hidden-import=beautifulsoup4',
        '--hidden-import=urllib3',
        '--hidden-import=certifi',
        'src/main.py'
    ]
    
    try:
        print("开始构建Windows .exe文件...")
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("构建成功!")
        
        # 检查生成的文件
        exe_path = Path('dist/VintedInventoryManager.exe')
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"✅ 生成文件: {exe_path}")
            print(f"   文件大小: {size_mb:.1f} MB")
            return True
        else:
            print("❌ 未找到生成的.exe文件")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ 构建失败: {e}")
        print(f"错误输出: {e.stderr}")
        return False

if __name__ == "__main__":
    success = build_windows_exe()
    sys.exit(0 if success else 1)
