#!/usr/bin/env python3
"""
版本管理工具
用于管理应用程序版本号
"""

import re
from pathlib import Path
from datetime import datetime

class VersionManager:
    """版本管理器"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.version_file = self.project_root / "VERSION"
        self.changelog_file = self.project_root / "CHANGELOG.md"
    
    def get_current_version(self) -> str:
        """获取当前版本号"""
        if self.version_file.exists():
            return self.version_file.read_text().strip()
        return "1.0.0"
    
    def set_version(self, version: str):
        """设置版本号"""
        self.version_file.write_text(version)
        print(f"版本号已更新为: {version}")
    
    def parse_version(self, version: str) -> tuple:
        """解析版本号为(major, minor, patch)"""
        parts = version.split('.')
        return (int(parts[0]), int(parts[1]), int(parts[2]))
    
    def format_version(self, major: int, minor: int, patch: int) -> str:
        """格式化版本号"""
        return f"{major}.{minor}.{patch}"
    
    def bump_patch(self) -> str:
        """增加补丁版本号 (x.y.z -> x.y.z+1)"""
        current = self.get_current_version()
        major, minor, patch = self.parse_version(current)
        new_version = self.format_version(major, minor, patch + 1)
        self.set_version(new_version)
        return new_version
    
    def bump_minor(self) -> str:
        """增加次版本号 (x.y.z -> x.y+1.0)"""
        current = self.get_current_version()
        major, minor, patch = self.parse_version(current)
        new_version = self.format_version(major, minor + 1, 0)
        self.set_version(new_version)
        return new_version
    
    def bump_major(self) -> str:
        """增加主版本号 (x.y.z -> x+1.0.0)"""
        current = self.get_current_version()
        major, minor, patch = self.parse_version(current)
        new_version = self.format_version(major + 1, 0, 0)
        self.set_version(new_version)
        return new_version
    
    def update_changelog_version(self, version: str, description: str = ""):
        """在CHANGELOG中添加新版本"""
        if not self.changelog_file.exists():
            return
        
        content = self.changelog_file.read_text(encoding='utf-8')
        
        # 查找第一个版本标题
        date_str = datetime.now().strftime("%Y-%m-%d")
        new_entry = f"## [v{version}] - {date_str} - {description}\n\n"
        
        # 在第一个##之前插入新版本
        lines = content.split('\n')
        insert_index = 0
        for i, line in enumerate(lines):
            if line.startswith('## ['):
                insert_index = i
                break
        
        lines.insert(insert_index, new_entry.rstrip())
        
        updated_content = '\n'.join(lines)
        self.changelog_file.write_text(updated_content, encoding='utf-8')
        print(f"CHANGELOG已更新，添加版本 v{version}")

def main():
    """主函数"""
    import sys
    
    vm = VersionManager()
    current = vm.get_current_version()
    
    if len(sys.argv) < 2:
        print(f"当前版本: {current}")
        print("用法:")
        print("  python version_manager.py patch [描述]  # 补丁版本 (bug修复)")
        print("  python version_manager.py minor [描述]  # 次版本 (新功能)")
        print("  python version_manager.py major [描述]  # 主版本 (重大更改)")
        print("  python version_manager.py set x.y.z    # 设置特定版本")
        return
    
    action = sys.argv[1]
    description = sys.argv[2] if len(sys.argv) > 2 else ""
    
    if action == "patch":
        new_version = vm.bump_patch()
        vm.update_changelog_version(new_version, description or "Bug修复和小改进")
    elif action == "minor":
        new_version = vm.bump_minor()
        vm.update_changelog_version(new_version, description or "新功能添加")
    elif action == "major":
        new_version = vm.bump_major()
        vm.update_changelog_version(new_version, description or "重大版本更新")
    elif action == "set" and len(sys.argv) > 2:
        new_version = sys.argv[2]
        vm.set_version(new_version)
        vm.update_changelog_version(new_version, description or "版本设置")
    else:
        print("无效的操作")
        return
    
    print(f"版本已从 {current} 更新到 {new_version}")

if __name__ == "__main__":
    main()
