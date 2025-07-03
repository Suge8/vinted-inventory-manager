#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GUI组件模块

提供各种可复用的GUI组件。
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
from typing import Callable, Optional, Any
import threading
import queue


class ProgressFrame(ttk.Frame):
    """进度显示框架"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.setup_ui()
    
    def setup_ui(self):
        """设置UI"""
        # 进度标签
        self.progress_label = ttk.Label(self, text="准备就绪")
        self.progress_label.pack(fill=tk.X, pady=(0, 5))
        
        # 进度条
        self.progress_bar = ttk.Progressbar(
            self, 
            mode='determinate',
            length=400
        )
        self.progress_bar.pack(fill=tk.X)
        
        # 百分比标签
        self.percentage_label = ttk.Label(self, text="0%")
        self.percentage_label.pack(fill=tk.X, pady=(5, 0))
    
    def update_progress(self, current: int, total: int, message: str = ""):
        """更新进度"""
        if total > 0:
            percentage = (current / total) * 100
            self.progress_bar['value'] = percentage
            self.percentage_label.config(text=f"{percentage:.1f}% ({current}/{total})")
        else:
            self.progress_bar['value'] = 0
            self.percentage_label.config(text="0%")
        
        if message:
            self.progress_label.config(text=message)
    
    def reset(self):
        """重置进度"""
        self.progress_bar['value'] = 0
        self.percentage_label.config(text="0%")
        self.progress_label.config(text="准备就绪")


class LogFrame(ttk.Frame):
    """日志显示框架"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.setup_ui()
        self.max_lines = 1000  # 最大日志行数
    
    def setup_ui(self):
        """设置UI"""
        # 标题
        title_label = ttk.Label(self, text="状态日志：")
        title_label.pack(anchor=tk.W, pady=(0, 5))
        
        # 日志文本框
        self.log_text = scrolledtext.ScrolledText(
            self,
            height=12,
            wrap=tk.WORD,
            state=tk.DISABLED,
            font=('Consolas', 9)
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # 移除按钮框架，简化界面
    
    def add_log(self, message: str):
        """添加日志消息"""
        self.log_text.config(state=tk.NORMAL)
        
        # 检查行数限制
        lines = self.log_text.get('1.0', tk.END).count('\n')
        if lines > self.max_lines:
            # 删除最早的日志行
            self.log_text.delete('1.0', '2.0')
        
        # 添加新消息
        self.log_text.insert(tk.END, message + '\n')
        self.log_text.see(tk.END)  # 滚动到底部
        self.log_text.config(state=tk.DISABLED)
    



class ConfigFrame(ttk.LabelFrame):
    """配置设置框架"""
    
    def __init__(self, parent, title="配置设置", **kwargs):
        super().__init__(parent, text=title, **kwargs)
        self.setup_ui()
    
    def setup_ui(self):
        """设置UI"""
        # 比特浏览器API地址
        api_frame = ttk.Frame(self)
        api_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(api_frame, text="比特浏览器 API 地址：").pack(anchor=tk.W)
        self.api_url_var = tk.StringVar(value="http://127.0.0.1:54345")
        self.api_url_entry = ttk.Entry(api_frame, textvariable=self.api_url_var, width=50)
        self.api_url_entry.pack(fill=tk.X, pady=(2, 0))
        
        # 浏览器窗口选择
        window_frame = ttk.Frame(self)
        window_frame.pack(fill=tk.X, pady=5)

        window_label_frame = ttk.Frame(window_frame)
        window_label_frame.pack(fill=tk.X)

        ttk.Label(window_label_frame, text="选择浏览器窗口：").pack(side=tk.LEFT)
        self.refresh_button = ttk.Button(window_label_frame, text="刷新窗口列表", command=self.refresh_browser_list)
        self.refresh_button.pack(side=tk.RIGHT)

        # 窗口选择下拉框
        self.window_var = tk.StringVar()
        self.window_combobox = ttk.Combobox(window_frame, textvariable=self.window_var, state="readonly", width=47)
        self.window_combobox.pack(fill=tk.X, pady=(2, 0))

        # 窗口列表状态标签
        self.window_status_label = ttk.Label(window_frame, text="点击'刷新窗口列表'获取可用窗口", foreground="gray")
        self.window_status_label.pack(anchor=tk.W, pady=(2, 0))

        # 存储窗口数据
        self.browser_windows = []

        # 管理员关注列表URL
        url_frame = ttk.Frame(self)
        url_frame.pack(fill=tk.X, pady=5)

        ttk.Label(url_frame, text="管理员关注列表 URL：").pack(anchor=tk.W)
        self.following_url_var = tk.StringVar()
        self.following_url_entry = ttk.Entry(url_frame, textvariable=self.following_url_var, width=50)
        self.following_url_entry.pack(fill=tk.X, pady=(2, 0))

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
                status = window.get('status', 'unknown')
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
    
    def get_config(self) -> dict:
        """获取配置信息"""
        return {
            'api_url': self.api_url_var.get().strip(),
            'window_id': self.get_selected_window_id(),
            'window_selection': self.window_var.get(),
            'following_url': self.following_url_var.get().strip()
        }
    
    def set_config(self, config: dict):
        """设置配置信息"""
        self.api_url_var.set(config.get('api_url', 'http://127.0.0.1:54345'))
        # 如果有保存的窗口选择，恢复它
        if config.get('window_selection'):
            self.window_var.set(config.get('window_selection'))
        self.following_url_var.set(config.get('following_url', ''))
    
    def validate_config(self) -> tuple:
        """验证配置"""
        config = self.get_config()
        
        if not config['api_url']:
            return False, "请输入比特浏览器API地址"
        
        if not config['api_url'].startswith('http'):
            return False, "API地址必须以http://或https://开头"
        
        if not config['window_id']:
            return False, "请选择一个浏览器窗口"
        
        if not config['following_url']:
            return False, "请输入管理员关注列表URL"
        
        if 'vinted.nl' not in config['following_url']:
            return False, "URL必须是vinted.nl域名"
        
        if '/following/' not in config['following_url']:
            return False, "URL必须是关注列表页面"
        
        return True, "配置验证通过"


class ButtonFrame(ttk.Frame):
    """按钮框架"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.setup_ui()
        self.callbacks = {}
    
    def setup_ui(self):
        """设置UI"""
        # 第一行按钮
        row1 = ttk.Frame(self)
        row1.pack(fill=tk.X, pady=5)
        
        self.test_button = ttk.Button(row1, text="测试连接", state=tk.NORMAL)
        self.test_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.start_button = ttk.Button(row1, text="开始库存查询", state=tk.NORMAL)
        self.start_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.stop_button = ttk.Button(row1, text="停止", state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # 第二行按钮
        row2 = ttk.Frame(self)
        row2.pack(fill=tk.X, pady=5)
        
        self.open_result_button = ttk.Button(row2, text="打开结果文件", state=tk.DISABLED)
        self.open_result_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.about_button = ttk.Button(row2, text="关于")
        self.about_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.exit_button = ttk.Button(row2, text="退出")
        self.exit_button.pack(side=tk.LEFT, padx=(0, 5))
    
    def set_callback(self, button_name: str, callback: Callable):
        """设置按钮回调函数"""
        self.callbacks[button_name] = callback
        
        button_map = {
            'test': self.test_button,
            'start': self.start_button,
            'stop': self.stop_button,
            'open_result': self.open_result_button,
            'about': self.about_button,
            'exit': self.exit_button
        }
        
        if button_name in button_map:
            button_map[button_name].config(command=callback)
    
    def set_button_state(self, button_name: str, state: str):
        """设置按钮状态"""
        button_map = {
            'test': self.test_button,
            'start': self.start_button,
            'stop': self.stop_button,
            'open_result': self.open_result_button,
            'about': self.about_button,
            'exit': self.exit_button
        }
        
        if button_name in button_map:
            button_map[button_name].config(state=state)


class ThreadSafeGUI:
    """线程安全的GUI更新器"""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.queue = queue.Queue()
        self.check_queue()
    
    def check_queue(self):
        """检查队列中的更新任务"""
        try:
            while True:
                task = self.queue.get_nowait()
                task()
        except queue.Empty:
            pass
        
        # 每100ms检查一次队列
        self.root.after(100, self.check_queue)
    
    def call_in_main_thread(self, func: Callable, *args, **kwargs):
        """在主线程中调用函数"""
        def task():
            func(*args, **kwargs)
        
        self.queue.put(task)
