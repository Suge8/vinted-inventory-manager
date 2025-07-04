#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Windows构建脚本 - 简化版
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def clean_build_dirs():
    """清理构建目录"""
    dirs_to_clean = ['build', 'dist']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"已清理目录: {dir_name}")

def build_windows():
    """构建Windows .exe文件"""
    print("=== Vinted 库存宝 - Windows构建脚本 ===")

    clean_build_dirs()

    print("开始构建Windows .exe文件...")

    # 确保图标存在
    if not Path('assets/icon.ico').exists():
        print("⚠️ 图标文件不存在，将使用默认图标")

    # 图标路径
    icon_path = Path('assets/icon.ico')
    icon_arg = f'--icon={icon_path}' if icon_path.exists() else ''

    # PyInstaller命令
    cmd = [
        'pyinstaller',
        '--onefile',
        '--windowed',
        '--name=Vinted 库存宝',
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
        'src/main.py'
    ]

    # 添加图标（如果存在）
    if icon_arg:
        cmd.insert(-1, icon_arg)

    try:
        print("执行构建命令...")
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ 构建成功!")

        # 检查生成的文件
        exe_path = Path('dist/Vinted 库存宝.exe')

        if exe_path.exists():
            # 计算.exe文件大小
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"📱 生成的.exe文件: {exe_path}")
            print(f"📏 文件大小: {size_mb:.1f} MB")
        else:
            print("❌ 未找到生成的.exe文件")
            return False

    except subprocess.CalledProcessError as e:
        print(f"❌ 构建失败: {e}")
        print("错误输出:", e.stderr)
        return False
    except Exception as e:
        print(f"❌ 构建过程中出错: {e}")
        return False

    print("\n🎉 构建完成！")
    print(f"📁 输出文件: dist/Vinted 库存宝.exe")
    print("💡 可以直接双击运行")
    print("=== 构建成功完成 ===")
    return True

if __name__ == "__main__":
    success = build_windows()
    sys.exit(0 if success else 1)
