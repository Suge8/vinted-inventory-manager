#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主窗口模块

提供应用程序的主要用户界面。
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import os
import subprocess
import sys
import logging
from pathlib import Path

from .components import (
    ProgressFrame, LogFrame, ConfigFrame, 
    ButtonFrame, ThreadSafeGUI
)
from ..core.bitbrowser_api import BitBrowserManager
from ..core.vinted_scraper import VintedScraper
from ..core.data_processor import DataProcessor
from ..utils.logger import setup_gui_logger
from ..utils.config import ConfigManager
from ..utils.helpers import validate_vinted_url


class VintedInventoryApp:
    """Vinted库存管理应用程序主窗口"""
    
    def __init__(self, config: dict):
        """
        初始化应用程序
        
        Args:
            config: 应用配置
        """
        self.config = config
        self.config_manager = ConfigManager()
        
        # 初始化主窗口
        self.root = tk.Tk()
        self.setup_window()
        
        # 线程安全的GUI更新器
        self.gui_updater = ThreadSafeGUI(self.root)
        
        # 设置GUI日志
        self.setup_logging()
        
        # 创建UI组件
        self.create_widgets()
        
        # 应用状态
        self.is_running = False
        self.browser_manager = None
        self.scraper = None
        self.current_thread = None
        self.last_result_file = None
        
        # 加载保存的配置
        self.load_saved_config()
    
    def setup_window(self):
        """设置主窗口"""
        # 设置现代简洁的窗口标题
        self.root.title('Vinted.nl 库存宝')

        # 设置窗口大小 - 减小高度，保持无滚动条
        window_size = self.config.get('ui', {}).get('window_size', '850x750')
        self.root.geometry(window_size)

        # 设置最小窗口大小
        self.root.minsize(700, 650)
        
        # 设置窗口图标（如果存在）
        try:
            icon_path = Path(__file__).parent.parent.parent / "resources" / "app_icon.ico"
            if icon_path.exists():
                self.root.iconbitmap(str(icon_path))
        except Exception:
            pass
        
        # 设置关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def get_version(self) -> str:
        """获取应用程序版本号"""
        # 直接返回当前版本，避免打包后文件路径问题
        return "1.4.0"
    
    def setup_logging(self):
        """设置日志系统"""
        def log_callback(message):
            self.gui_updater.call_in_main_thread(self.log_frame.add_log, message)
        
        self.logger = setup_gui_logger(log_callback)
    
    def create_widgets(self):
        """创建步骤式UI组件 - 使用简单直接布局，不使用滚动"""
        # 创建主框架，直接在root上布局
        self.main_frame = ttk.Frame(self.root, padding="15")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # 创建步骤界面
        self.create_step_interface(self.main_frame)

    def create_step_interface(self, parent):
        """创建步骤式界面"""
        # 添加版本号角标
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, pady=(0, 15))

        version_label = ttk.Label(header_frame, text=f"v{self.get_version()}",
                                 foreground="gray", font=("Arial", 8))
        version_label.pack(side=tk.RIGHT)

        # Step 1: API配置
        self.step1_frame = ttk.LabelFrame(parent, text="🔧 Step 1", padding="10")
        self.step1_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(self.step1_frame, text="比特浏览器 API 地址：").pack(anchor=tk.W)
        self.api_url_var = tk.StringVar(value="http://127.0.0.1:54345")
        self.api_url_entry = ttk.Entry(self.step1_frame, textvariable=self.api_url_var, width=50)
        self.api_url_entry.pack(fill=tk.X, pady=(5, 0))

        # Step 2: 连接测试
        self.step2_frame = ttk.LabelFrame(parent, text="🔗 Step 2", padding="10")
        self.step2_frame.pack(fill=tk.X, pady=(0, 10))

        self.test_button = ttk.Button(self.step2_frame, text="🧪 测试连接", command=self.test_connection)
        self.test_button.pack(side=tk.LEFT)

        self.connection_status = ttk.Label(self.step2_frame, text="点击测试连接", foreground="blue")
        self.connection_status.pack(side=tk.LEFT, padx=(10, 0))

        # Step 3: 浏览器选择 (初始隐藏)
        self.step3_frame = ttk.LabelFrame(parent, text="🌐 Step 3", padding="10")
        # 不立即pack，等连接成功后显示

        window_select_frame = ttk.Frame(self.step3_frame)
        window_select_frame.pack(fill=tk.X)

        ttk.Label(window_select_frame, text="选择浏览器窗口：").pack(side=tk.LEFT)
        self.refresh_button = ttk.Button(window_select_frame, text="🔄 刷新列表", command=self.refresh_browser_list)
        self.refresh_button.pack(side=tk.RIGHT)

        self.window_var = tk.StringVar()
        self.window_combobox = ttk.Combobox(self.step3_frame, textvariable=self.window_var, state="readonly", width=60)
        self.window_combobox.pack(fill=tk.X, pady=(5, 0))

        self.window_status_label = ttk.Label(self.step3_frame, text="点击'刷新窗口列表'获取可用窗口", foreground="gray")
        self.window_status_label.pack(anchor=tk.W, pady=(5, 0))

        # 存储窗口数据
        self.browser_windows = []

        # Step 4: 关注列表URL
        self.step4_frame = ttk.LabelFrame(parent, text="📋 Step 4", padding="10")
        # 不立即pack，等窗口选择后显示

        ttk.Label(self.step4_frame, text="管理员关注列表 URL：").pack(anchor=tk.W)
        self.following_url_var = tk.StringVar()
        self.following_url_entry = ttk.Entry(self.step4_frame, textvariable=self.following_url_var, width=60)
        self.following_url_entry.pack(fill=tk.X, pady=(5, 0))

        # Step 5: 开始查询
        self.step5_frame = ttk.LabelFrame(parent, text="🚀 Step 5", padding="10")
        # 不立即pack，等URL填写后显示

        button_frame = ttk.Frame(self.step5_frame)
        button_frame.pack(fill=tk.X)

        self.start_button = ttk.Button(button_frame, text="🔍 开始查询", command=self.start_scraping, state="disabled")
        self.start_button.pack(side=tk.LEFT)

        self.query_status = ttk.Label(button_frame, text="请完成上述步骤", foreground="gray")
        self.query_status.pack(side=tk.LEFT, padx=(10, 0))

        # 进度框架 (在Step 5内部)
        self.progress_frame = ttk.Frame(self.step5_frame)
        self.progress_frame.pack(fill=tk.X, pady=(10, 0))

        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.progress_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X)

        self.progress_label = ttk.Label(self.progress_frame, text="准备就绪")
        self.progress_label.pack(anchor=tk.W, pady=(2, 0))

        # Step 6: 查询结果 (初始隐藏)
        self.step6_frame = ttk.LabelFrame(parent, text="📊 Step 6", padding="10")
        # 不立即pack，等查询完成后显示

        self.result_button = ttk.Button(self.step6_frame, text="📄 打开结果", command=self.open_result_file, state="disabled")
        self.result_button.pack(side=tk.LEFT)

        self.result_status = ttk.Label(self.step6_frame, text="查询完成后可查看结果", foreground="gray")
        self.result_status.pack(side=tk.LEFT, padx=(10, 0))

        # 不在这里创建日志区域，等到Step 5显示后再创建

        # 延迟设置监听器，避免初始化时触发
        self.root.after(100, self.setup_event_listeners)

    def setup_event_listeners(self):
        """设置事件监听器"""
        # 监听API地址变化
        self.api_url_var.trace('w', self.on_api_url_change)

        # 监听窗口选择变化
        self.window_var.trace('w', self.on_window_selection_change)

        # 监听URL变化
        self.following_url_var.trace('w', self.on_url_change)

    def create_bottom_log_area(self, parent):
        """创建底部的可折叠日志区域"""
        # 移除黑色分隔线，使用空白间距
        spacer = ttk.Frame(parent, height=20)
        spacer.pack(fill=tk.X)

        # 创建一个容器来保持布局稳定 - 修复：不使用side=tk.BOTTOM
        self.log_container = ttk.Frame(parent)
        self.log_container.pack(fill=tk.X, pady=(0, 10))

        # 日志控制框架 - 在容器内
        log_control_frame = ttk.Frame(self.log_container)
        log_control_frame.pack(fill=tk.X, pady=(0, 5))

        self.log_expanded = tk.BooleanVar(value=False)
        self.log_toggle_button = ttk.Button(log_control_frame, text="📋 显示日志", command=self.toggle_log_area)
        self.log_toggle_button.pack(side=tk.LEFT)

        # 添加日志状态标签
        self.log_status_label = ttk.Label(log_control_frame, text="点击查看详细运行日志", foreground="gray")
        self.log_status_label.pack(side=tk.LEFT, padx=(10, 0))

        # 日志框架容器 (用于稳定布局)
        self.log_frame_container = ttk.Frame(self.log_container)
        # 不立即pack

        # 日志框架 (初始隐藏)
        self.log_frame = LogFrame(self.log_frame_container)
        # 不立即pack，会在toggle时动态添加

    def toggle_log_area(self):
        """切换日志区域显示/隐藏"""
        if self.log_expanded.get():
            # 隐藏日志
            self.log_frame.pack_forget()
            self.log_frame_container.pack_forget()
            self.log_toggle_button.config(text="📋 显示日志")
            self.log_status_label.config(text="点击查看详细运行日志", foreground="gray")
            self.log_expanded.set(False)
            # 不改变窗口大小，保持布局稳定
        else:
            # 显示日志 - 在容器内展开
            self.log_frame_container.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
            self.log_frame.pack(fill=tk.BOTH, expand=True)
            self.log_toggle_button.config(text="📋 隐藏日志")
            self.log_status_label.config(text="运行日志已展开", foreground="green")
            self.log_expanded.set(True)
            # 只在必要时调整窗口大小
            current_height = self.root.winfo_height()
            if current_height < 600:
                self.root.geometry(f"{self.root.winfo_width()}x700")

    def on_api_url_change(self, *args):
        """API地址变化时的处理"""
        # 测试按钮始终可用，不受API地址限制
        self.test_button.config(state="normal")
        api_url = self.api_url_var.get().strip()
        if api_url and api_url.startswith('http'):
            self.connection_status.config(text="点击测试连接", foreground="blue")
        else:
            self.connection_status.config(text="点击测试连接", foreground="blue")

    def on_window_selection_change(self, *args):
        """窗口选择变化时的处理"""
        window_selected = bool(self.window_var.get())
        if window_selected:
            # 显示Step 4
            if not self.step4_frame.winfo_viewable():
                self.step4_frame.pack(fill=tk.X, pady=(0, 10))
        else:
            # 隐藏后续步骤
            self.step4_frame.pack_forget()
            self.step5_frame.pack_forget()
            self.step6_frame.pack_forget()

        self.check_can_start_query()

    def on_url_change(self, *args):
        """URL变化时的处理"""
        self.check_can_start_query()

    def check_can_start_query(self):
        """检查是否可以开始查询"""
        window_selected = bool(self.window_var.get())
        url_filled = bool(self.following_url_var.get().strip())

        if window_selected and url_filled:
            self.start_button.config(state="normal")
            self.query_status.config(text="可以开始查询", foreground="green")
            # 显示Step 5
            if not self.step5_frame.winfo_viewable():
                self.step5_frame.pack(fill=tk.X, pady=(0, 10))

                # 在Step 5显示后，创建日志区域并放在最底部
                if not hasattr(self, 'log_container'):
                    self.create_bottom_log_area(self.main_frame)
        else:
            self.start_button.config(state="disabled")
            if not window_selected:
                self.query_status.config(text="请选择浏览器窗口", foreground="gray")
            elif not url_filled:
                self.query_status.config(text="请填写关注列表URL", foreground="gray")

    def refresh_browser_list(self):
        """刷新浏览器窗口列表"""
        try:
            # 获取API配置
            api_url = self.api_url_var.get().strip()
            if not api_url:
                self.window_status_label.config(text="请先输入API地址", foreground="red")
                return

            # 导入API类
            from ..core.bitbrowser_api import BitBrowserAPI

            # 创建API实例并获取窗口列表
            api = BitBrowserAPI(api_url)
            browser_list = api.get_browser_list()

            if not browser_list:
                self.window_status_label.config(text="未找到可用的浏览器窗口", foreground="orange")
                self.window_combobox['values'] = []
                self.browser_windows = []
                return

            # 更新窗口列表
            self.browser_windows = browser_list
            window_options = []

            for i, window in enumerate(browser_list, 1):
                window_name = window.get('name', f'窗口{i}')
                window_id = window.get('id', 'unknown')
                status = "关闭" if window.get('status', 0) == 0 else "打开"
                option = f"{i}. {window_name} (ID: {window_id[:8]}...) [{status}]"
                window_options.append(option)

            self.window_combobox['values'] = window_options
            if window_options:
                self.window_combobox.current(0)  # 默认选择第一个
                self.window_status_label.config(text=f"找到 {len(browser_list)} 个浏览器窗口", foreground="green")

        except Exception as e:
            self.window_status_label.config(text=f"获取窗口列表失败: {str(e)}", foreground="red")
            self.window_combobox['values'] = []
            self.browser_windows = []

    def get_selected_window_id(self) -> str:
        """获取选中窗口的ID"""
        try:
            selection = self.window_var.get()
            if not selection or not self.browser_windows:
                return ""

            # 从选择文本中提取序号
            window_index = int(selection.split('.')[0]) - 1
            if 0 <= window_index < len(self.browser_windows):
                return self.browser_windows[window_index].get('id', '')
            return ""
        except:
            return ""
    
    def load_saved_config(self):
        """加载保存的配置"""
        try:
            saved_config = self.config_manager.load_config()

            # 设置UI配置
            self.api_url_var.set(saved_config.get('bitbrowser', {}).get('api_url', 'http://127.0.0.1:54345'))
            self.following_url_var.set(saved_config.get('last_following_url', ''))

            # 如果有保存的窗口选择，尝试恢复
            window_selection = saved_config.get('bitbrowser', {}).get('window_selection', '')
            if window_selection:
                self.window_var.set(window_selection)

            self.logger.info("已加载保存的配置")

        except Exception as e:
            self.logger.warning(f"加载配置失败: {str(e)}")

    def save_current_config(self):
        """保存当前配置"""
        try:
            # 更新配置
            self.config['bitbrowser']['api_url'] = self.api_url_var.get().strip()
            self.config['bitbrowser']['window_id'] = self.get_selected_window_id()
            self.config['bitbrowser']['window_selection'] = self.window_var.get()
            self.config['last_following_url'] = self.following_url_var.get().strip()

            # 保存到文件
            self.config_manager.save_config(self.config)

        except Exception as e:
            self.logger.error(f"保存配置失败: {str(e)}")
    
    def test_connection(self):
        """测试比特浏览器连接"""
        try:
            # 验证API地址
            api_url = self.api_url_var.get().strip()
            if not api_url:
                self.connection_status.config(text="请输入API地址", foreground="red")
                return

            if not api_url.startswith('http'):
                self.connection_status.config(text="API地址必须以http://或https://开头", foreground="red")
                return

            self.connection_status.config(text="正在测试连接...", foreground="blue")
            self.test_button.config(state="disabled")

            # 创建API实例测试连接
            from ..core.bitbrowser_api import BitBrowserAPI
            api = BitBrowserAPI(api_url)

            # 测试连接
            success, message = api.test_connection()

            if success:
                self.connection_status.config(text="✓ 连接成功", foreground="green")
                self.logger.info("✓ 比特浏览器连接测试成功")

                # 显示Step 3（浏览器窗口选择）
                self.step3_frame.pack(fill=tk.X, pady=(0, 10))

                # 自动刷新窗口列表
                self.refresh_browser_list()

            else:
                self.connection_status.config(text=f"✗ 连接失败: {message}", foreground="red")
                self.logger.error(f"✗ 比特浏览器连接测试失败: {message}")

                # 隐藏后续步骤
                self.step3_frame.pack_forget()
                self.step4_frame.pack_forget()
                self.step5_frame.pack_forget()
                self.step6_frame.pack_forget()

            self.test_button.config(state="normal")

        except Exception as e:
            error_msg = f"连接测试异常: {str(e)}"
            self.connection_status.config(text=f"✗ 测试异常: {str(e)}", foreground="red")
            self.logger.error(error_msg)
            self.test_button.config(state="normal")

            # 隐藏后续步骤
            self.step3_frame.pack_forget()
            self.step4_frame.pack_forget()
            self.step5_frame.pack_forget()
            self.step6_frame.pack_forget()


    def start_scraping(self):
        """开始库存查询"""
        if self.is_running:
            # 如果正在运行，则停止查询
            self.stop_scraping()
            return

        try:
            # 验证配置
            api_url = self.api_url_var.get().strip()
            window_id = self.get_selected_window_id()
            following_url = self.following_url_var.get().strip()

            if not api_url:
                self.query_status.config(text="请输入API地址", foreground="red")
                return

            if not window_id:
                self.query_status.config(text="请选择浏览器窗口", foreground="red")
                return

            if not following_url:
                self.query_status.config(text="请输入关注列表URL", foreground="red")
                return

            # 验证URL
            url_valid, url_message = validate_vinted_url(following_url)
            if not url_valid:
                self.query_status.config(text=f"URL错误: {url_message}", foreground="red")
                return

            # 构建配置
            config = {
                'api_url': api_url,
                'window_id': window_id,
                'following_url': following_url
            }

            # 保存配置
            self.save_current_config()

            # 更新UI状态
            self.set_running_state(True)
            self.progress_var.set(0)
            self.progress_label.config(text="正在初始化...")

            # 在新线程中执行采集
            self.current_thread = threading.Thread(
                target=self._scraping_worker,
                args=(config,),
                daemon=True
            )
            self.current_thread.start()
            
        except Exception as e:
            error_msg = f"启动查询失败: {str(e)}"
            self.logger.error(error_msg)
            messagebox.showerror("启动错误", error_msg)
            self.set_running_state(False)
    
    def _scraping_worker(self, config: dict):
        """采集工作线程"""
        try:
            self.logger.info("=" * 50)
            self.logger.info("开始库存查询任务")
            self.logger.info("=" * 50)
            
            # 初始化浏览器管理器
            self.logger.info("正在初始化浏览器环境...")
            self.config['bitbrowser']['api_url'] = config['api_url']
            self.browser_manager = BitBrowserManager(self.config['bitbrowser'])
            
            success, message = self.browser_manager.initialize(config['window_id'])
            if not success:
                raise Exception(f"浏览器初始化失败: {message}")
            
            self.logger.info("✓ 浏览器环境初始化成功")
            
            # 创建采集器
            driver = self.browser_manager.get_driver()
            self.scraper = VintedScraper(driver, self.config['vinted'])
            
            # 设置回调函数
            def progress_callback(current, total, message):
                progress_percent = (current / total * 100) if total > 0 else 0
                self.gui_updater.call_in_main_thread(
                    self.update_progress,
                    progress_percent, message
                )

            def status_callback(message):
                self.logger.info(message)

            self.scraper.set_callbacks(progress_callback, status_callback)
            
            # 开始采集
            self.logger.info(f"开始采集关注列表: {config['following_url']}")
            result = self.scraper.scrape_all_users(config['following_url'])
            
            # 生成报告
            self.logger.info("正在生成报告...")
            data_processor = DataProcessor(self.config)
            report_file = data_processor.generate_report(result)
            
            # 保存结果文件路径
            self.last_result_file = report_file
            
            # 显示结果摘要
            stats = data_processor.get_summary_stats(result)
            self.logger.info("=" * 30)
            self.logger.info("查询结果摘要:")
            self.logger.info(f"- 总用户数: {stats['total_users']}")
            self.logger.info(f"- 有库存用户: {stats['users_with_inventory']}")
            self.logger.info(f"- 无库存用户: {stats['users_without_inventory']}")
            self.logger.info(f"- 访问失败: {stats['users_with_errors']}")
            self.logger.info(f"- 成功率: {stats['success_rate']:.1f}%")
            self.logger.info(f"- 总商品数: {stats['total_items']}")
            self.logger.info(f"- 报告文件: {report_file}")
            self.logger.info("=" * 30)
            
            # 更新UI - 显示Step 6和结果按钮
            def show_result_step():
                self.step6_frame.pack(fill=tk.X, pady=(0, 10))
                self.result_button.config(state="normal")
                self.result_status.config(text="查询完成，可查看结果", foreground="green")
                self.progress_var.set(100)
                self.progress_label.config(text="查询完成")

            self.gui_updater.call_in_main_thread(show_result_step)

            # 询问是否打开报告文件
            def ask_open_file():
                if messagebox.askyesno("查询完成", f"库存查询已完成！\n\n报告已保存到:\n{report_file}\n\n是否现在打开报告文件？"):
                    self.open_result_file()

            self.gui_updater.call_in_main_thread(ask_open_file)
            
        except Exception as e:
            error_msg = f"查询过程失败: {str(e)}"
            self.logger.error(error_msg)
            self.gui_updater.call_in_main_thread(
                messagebox.showerror, "查询错误", error_msg
            )
        
        finally:
            # 清理资源
            try:
                if self.scraper:
                    self.scraper.stop_scraping()
                if self.browser_manager:
                    self.browser_manager.cleanup()
            except Exception as e:
                self.logger.error(f"清理资源失败: {str(e)}")
            
            # 更新UI状态
            self.gui_updater.call_in_main_thread(self.set_running_state, False)

    def stop_scraping(self):
        """停止库存查询"""
        if not self.is_running:
            return

        try:
            self.logger.info("用户请求停止查询...")

            # 停止采集器
            if self.scraper:
                self.scraper.stop_scraping()

            # 等待线程结束（最多5秒）
            if self.current_thread and self.current_thread.is_alive():
                self.current_thread.join(timeout=5)

            self.logger.info("查询已停止")

        except Exception as e:
            self.logger.error(f"停止查询失败: {str(e)}")

    def open_result_file(self):
        """打开结果文件"""
        if not self.last_result_file or not os.path.exists(self.last_result_file):
            messagebox.showwarning("警告", "没有可用的结果文件")
            return

        try:
            # 根据操作系统选择打开方式
            if sys.platform.startswith('win'):
                os.startfile(self.last_result_file)
            elif sys.platform.startswith('darwin'):  # macOS
                subprocess.run(['open', self.last_result_file])
            else:  # Linux
                subprocess.run(['xdg-open', self.last_result_file])

            self.logger.info(f"已打开结果文件: {self.last_result_file}")

        except Exception as e:
            error_msg = f"打开文件失败: {str(e)}"
            self.logger.error(error_msg)
            messagebox.showerror("打开文件", error_msg)

    def show_about(self):
        """显示关于对话框"""
        about_text = """Vinted.nl 库存管理系统 v1.0

一个针对 vinted.nl 网站的自动化库存管理解决方案。

主要功能：
• 自动化数据采集
• 多账户库存管理
• 智能状态分类
• 详细报告生成

技术支持：
• 比特浏览器 API 集成
• Selenium WebDriver 自动化
• 用户友好的图形界面

开发团队：Vinted Inventory Team
版本：1.0.0
发布日期：2025-06-02

© 2025 保留所有权利"""

        messagebox.showinfo("关于", about_text)

    def set_running_state(self, running: bool):
        """设置运行状态"""
        self.is_running = running

        if running:
            # 运行状态：禁用前面的步骤，显示停止按钮
            self.test_button.config(state="disabled")
            self.refresh_button.config(state="disabled")
            self.start_button.config(text="停止查询", state="normal")
            self.query_status.config(text="查询进行中...", foreground="blue")
        else:
            # 停止状态：恢复按钮状态
            self.test_button.config(state="normal")
            self.refresh_button.config(state="normal")
            self.start_button.config(text="开始查询")
            self.check_can_start_query()  # 重新检查是否可以开始查询

    def update_progress(self, percent: float, message: str):
        """更新进度显示"""
        self.progress_var.set(percent)
        self.progress_label.config(text=message)

    def on_closing(self):
        """窗口关闭事件"""
        if self.is_running:
            if messagebox.askyesno("确认退出", "查询正在进行中，确定要退出吗？"):
                self.stop_scraping()
                # 等待一下让停止操作完成
                self.root.after(1000, self.root.destroy)
            return

        try:
            # 保存当前配置
            self.save_current_config()

            # 清理资源
            if self.browser_manager:
                self.browser_manager.cleanup()

        except Exception as e:
            self.logger.error(f"退出时清理失败: {str(e)}")

        self.root.destroy()

    def run(self):
        """运行应用程序"""
        try:
            self.logger.info("Vinted.nl 库存管理系统启动")
            self.logger.info("请配置比特浏览器API地址和关注列表URL，然后点击'测试连接'")

            # 启动主循环
            self.root.mainloop()

        except Exception as e:
            self.logger.error(f"应用程序运行失败: {str(e)}")
            messagebox.showerror("运行错误", f"应用程序运行失败: {str(e)}")

        finally:
            # 确保清理资源
            try:
                if hasattr(self, 'browser_manager') and self.browser_manager:
                    self.browser_manager.cleanup()
            except Exception:
                pass
