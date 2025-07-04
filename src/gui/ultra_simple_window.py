#!/usr/bin/env python3
"""
极简化的主窗口界面 - 每次只显示当前需要的内容
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import threading
import requests
from pathlib import Path
import logging
import os
from ..core.bitbrowser_api import BitBrowserManager
from ..core.vinted_scraper import VintedScraper

# 设置CustomTkinter主题
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

class UltraSimpleVintedApp:
    def __init__(self, config=None):
        try:
            self.config = config or {}
            self.logger = logging.getLogger(__name__)

            # 初始化tkinter
            self.root = ctk.CTk()
            self.setup_window()

            # 应用状态
            self.current_step = "connect"  # connect, select_windows, input_urls, running
            self.selected_windows = []  # 改为多选窗口
            self.selected_window_ids = []  # 存储选中窗口的ID列表
            self.current_window_index = 0  # 当前使用的窗口索引
            self.window_list = []
            self.window_data = []  # 存储完整的窗口数据
            self.url_entries = []
            self.is_running = False
            self.interval_minutes = 5  # 默认间隔5分钟

            # 浏览器管理器
            self.browser_manager = None
            self.scraper = None

            # 已出库账号列表（持久保存）
            self.persistent_out_of_stock = []

            # 创建界面
            self.create_ui()

        except Exception as e:
            self.logger.error(f"应用初始化失败: {str(e)}")
            try:
                import tkinter as tk
                from tkinter import messagebox
                root = tk.Tk()
                root.withdraw()
                messagebox.showerror("初始化错误", f"应用初始化失败:\n{str(e)}")
                root.destroy()
            except:
                pass
            raise
        
    def setup_window(self):
        """设置窗口基本属性"""
        self.root.title("Vinted 库存宝")  # 去掉版本号
        self.root.geometry("650x500")  # 合适的宽高比
        self.root.minsize(600, 450)    # 最小尺寸

        # 完全去掉窗口图标（避免渲染问题）
        self._create_empty_icon()
        
        # 设置窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def _create_empty_icon(self):
        """创建并设置空图标"""
        try:
            # 最简单的方法：设置为空字符串
            self.root.iconbitmap('')
            self.root.wm_iconbitmap('')
        except:
            try:
                # 创建一个1x1透明图标
                import tkinter as tk
                empty_icon = tk.PhotoImage(width=1, height=1)
                empty_icon.put("", (0, 0))
                self.root.iconphoto(True, empty_icon)
            except:
                pass
        
    def create_ui(self):
        """创建极简UI"""
        # 主容器 - 减少边距
        self.main_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # 标题区域 - 包含logo和文字
        title_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        title_frame.pack(pady=(0, 15))

        # 尝试加载logo
        try:
            from PIL import Image
            import sys

            # 获取资源路径（支持PyInstaller打包）
            def get_resource_path(relative_path):
                """获取资源文件路径，支持开发环境和打包环境"""
                try:
                    # PyInstaller打包后的临时目录
                    base_path = sys._MEIPASS
                except AttributeError:
                    # 开发环境
                    base_path = os.path.abspath(".")
                return os.path.join(base_path, relative_path)

            # 尝试多个可能的logo路径
            logo_paths = [
                get_resource_path("assets/icon_64.png"),
                get_resource_path("assets/icon_32.png"),
                get_resource_path("assets/icon.png"),
                "assets/icon_64.png",
                "assets/icon_32.png",
                "assets/icon.png",
                "../assets/icon_64.png",
                "../assets/icon_32.png",
                "../assets/icon.png"
            ]

            logo_loaded = False
            for logo_path in logo_paths:
                if os.path.exists(logo_path):
                    try:
                        logo_image = Image.open(logo_path)
                        logo_photo = ctk.CTkImage(light_image=logo_image, dark_image=logo_image, size=(32, 32))

                        self.logo_label = ctk.CTkLabel(
                            title_frame,
                            image=logo_photo,
                            text=""
                        )
                        self.logo_label.pack(side="left", padx=(0, 10))
                        logo_loaded = True
                        print(f"✅ 成功加载logo: {logo_path}")
                        break
                    except Exception as e:
                        print(f"尝试加载 {logo_path} 失败: {e}")
                        continue

            if not logo_loaded:
                print(f"❌ 所有logo路径都加载失败")
                print(f"当前工作目录: {os.getcwd()}")
                print(f"assets目录存在: {os.path.exists('assets')}")
                if hasattr(sys, '_MEIPASS'):
                    print(f"PyInstaller临时目录: {sys._MEIPASS}")
                    print(f"临时目录assets存在: {os.path.exists(os.path.join(sys._MEIPASS, 'assets'))}")

        except Exception as e:
            print(f"加载logo时出错: {e}")

        # 标题文字
        self.title_label = ctk.CTkLabel(
            title_frame,
            text="Vinted 库存宝",
            font=ctk.CTkFont(size=22, weight="bold")
        )
        self.title_label.pack(side="left")

        # 内容区域（动态变化）
        self.content_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True)

        # 版本号标签 - 放在右下角
        self.version_label = ctk.CTkLabel(
            self.main_frame,
            text="v4.3.0",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        )
        self.version_label.place(relx=0.98, rely=0.98, anchor="se")

        # 显示初始界面
        self.show_connect_step()
        
    def clear_content(self):
        """清空内容区域"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
            
    def show_connect_step(self):
        """显示连接测试步骤"""
        self.clear_content()
        self.current_step = "connect"
        
        # 居中的连接按钮
        connect_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        connect_frame.pack(expand=True)
        
        self.connect_button = ctk.CTkButton(
            connect_frame,
            text="🔗 测试连接",
            height=50,
            width=200,
            font=ctk.CTkFont(size=16, weight="bold"),
            command=self.test_connection
        )
        self.connect_button.pack(pady=20)
        
        # 连接状态
        self.connection_status = ctk.CTkLabel(
            connect_frame,
            text="",
            font=ctk.CTkFont(size=14)
        )
        self.connection_status.pack(pady=10)
        
    def show_window_selection(self):
        """显示多窗口选择步骤"""
        self.clear_content()
        self.current_step = "select_windows"

        # 主容器
        main_container = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        main_container.pack(fill="both", expand=True)

        # 标题 - 更小
        title = ctk.CTkLabel(
            main_container,
            text="选择浏览器窗口（至少2个）",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        title.pack(pady=(0, 10))

        # 窗口选择区域 - 带滚动条的容器
        window_container = ctk.CTkFrame(main_container, fg_color="gray90", corner_radius=8)
        window_container.pack(fill="both", expand=True, pady=(0, 10))

        # 创建滚动框架
        scrollable_frame = ctk.CTkScrollableFrame(
            window_container,
            width=580,
            height=200,  # 限制高度，超出时显示滚动条
            fg_color="transparent"
        )
        scrollable_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # 创建复选框列表 - 在滚动框架内
        self.window_checkboxes = []
        for i, window_display in enumerate(self.window_list):
            checkbox = ctk.CTkCheckBox(
                scrollable_frame,
                text=window_display,
                font=ctk.CTkFont(size=11),
                width=500
            )
            checkbox.pack(pady=3, anchor="w", padx=5)
            self.window_checkboxes.append(checkbox)

        # 间隔时间设置 - 紧凑
        interval_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        interval_frame.pack(pady=10)

        interval_label = ctk.CTkLabel(
            interval_frame,
            text="间隔时间（分钟）:",
            font=ctk.CTkFont(size=12)
        )
        interval_label.pack(side="left", padx=(0, 8))

        self.interval_entry = ctk.CTkEntry(
            interval_frame,
            width=60,
            height=28,
            font=ctk.CTkFont(size=12),
            justify="center"
        )
        self.interval_entry.pack(side="left")
        self.interval_entry.insert(0, "5")

        # 按钮区域 - 始终固定在底部，不受滚动影响
        button_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        button_frame.pack(side="bottom", fill="x", pady=15)

        # 上一步按钮
        back_button = ctk.CTkButton(
            button_frame,
            text="← 上一步",
            width=80,
            height=32,
            font=ctk.CTkFont(size=12),
            command=self.show_connect_step
        )
        back_button.pack(side="left", padx=(0, 15))

        # 确认按钮
        confirm_button = ctk.CTkButton(
            button_frame,
            text="✅ 确认",
            width=80,
            height=32,
            font=ctk.CTkFont(size=12),
            command=self.confirm_window_selection
        )
        confirm_button.pack(side="left")
        
    def show_url_input(self):
        """显示用户ID输入步骤"""
        self.clear_content()
        self.current_step = "input_urls"

        # ID输入区域
        id_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        id_frame.pack(expand=True, fill="both")

        # ID输入区域
        self.url_container = ctk.CTkFrame(id_frame, fg_color="transparent")
        self.url_container.pack(fill="both", expand=True, pady=20)

        # 添加第一个ID输入框
        self.url_entries = []
        self.add_url_entry()

        # 按钮区域
        button_frame = ctk.CTkFrame(id_frame, fg_color="transparent")
        button_frame.pack(pady=20)

        # 添加/删除按钮
        add_button = ctk.CTkButton(
            button_frame,
            text="➕",
            width=40,
            command=self.add_url_entry
        )
        add_button.pack(side="left", padx=(0, 5))

        remove_button = ctk.CTkButton(
            button_frame,
            text="➖",
            width=40,
            command=self.remove_url_entry
        )
        remove_button.pack(side="left", padx=(0, 20))

        # 上一步按钮
        back_button = ctk.CTkButton(
            button_frame,
            text="← 上一步",
            width=100,
            command=self.show_window_selection
        )
        back_button.pack(side="left", padx=(0, 10))

        # 开始查询按钮
        start_button = ctk.CTkButton(
            button_frame,
            text="🚀 开始查询",
            width=120,
            command=self.start_query
        )
        start_button.pack(side="left")
        
    def show_running_status(self):
        """显示循环运行状态"""
        self.clear_content()
        self.current_step = "running"

        # 运行状态区域
        status_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        status_frame.pack(expand=True, fill="both")

        # 当前状态显示
        current_status_frame = ctk.CTkFrame(status_frame, fg_color="transparent")
        current_status_frame.pack(fill="x", pady=(0, 20))

        # 当前窗口信息
        self.current_window_label = ctk.CTkLabel(
            current_status_frame,
            text=f"当前窗口: {self.selected_windows[0] if self.selected_windows else '未知'}",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.current_window_label.pack(pady=5)

        # 查询状态
        self.status_label = ctk.CTkLabel(
            current_status_frame,
            text="准备开始...",
            font=ctk.CTkFont(size=14)
        )
        self.status_label.pack(pady=5)

        # 进度条
        self.progress_bar = ctk.CTkProgressBar(current_status_frame, width=400, height=20)
        self.progress_bar.pack(pady=10)
        self.progress_bar.set(0)

        # 倒计时显示
        self.countdown_label = ctk.CTkLabel(
            current_status_frame,
            text="",
            font=ctk.CTkFont(size=14)
        )
        self.countdown_label.pack(pady=5)

        # 停止/开始按钮
        self.stop_start_button = ctk.CTkButton(
            current_status_frame,
            text="⏹ 停止",
            width=100,
            command=self.toggle_query
        )
        self.stop_start_button.pack(pady=10)

        # 待补货账号区域（持久显示）
        alert_header_frame = ctk.CTkFrame(status_frame, fg_color="transparent")
        alert_header_frame.pack(fill="x", pady=(20, 5))

        alert_title = ctk.CTkLabel(
            alert_header_frame,
            text="🔔 待补货账号",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        alert_title.pack(side="left")

        # 清空按钮
        clear_all_button = ctk.CTkButton(
            alert_header_frame,
            text="清空",
            width=60,
            height=28,
            font=ctk.CTkFont(size=11),
            command=self._clear_all_alerts
        )
        clear_all_button.pack(side="right")

        # 创建滚动框架来显示待补货账号列表
        self.alerts_scroll_frame = ctk.CTkScrollableFrame(
            status_frame,
            height=150,
            fg_color="gray95"
        )
        self.alerts_scroll_frame.pack(fill="both", expand=True, pady=(0, 20))

        # 显示之前累积的待补货账号
        self._refresh_alerts_display()
        
    # 事件处理方法
    def test_connection(self):
        """测试连接"""
        self.connection_status.configure(text="🔄 连接中...", text_color="orange")
        self.connect_button.configure(state="disabled")
        
        # 异步测试连接
        threading.Thread(target=self._test_connection_thread, daemon=True).start()
        
    def _test_connection_thread(self):
        """连接测试线程"""
        try:
            api_url = "http://127.0.0.1:54345"
            print(f"正在测试连接: {api_url}")

            # 测试基础连接
            response = requests.get(api_url, timeout=5)
            print(f"基础连接响应: {response.status_code}")

            if response.status_code == 200:
                print("基础连接成功，尝试获取浏览器列表...")

                try:
                    # 获取真实的浏览器窗口列表
                    browser_response = requests.post(f"{api_url}/browser/list",
                                                   json={"page": 0, "pageSize": 100},
                                                   timeout=10)

                    print(f"浏览器列表API响应: {browser_response.status_code}")

                    if browser_response.status_code == 200:
                        try:
                            data = browser_response.json()
                            print(f"API响应数据类型: {type(data)}")
                            print(f"API响应内容: {data}")

                            if isinstance(data, dict) and data.get('success') and 'data' in data:
                                data_obj = data['data']
                                # BitBrowser API返回的数据结构是 data.list
                                browsers = data_obj.get('list', []) if isinstance(data_obj, dict) else data_obj
                                self.window_list = []
                                self.window_data = []  # 清空窗口数据

                                if isinstance(browsers, list) and len(browsers) > 0:
                                    for browser in browsers:
                                        if isinstance(browser, dict):
                                            # 获取浏览器信息
                                            name = browser.get('name', '未知窗口')
                                            seq = browser.get('seq', 'N/A')
                                            platform = browser.get('platform', '')
                                            browser_id = browser.get('id', '')

                                            # 获取指纹信息
                                            fingerprint = browser.get('browserFingerPrint', {})
                                            if isinstance(fingerprint, dict):
                                                os_type = fingerprint.get('ostype', 'PC')
                                                core_product = fingerprint.get('coreProduct', 'chrome')
                                            else:
                                                os_type = 'PC'
                                                core_product = 'chrome'

                                            # 格式化显示信息
                                            platform_name = self._extract_platform_name(platform)
                                            display_name = f"{name} | {platform_name} | {os_type} | {core_product.title()} | #{seq}"

                                            self.window_list.append(display_name)
                                            # 存储完整的窗口数据
                                            self.window_data.append({
                                                'id': browser_id,
                                                'name': name,
                                                'display_name': display_name,
                                                'browser_data': browser
                                            })

                                    print(f"找到 {len(self.window_list)} 个浏览器窗口")
                                    # 在主线程中更新UI
                                    self.root.after(0, self._connection_success)
                                else:
                                    print("浏览器列表为空，使用默认窗口")
                                    # 如果没有浏览器，创建一些默认选项
                                    self.window_list = ["默认窗口1 | 未知平台 | PC | Chrome | #1",
                                                      "默认窗口2 | 未知平台 | PC | Chrome | #2"]
                                    self.root.after(0, self._connection_success)
                            else:
                                print("API数据格式不正确，使用默认窗口")
                                self.window_list = ["默认窗口 | 未知平台 | PC | Chrome | #1"]
                                self.root.after(0, self._connection_success)
                        except Exception as json_error:
                            print(f"解析JSON失败: {json_error}")
                            error_msg = f"解析API响应失败: {str(json_error)}"
                            self.root.after(0, lambda: self._connection_failed(error_msg))
                    else:
                        print(f"浏览器列表API失败: {browser_response.status_code}")
                        # API失败但基础连接成功，使用默认窗口
                        self.window_list = ["默认窗口 | 未知平台 | PC | Chrome | #1"]
                        self.root.after(0, self._connection_success)

                except Exception as api_error:
                    print(f"API调用异常: {api_error}")
                    # API调用失败但基础连接成功，使用默认窗口
                    self.window_list = ["默认窗口 | 未知平台 | PC | Chrome | #1"]
                    self.root.after(0, self._connection_success)
            else:
                error_msg = f"API错误: {response.status_code}"
                self.root.after(0, lambda: self._connection_failed(error_msg))

        except Exception as e:
            error_msg = str(e)
            self.root.after(0, lambda: self._connection_failed(error_msg))

    def _extract_platform_name(self, platform_url):
        """从平台URL提取平台名称"""
        if not platform_url:
            return "未知平台"

        try:
            from urllib.parse import urlparse
            domain = urlparse(platform_url).netloc.lower()

            # 常见平台映射
            platform_map = {
                'facebook.com': 'Facebook',
                'instagram.com': 'Instagram',
                'twitter.com': 'Twitter',
                'linkedin.com': 'LinkedIn',
                'amazon.com': 'Amazon',
                'ebay.com': 'eBay',
                'vinted.nl': 'Vinted',
                'vinted.com': 'Vinted',
                'google.com': 'Google',
                'youtube.com': 'YouTube'
            }

            for key, value in platform_map.items():
                if key in domain:
                    return value

            # 如果没有匹配，返回域名
            return domain.replace('www.', '').title()

        except:
            return "未知平台"
            
    def _connection_success(self):
        """连接成功"""
        self.connection_status.configure(text="✅ 连接成功", text_color="green")
        self.connect_button.configure(state="normal")

        # 成功动效 - 按钮闪烁
        self._success_animation()

        # 播放成功音效（在动效完成后）
        self.root.after(1000, self._play_success_sound)

        # 2秒后自动跳转到窗口选择
        self.root.after(2000, self.show_window_selection)

    def _play_success_sound(self):
        """播放成功音效"""
        try:
            import os
            import platform

            system = platform.system()
            if system == "Darwin":  # macOS
                # 播放更响亮的系统音效
                os.system("afplay /System/Library/Sounds/Sosumi.aiff")
            elif system == "Windows":
                import winsound
                winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
            else:  # Linux
                os.system("paplay /usr/share/sounds/alsa/Front_Left.wav")
        except:
            pass  # 忽略音效播放失败

    def _play_alert_sound_sequence(self):
        """播放待补货提醒音效序列"""
        try:
            import os
            import platform

            system = platform.system()
            if system == "Darwin":  # macOS
                # 连续播放3次更响亮的音效
                for i in range(3):
                    os.system("afplay /System/Library/Sounds/Sosumi.aiff")
                    if i < 2:  # 不是最后一次
                        import time
                        time.sleep(0.3)
            elif system == "Windows":
                import winsound
                for i in range(3):
                    winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
                    if i < 2:
                        import time
                        time.sleep(0.3)
            else:  # Linux
                for i in range(3):
                    os.system("paplay /usr/share/sounds/alsa/Front_Left.wav")
                    if i < 2:
                        import time
                        time.sleep(0.3)
        except:
            pass  # 忽略音效播放失败

    def _trigger_alert_effects(self):
        """触发待补货提醒效果"""
        # 立即播放音效（不等待）
        import threading
        threading.Thread(target=self._play_alert_sound_sequence, daemon=True).start()

        # 立即开始UI闪烁效果
        self._flash_ui()

    def _flash_ui(self):
        """UI警告效果 - 显示警告emoji"""
        try:
            # 创建警告emoji标签
            warning_label = ctk.CTkLabel(
                self.content_frame,
                text="⚠️",
                font=ctk.CTkFont(size=80),
                text_color="orange"
            )

            # 显示在中间
            warning_label.place(relx=0.5, rely=0.5, anchor="center")

            # 闪烁效果：显示和隐藏
            def flash_sequence(count, visible=True):
                if count > 0:
                    if visible:
                        warning_label.place(relx=0.5, rely=0.5, anchor="center")
                        # 改变窗口标题
                        self.root.title("⚠️ 发现待补货账号！")
                    else:
                        warning_label.place_forget()
                        self.root.title("Vinted 库存宝")

                    # 500ms后切换状态
                    self.root.after(500, lambda: flash_sequence(count - 1, not visible))
                else:
                    # 闪烁结束，清理
                    warning_label.destroy()
                    self.root.title("Vinted 库存宝")

            flash_sequence(10)  # 闪烁5次（10个状态切换）
        except Exception as e:
            print(f"警告效果失败: {e}")

    def _success_animation(self):
        """成功动效"""
        # 按钮闪烁动画
        original_color = self.connect_button.cget("fg_color")

        def flash(count):
            if count > 0:
                # 变绿
                self.connect_button.configure(fg_color="green")
                self.root.after(200, lambda: self.connect_button.configure(fg_color=original_color))
                self.root.after(400, lambda: flash(count - 1))

        flash(3)  # 闪烁3次
        
    def _connection_failed(self, error):
        """连接失败"""
        self.connection_status.configure(text=f"❌ {error}", text_color="red")
        self.connect_button.configure(state="normal")
        
    def confirm_window_selection(self):
        """确认多窗口选择"""
        try:
            print("开始确认窗口选择...")

            # 检查是否有复选框
            if not hasattr(self, 'window_checkboxes') or not self.window_checkboxes:
                messagebox.showerror("错误", "未找到窗口选择框")
                return

            print(f"找到 {len(self.window_checkboxes)} 个复选框")

            # 获取选中的窗口
            selected_windows = []
            selected_window_ids = []

            for i, checkbox in enumerate(self.window_checkboxes):
                is_checked = checkbox.get()
                print(f"复选框 {i}: {is_checked}")

                if is_checked:
                    if i < len(self.window_data):
                        window_data = self.window_data[i]
                        selected_windows.append(window_data['display_name'])
                        selected_window_ids.append(window_data['id'])
                        print(f"选中窗口: {window_data['display_name']}")
                    else:
                        print(f"警告: 复选框索引 {i} 超出窗口数据范围")

            print(f"总共选中 {len(selected_windows)} 个窗口")

            if len(selected_windows) < 2:
                messagebox.showwarning("提示", "请至少选择2个窗口")
                return

            # 获取间隔时间
            try:
                interval_text = self.interval_entry.get()
                print(f"间隔时间输入: '{interval_text}'")
                interval = int(interval_text)
                if interval < 1:
                    raise ValueError("间隔时间必须大于0")
                self.interval_minutes = interval
                print(f"设置间隔时间: {self.interval_minutes} 分钟")
            except ValueError as e:
                print(f"间隔时间错误: {e}")
                messagebox.showwarning("提示", "请输入有效的间隔时间（分钟）")
                return

            self.selected_windows = selected_windows
            self.selected_window_ids = selected_window_ids

            self.logger.info(f"选择了 {len(selected_windows)} 个窗口，间隔时间 {self.interval_minutes} 分钟")
            print("跳转到URL输入界面...")
            self.show_url_input()

        except Exception as e:
            print(f"确认窗口选择时出错: {e}")
            messagebox.showerror("错误", f"确认窗口选择时出错: {str(e)}")
            
    def add_url_entry(self):
        """添加用户ID输入框"""
        if len(self.url_entries) >= 5:
            messagebox.showwarning("提示", "最多只能添加5个管理员账号")
            return

        entry_number = len(self.url_entries) + 1
        placeholder_text = f"管理员 ID {entry_number}"

        entry = ctk.CTkEntry(
            self.url_container,
            placeholder_text=placeholder_text,
            height=40,
            width=300,
            font=ctk.CTkFont(size=14),
            justify="center"  # 文本居中
        )
        entry.pack(pady=5)

        # 强制更新显示
        self.url_container.update_idletasks()
        entry.update()

        # 确保placeholder显示
        def ensure_placeholder():
            try:
                if hasattr(entry, '_placeholder_text'):
                    entry._placeholder_text = placeholder_text
                if hasattr(entry, '_draw'):
                    entry._draw()
                entry.update()
            except:
                pass

        # 延迟执行确保显示
        self.root.after(10, ensure_placeholder)

        self.url_entries.append(entry)
        
    def remove_url_entry(self):
        """删除最后一个URL输入框"""
        if len(self.url_entries) > 1:
            entry = self.url_entries.pop()
            entry.destroy()
            
    def start_query(self):
        """开始查询"""
        # 获取所有用户ID并转换为URL
        urls = []
        for i, entry in enumerate(self.url_entries):
            user_id = entry.get().strip()
            if user_id:
                # 验证用户ID是否为数字
                if not user_id.isdigit():
                    messagebox.showwarning("提示", f"用户ID必须是数字，请检查第{i+1}个输入框")
                    return

                # 构建完整的URL
                full_url = f"https://www.vinted.nl/member/general/following/{user_id}"
                urls.append({
                    'admin_name': f"管理员{i+1}",
                    'url': full_url,
                    'user_id': user_id
                })

        if not urls:
            messagebox.showwarning("提示", "请至少输入一个用户ID")
            return

        self.admin_urls = urls  # 保存URL列表供后续使用
        self.is_running = True
        self.show_running_status()

        # 启动实际的查询逻辑
        self._start_scraping_thread()

    def _start_scraping_thread(self):
        """启动查询线程"""
        threading.Thread(target=self._scraping_worker, daemon=True).start()

    def _scraping_worker(self):
        """查询工作线程 - 只执行一轮查询"""
        try:
            # 检查是否已停止
            if not self.is_running:
                self.logger.info("查询已停止，退出工作线程")
                return

            self.logger.info("开始单轮库存查询任务")

            # 获取当前窗口
            current_window_id = self.selected_window_ids[self.current_window_index]
            current_window_name = self.selected_windows[self.current_window_index]

            self.root.after(0, lambda name=current_window_name:
                self.current_window_label.configure(text=f"当前窗口: {name}"))

            try:
                # 再次检查是否已停止
                if not self.is_running:
                    self.logger.info("查询在执行前被停止")
                    return

                # 执行一轮查询
                self._run_single_round(current_window_id)

                # 检查是否在查询过程中被停止
                if not self.is_running:
                    self.logger.info("查询在执行后被停止")
                    return

                # 切换到下一个窗口
                self.current_window_index = (self.current_window_index + 1) % len(self.selected_window_ids)

                # 如果还在运行，开始倒计时等待下一轮
                if self.is_running:
                    self.logger.info(f"本轮查询完成，开始 {self.interval_minutes} 分钟倒计时")
                    self._start_countdown()
                else:
                    self.logger.info("查询已停止，不开始倒计时")

            except Exception as e:
                self.logger.error(f"查询轮次失败: {str(e)}")
                self.root.after(0, lambda error=str(e):
                    self.status_label.configure(text=f"查询失败: {error}"))

                # 等待一段时间后重试（如果还在运行）
                if self.is_running:
                    self.logger.info("查询失败，等待1分钟后重试")
                    self._wait_with_countdown(60)  # 失败后等待1分钟

        except Exception as e:
            self.logger.error(f"查询任务失败: {str(e)}")
            self.root.after(0, lambda error=str(e):
                self.status_label.configure(text=f"查询任务失败: {error}"))

    def _run_single_round(self, window_id):
        """执行单轮查询"""
        self.root.after(0, lambda: self.status_label.configure(text="正在初始化浏览器..."))

        # 使用原来的配置结构
        bitbrowser_config = {
            'api_url': 'http://127.0.0.1:54345',
            'timeout': 30
        }

        vinted_config = {
            'element_wait_timeout': 10,
            'page_load_timeout': 15,
            'scroll_pause_time': 2
        }

        # 初始化浏览器管理器
        browser_manager = BitBrowserManager(bitbrowser_config)

        try:
            # 初始化浏览器环境
            self.logger.info(f"开始初始化浏览器窗口: {window_id}")
            success, message = browser_manager.initialize(window_id)
            if not success:
                self.logger.error(f"浏览器初始化失败: {message}")
                raise Exception(f"浏览器初始化失败: {message}")

            self.logger.info("浏览器初始化成功")
            self.root.after(0, lambda: self.status_label.configure(text="浏览器初始化成功"))

            # 获取WebDriver
            driver = browser_manager.get_driver()
            if not driver:
                self.logger.error("无法获取WebDriver实例")
                raise Exception("无法获取WebDriver")

            self.logger.info("WebDriver获取成功")

            # 创建Vinted采集器
            scraper = VintedScraper(driver, vinted_config)

            # 设置简单的回调函数
            def simple_progress_callback(current, total, message):
                if total > 0:
                    progress = current / total
                    self.root.after(0, lambda: self.progress_bar.set(progress))
                if message:
                    self.root.after(0, lambda: self.status_label.configure(text=message))

            def simple_status_callback(message):
                self.root.after(0, lambda: self.status_label.configure(text=message))

            def simple_inventory_callback(username, admin_name, profile_url=None, admin_id=None):
                # 添加到持久列表并播放音效
                # 如果没有提供profile_url，使用用户名构建
                if not profile_url:
                    profile_url = f"https://www.vinted.nl/member/{username}"

                # 构建显示文本：用户名(profile_url) - 不显示管理员信息
                alert_text = f"{username}({profile_url})"

                # 检查是否已经在列表中，避免重复添加和重复报警
                if alert_text not in self.persistent_out_of_stock:
                    self.persistent_out_of_stock.append(alert_text)
                    # 只有新增的才更新显示和触发提醒效果
                    self.root.after(0, lambda: self._refresh_alerts_display())
                    self.root.after(0, lambda: self._trigger_alert_effects())
                    self.logger.info(f"新增待补货账号: {alert_text}")
                else:
                    # 已存在，不重复报警
                    self.logger.debug(f"账号已在待补货列表中，跳过: {alert_text}")

            def simple_restocked_callback(username, admin_name, profile_url=None, admin_id=None):
                # 从持久列表中移除已补货的账号
                if not profile_url:
                    profile_url = f"https://www.vinted.nl/member/{username}"

                alert_text = f"{username}({profile_url})"

                if alert_text in self.persistent_out_of_stock:
                    self.persistent_out_of_stock.remove(alert_text)
                    self.root.after(0, lambda: self._refresh_alerts_display())
                    self.logger.info(f"账号已补货，从待补货列表移除: {alert_text}")

            scraper.set_callbacks(
                progress_callback=simple_progress_callback,
                status_callback=simple_status_callback,
                inventory_callback=simple_inventory_callback,
                restocked_callback=simple_restocked_callback
            )

            # 准备管理员URL数据
            admin_urls = []
            for admin_data in self.admin_urls:
                admin_urls.append({
                    'admin_name': admin_data['admin_name'],
                    'url': admin_data['url']
                })

            self.logger.info(f"开始采集 {len(admin_urls)} 个管理员的关注列表")
            for i, admin_data in enumerate(admin_urls):
                self.logger.info(f"管理员 {i+1}: {admin_data['admin_name']} - {admin_data['url']}")

            self.root.after(0, lambda: self.status_label.configure(text="开始采集关注列表..."))

            # 使用真实的多管理员采集方法
            self.logger.info("调用scraper.scrape_multiple_admins方法")
            result = scraper.scrape_multiple_admins(admin_urls)
            self.logger.info(f"采集完成，结果: {result}")

            # 处理结果
            if result:
                total_users = result.total_users
                out_of_stock_count = len(result.users_without_inventory)

                # 不需要在这里重复添加已出库用户，因为scraper中的回调已经处理了
                # 只更新状态显示
                self.logger.info(f"查询完成: 总用户 {total_users}, 本轮发现已出库 {out_of_stock_count}")
                self.root.after(0, lambda: self.status_label.configure(text=f"本轮完成: 总用户 {total_users}, 累计已出库 {len(self.persistent_out_of_stock)}"))
            else:
                self.logger.warning("查询结果为空")
                self.root.after(0, lambda: self.status_label.configure(text="本轮完成，但未找到结果"))

            # 查询完成
            self.root.after(0, lambda: self.progress_bar.set(1.0))

        except Exception as e:
            self.logger.error(f"查询过程中发生异常: {str(e)}")
            import traceback
            self.logger.error(f"异常堆栈: {traceback.format_exc()}")
            self.root.after(0, lambda error=str(e): self.status_label.configure(text=f"查询失败: {error}"))
            raise
        finally:
            # 清理资源
            try:
                self.logger.info("开始清理浏览器资源")
                browser_manager.cleanup()
                self.logger.info("浏览器资源清理完成")
            except Exception as e:
                self.logger.error(f"清理浏览器资源失败: {str(e)}")

    def _start_countdown(self):
        """开始倒计时"""
        self._wait_with_countdown(self.interval_minutes * 60)

    def _wait_with_countdown(self, seconds):
        """带倒计时的等待"""
        if not self.is_running:
            self.logger.info("倒计时被停止")
            return

        if seconds > 0:
            minutes = seconds // 60
            secs = seconds % 60
            self.root.after(0, lambda: self.countdown_label.configure(
                text=f"下轮开始倒计时: {minutes:02d}:{secs:02d}"
            ))
            self.root.after(0, lambda: self.status_label.configure(text="等待下一轮查询..."))

            # 1秒后递减（再次检查是否停止）
            self.root.after(1000, lambda: self._wait_with_countdown(seconds - 1))
        else:
            # 倒计时结束，清空显示并继续下一轮
            self.root.after(0, lambda: self.countdown_label.configure(text=""))
            # 继续循环查询（再次检查是否停止）
            if self.is_running:
                self.logger.info("倒计时结束，开始下一轮")
                self._start_next_round()
            else:
                self.logger.info("倒计时结束时查询已停止")

    def _start_next_round(self):
        """开始下一轮查询"""
        try:
            # 再次检查是否停止
            if not self.is_running:
                self.logger.info("查询已停止，不开始下一轮")
                return

            # 直接在后台线程中执行下一轮，不创建新线程
            if hasattr(self, 'admin_urls') and self.admin_urls and self.is_running:
                self.logger.info("倒计时结束，开始下一轮查询")
                # 在后台线程中执行
                threading.Thread(target=self._scraping_worker, daemon=True).start()
            else:
                self.logger.error("没有保存的URL或已停止运行，无法继续下一轮")
                self.root.after(0, lambda: self.status_label.configure(text="查询已停止"))
        except Exception as e:
            self.logger.error(f"开始下一轮查询失败: {e}")
            self.root.after(0, lambda: self.status_label.configure(text=f"下一轮启动失败: {str(e)}"))

    def _refresh_alerts_display(self):
        """刷新待补货账号显示"""
        if hasattr(self, 'alerts_scroll_frame'):
            # 清空现有显示
            for widget in self.alerts_scroll_frame.winfo_children():
                widget.destroy()

            if self.persistent_out_of_stock:
                # 为每个待补货账号创建一行，包含删除按钮
                for alert_text in self.persistent_out_of_stock:
                    alert_frame = ctk.CTkFrame(self.alerts_scroll_frame, fg_color="transparent")
                    alert_frame.pack(fill="x", pady=2, padx=5)

                    # 账号信息标签
                    alert_label = ctk.CTkLabel(
                        alert_frame,
                        text=alert_text,
                        font=ctk.CTkFont(size=12),
                        anchor="w"
                    )
                    alert_label.pack(side="left", fill="x", expand=True)

                    # 删除按钮
                    delete_button = ctk.CTkButton(
                        alert_frame,
                        text="✕",
                        width=25,
                        height=25,
                        font=ctk.CTkFont(size=12),
                        command=lambda text=alert_text: self._remove_alert(text)
                    )
                    delete_button.pack(side="right", padx=(5, 0))
            else:
                # 显示暂无信息
                no_alerts_label = ctk.CTkLabel(
                    self.alerts_scroll_frame,
                    text="暂无",
                    font=ctk.CTkFont(size=12),
                    text_color="gray"
                )
                no_alerts_label.pack(pady=20)

    def _remove_alert(self, alert_text):
        """移除单个待补货账号"""
        if alert_text in self.persistent_out_of_stock:
            self.persistent_out_of_stock.remove(alert_text)
            self._refresh_alerts_display()
            self.logger.info(f"手动移除待补货账号: {alert_text}")

    def _clear_all_alerts(self):
        """清空所有待补货账号"""
        if self.persistent_out_of_stock:
            count = len(self.persistent_out_of_stock)
            self.persistent_out_of_stock.clear()
            self._refresh_alerts_display()
            self.logger.info(f"手动清空所有待补货账号，共 {count} 个")

    def _add_out_of_stock_alert(self, message):
        """添加已出库提醒（兼容旧接口）"""
        if message not in self.persistent_out_of_stock:
            self.persistent_out_of_stock.append(message)
            self._refresh_alerts_display()
            self._play_success_sound()

    def _update_progress_with_params(self, current: int, total: int, message: str = ""):
        """更新进度回调（带参数）"""
        if total > 0:
            progress = current / total
            self.root.after(0, lambda: self.progress_bar.set(progress))
        if message:
            self.root.after(0, lambda: self.status_label.configure(text=message))

    def _update_status(self, message: str):
        """更新状态回调"""
        self.root.after(0, lambda: self.status_label.configure(text=message))

    def _inventory_found_callback(self, username: str, admin_name: str):
        """库存提醒回调"""
        self.root.after(0, lambda: self._add_out_of_stock_alert(f"{username} ({admin_name})"))
        
    def toggle_query(self):
        """切换查询状态"""
        if self.is_running:
            self.stop_query()
        else:
            self.restart_query()

    def stop_query(self):
        """停止查询 - 立即停止"""
        self.logger.info("用户请求立即停止查询")
        self.is_running = False

        # 立即停止采集器
        if hasattr(self, 'scraper') and self.scraper:
            self.scraper.should_stop = True
            self.logger.info("已发送停止信号给采集器")

        # 立即强制清理浏览器资源
        if hasattr(self, 'browser_manager') and self.browser_manager:
            try:
                # 立即清理，不使用后台线程
                self.logger.info("立即清理浏览器资源...")
                self.browser_manager.cleanup()
                self.logger.info("浏览器资源立即清理完成")
            except Exception as e:
                self.logger.error(f"立即清理浏览器资源失败: {e}")
                # 如果清理失败，尝试强制关闭
                try:
                    import threading
                    def force_cleanup():
                        try:
                            self.browser_manager.cleanup()
                            self.logger.info("浏览器资源强制清理完成")
                        except Exception as e2:
                            self.logger.error(f"强制清理也失败: {e2}")

                    threading.Thread(target=force_cleanup, daemon=True).start()
                except Exception as e3:
                    self.logger.error(f"启动强制清理线程失败: {e3}")

        # 立即更新界面状态
        self.root.after(0, lambda: self.status_label.configure(text="查询已停止"))
        self.root.after(0, lambda: self.countdown_label.configure(text=""))
        self.root.after(0, lambda: self.progress_bar.set(0))

        # 更改按钮文本为"开始查询"
        self.root.after(0, lambda: self.stop_start_button.configure(text="▶ 开始查询"))

        self.logger.info("查询已立即停止，界面已更新")

    def restart_query(self):
        """重新开始查询"""
        if hasattr(self, 'admin_urls') and self.admin_urls:
            self.logger.info("重新开始查询")
            self.is_running = True

            # 更改按钮文本为"停止"
            self.root.after(0, lambda: self.stop_start_button.configure(text="⏹ 停止"))

            # 重置状态
            self.current_window_index = 0

            # 启动查询线程
            self._start_scraping_thread()
        else:
            self.logger.error("没有保存的URL，无法重新开始查询")
            self.root.after(0, lambda: self.status_label.configure(text="错误：没有保存的URL"))
        
    def on_closing(self):
        """窗口关闭事件"""
        try:
            # 停止查询
            self.is_running = False

            # 清理浏览器资源
            if hasattr(self, 'browser_manager') and self.browser_manager:
                try:
                    self.browser_manager.cleanup()
                except:
                    pass

            # 停止采集器
            if hasattr(self, 'scraper') and self.scraper:
                try:
                    self.scraper.should_stop = True
                except:
                    pass

            # 销毁窗口
            self.root.quit()
            self.root.destroy()
        except:
            # 强制退出
            import sys
            sys.exit(0)
        
    def run(self):
        """运行应用"""
        try:
            # 确保窗口正确显示
            self.root.update()
            self.root.deiconify()  # 确保窗口显示
            self.root.lift()       # 提升窗口到前台
            self.root.focus_force() # 强制获取焦点

            # 运行主循环
            self.root.mainloop()
        except Exception as e:
            self.logger.error(f"应用运行时出错: {e}")
            try:
                import tkinter as tk
                from tkinter import messagebox
                root = tk.Tk()
                root.withdraw()
                messagebox.showerror("运行错误", f"应用运行时出错:\n{str(e)}")
                root.destroy()
            except:
                pass

def main():
    """主函数"""
    app = UltraSimpleVintedApp()
    app.run()

if __name__ == "__main__":
    main()
