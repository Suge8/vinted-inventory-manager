#!/usr/bin/env python3
"""
跨平台构建脚本
在macOS上构建.app，使用GitHub Actions构建.exe
"""

import subprocess
import sys
import os
import platform
from pathlib import Path

def build_macos():
    """构建macOS .app文件"""
    print("=== 构建macOS版本 ===")
    
    try:
        result = subprocess.run(['python', 'build.py'], check=True, capture_output=True, text=True)
        print("✅ macOS .app构建成功!")
        
        # 检查生成的文件
        app_path = Path('dist/VintedInventoryManager.app')
        if app_path.exists():
            print(f"✅ 生成文件: {app_path}")
            return True
        else:
            print("❌ 未找到.app文件")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ macOS构建失败: {e}")
        return False

def trigger_github_actions():
    """触发GitHub Actions构建Windows版本"""
    print("\n=== 触发GitHub Actions构建Windows版本 ===")
    
    try:
        # 检查是否有git仓库
        result = subprocess.run(['git', 'status'], check=True, capture_output=True, text=True)
        
        # 获取当前版本
        version_file = Path('VERSION')
        if version_file.exists():
            version = version_file.read_text().strip()
        else:
            version = "1.4.0"
        
        print(f"当前版本: v{version}")
        
        # 创建并推送标签
        tag_name = f"v{version}"
        
        print(f"创建标签: {tag_name}")
        subprocess.run(['git', 'tag', '-f', tag_name], check=True)
        
        print(f"推送标签到GitHub...")
        subprocess.run(['git', 'push', 'origin', tag_name, '--force'], check=True)
        
        print("✅ GitHub Actions构建已触发!")
        print("📋 请访问GitHub仓库的Actions页面查看构建进度")
        print("🔗 构建完成后可在Releases页面下载Windows .exe文件")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ GitHub Actions触发失败: {e}")
        print("💡 请确保:")
        print("   1. 项目已推送到GitHub")
        print("   2. 已配置GitHub Actions")
        print("   3. 有推送权限")
        return False

def build_with_online_service():
    """使用在线服务构建Windows版本"""
    print("\n=== 在线构建服务选项 ===")
    print("由于PyInstaller无法跨平台构建，推荐使用以下方式获取Windows .exe文件:")
    print()
    print("🔥 方法1: GitHub Actions (推荐)")
    print("   - 自动构建Windows和macOS版本")
    print("   - 运行: python build_cross_platform.py --github")
    print()
    print("🔧 方法2: 在线构建服务")
    print("   - 使用GitHub Codespaces")
    print("   - 使用Replit等在线IDE")
    print()
    print("💻 方法3: 虚拟机")
    print("   - 使用Parallels Desktop运行Windows")
    print("   - 在Windows虚拟机中运行: python build_windows.py")
    print()
    print("☁️  方法4: 云服务")
    print("   - 使用AWS/Azure Windows实例")
    print("   - 临时租用Windows云服务器")

def main():
    """主函数"""
    print("=== Vinted.nl 库存宝 - 跨平台构建工具 ===")
    print(f"当前系统: {platform.system()}")
    
    if len(sys.argv) > 1 and sys.argv[1] == '--github':
        # 构建macOS版本并触发GitHub Actions
        if platform.system() == "Darwin":
            if build_macos():
                trigger_github_actions()
        else:
            print("❌ 此选项需要在macOS上运行")
            sys.exit(1)
    
    elif len(sys.argv) > 1 and sys.argv[1] == '--help':
        print("\n使用方法:")
        print("  python build_cross_platform.py           # 显示构建选项")
        print("  python build_cross_platform.py --github  # 构建macOS并触发GitHub Actions")
        print("  python build_cross_platform.py --help    # 显示帮助")
    
    else:
        # 根据系统显示相应的构建选项
        if platform.system() == "Darwin":
            print("\n🍎 macOS构建选项:")
            print("1. 构建本地macOS .app文件:")
            print("   python build.py")
            print()
            print("2. 构建macOS + 触发Windows构建:")
            print("   python build_cross_platform.py --github")
            print()
            
            # 构建macOS版本
            build_macos()
            
        elif platform.system() == "Windows":
            print("\n🪟 Windows构建:")
            print("   python build_windows.py")
        
        # 显示在线构建选项
        build_with_online_service()

if __name__ == "__main__":
    main()
