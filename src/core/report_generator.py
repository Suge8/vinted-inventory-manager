#!/usr/bin/env python3
"""
美观的HTML报告生成器
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List
import base64

class ModernReportGenerator:
    def __init__(self):
        self.template_dir = Path(__file__).parent / "templates"
        self.template_dir.mkdir(exist_ok=True)
        
    def generate_html_report(self, data: Dict) -> str:
        """生成现代化的HTML报告"""
        
        # 创建HTML模板
        html_template = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vinted 库存报告</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #ff6b6b 0%, #4ecdc4 100%);
            color: white;
            padding: 40px;
            text-align: center;
            position: relative;
        }
        
        .header::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="25" cy="25" r="1" fill="white" opacity="0.1"/><circle cx="75" cy="75" r="1" fill="white" opacity="0.1"/><circle cx="50" cy="10" r="0.5" fill="white" opacity="0.1"/></pattern></defs><rect width="100" height="100" fill="url(%23grain)"/></svg>');
        }
        
        .header h1 {
            font-size: 3em;
            margin-bottom: 10px;
            position: relative;
            z-index: 1;
        }
        
        .header .subtitle {
            font-size: 1.2em;
            opacity: 0.9;
            position: relative;
            z-index: 1;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            padding: 40px;
            background: #f8f9fa;
        }
        
        .stat-card {
            background: white;
            padding: 30px;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }
        
        .stat-card:hover {
            transform: translateY(-5px);
        }
        
        .stat-number {
            font-size: 3em;
            font-weight: bold;
            margin-bottom: 10px;
        }
        
        .stat-label {
            color: #666;
            font-size: 1.1em;
        }
        
        .has-inventory { color: #28a745; }
        .no-inventory { color: #dc3545; }
        .errors { color: #ffc107; }
        .total { color: #007bff; }
        
        .section {
            padding: 40px;
        }
        
        .section h2 {
            font-size: 2em;
            margin-bottom: 20px;
            color: #333;
            border-bottom: 3px solid #4ecdc4;
            padding-bottom: 10px;
        }
        
        .user-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        
        .user-card {
            background: white;
            border: 1px solid #e9ecef;
            border-radius: 10px;
            padding: 20px;
            transition: all 0.3s ease;
        }
        
        .user-card:hover {
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            transform: translateY(-2px);
        }
        
        .user-name {
            font-weight: bold;
            font-size: 1.1em;
            margin-bottom: 10px;
            color: #333;
        }
        
        .user-admin {
            color: #666;
            font-size: 0.9em;
            margin-bottom: 10px;
        }
        
        .user-status {
            padding: 5px 10px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: bold;
            display: inline-block;
        }
        
        .status-inventory {
            background: #d4edda;
            color: #155724;
        }
        
        .status-no-inventory {
            background: #f8d7da;
            color: #721c24;
        }
        
        .status-error {
            background: #fff3cd;
            color: #856404;
        }
        
        .chart-container {
            background: white;
            border-radius: 15px;
            padding: 30px;
            margin: 20px 0;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        
        .progress-bar {
            background: #e9ecef;
            border-radius: 10px;
            height: 20px;
            overflow: hidden;
            margin: 10px 0;
        }
        
        .progress-fill {
            height: 100%;
            border-radius: 10px;
            transition: width 0.3s ease;
        }
        
        .footer {
            background: #333;
            color: white;
            text-align: center;
            padding: 30px;
        }
        
        .emoji {
            font-size: 1.5em;
            margin-right: 10px;
        }
        
        @media print {
            body { background: white; }
            .container { box-shadow: none; }
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- 头部 -->
        <div class="header">
            <h1>🛍️ Vinted 库存报告</h1>
            <div class="subtitle">生成时间: {timestamp}</div>
        </div>
        
        <!-- 统计卡片 -->
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number total">{total_users}</div>
                <div class="stat-label">总用户数</div>
            </div>
            <div class="stat-card">
                <div class="stat-number has-inventory">{users_with_inventory}</div>
                <div class="stat-label">有库存用户</div>
            </div>
            <div class="stat-card">
                <div class="stat-number no-inventory">{users_without_inventory}</div>
                <div class="stat-label">已出库用户</div>
            </div>
            <div class="stat-card">
                <div class="stat-number errors">{users_with_errors}</div>
                <div class="stat-label">检查失败</div>
            </div>
        </div>
        
        <!-- 管理员统计 -->
        {admin_section}
        
        <!-- 进度图表 -->
        <div class="section">
            <h2>📊 库存分布</h2>
            <div class="chart-container">
                <div style="margin-bottom: 15px;">
                    <strong>有库存用户: {inventory_percentage}%</strong>
                    <div class="progress-bar">
                        <div class="progress-fill has-inventory" style="width: {inventory_percentage}%; background: #28a745;"></div>
                    </div>
                </div>
                <div style="margin-bottom: 15px;">
                    <strong>已出库用户: {no_inventory_percentage}%</strong>
                    <div class="progress-bar">
                        <div class="progress-fill no-inventory" style="width: {no_inventory_percentage}%; background: #dc3545;"></div>
                    </div>
                </div>
                <div>
                    <strong>检查失败: {error_percentage}%</strong>
                    <div class="progress-bar">
                        <div class="progress-fill errors" style="width: {error_percentage}%; background: #ffc107;"></div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- 已出库用户列表 -->
        {no_inventory_section}
        
        <!-- 有库存用户列表 -->
        {inventory_section}
        
        <!-- 错误用户列表 -->
        {error_section}
        
        <!-- 页脚 -->
        <div class="footer">
            <p>📱 Vinted 库存宝 - 智能库存管理系统</p>
            <p>采集耗时: {scraping_time:.1f} 秒</p>
        </div>
    </div>
</body>
</html>
        """
        
        # 计算百分比
        total = data['total_users']
        inventory_pct = round(data['percentage_with_inventory'], 1) if total > 0 else 0
        no_inventory_pct = round(data['percentage_without_inventory'], 1) if total > 0 else 0
        error_pct = round(data['percentage_with_errors'], 1) if total > 0 else 0
        
        # 生成管理员统计部分
        admin_section = self._generate_admin_section(data)
        
        # 生成用户列表部分
        no_inventory_section = self._generate_user_section(
            "🚨 已出库用户", data.get('no_inventory_users_data', []), "status-no-inventory"
        )
        
        inventory_section = self._generate_user_section(
            "✅ 有库存用户", data.get('inventory_users_data', []), "status-inventory"
        )
        
        error_section = self._generate_user_section(
            "⚠️ 检查失败用户", data.get('error_users_data', []), "status-error"
        )
        
        # 填充模板
        html_content = html_template.format(
            timestamp=data['timestamp'],
            total_users=data['total_users'],
            users_with_inventory=data['users_with_inventory'],
            users_without_inventory=data['users_without_inventory'],
            users_with_errors=data['users_with_errors'],
            inventory_percentage=inventory_pct,
            no_inventory_percentage=no_inventory_pct,
            error_percentage=error_pct,
            scraping_time=data['scraping_time'],
            admin_section=admin_section,
            no_inventory_section=no_inventory_section,
            inventory_section=inventory_section,
            error_section=error_section
        )
        
        return html_content
        
    def _generate_admin_section(self, data: Dict) -> str:
        """生成管理员统计部分"""
        admin_summary = data.get('admin_summary', {})
        if not admin_summary:
            return ""
            
        section_html = """
        <div class="section">
            <h2>👥 管理员统计</h2>
            <div class="user-grid">
        """
        
        for admin_name, summary in admin_summary.items():
            if 'error' in summary:
                status_html = f'<div class="user-status status-error">获取失败</div>'
                detail_html = f'<div style="color: #dc3545; margin-top: 10px;">错误: {summary["error"]}</div>'
            else:
                count = summary.get('following_count', 0)
                status_html = f'<div class="user-status status-inventory">关注 {count} 个用户</div>'
                detail_html = f'<div style="color: #666; margin-top: 10px;">URL: {summary.get("url", "")}</div>'
            
            section_html += f"""
                <div class="user-card">
                    <div class="user-name">{admin_name}</div>
                    {status_html}
                    {detail_html}
                </div>
            """
        
        section_html += """
            </div>
        </div>
        """
        
        return section_html
        
    def _generate_user_section(self, title: str, users: List, status_class: str) -> str:
        """生成用户列表部分"""
        if not users:
            return ""
            
        section_html = f"""
        <div class="section">
            <h2>{title}</h2>
            <div class="user-grid">
        """
        
        for user in users:
            admin_info = f" - {user.admin_name}" if hasattr(user, 'admin_name') and user.admin_name else ""
            
            if hasattr(user, 'item_count') and user.item_count > 0:
                status_text = f"商品数量: {user.item_count}"
            elif hasattr(user, 'error_message') and user.error_message:
                status_text = f"错误: {user.error_message}"
            else:
                status_text = "无库存"
            
            section_html += f"""
                <div class="user-card">
                    <div class="user-name">{user.username}</div>
                    <div class="user-admin">所属: {user.admin_name if hasattr(user, 'admin_name') else '未知'}</div>
                    <div class="user-status {status_class}">{status_text}</div>
                    <div style="margin-top: 10px; font-size: 0.9em; color: #666;">
                        <a href="{user.profile_url}" target="_blank" style="color: #007bff; text-decoration: none;">查看用户页面</a>
                    </div>
                </div>
            """
        
        section_html += """
            </div>
        </div>
        """
        
        return section_html
        
    def save_html_report(self, data: Dict, output_dir: str = "reports") -> str:
        """保存HTML报告"""
        # 创建输出目录
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # 生成文件名
        now = datetime.now()
        date_str = now.strftime("%m.%d")
        time_str = now.strftime("%H:%M")
        filename = f"Vinted库存报告_{date_str}-{time_str}.html"
        
        # 生成HTML内容
        html_content = self.generate_html_report(data)
        
        # 保存文件
        file_path = output_path / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
            
        return str(file_path)
        
    def convert_to_pdf(self, html_file: str) -> str:
        """将HTML转换为PDF"""
        try:
            import pdfkit
            
            # PDF文件路径
            pdf_file = html_file.replace('.html', '.pdf')
            
            # 配置选项
            options = {
                'page-size': 'A4',
                'margin-top': '0.75in',
                'margin-right': '0.75in',
                'margin-bottom': '0.75in',
                'margin-left': '0.75in',
                'encoding': "UTF-8",
                'no-outline': None,
                'enable-local-file-access': None
            }
            
            # 转换为PDF
            pdfkit.from_file(html_file, pdf_file, options=options)
            
            return pdf_file
            
        except ImportError:
            print("⚠️ 需要安装 pdfkit: pip install pdfkit")
            print("⚠️ 还需要安装 wkhtmltopdf: https://wkhtmltopdf.org/downloads.html")
            return html_file
        except Exception as e:
            print(f"⚠️ PDF转换失败: {e}")
            return html_file
