#!/usr/bin/env python3
"""
测试构建结果的脚本
"""

import os
import platform
from pathlib import Path

def test_macos_build():
    """测试macOS构建结果"""
    print("=== 测试macOS构建结果 ===")
    
    app_path = Path('dist/VintedInventoryManager.app')
    if app_path.exists() and app_path.is_dir():
        print("✅ VintedInventoryManager.app 存在")
        
        # 检查.app内部结构
        contents_path = app_path / 'Contents'
        macos_path = contents_path / 'MacOS' / 'VintedInventoryManager'
        info_plist = contents_path / 'Info.plist'
        
        if contents_path.exists():
            print("✅ Contents 文件夹存在")
        else:
            print("❌ Contents 文件夹不存在")
            
        if macos_path.exists():
            print("✅ 可执行文件存在")
            print(f"   路径: {macos_path}")
        else:
            print("❌ 可执行文件不存在")
            
        if info_plist.exists():
            print("✅ Info.plist 存在")
        else:
            print("❌ Info.plist 不存在")
            
        # 计算.app大小
        total_size = sum(f.stat().st_size for f in app_path.rglob('*') if f.is_file())
        size_mb = total_size / (1024 * 1024)
        print(f"📦 .app 总大小: {size_mb:.1f} MB")
        
        return True
    else:
        print("❌ VintedInventoryManager.app 不存在")
        return False

def test_windows_build():
    """测试Windows构建结果"""
    print("=== 测试Windows构建结果 ===")
    
    exe_path = Path('dist/VintedInventoryManager.exe')
    if exe_path.exists() and exe_path.is_file():
        print("✅ VintedInventoryManager.exe 存在")
        
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print(f"📦 .exe 文件大小: {size_mb:.1f} MB")
        
        return True
    else:
        print("❌ VintedInventoryManager.exe 不存在")
        return False

def create_distribution_package():
    """创建分发包"""
    print("=== 创建分发包 ===")
    
    dist_path = Path('dist')
    if not dist_path.exists():
        print("❌ dist 文件夹不存在")
        return False
    
    current_os = platform.system()
    
    if current_os == "Darwin":  # macOS
        app_path = dist_path / 'VintedInventoryManager.app'
        if app_path.exists():
            # 创建zip文件
            import zipfile
            zip_path = dist_path / 'VintedInventoryManager-macOS-v1.4.0.zip'
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in app_path.rglob('*'):
                    if file_path.is_file():
                        arcname = file_path.relative_to(dist_path)
                        zipf.write(file_path, arcname)
            
            print(f"✅ 创建macOS分发包: {zip_path}")
            print(f"📦 压缩包大小: {zip_path.stat().st_size / (1024 * 1024):.1f} MB")
            return True
    
    elif current_os == "Windows":
        exe_path = dist_path / 'VintedInventoryManager.exe'
        if exe_path.exists():
            print(f"✅ Windows可执行文件已准备: {exe_path}")
            return True
    
    return False

def main():
    """主函数"""
    print("🔍 测试构建结果")
    print(f"当前系统: {platform.system()}")
    print()
    
    success = False
    
    if platform.system() == "Darwin":
        success = test_macos_build()
        if success:
            create_distribution_package()
    elif platform.system() == "Windows":
        success = test_windows_build()
    else:
        print("❌ 不支持的操作系统")
    
    print()
    if success:
        print("✅ 构建测试通过！")
        print("📋 文件可以直接发给用户使用")
    else:
        print("❌ 构建测试失败！")
        print("🔧 请检查构建过程")

if __name__ == "__main__":
    main()
