#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日志系统模块

提供统一的日志记录功能。
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from logging.handlers import RotatingFileHandler


def setup_logger(
    name: str = None,
    level: str = "INFO",
    log_file: Optional[str] = None,
    max_file_size: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5
) -> logging.Logger:
    """
    设置日志系统
    
    Args:
        name: 日志器名称，默认为根日志器
        level: 日志级别
        log_file: 日志文件路径，None表示不写入文件
        max_file_size: 日志文件最大大小（字节）
        backup_count: 备份文件数量
        
    Returns:
        配置好的日志器
    """
    # 获取日志器
    logger = logging.getLogger(name)
    
    # 如果已经配置过，直接返回
    if logger.handlers:
        return logger
    
    # 设置日志级别
    log_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(log_level)
    
    # 创建格式化器
    formatter = logging.Formatter(
        fmt='[%(asctime)s] %(levelname)s [%(name)s]: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 文件处理器（如果指定了日志文件）
    if log_file:
        try:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=max_file_size,
                backupCount=backup_count,
                encoding='utf-8'
            )
            file_handler.setLevel(log_level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
            
        except Exception as e:
            logger.error(f"无法创建日志文件处理器: {str(e)}")
    
    return logger


class GUILogHandler(logging.Handler):
    """GUI日志处理器，将日志消息发送到GUI组件"""
    
    def __init__(self, callback_func):
        """
        初始化GUI日志处理器
        
        Args:
            callback_func: 回调函数，接收日志消息
        """
        super().__init__()
        self.callback_func = callback_func
    
    def emit(self, record):
        """发送日志记录"""
        try:
            msg = self.format(record)
            self.callback_func(msg)
        except Exception:
            # 避免在日志处理中产生异常
            pass


def setup_gui_logger(callback_func, level: str = "INFO") -> logging.Logger:
    """
    为GUI设置专用的日志器
    
    Args:
        callback_func: GUI日志回调函数
        level: 日志级别
        
    Returns:
        配置好的日志器
    """
    logger = logging.getLogger("gui")
    
    # 清除现有处理器
    logger.handlers.clear()
    
    # 设置日志级别
    log_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(log_level)
    
    # 创建GUI处理器
    gui_handler = GUILogHandler(callback_func)
    gui_handler.setLevel(log_level)
    
    # 创建格式化器
    formatter = logging.Formatter(
        fmt='[%(asctime)s] %(levelname)s: %(message)s',
        datefmt='%H:%M:%S'
    )
    gui_handler.setFormatter(formatter)
    
    logger.addHandler(gui_handler)
    
    # 防止日志向上传播到根日志器
    logger.propagate = False
    
    return logger


def get_default_log_file() -> str:
    """
    获取默认日志文件路径
    
    Returns:
        日志文件路径
    """
    home_dir = Path.home()
    log_dir = home_dir / ".vinted_inventory" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    return str(log_dir / "vinted_inventory.log")


# 预配置的日志器实例
def get_logger(name: str = None) -> logging.Logger:
    """
    获取日志器实例
    
    Args:
        name: 日志器名称
        
    Returns:
        日志器实例
    """
    if name:
        return logging.getLogger(name)
    else:
        # 返回根日志器，如果未配置则进行基础配置
        root_logger = logging.getLogger()
        if not root_logger.handlers:
            setup_logger(log_file=get_default_log_file())
        return root_logger
