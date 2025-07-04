#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
应用打包脚本

使用 PyInstaller 将应用打包为可执行文件。
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path


def clean_build_dirs():
    """清理构建目录"""
    dirs_to_clean = ['build', 'dist', '__pycache__']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"已清理目录: {dir_name}")


def build_executable():
    """构建可执行文件"""
    import platform
    current_os = platform.system()

    print(f"开始构建可执行文件... (当前系统: {current_os})")

    # 根据操作系统确定可执行文件名
    if current_os == "Windows":
        exe_name = "Vinted 库存宝.exe"
    elif current_os == "Darwin":  # macOS
        exe_name = "Vinted 库存宝"
    else:  # Linux
        exe_name = "Vinted 库存宝"

    # PyInstaller 命令参数
    if current_os == "Darwin":  # macOS - 生成.app包
        cmd = [
            'pyinstaller',
            '--onefile',                    # 单文件模式
            '--windowed',                   # 无控制台窗口
            f'--name={exe_name}',           # 应用名称
            '--add-data=src:src',           # 添加源码
            '--add-data=assets:assets',     # 添加图标资源
            '--hidden-import=tkinter',      # 隐式导入
            '--hidden-import=customtkinter', # 现代UI库
            '--hidden-import=darkdetect',   # 主题检测
            '--hidden-import=PIL',          # 图像处理
            '--hidden-import=selenium',
            '--hidden-import=requests',
            '--hidden-import=beautifulsoup4',
            '--hidden-import=lxml',
            'src/main.py'                   # 主程序文件
        ]
    else:  # Windows/Linux - 生成单文件
        cmd = [
            'pyinstaller',
            '--onefile',                    # 单文件模式
            '--windowed',                   # 无控制台窗口
            f'--name={exe_name.split(".")[0]}', # 可执行文件名称（不含扩展名）
            '--distpath=dist',              # 输出目录
            '--workpath=build',             # 工作目录
            '--specpath=.',                 # spec文件位置
            '--add-data=resources:resources',  # 添加资源文件
            '--add-data=assets:assets',     # 添加图标资源
            '--hidden-import=tkinter',      # 隐式导入
            '--hidden-import=customtkinter', # 现代UI库
            '--hidden-import=darkdetect',   # 主题检测
            '--hidden-import=PIL',          # 图像处理
            '--hidden-import=selenium',
            '--hidden-import=requests',
            '--hidden-import=beautifulsoup4',
            'src/main.py'                   # 主程序文件
        ]

    # 添加图标参数
    if current_os == "Darwin":  # macOS
        icon_path = Path('assets/icon.icns')
        if icon_path.exists():
            cmd.extend(['--icon', str(icon_path)])
    elif current_os == "Windows":  # Windows
        icon_path = Path('assets/icon.ico')
        if icon_path.exists():
            cmd.extend(['--icon', str(icon_path)])
    else:  # Linux
        icon_path = Path('assets/icon.png')
        if icon_path.exists():
            cmd.extend(['--icon', str(icon_path)])

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("构建成功!")

        # 在macOS上，只生成.app包并清理其他文件
        if current_os == "Darwin":
            print("macOS构建完成:")

            # 检查.app文件
            app_path = Path(f'dist/{exe_name}')
            if app_path.exists() and app_path.is_dir():
                # 计算.app文件大小
                total_size = sum(f.stat().st_size for f in app_path.rglob('*') if f.is_file())
                size_mb = total_size / (1024 * 1024)
                print(f"- {exe_name} ({size_mb:.1f} MB)")

                # 清理dist目录中的其他文件，只保留.app
                dist_path = Path('dist')
                for item in dist_path.iterdir():
                    if item.name != exe_name:
                        if item.is_file():
                            item.unlink()
                            print(f"清理文件: {item.name}")
                        elif item.is_dir():
                            import shutil
                            shutil.rmtree(item)
                            print(f"清理目录: {item.name}")

                print(f"\n✅ 只保留了 {exe_name} 文件")
            else:
                print("❌ .app文件未找到")

            print("\n注意: 要为Windows用户构建.exe文件，需要在Windows系统上运行此脚本")
        else:
            print(f"构建完成: {exe_name}")

        return True
    except subprocess.CalledProcessError as e:
        print(f"构建失败: {e}")
        print(f"错误输出: {e.stderr}")
        return False


def copy_additional_files():
    """复制额外的文件到输出目录"""
    dist_dir = Path('dist')
    if not dist_dir.exists():
        return
    
    # 要复制的文件列表 - 不复制任何额外文件
    files_to_copy = [
    ]
    
    for src, dst in files_to_copy:
        src_path = Path(src)
        if src_path.exists():
            dst_path = dist_dir / dst
            shutil.copy2(src_path, dst_path)
            print(f"已复制: {src} -> {dst_path}")


def main():
    """主函数"""
    print("=== Vinted 库存管理系统 - 构建脚本 ===")
    
    # 检查是否安装了 PyInstaller
    try:
        subprocess.run(['pyinstaller', '--version'], 
                      check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("错误: 未找到 PyInstaller，请先安装:")
        print("pip install pyinstaller")
        sys.exit(1)
    
    # 清理旧的构建文件
    clean_build_dirs()
    
    # 构建可执行文件
    if build_executable():
        # 复制额外文件
        copy_additional_files()
        
        import platform
        current_os = platform.system()

        print("\n=== 构建完成 ===")
        if current_os == "Darwin":  # macOS
            print("可执行文件位置:")
            print("- dist/VintedInventoryManager (macOS命令行)")
            print("- dist/VintedInventoryManager.app (macOS应用包)")
            print("\n⚠️  注意: 要构建Windows .exe文件，需要在Windows系统上运行此脚本")
        elif current_os == "Windows":
            print("可执行文件位置: dist/VintedInventoryManager.exe")
        else:
            print("可执行文件位置: dist/VintedInventoryManager")
        print("请测试应用程序是否正常运行。")
    else:
        print("\n=== 构建失败 ===")
        sys.exit(1)


if __name__ == "__main__":
    main()
