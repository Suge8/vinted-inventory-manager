#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vinted.nl 库存管理系统 - 主程序入口

作者: Vinted Inventory Team
版本: 1.0.0
创建时间: 2025-06-02
"""

import sys
import os
import logging
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.logger import setup_logger
from src.utils.config import ConfigManager
from src.gui.modern_window import ModernVintedApp


def main():
    """主程序入口函数"""
    try:
        print("🚀 开始启动应用程序...")

        # 设置日志系统
        print("📝 设置日志系统...")
        logger = setup_logger()
        logger.info("启动 Vinted.nl 库存管理系统 v1.0.0")
        print("✅ 日志系统设置完成")

        # 加载配置
        print("⚙️ 加载配置...")
        config_manager = ConfigManager()
        config = config_manager.load_config()
        print("✅ 配置加载完成")

        # 启动现代化GUI应用
        print("🖥️ 创建现代化GUI应用...")
        app = ModernVintedApp(config)
        print("✅ 现代化GUI应用创建完成")

        print("🎯 启动应用主循环...")
        app.run()
        
    except Exception as e:
        # 如果日志系统未初始化，使用基础日志
        if 'logger' not in locals():
            logging.basicConfig(level=logging.ERROR)
            logger = logging.getLogger(__name__)
        
        logger.error(f"程序启动失败: {str(e)}", exc_info=True)
        
        # 显示错误对话框
        try:
            import tkinter as tk
            from tkinter import messagebox
            
            root = tk.Tk()
            root.withdraw()  # 隐藏主窗口
            messagebox.showerror(
                "启动错误", 
                f"程序启动失败:\n{str(e)}\n\n请检查配置文件和依赖是否正确安装。"
            )
        except ImportError:
            print(f"程序启动失败: {str(e)}")
        
        sys.exit(1)


if __name__ == "__main__":
    main()
