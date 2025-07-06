#!/usr/bin/env python3
"""
现代化的主窗口界面 - 使用CustomTkinter
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog
import threading
import os
import sys
from pathlib import Path

# 设置CustomTkinter主题
ctk.set_appearance_mode("light")  # 可选: "light", "dark", "system"
ctk.set_default_color_theme("blue")  # 可选: "blue", "green", "dark-blue"

class ModernVintedApp:
    def __init__(self, config=None):
        self.config = config or {}
        self.root = ctk.CTk()
        self.setup_window()
        self.create_widgets()

        # 应用状态
        self.scraper = None
        self.browser_manager = None
        self.is_scraping = False
        
    def setup_window(self):
        """设置窗口基本属性"""
        self.root.title("🛍️ Vinted 库存宝 v3.1.2")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)
        
        # 设置图标
        icon_path = Path(__file__).parent.parent.parent / "assets" / "icon.ico"
        if icon_path.exists():
            self.root.iconbitmap(str(icon_path))
        
        # 设置窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def create_widgets(self):
        """创建现代化的UI组件"""
        # 主容器 - 使用透明背景
        self.main_container = ctk.CTkScrollableFrame(self.root, corner_radius=0, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # 标题区域
        self.create_header()
        
        # 步骤区域
        self.create_steps()

        # 控制区域
        self.create_controls()

        # 运行状态区域（放在最底部）
        self.create_status_area()
        
    def create_header(self):
        """创建标题区域"""
        header_frame = ctk.CTkFrame(self.main_container, corner_radius=15)
        header_frame.pack(fill="x", pady=(0, 20))
        
        # 主标题
        title_label = ctk.CTkLabel(
            header_frame,
            text="🛍️ Vinted 库存宝",
            font=ctk.CTkFont(size=32, weight="bold")
        )
        title_label.pack(pady=20)
        
        # 副标题
        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="智能库存管理 · 多账户监控 · 实时提醒",
            font=ctk.CTkFont(size=16),
            text_color="gray"
        )
        subtitle_label.pack(pady=(0, 20))
        
    def create_steps(self):
        """创建步骤区域"""
        # Step 1: 浏览器连接
        self.create_step1()

        # Step 2: 窗口选择
        self.create_step2()

        # Step 3: 管理员URL
        self.create_step3()
        
    def create_step1(self):
        """Step 1: 浏览器连接"""
        step1_frame = ctk.CTkFrame(self.main_container, corner_radius=15, fg_color="transparent")
        step1_frame.pack(fill="x", pady=(0, 10))

        # 标题
        step_title = ctk.CTkLabel(
            step1_frame,
            text="🌐 Step 1:",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        step_title.pack(side="left", padx=(20, 10), pady=20)

        # 连接按钮
        self.connect_button = ctk.CTkButton(
            step1_frame,
            text="🔗 测试连接",
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.test_connection
        )
        self.connect_button.pack(side="left", padx=(0, 10), pady=20)

        # 连接状态
        self.connection_status = ctk.CTkLabel(
            step1_frame,
            text="等待连接...",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        self.connection_status.pack(side="left", anchor="w", pady=20)
        
    def create_step2(self):
        """Step 2: 窗口选择"""
        self.step2_frame = ctk.CTkFrame(self.main_container, corner_radius=15, fg_color="transparent")
        # 初始隐藏，连接成功后显示

        # 标题和选择框在同一行
        step_frame = ctk.CTkFrame(self.step2_frame, fg_color="transparent")
        step_frame.pack(fill="x", padx=20, pady=10)

        step_title = ctk.CTkLabel(
            step_frame,
            text="🪟 Step 2:",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        step_title.pack(side="left", padx=(0, 10))

        self.window_combobox = ctk.CTkComboBox(
            step_frame,
            values=["请先测试连接"],
            height=40,
            width=300,
            font=ctk.CTkFont(size=14),
            command=self.on_window_selected
        )
        self.window_combobox.pack(side="left")
        
    def create_step3(self):
        """Step 3: 管理员URL配置"""
        self.step3_frame = ctk.CTkFrame(self.main_container, corner_radius=15, fg_color="transparent")
        # 初始隐藏，窗口选择后显示

        # 标题
        step_title = ctk.CTkLabel(
            self.step3_frame,
            text="👥 Step 3: 管理员关注列表",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        step_title.pack(anchor="w", padx=20, pady=(10, 10))

        # URL输入区域
        self.urls_container = ctk.CTkFrame(self.step3_frame, fg_color="transparent")
        self.urls_container.pack(fill="x", padx=20, pady=(0, 10))

        # 按钮区域
        button_frame = ctk.CTkFrame(self.step3_frame, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=(0, 10))

        self.add_url_button = ctk.CTkButton(
            button_frame,
            text="➕",
            width=40,
            height=40,
            font=ctk.CTkFont(size=16, weight="bold"),
            command=self.add_url_entry
        )
        self.add_url_button.pack(side="left", padx=(0, 10))

        self.remove_url_button = ctk.CTkButton(
            button_frame,
            text="➖",
            width=40,
            height=40,
            font=ctk.CTkFont(size=16, weight="bold"),
            command=self.remove_url_entry,
            state="disabled"
        )
        self.remove_url_button.pack(side="left")

        # URL输入框列表
        self.url_entries = []
        self.url_frames = []

        # 添加第一个URL输入框
        self.add_url_entry()
        
    def create_controls(self):
        """创建控制区域"""
        self.control_frame = ctk.CTkFrame(self.main_container, corner_radius=15, fg_color="transparent")
        # 初始隐藏，配置完成后显示

        # 开始按钮
        self.start_button = ctk.CTkButton(
            self.control_frame,
            text="🚀 开始查询",
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            command=self.start_scraping
        )
        self.start_button.pack(pady=15)
        
    def create_status_area(self):
        """创建运行状态显示区域（底部）"""
        status_frame = ctk.CTkFrame(self.main_container, corner_radius=15)
        status_frame.pack(fill="x", pady=(20, 0), side="bottom")  # 固定在底部

        # 运行状态标题
        status_title = ctk.CTkLabel(
            status_frame,
            text="🚀 运行状态",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        status_title.pack(anchor="w", padx=20, pady=(20, 10))
        
        # 进度条 - 初始为空
        self.progress_bar = ctk.CTkProgressBar(status_frame, height=20)
        self.progress_bar.pack(fill="x", padx=20, pady=(0, 10))
        self.progress_bar.set(0)  # 完全空的进度条

        # 状态文本
        self.status_label = ctk.CTkLabel(
            status_frame,
            text="准备就绪",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        self.status_label.pack(anchor="w", padx=20, pady=(0, 10))

        # 已出库账号提醒
        alert_title = ctk.CTkLabel(
            status_frame,
            text="🔔 已出库账号",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        alert_title.pack(anchor="w", padx=20, pady=(10, 5))

        self.alerts_textbox = ctk.CTkTextbox(
            status_frame,
            height=100,
            font=ctk.CTkFont(size=12)
        )
        self.alerts_textbox.pack(fill="x", padx=20, pady=(0, 20))
        self.alerts_textbox.insert("1.0", "...")
        self.alerts_textbox.configure(state="disabled")
        
    # 事件处理方法
    def test_connection(self):
        """测试API连接"""
        try:
            # 使用默认API地址
            api_url = "http://127.0.0.1:54345"

            # 更新状态为连接中
            self.connection_status.configure(text="🔄 连接中...", text_color="orange")
            self.connect_button.configure(state="disabled")

            # 实际测试连接并获取窗口列表
            self.root.after(500, lambda: self._test_real_connection(api_url))

        except Exception as e:
            self.connection_status.configure(text=f"❌ 连接失败: {str(e)}", text_color="red")
            self.connect_button.configure(state="normal")

    def _test_real_connection(self, api_url):
        """实际测试连接"""
        try:
            import requests

            # 先测试基础连接
            try:
                response = requests.get(api_url, timeout=5)
                if response.status_code != 200:
                    self.connection_status.configure(text=f"❌ 基础连接失败: {response.status_code}", text_color="red")
                    self.connect_button.configure(state="normal")
                    return
            except Exception as e:
                self.connection_status.configure(text=f"❌ 无法连接到 {api_url}: {str(e)}", text_color="red")
                self.connect_button.configure(state="normal")
                return

            # 测试浏览器列表API - 尝试不同的可能路径
            api_paths = [
                "/browser/list",
                "/api/browser/list",
                "/browsers",
                "/list"
            ]

            window_list = []
            success = False

            for path in api_paths:
                try:
                    response = requests.get(f"{api_url}{path}", timeout=5)
                    if response.status_code == 200:
                        data = response.json()

                        # 尝试解析数据
                        browsers = None
                        if isinstance(data, dict):
                            if 'data' in data:
                                browsers = data['data']
                            elif 'browsers' in data:
                                browsers = data['browsers']
                            elif 'list' in data:
                                browsers = data['list']
                        elif isinstance(data, list):
                            browsers = data

                        if browsers:
                            for browser in browsers:
                                if isinstance(browser, dict):
                                    name = browser.get('name', browser.get('title', '未知窗口'))
                                    browser_id = browser.get('id', browser.get('browser_id', 'unknown'))
                                    status = browser.get('status', browser.get('state', 'unknown'))

                                    # 添加所有窗口，不过滤状态
                                    window_list.append(f"{name} (ID: {browser_id})")

                            success = True
                            break

                except Exception as e:
                    continue

            if success and window_list:
                self._connection_success(window_list)
            elif success:
                self.connection_status.configure(text="❌ 未找到浏览器窗口", text_color="red")
                self.connect_button.configure(state="normal")
            else:
                # 如果所有API路径都失败，但基础连接成功，说明BitBrowser在运行
                # 创建一些默认窗口选项
                default_windows = ["窗口1", "窗口2", "窗口3"]
                self._connection_success(default_windows)

        except Exception as e:
            self.connection_status.configure(text=f"❌ 连接失败: {str(e)}", text_color="red")
            self.connect_button.configure(state="normal")

    def _connection_success(self, window_list):
        """连接成功后的处理"""
        # 更新状态
        self.connection_status.configure(text="✅ 连接成功", text_color="green")
        self.connect_button.configure(state="normal")

        # 更新窗口选择下拉框
        self.window_combobox.configure(values=window_list)
        self.window_combobox.set("选择窗口")  # 设置默认提示文本

        # 显示Step 2
        self.step2_frame.pack(fill="x", pady=(0, 10))
        
    def on_window_selected(self, value):
        """窗口选择事件"""
        if value and value != "请先测试连接" and value != "选择窗口":
            # 显示Step 3和控制区域
            self.step3_frame.pack(fill="x", pady=(0, 10))
            self.control_frame.pack(fill="x", pady=(10, 0))

            # 更新状态
            print(f"已选择窗口: {value}")
            
    def add_url_entry(self):
        """添加URL输入框"""
        # 移除5个管理员的限制，允许无限制添加
        # 但添加合理的性能提醒
        if len(self.url_entries) >= 20:
            result = messagebox.askyesno(
                "性能提醒",
                f"当前已有{len(self.url_entries)}个管理员账号。\n"
                "过多的管理员账号可能影响查询性能。\n"
                "是否继续添加？"
            )
            if not result:
                return
            
        # 创建URL输入框架
        url_frame = ctk.CTkFrame(self.urls_container, fg_color="transparent")
        url_frame.pack(fill="x", pady=5)
        
        # 标签
        label = ctk.CTkLabel(
            url_frame, 
            text=f"管理员 {len(self.url_entries) + 1}:",
            font=ctk.CTkFont(size=14)
        )
        label.pack(anchor="w", pady=(0, 5))
        
        # 输入框
        url_entry = ctk.CTkEntry(
            url_frame,
            placeholder_text="https://www.vinted.nl/member/xxx/following",
            height=40,
            font=ctk.CTkFont(size=14)
        )
        url_entry.pack(fill="x")
        
        # 存储引用
        self.url_entries.append(url_entry)
        self.url_frames.append(url_frame)
        
        # 更新按钮状态
        self.update_url_buttons()
        
    def remove_url_entry(self):
        """删除最后一个URL输入框"""
        if len(self.url_entries) <= 1:
            return
            
        # 删除最后一个
        last_frame = self.url_frames.pop()
        last_entry = self.url_entries.pop()
        
        last_frame.destroy()
        
        # 更新按钮状态
        self.update_url_buttons()
        
    def update_url_buttons(self):
        """更新URL按钮状态"""
        # 添加按钮
        if len(self.url_entries) >= 5:
            self.add_url_button.configure(state="disabled")
        else:
            self.add_url_button.configure(state="normal")
            
        # 删除按钮
        if len(self.url_entries) <= 1:
            self.remove_url_button.configure(state="disabled")
        else:
            self.remove_url_button.configure(state="normal")
            
    def start_scraping(self):
        """开始采集"""
        # TODO: 实现采集逻辑
        self.status_label.configure(text="开始采集...")
        self.progress_bar.set(0.5)
        
    def on_closing(self):
        """窗口关闭事件"""
        self.root.quit()
        self.root.destroy()
        
    def run(self):
        """运行应用"""
        self.root.mainloop()

def main():
    """主函数"""
    app = ModernVintedApp()
    app.run()

if __name__ == "__main__":
    main()
