#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
比特浏览器 API 集成模块

提供与比特浏览器的API连接、窗口管理、状态监控等功能。
"""

import json
import time
import logging
import requests
from typing import Dict, List, Optional, Tuple
from functools import wraps
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException


def retry_on_api_error(max_retries=5, delay=1):
    """重试装饰器，处理各种API错误"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    result = func(*args, **kwargs)
                    return result
                except requests.exceptions.HTTPError as e:
                    # 处理HTTP错误（包括503）
                    if e.response.status_code in [503, 502, 504, 500]:
                        last_exception = e
                        if attempt < max_retries - 1:
                            wait_time = delay * (2 ** attempt)  # 指数退避
                            time.sleep(wait_time)
                            continue
                    raise e
                except requests.exceptions.ProxyError as e:
                    # 处理代理错误
                    last_exception = e
                    if attempt < max_retries - 1:
                        wait_time = delay * (attempt + 1)
                        time.sleep(wait_time)
                        continue
                    raise e
                except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
                    # 处理连接错误和超时
                    last_exception = e
                    if attempt < max_retries - 1:
                        wait_time = delay * (attempt + 1)
                        time.sleep(wait_time)
                        continue
                    raise e
                except Exception as e:
                    # 其他未预期的错误，不重试
                    raise e
            raise last_exception
        return wrapper
    return decorator


