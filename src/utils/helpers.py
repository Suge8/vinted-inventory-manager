#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
辅助函数模块

提供各种通用的辅助函数。
"""

import re
import time
import urllib.parse
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple, Dict, Any
import logging


def extract_user_id_from_url(url: str) -> Optional[str]:
    """
    从Vinted用户URL中提取用户ID
    
    Args:
        url: 用户URL，如 https://www.vinted.nl/member/12345
        
    Returns:
        用户ID，提取失败返回None
    """
    try:
        # 匹配用户ID的正则表达式
        pattern = r'/member/(\d+)'
        match = re.search(pattern, url)
        if match:
            return match.group(1)
        return None
    except Exception:
        return None


def extract_user_id_from_following_url(url: str) -> Optional[str]:
    """
    从关注列表URL中提取管理员用户ID
    
    Args:
        url: 关注列表URL，如 https://www.vinted.nl/member/general/following/12345?page=1
        
    Returns:
        用户ID，提取失败返回None
    """
    try:
        pattern = r'/following/(\d+)'
        match = re.search(pattern, url)
        if match:
            return match.group(1)
        return None
    except Exception:
        return None


def build_user_profile_url(user_id: str, base_url: str = "https://www.vinted.nl") -> str:
    """
    构建用户主页URL
    
    Args:
        user_id: 用户ID
        base_url: 基础URL
        
    Returns:
        用户主页URL
    """
    return f"{base_url.rstrip('/')}/member/{user_id}"


def build_following_url(user_id: str, page: int = 1, base_url: str = "https://www.vinted.nl") -> str:
    """
    构建关注列表URL
    
    Args:
        user_id: 用户ID
        page: 页码
        base_url: 基础URL
        
    Returns:
        关注列表URL
    """
    return f"{base_url.rstrip('/')}/member/general/following/{user_id}?page={page}"


def validate_vinted_url(url: str) -> Tuple[bool, str]:
    """
    验证Vinted URL的有效性
    
    Args:
        url: 要验证的URL
        
    Returns:
        (是否有效, 错误消息)
    """
    try:
        parsed = urllib.parse.urlparse(url)
        
        # 检查协议
        if parsed.scheme not in ['http', 'https']:
            return False, "URL必须使用http或https协议"
        
        # 检查域名
        if 'vinted.nl' not in parsed.netloc:
            return False, "URL必须是vinted.nl域名"
        
        # 检查路径格式
        if '/member/' not in parsed.path:
            return False, "URL必须包含用户信息路径"
        
        return True, "URL格式有效"
        
    except Exception as e:
        return False, f"URL格式错误: {str(e)}"


def generate_timestamp_filename(template: str, extension: str = None) -> str:
    """
    生成带时间戳的文件名
    
    Args:
        template: 文件名模板，包含{timestamp}占位符
        extension: 文件扩展名（可选）
        
    Returns:
        生成的文件名
    """
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = template.format(timestamp=timestamp)
    
    if extension and not filename.endswith(f".{extension}"):
        filename += f".{extension}"
    
    return filename


def ensure_directory_exists(directory: str) -> bool:
    """
    确保目录存在，如果不存在则创建
    
    Args:
        directory: 目录路径
        
    Returns:
        是否成功创建或已存在
    """
    try:
        Path(directory).mkdir(parents=True, exist_ok=True)
        return True
    except Exception:
        return False


def safe_filename(filename: str) -> str:
    """
    生成安全的文件名，移除或替换非法字符
    
    Args:
        filename: 原始文件名
        
    Returns:
        安全的文件名
    """
    # 移除或替换Windows文件名中的非法字符
    illegal_chars = r'<>:"/\|?*'
    for char in illegal_chars:
        filename = filename.replace(char, '_')
    
    # 移除前后空格和点
    filename = filename.strip(' .')
    
    # 确保文件名不为空
    if not filename:
        filename = "unnamed"
    
    return filename


def format_duration(seconds: float) -> str:
    """
    格式化时间持续时间
    
    Args:
        seconds: 秒数
        
    Returns:
        格式化的时间字符串
    """
    if seconds < 60:
        return f"{seconds:.1f}秒"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}分钟"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}小时"


def retry_on_exception(max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """
    重试装饰器
    
    Args:
        max_retries: 最大重试次数
        delay: 初始延迟时间（秒）
        backoff: 延迟时间倍数
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            last_exception = None
            current_delay = delay
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries:
                        logging.getLogger(__name__).warning(
                            f"函数 {func.__name__} 第{attempt + 1}次尝试失败: {str(e)}，"
                            f"{current_delay}秒后重试"
                        )
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logging.getLogger(__name__).error(
                            f"函数 {func.__name__} 在{max_retries}次重试后仍然失败"
                        )
            
            raise last_exception
        return wrapper
    return decorator


def parse_page_number_from_url(url: str) -> int:
    """
    从URL中解析页码
    
    Args:
        url: 包含页码参数的URL
        
    Returns:
        页码，默认为1
    """
    try:
        parsed = urllib.parse.urlparse(url)
        query_params = urllib.parse.parse_qs(parsed.query)
        page = query_params.get('page', ['1'])[0]
        return int(page)
    except (ValueError, IndexError):
        return 1


def build_next_page_url(url: str) -> str:
    """
    构建下一页的URL
    
    Args:
        url: 当前页面URL
        
    Returns:
        下一页URL
    """
    try:
        parsed = urllib.parse.urlparse(url)
        query_params = urllib.parse.parse_qs(parsed.query)
        
        current_page = int(query_params.get('page', ['1'])[0])
        next_page = current_page + 1
        
        query_params['page'] = [str(next_page)]
        new_query = urllib.parse.urlencode(query_params, doseq=True)
        
        return urllib.parse.urlunparse((
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            new_query,
            parsed.fragment
        ))
    except Exception:
        return url


def clean_text(text: str) -> str:
    """
    清理文本，移除多余的空白字符
    
    Args:
        text: 原始文本
        
    Returns:
        清理后的文本
    """
    if not text:
        return ""
    
    # 移除前后空白
    text = text.strip()
    
    # 将多个空白字符替换为单个空格
    text = re.sub(r'\s+', ' ', text)
    
    return text


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    截断文本到指定长度
    
    Args:
        text: 原始文本
        max_length: 最大长度
        suffix: 截断后缀
        
    Returns:
        截断后的文本
    """
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix
