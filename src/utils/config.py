#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理模块

提供应用程序配置的加载、保存和验证功能。
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List
import logging


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_file: str = None):
        """
        初始化配置管理器
        
        Args:
            config_file: 配置文件路径，默认为用户目录下的配置文件
        """
        self.logger = logging.getLogger(__name__)
        
        if config_file:
            self.config_file = Path(config_file)
        else:
            # 默认配置文件位置
            home_dir = Path.home()
            self.config_file = home_dir / ".vinted_inventory" / "config.json"
        
        # 确保配置目录存在
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 默认配置
        self.default_config = {
            "bitbrowser": {
                "api_url": "http://127.0.0.1:54345",
                "window_name": "vinted_inventory_script",
                "timeout": 30,
                "retry_count": 3
            },
            "vinted": {
                "base_url": "https://www.vinted.nl",
                "page_load_timeout": 15,
                "element_wait_timeout": 10,
                "scroll_pause_time": 2
            },
            "scraping": {
                "max_concurrent_requests": 3,
                "delay_between_requests": 1,
                "max_retries": 3,
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            },
            "output": {
                "report_format": "txt",
                "output_directory": str(Path.home() / "Desktop"),
                "filename_template": "vinted_inventory_report_{timestamp}.txt",
                "encoding": "utf-8"
            },
            "logging": {
                "level": "INFO",
                "format": "[%(asctime)s] %(levelname)s: %(message)s",
                "date_format": "%Y-%m-%d %H:%M:%S"
            },
            "ui": {
                "window_size": "900x1000",
                "theme": "default"
            }
        }
    
    def load_config(self) -> Dict[str, Any]:
        """
        加载配置文件
        
        Returns:
            配置字典
        """
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                
                # 合并用户配置和默认配置
                config = self._merge_config(self.default_config, user_config)
                self.logger.info(f"已加载配置文件: {self.config_file}")
                return config
            else:
                # 如果配置文件不存在，创建默认配置文件
                self.save_config(self.default_config)
                self.logger.info("已创建默认配置文件")
                return self.default_config.copy()
                
        except Exception as e:
            self.logger.error(f"加载配置文件失败: {str(e)}")
            self.logger.info("使用默认配置")
            return self.default_config.copy()
    
    def save_config(self, config: Dict[str, Any]) -> bool:
        """
        保存配置到文件
        
        Args:
            config: 要保存的配置字典
            
        Returns:
            是否保存成功
        """
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"配置已保存到: {self.config_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"保存配置文件失败: {str(e)}")
            return False
    
    def _merge_config(self, default: Dict, user: Dict) -> Dict:
        """
        递归合并配置字典
        
        Args:
            default: 默认配置
            user: 用户配置
            
        Returns:
            合并后的配置
        """
        result = default.copy()
        
        for key, value in user.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_config(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def validate_config(self, config: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        验证配置的有效性
        
        Args:
            config: 要验证的配置
            
        Returns:
            (是否有效, 错误消息列表)
        """
        errors = []
        
        # 验证必需的配置项
        required_sections = ['bitbrowser', 'vinted', 'output']
        for section in required_sections:
            if section not in config:
                errors.append(f"缺少必需的配置节: {section}")
        
        # 验证比特浏览器配置
        if 'bitbrowser' in config:
            bitbrowser_config = config['bitbrowser']
            if 'api_url' not in bitbrowser_config:
                errors.append("缺少比特浏览器API地址配置")
            elif not bitbrowser_config['api_url'].startswith('http'):
                errors.append("比特浏览器API地址格式无效")
        
        # 验证输出目录
        if 'output' in config:
            output_config = config['output']
            if 'output_directory' in output_config:
                output_dir = Path(output_config['output_directory'])
                if not output_dir.exists():
                    try:
                        output_dir.mkdir(parents=True, exist_ok=True)
                    except Exception:
                        errors.append(f"无法创建输出目录: {output_dir}")
        
        return len(errors) == 0, errors
    
    def get_config_value(self, config: Dict[str, Any], key_path: str, default=None):
        """
        获取嵌套配置值
        
        Args:
            config: 配置字典
            key_path: 配置键路径，如 'bitbrowser.api_url'
            default: 默认值
            
        Returns:
            配置值
        """
        keys = key_path.split('.')
        value = config
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def set_config_value(self, config: Dict[str, Any], key_path: str, value: Any):
        """
        设置嵌套配置值
        
        Args:
            config: 配置字典
            key_path: 配置键路径，如 'bitbrowser.api_url'
            value: 要设置的值
        """
        keys = key_path.split('.')
        current = config
        
        # 导航到最后一级的父级
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        # 设置最终值
        current[keys[-1]] = value
