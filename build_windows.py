#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Windows专用构建脚本

此脚本专门用于在Windows系统上构建.exe文件。
与build.py功能相同，但针对Windows优化。
"""

import os
import sys
import shutil
import subprocess
import platform
from pathlib import Path


def clean_build_dirs():
    """清理构建目录"""
    dirs_to_clean = ['build', 'dist', '__pycache__']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"已清理目录: {dir_name}")


def build_windows_executable():
    """构建Windows可执行文件"""
    print("开始构建Windows .exe文件...")
    
    # 检查是否在Windows系统上运行
    if platform.system() != "Windows":
        print("错误: 此脚本只能在Windows系统上运行")
        print("当前系统:", platform.system())
        return False
    
    # PyInstaller 命令参数 - Windows专用配置
    cmd = [
        'pyinstaller',
        '--onefile',                    # 单文件模式
        '--windowed',                   # 无控制台窗口
        '--name=VintedInventoryManager', # 可执行文件名称
        '--distpath=dist',              # 输出目录
        '--workpath=build',             # 工作目录
        '--specpath=.',                 # spec文件位置
        '--add-data=resources;resources',  # Windows使用分号
        '--hidden-import=tkinter',      # 隐式导入
        '--hidden-import=selenium',
        '--hidden-import=requests',
        '--hidden-import=beautifulsoup4',
        '--hidden-import=urllib3',
        '--hidden-import=certifi',
        'src/main.py'                   # 主程序文件
    ]
    
    # 添加Windows图标
    icon_path = Path('resources/app_icon.ico')
    if icon_path.exists():
        cmd.extend(['--icon', str(icon_path)])
    
    # 添加Windows特定的优化参数
    cmd.extend([
        '--noupx',                      # 不使用UPX压缩
        '--clean',                      # 清理临时文件
    ])
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True, encoding='utf-8', errors='ignore')
        print("Windows .exe构建成功!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"构建失败: {e}")
        if e.stderr:
            print(f"错误输出: {e.stderr}")
        return False


def verify_executable():
    """验证生成的可执行文件"""
    exe_path = Path('dist/VintedInventoryManager.exe')
    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print(f"✅ 可执行文件生成成功: {exe_path}")
        print(f"   文件大小: {size_mb:.1f} MB")
        return True
    else:
        print("❌ 可执行文件生成失败")
        return False


def main():
    """主函数"""
    print("=== Vinted.nl 库存宝 - Windows构建脚本 ===")
    print(f"当前系统: {platform.system()}")
    
    # 检查系统
    if platform.system() != "Windows":
        print("\n❌ 错误: 此脚本只能在Windows系统上运行")
        print("要在其他系统上构建，请使用:")
        print("- macOS: python build.py")
        print("- Linux: python build.py")
        sys.exit(1)
    
    # 检查是否安装了 PyInstaller
    try:
        result = subprocess.run(['pyinstaller', '--version'],
                              check=True, capture_output=True, text=True, encoding='utf-8', errors='ignore')
        print(f"PyInstaller版本: {result.stdout.strip()}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ 错误: 未找到 PyInstaller，请先安装:")
        print("pip install pyinstaller")
        sys.exit(1)
    
    # 清理旧的构建文件
    clean_build_dirs()
    
    # 构建Windows可执行文件
    if build_windows_executable():
        # 验证生成的文件
        if verify_executable():
            print("\n=== Windows构建完成 ===")
            print("✅ 生成文件: dist/VintedInventoryManager.exe")
            print("📋 文件说明:")
            print("   - 这是一个独立的Windows可执行文件")
            print("   - 可以在任何Windows 10/11系统上运行")
            print("   - 无需安装Python或其他依赖")
            print("\n🧪 建议测试:")
            print("   1. 在当前系统上测试运行")
            print("   2. 在其他Windows电脑上测试")
            print("   3. 确认比特浏览器API连接正常")
        else:
            print("\n❌ 构建验证失败")
            sys.exit(1)
    else:
        print("\n❌ Windows构建失败")
        sys.exit(1)


if __name__ == "__main__":
    main()
