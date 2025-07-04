#!/usr/bin/env python3
"""
简化的构建脚本 - 只生成.app文件
"""

import subprocess
import platform
import shutil
from pathlib import Path

def clean_directories():
    """清理构建目录"""
    dirs_to_clean = ['build', 'dist']
    for dir_name in dirs_to_clean:
        dir_path = Path(dir_name)
        if dir_path.exists():
            shutil.rmtree(dir_path)
            print(f"已清理目录: {dir_name}")

def build_app():
    """构建应用程序"""
    current_os = platform.system()
    
    if current_os != "Darwin":
        print("此脚本仅适用于macOS系统")
        return False
    
    # 清理目录
    clean_directories()
    
    print("开始构建macOS .app文件...")
    
    # 图标路径
    icon_path = Path('assets/icon.icns')
    icon_arg = f'--icon={icon_path}' if icon_path.exists() else ''
    
    # PyInstaller命令
    cmd = [
        'pyinstaller',
        '--onefile',
        '--windowed',
        '--name=Vinted 库存宝',
        '--add-data=src:src',
        '--add-data=assets:assets',
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
        app_path = Path('dist/Vinted 库存宝.app')
        exe_path = Path('dist/Vinted 库存宝')
        
        if app_path.exists():
            # 计算.app文件大小
            total_size = sum(f.stat().st_size for f in app_path.rglob('*') if f.is_file())
            size_mb = total_size / (1024 * 1024)
            print(f"📱 生成的.app文件: {app_path}")
            print(f"📏 文件大小: {size_mb:.1f} MB")
            
            # 删除单独的可执行文件（如果存在）
            if exe_path.exists():
                exe_path.unlink()
                print(f"🗑️ 删除了单独的可执行文件: {exe_path}")
                
        elif exe_path.exists():
            # 如果只有可执行文件，重命名为.app
            app_path.mkdir()
            contents_dir = app_path / "Contents"
            contents_dir.mkdir()
            macos_dir = contents_dir / "MacOS"
            macos_dir.mkdir()
            
            # 移动可执行文件
            shutil.move(str(exe_path), str(macos_dir / "Vinted 库存宝"))
            
            # 创建Info.plist
            info_plist = contents_dir / "Info.plist"
            info_plist.write_text("""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>Vinted 库存宝</string>
    <key>CFBundleIdentifier</key>
    <string>com.vinted.inventory</string>
    <key>CFBundleName</key>
    <string>Vinted 库存宝</string>
    <key>CFBundleVersion</key>
    <string>4.0.0</string>
    <key>CFBundleShortVersionString</key>
    <string>4.0.0</string>
</dict>
</plist>""")
            
            print(f"📱 创建了.app包: {app_path}")
        else:
            print("❌ 未找到生成的文件")
            return False
        
        # 清理dist目录中的其他文件
        dist_path = Path('dist')
        for item in dist_path.iterdir():
            if item.name != 'Vinted 库存宝.app':
                if item.is_file():
                    item.unlink()
                    print(f"🗑️ 清理文件: {item.name}")
                elif item.is_dir():
                    shutil.rmtree(item)
                    print(f"🗑️ 清理目录: {item.name}")
        
        print("\n🎉 构建完成！")
        print(f"📁 输出文件: dist/Vinted 库存宝.app")
        print("💡 可以直接双击运行或拖拽到应用程序文件夹")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 构建失败: {e}")
        if e.stdout:
            print(f"输出: {e.stdout}")
        if e.stderr:
            print(f"错误: {e.stderr}")
        return False

if __name__ == "__main__":
    print("=== Vinted 库存宝 - macOS构建脚本 ===")
    success = build_app()
    if success:
        print("=== 构建成功完成 ===")
    else:
        print("=== 构建失败 ===")
        exit(1)
