#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据处理和报告生成模块

提供数据分类、统计分析、TXT报告生成等功能。
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

from .vinted_scraper import ScrapingResult, UserInfo
from ..utils.helpers import (
    generate_timestamp_filename,
    ensure_directory_exists,
    safe_filename,
    format_duration
)


class DataProcessor:
    """数据处理器"""
    
    def __init__(self, config: Dict):
        """
        初始化数据处理器
        
        Args:
            config: 配置信息
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.output_config = config.get('output', {})
    
    def generate_report(self, result: ScrapingResult) -> str:
        """
        生成TXT格式的库存报告
        
        Args:
            result: 采集结果
            
        Returns:
            报告文件路径
        """
        try:
            # 准备报告数据
            report_data = self._prepare_report_data(result)
            
            # 生成报告内容
            report_content = self._generate_report_content(report_data)
            
            # 保存报告文件
            report_file = self._save_report_file(report_content)
            
            self.logger.info(f"报告生成成功: {report_file}")
            return report_file
            
        except Exception as e:
            self.logger.error(f"生成报告失败: {str(e)}")
            raise
    
    def _prepare_report_data(self, result: ScrapingResult) -> Dict[str, Any]:
        """
        准备报告数据
        
        Args:
            result: 采集结果
            
        Returns:
            报告数据字典
        """
        total_users = result.total_users
        users_with_inventory = len(result.users_with_inventory)
        users_without_inventory = len(result.users_without_inventory)
        users_with_errors = len(result.users_with_errors)
        
        # 计算百分比
        def calc_percentage(count: int, total: int) -> float:
            return (count / total * 100) if total > 0 else 0.0
        
        # 统计总商品数量
        total_items = sum(user.item_count for user in result.users_with_inventory)
        
        return {
            'timestamp': result.timestamp,
            'admin_url': result.admin_url,
            'scraping_time': result.scraping_time,
            'total_users': total_users,
            'users_with_inventory': users_with_inventory,
            'users_without_inventory': users_without_inventory,
            'users_with_errors': users_with_errors,
            'percentage_with_inventory': calc_percentage(users_with_inventory, total_users),
            'percentage_without_inventory': calc_percentage(users_without_inventory, total_users),
            'percentage_with_errors': calc_percentage(users_with_errors, total_users),
            'total_items': total_items,
            'inventory_users_data': result.users_with_inventory,
            'no_inventory_users_data': result.users_without_inventory,
            'error_users_data': result.users_with_errors
        }
    
    def _generate_report_content(self, data: Dict[str, Any]) -> str:
        """
        生成报告内容
        
        Args:
            data: 报告数据
            
        Returns:
            报告内容字符串
        """
        lines = []
        
        # 报告头部
        lines.append("=" * 50)
        lines.append("VINTED.NL 库存管理报告")
        lines.append("=" * 50)
        lines.append(f"生成时间：{data['timestamp']}")
        lines.append(f"管理员账户：{data['admin_url']}")
        lines.append(f"总计账户数：{data['total_users']}")
        lines.append(f"采集耗时：{format_duration(data['scraping_time'])}")
        lines.append("")
        
        # 已出库账户（无商品在售）
        lines.append("=" * 30)
        lines.append("已出库账户（无商品在售）")
        lines.append("=" * 30)
        lines.append(f"总计：{data['users_without_inventory']} 个账户 ({data['percentage_without_inventory']:.1f}%)")
        lines.append("")
        
        for user in data['no_inventory_users_data']:
            lines.append(f"{user.profile_url} - 用户名：{user.username}")
        
        if not data['no_inventory_users_data']:
            lines.append("（无）")
        
        lines.append("")
        
        # 有库存账户
        lines.append("=" * 30)
        lines.append("有库存账户")
        lines.append("=" * 30)
        lines.append(f"总计：{data['users_with_inventory']} 个账户 ({data['percentage_with_inventory']:.1f}%)")
        lines.append("")
        
        for user in data['inventory_users_data']:
            items_preview = ", ".join(user.items[:5])  # 显示前5个商品
            if len(user.items) > 5:
                items_preview += f"... (共{len(user.items)}个商品)"
            
            lines.append(f"{user.profile_url} - 用户名：{user.username} - 商品数量：{user.item_count}")
            if items_preview:
                lines.append(f"  商品列表：{items_preview}")
            lines.append("")
        
        if not data['inventory_users_data']:
            lines.append("（无）")
            lines.append("")
        
        # 访问失败账户
        lines.append("=" * 30)
        lines.append("访问失败账户")
        lines.append("=" * 30)
        lines.append(f"总计：{data['users_with_errors']} 个账户 ({data['percentage_with_errors']:.1f}%)")
        lines.append("")
        
        for user in data['error_users_data']:
            lines.append(f"{user.profile_url} - 用户名：{user.username} - 错误类型：{user.error_message}")
        
        if not data['error_users_data']:
            lines.append("（无）")
        
        lines.append("")
        
        # 统计摘要
        lines.append("=" * 30)
        lines.append("统计摘要")
        lines.append("=" * 30)
        lines.append(f"- 已出库账户：{data['users_without_inventory']} ({data['percentage_without_inventory']:.1f}%)")
        lines.append(f"- 有库存账户：{data['users_with_inventory']} ({data['percentage_with_inventory']:.1f}%)")
        lines.append(f"- 访问失败账户：{data['users_with_errors']} ({data['percentage_with_errors']:.1f}%)")
        lines.append(f"- 总商品数量：{data['total_items']}")
        lines.append("")
        lines.append("=" * 50)
        lines.append("报告结束")
        lines.append("=" * 50)
        
        return "\n".join(lines)
    
    def _save_report_file(self, content: str) -> str:
        """
        保存报告文件
        
        Args:
            content: 报告内容
            
        Returns:
            保存的文件路径
        """
        # 获取输出目录
        output_dir = self.output_config.get('output_directory', str(Path.home() / "Desktop"))
        output_dir = Path(output_dir).expanduser()
        
        # 确保输出目录存在
        if not ensure_directory_exists(str(output_dir)):
            raise Exception(f"无法创建输出目录: {output_dir}")
        
        # 生成文件名
        filename_template = self.output_config.get('filename_template', 'vinted_inventory_report_{timestamp}.txt')
        filename = generate_timestamp_filename(filename_template)
        filename = safe_filename(filename)
        
        # 完整文件路径
        file_path = output_dir / filename
        
        # 保存文件
        encoding = self.output_config.get('encoding', 'utf-8')
        with open(file_path, 'w', encoding=encoding) as f:
            f.write(content)
        
        return str(file_path)
    
    def export_json(self, result: ScrapingResult) -> str:
        """
        导出JSON格式的数据
        
        Args:
            result: 采集结果
            
        Returns:
            JSON文件路径
        """
        try:
            # 转换为可序列化的字典
            data = {
                'timestamp': result.timestamp,
                'admin_url': result.admin_url,
                'scraping_time': result.scraping_time,
                'total_users': result.total_users,
                'users_with_inventory': [self._user_to_dict(user) for user in result.users_with_inventory],
                'users_without_inventory': [self._user_to_dict(user) for user in result.users_without_inventory],
                'users_with_errors': [self._user_to_dict(user) for user in result.users_with_errors]
            }
            
            # 生成文件路径
            output_dir = Path(self.output_config.get('output_directory', str(Path.home() / "Desktop"))).expanduser()
            ensure_directory_exists(str(output_dir))
            
            filename = generate_timestamp_filename('vinted_inventory_data_{timestamp}.json')
            file_path = output_dir / filename
            
            # 保存JSON文件
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"JSON数据导出成功: {file_path}")
            return str(file_path)
            
        except Exception as e:
            self.logger.error(f"导出JSON数据失败: {str(e)}")
            raise
    
    def _user_to_dict(self, user: UserInfo) -> Dict[str, Any]:
        """
        将用户信息转换为字典
        
        Args:
            user: 用户信息对象
            
        Returns:
            用户信息字典
        """
        return {
            'user_id': user.user_id,
            'username': user.username,
            'profile_url': user.profile_url,
            'status': user.status,
            'item_count': user.item_count,
            'items': user.items,
            'error_message': user.error_message
        }
    
    def get_summary_stats(self, result: ScrapingResult) -> Dict[str, Any]:
        """
        获取摘要统计信息
        
        Args:
            result: 采集结果
            
        Returns:
            统计信息字典
        """
        total = result.total_users
        with_inventory = len(result.users_with_inventory)
        without_inventory = len(result.users_without_inventory)
        with_errors = len(result.users_with_errors)
        
        return {
            'total_users': total,
            'users_with_inventory': with_inventory,
            'users_without_inventory': without_inventory,
            'users_with_errors': with_errors,
            'success_rate': ((with_inventory + without_inventory) / total * 100) if total > 0 else 0,
            'total_items': sum(user.item_count for user in result.users_with_inventory),
            'avg_items_per_user': (sum(user.item_count for user in result.users_with_inventory) / with_inventory) if with_inventory > 0 else 0
        }