class BitBrowserAPI:
    """比特浏览器API客户端"""
    
    def __init__(self, api_url: str = "http://127.0.0.1:54345", timeout: int = 30):
        """
        初始化比特浏览器API客户端

        Args:
            api_url: API服务地址
            timeout: 请求超时时间（秒）
        """
        self.api_url = api_url.rstrip('/')
        self.timeout = timeout
        self.logger = logging.getLogger(__name__)
        self.session = requests.Session()
        self.session.timeout = timeout

        # 绕过代理设置，直接连接本地API
        self.session.proxies = {
            'http': None,
            'https': None
        }

        # 设置连接池参数，提高稳定性
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=1,
            pool_maxsize=1,
            max_retries=0  # 禁用内置重试，使用我们自己的重试机制
        )
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
        
    @retry_on_api_error(max_retries=5, delay=1)
    def test_connection(self) -> Tuple[bool, str]:
        """
        测试API连接状态

        Returns:
            (是否连接成功, 状态消息)
        """
        try:
            # 比特浏览器使用 POST 方法，需要传递参数
            payload = {
                "page": 0,  # 比特浏览器从0开始计页
                "pageSize": 10
            }
            response = self.session.post(f"{self.api_url}/browser/list", json=payload, timeout=10)
            response.raise_for_status()  # 抛出HTTP错误

            if response.status_code == 200:
                data = response.json()
                if data.get('success', False):
                    return True, "API连接成功"
                else:
                    return True, f"API连接成功，但返回: {data.get('msg', '未知消息')}"
            else:
                return False, f"API响应错误: {response.status_code}"
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 503:
                return False, "BitBrowser服务暂时不可用(503)，已重试多次仍失败"
            elif e.response.status_code in [502, 504]:
                return False, f"BitBrowser网关错误({e.response.status_code})，请检查服务状态"
            return False, f"API HTTP错误: {e.response.status_code}"
        except requests.exceptions.ProxyError:
            return False, "代理连接错误，已尝试绕过代理仍失败，请检查网络设置"
        except requests.exceptions.ConnectionError:
            return False, "无法连接到比特浏览器API，请确保比特浏览器已启动且端口54345可用"
        except requests.exceptions.Timeout:
            return False, "API连接超时，已重试多次仍失败，请检查网络连接"
        except Exception as e:
            return False, f"连接测试失败: {str(e)}"

    def diagnose_connection(self) -> str:
        """
        诊断连接问题，提供详细的故障排除信息

        Returns:
            诊断信息字符串
        """
        diagnosis = []

        # 检查基本网络连接
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex(('127.0.0.1', 54345))
            sock.close()

            if result == 0:
                diagnosis.append("✅ 端口54345可访问")
            else:
                diagnosis.append("❌ 端口54345不可访问 - BitBrowser可能未启动")
        except Exception as e:
            diagnosis.append(f"❌ 网络检查失败: {str(e)}")

        # 检查代理设置
        import os
        proxy_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy']
        proxy_found = False
        for var in proxy_vars:
            if os.environ.get(var):
                diagnosis.append(f"⚠️ 发现代理设置: {var}={os.environ.get(var)}")
                proxy_found = True

        if not proxy_found:
            diagnosis.append("✅ 未发现系统代理设置")

        # 检查BitBrowser进程
        try:
            import psutil
            bitbrowser_processes = []
            for proc in psutil.process_iter(['pid', 'name']):
                if 'bitbrowser' in proc.info['name'].lower():
                    bitbrowser_processes.append(proc.info)

            if bitbrowser_processes:
                diagnosis.append(f"✅ 发现BitBrowser进程: {len(bitbrowser_processes)}个")
            else:
                diagnosis.append("❌ 未发现BitBrowser进程")
        except ImportError:
            diagnosis.append("⚠️ 无法检查进程状态（缺少psutil）")
        except Exception as e:
            diagnosis.append(f"⚠️ 进程检查失败: {str(e)}")

        # 添加VPN/代理配置建议
        diagnosis.append("\n🔧 VPN/代理配置建议:")
        diagnosis.append("1. 如使用VPN，建议设置为TUN模式而非系统代理模式")
        diagnosis.append("2. 推荐VPN提供商: ExpressVPN, NordVPN, Surfshark")
        diagnosis.append("3. 避免使用免费代理，可能导致连接不稳定")
        diagnosis.append("4. 如必须使用代理，请在BitBrowser中单独配置")
        diagnosis.append("5. 检查防火墙是否阻止了端口54345")

        return "\n".join(diagnosis)

    def get_vpn_troubleshooting_guide(self) -> str:
        """
        获取VPN/代理故障排除指南

        Returns:
            详细的故障排除指南
        """
        guide = [
            "🔧 VPN/代理连接问题解决指南",
            "=" * 50,
            "",
            "📋 常见问题及解决方案:",
            "",
            "1. 503错误频繁出现:",
            "   • 原因: VPN代理干扰本地API连接",
            "   • 解决: 将VPN设置为TUN模式，避免系统代理",
            "   • 备选: 在VPN软件中排除127.0.0.1和localhost",
            "",
            "2. 连接超时或不稳定:",
            "   • 检查VPN服务器负载，选择延迟较低的服务器",
            "   • 尝试更换VPN协议(OpenVPN → WireGuard)",
            "   • 临时关闭VPN测试是否为VPN问题",
            "",
            "3. 推荐VPN配置:",
            "   • ExpressVPN: 使用Lightway协议，开启Split Tunneling",
            "   • NordVPN: 使用NordLynx协议，配置应用排除",
            "   • Surfshark: 启用Bypasser功能，排除BitBrowser",
            "",
            "4. BitBrowser专用配置:",
            "   • 在BitBrowser中单独配置代理而非系统级",
            "   • 使用SOCKS5代理而非HTTP代理",
            "   • 设置代理认证信息（如需要）",
            "",
            "5. 网络环境检查:",
            "   • 确保防火墙允许端口54345",
            "   • 检查杀毒软件是否拦截网络连接",
            "   • 尝试以管理员权限运行BitBrowser",
            "",
            "6. 应急解决方案:",
            "   • 双VPN设置: 路由器VPN + 软件VPN",
            "   • 使用移动热点测试网络环境",
            "   • 联系VPN客服获取专用配置",
            "",
            "⚠️ 注意事项:",
            "• 避免使用免费VPN，稳定性差且可能有安全风险",
            "• 定期更新VPN客户端到最新版本",
            "• 保持BitBrowser和系统更新到最新版本"
        ]

        return "\n".join(guide)
    
    @retry_on_api_error(max_retries=5, delay=1)
    def get_browser_list(self) -> List[Dict]:
        """
        获取浏览器窗口列表

        Returns:
            浏览器窗口信息列表
        """
        try:
            payload = {
                "page": 0,  # 比特浏览器从0开始计页
                "pageSize": 100  # 获取更多浏览器窗口
            }
            response = self.session.post(f"{self.api_url}/browser/list", json=payload, timeout=15)
            response.raise_for_status()  # 抛出HTTP错误
            response.raise_for_status()
            data = response.json()
            if data.get('success', False):
                return data.get('data', {}).get('list', [])
            else:
                self.logger.error(f"获取浏览器列表失败: {data.get('msg', '未知错误')}")
                return []
        except Exception as e:
            self.logger.error(f"获取浏览器列表失败: {str(e)}")
            return []
    
    def create_browser_window(self, window_name: str, group_id: str = None) -> Optional[Dict]:
        """
        创建新的浏览器窗口

        Args:
            window_name: 窗口名称
            group_id: 分组ID（可选）

        Returns:
            创建的窗口信息，失败返回None
        """
        try:
            payload = {
                "name": window_name,
                "remark": "Vinted库存管理系统专用窗口",
                "proxyMethod": 2,  # 不使用代理
                "proxyType": "noproxy",  # 添加代理类型
                "browserFingerPrint": {
                    "coreVersion": "112",
                    "ostype": "PC",
                    "os": "Mac",
                    "osVersion": "10.15",
                    "userAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
                    "resolution": "1920x1080",
                    "language": "zh-CN,zh;q=0.9,en;q=0.8",
                    "timeZone": "Asia/Shanghai",
                    "webRTC": "proxy",
                    "canvas": "noise",
                    "webGL": "noise"
                }
            }

            if group_id:
                payload["groupId"] = group_id

            response = self.session.post(
                f"{self.api_url}/browser/update",
                json=payload
            )
            response.raise_for_status()
            data = response.json()

            if data.get('success'):
                self.logger.info(f"成功创建浏览器窗口: {window_name}")
                return data.get('data')
            else:
                self.logger.error(f"创建窗口失败: {data.get('msg', '未知错误')}")
                return None

        except Exception as e:
            self.logger.error(f"创建浏览器窗口失败: {str(e)}")
            return None
    
    def find_browser_by_name(self, window_name: str) -> Optional[Dict]:
        """
        根据名称查找浏览器窗口
        
        Args:
            window_name: 窗口名称
            
        Returns:
            窗口信息，未找到返回None
        """
        browsers = self.get_browser_list()
        for browser in browsers:
            if browser.get('name') == window_name:
                return browser
        return None
    
    def open_browser(self, browser_id: str) -> Optional[Dict]:
        """
        打开指定的浏览器窗口

        Args:
            browser_id: 浏览器ID

        Returns:
            打开结果信息
        """
        try:
            payload = {"id": browser_id}
            response = self.session.post(
                f"{self.api_url}/browser/open",
                json=payload
            )
            response.raise_for_status()
            data = response.json()

            if data.get('success'):
                self.logger.info(f"成功打开浏览器窗口: {browser_id}")
                return data.get('data')
            else:
                self.logger.error(f"打开窗口失败: {data.get('msg', '未知错误')}")
                return None

        except Exception as e:
            self.logger.error(f"打开浏览器窗口失败: {str(e)}")
            return None

    def close_browser(self, browser_id: str) -> bool:
        """
        关闭指定的浏览器窗口

        Args:
            browser_id: 浏览器ID

        Returns:
            是否成功关闭
        """
        try:
            payload = {"id": browser_id}
            response = self.session.post(
                f"{self.api_url}/browser/close",
                json=payload
            )
            response.raise_for_status()
            data = response.json()

            if data.get('success'):
                self.logger.info(f"成功关闭浏览器窗口: {browser_id}")
                return True
            else:
                self.logger.error(f"关闭窗口失败: {data.get('msg', '未知错误')}")
                return False

        except Exception as e:
            self.logger.error(f"关闭浏览器窗口失败: {str(e)}")
            return False


class BitBrowserManager:
    """比特浏览器管理器"""
    
    def __init__(self, config: Dict):
        """
        初始化浏览器管理器
        
        Args:
            config: 配置信息
        """
        self.config = config
        self.api = BitBrowserAPI(
            api_url=config.get('api_url', 'http://127.0.0.1:54345'),
            timeout=config.get('timeout', 30)
        )
        self.logger = logging.getLogger(__name__)
        self.driver = None
        self.browser_info = None
        
    def initialize(self, window_id: str) -> Tuple[bool, str]:
        """
        初始化浏览器环境

        Args:
            window_id: 窗口ID

        Returns:
            (是否成功, 状态消息)
        """
        try:
            # 测试API连接
            success, message = self.api.test_connection()
            if not success:
                return False, message

            # 验证窗口ID是否存在
            browser_list = self.api.get_browser_list()
            browser_info = None
            for browser in browser_list:
                if browser.get('id') == window_id:
                    browser_info = browser
                    break

            if not browser_info:
                return False, f"未找到窗口ID: {window_id}"

            # 打开浏览器窗口
            self.logger.info(f"正在打开浏览器窗口: {window_id}")
            open_result = self.api.open_browser(window_id)
            if not open_result:
                return False, "打开浏览器窗口失败"

            self.logger.info(f"浏览器窗口打开成功，响应数据: {open_result}")

            # 等待浏览器完全启动
            self.logger.info("等待浏览器完全启动...")
            time.sleep(3)

            # 连接到WebDriver
            debug_port = open_result.get('http')
            if not debug_port:
                self.logger.error(f"未获取到调试端口，响应数据: {open_result}")
                return False, "未获取到调试端口"

            # 验证和格式化调试地址
            if isinstance(debug_port, str):
                if ':' in debug_port:
                    # 已经是完整地址格式
                    debugger_address = debug_port
                else:
                    # 只是端口号，需要添加主机
                    debugger_address = f"127.0.0.1:{debug_port}"
            elif isinstance(debug_port, int):
                # 整数端口号
                debugger_address = f"127.0.0.1:{debug_port}"
            else:
                self.logger.error(f"调试端口格式不正确: {debug_port} (类型: {type(debug_port)})")
                return False, f"调试端口格式不正确: {debug_port}"

            self.logger.info(f"使用调试地址: {debugger_address}")

            # 验证调试端口是否可访问
            try:
                import requests
                test_url = f"http://{debugger_address}/json"
                response = requests.get(test_url, timeout=5)
                if response.status_code != 200:
                    return False, f"调试端口不可访问，状态码: {response.status_code}"
                self.logger.info(f"调试端口验证成功: {test_url}")
            except Exception as e:
                return False, f"调试端口连接失败: {str(e)}"

            # 获取正确的ChromeDriver路径
            driver_path = open_result.get('driver')
            if not driver_path:
                self.logger.warning("未获取到ChromeDriver路径，使用系统默认路径")
                driver_path = None
            else:
                self.logger.info(f"使用比特浏览器提供的ChromeDriver: {driver_path}")

            # 创建Chrome选项
            chrome_options = Options()
            chrome_options.add_experimental_option("debuggerAddress", debugger_address)
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")

            # 连接到WebDriver
            self.logger.info("正在连接WebDriver...")
            if driver_path:
                from selenium.webdriver.chrome.service import Service
                service = Service(executable_path=driver_path)
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
            else:
                self.driver = webdriver.Chrome(options=chrome_options)
            self.browser_info = browser_info

            self.logger.info(f"浏览器环境初始化成功: {window_id}")
            return True, "浏览器环境初始化成功"
            
        except Exception as e:
            self.logger.error(f"浏览器环境初始化失败: {str(e)}")
            return False, f"初始化失败: {str(e)}"
    
    def get_driver(self) -> Optional[webdriver.Chrome]:
        """获取WebDriver实例"""
        return self.driver
    
    def cleanup(self):
        """清理资源 - 快速清理"""
        try:
            # 快速关闭WebDriver
            if self.driver:
                try:
                    # 设置短超时，快速退出
                    self.driver.set_page_load_timeout(1)
                    self.driver.quit()
                except:
                    # 如果正常退出失败，强制终止
                    try:
                        import signal
                        import psutil
                        # 尝试强制终止浏览器进程
                        for proc in psutil.process_iter(['pid', 'name']):
                            if 'chrome' in proc.info['name'].lower():
                                proc.terminate()
                    except:
                        pass
                finally:
                    self.driver = None

            # 快速关闭浏览器窗口
            if self.browser_info:
                try:
                    # 使用API对象的close_browser方法
                    self.logger.info(f"正在关闭浏览器窗口: {self.browser_info['id']}")
                    self.api.close_browser(self.browser_info['id'])
                    self.logger.info("浏览器窗口关闭成功")
                except Exception as e:
                    self.logger.warning(f"使用API关闭浏览器失败: {e}")
                    try:
                        # 备用方法：直接发送HTTP请求
                        import requests
                        response = requests.post(
                            f"{self.api.base_url}/browser/close",
                            json={"id": self.browser_info['id']},
                            timeout=3  # 3秒超时
                        )
                        self.logger.info(f"HTTP关闭浏览器响应: {response.status_code}")
                    except Exception as e2:
                        self.logger.error(f"HTTP关闭浏览器也失败: {e2}")
                finally:
                    self.browser_info = None

            self.logger.info("浏览器资源快速清理完成")

        except Exception as e:
            self.logger.error(f"清理浏览器资源失败: {str(e)}")
            # 即使失败也要重置状态
            self.driver = None
            self.browser_info = None
    
    def is_ready(self) -> bool:
        """检查浏览器是否就绪"""
        return self.driver is not None and self.browser_info is not None
