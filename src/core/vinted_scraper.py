#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vinted网站数据采集引擎

实现关注列表解析、用户信息提取、库存状态检测等采集功能。
"""

import time
import logging
import re
from typing import List, Dict, Optional, Tuple, Callable
from dataclasses import dataclass
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from bs4 import BeautifulSoup

from ..utils.helpers import (
    extract_user_id_from_url, 
    build_user_profile_url, 
    build_next_page_url,
    clean_text,
    retry_on_exception
)


@dataclass
class UserInfo:
    """用户信息数据类"""
    user_id: str
    username: str
    profile_url: str
    status: str = "unknown"  # unknown, has_inventory, no_inventory, error
    item_count: int = 0
    items: List[str] = None
    error_message: str = ""
    
    def __post_init__(self):
        if self.items is None:
            self.items = []


@dataclass
class ScrapingResult:
    """采集结果数据类"""
    admin_url: str
    total_users: int
    users_with_inventory: List[UserInfo]
    users_without_inventory: List[UserInfo]
    users_with_errors: List[UserInfo]
    scraping_time: float
    timestamp: str


class VintedScraper:
    """Vinted网站数据采集器"""
    
    def __init__(self, driver: webdriver.Chrome, config: Dict):
        """
        初始化采集器
        
        Args:
            driver: WebDriver实例
            config: 配置信息
        """
        self.driver = driver
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.wait = WebDriverWait(driver, config.get('element_wait_timeout', 10))
        self.page_load_timeout = config.get('page_load_timeout', 15)
        self.scroll_pause_time = config.get('scroll_pause_time', 2)
        
        # 设置页面加载超时
        self.driver.set_page_load_timeout(self.page_load_timeout)
        
        # 进度回调函数
        self.progress_callback: Optional[Callable] = None
        self.status_callback: Optional[Callable] = None
        
        # 停止标志
        self.should_stop = False
    
    def set_callbacks(self, progress_callback: Callable = None, status_callback: Callable = None):
        """
        设置回调函数
        
        Args:
            progress_callback: 进度回调函数 (current, total, message)
            status_callback: 状态回调函数 (message)
        """
        self.progress_callback = progress_callback
        self.status_callback = status_callback
    
    def stop_scraping(self):
        """停止采集"""
        self.should_stop = True
        self.logger.info("收到停止采集信号")
    
    def _update_progress(self, current: int, total: int, message: str = ""):
        """更新进度"""
        if self.progress_callback:
            self.progress_callback(current, total, message)
    
    def _update_status(self, message: str):
        """更新状态"""
        self.logger.info(message)
        if self.status_callback:
            self.status_callback(message)
    
    @retry_on_exception(max_retries=3, delay=2.0)
    def _safe_get_page(self, url: str) -> bool:
        """
        安全地访问页面
        
        Args:
            url: 要访问的URL
            
        Returns:
            是否成功访问
        """
        try:
            self.driver.get(url)
            # 等待页面基本加载完成
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            time.sleep(1)  # 额外等待时间确保页面稳定
            return True
        except TimeoutException:
            self.logger.warning(f"页面加载超时: {url}")
            return False
        except WebDriverException as e:
            self.logger.error(f"访问页面失败: {url}, 错误: {str(e)}")
            return False
    
    def _check_browser_connection(self) -> bool:
        """检查浏览器连接状态"""
        try:
            # 尝试获取当前URL来验证连接
            current_url = self.driver.current_url
            self.logger.debug(f"浏览器连接正常，当前URL: {current_url}")
            return True
        except Exception as e:
            self.logger.error(f"浏览器连接已断开: {str(e)}")
            return False

    def extract_following_users(self, following_url: str) -> List[UserInfo]:
        """
        提取关注列表中的用户信息

        Args:
            following_url: 关注列表URL

        Returns:
            用户信息列表
        """
        users = []
        current_url = following_url
        page_num = 1

        self._update_status("开始提取关注列表...")
        self.logger.info(f"开始提取关注列表: {following_url}")

        # 首先检查浏览器连接状态
        if not self._check_browser_connection():
            raise Exception("浏览器连接已断开，无法继续操作")

        while current_url and not self.should_stop:
            self._update_status(f"正在处理关注列表第{page_num}页...")
            self.logger.info(f"处理第{page_num}页: {current_url}")

            # 在每次页面访问前检查浏览器连接
            if not self._check_browser_connection():
                raise Exception(f"在第{page_num}页处理过程中浏览器连接断开")

            if not self._safe_get_page(current_url):
                self.logger.error(f"无法访问关注列表页面: {current_url}")
                # 再次检查浏览器连接状态
                if not self._check_browser_connection():
                    raise Exception("页面访问失败，浏览器连接已断开")
                break
            
            # 查找关注用户容器
            try:
                # 检查浏览器连接状态
                if not self._check_browser_connection():
                    raise Exception(f"第{page_num}页加载前浏览器连接断开")

                # 等待页面完全加载 - 增加更长的等待时间和更好的检测
                self.logger.info(f"等待第{page_num}页加载完成...")

                # 等待页面基本元素加载
                try:
                    # 等待页面主体内容加载
                    self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "main")))
                    self.logger.info("✓ main标签加载完成")
                    time.sleep(2)
                except TimeoutException:
                    self.logger.warning("未找到main标签，尝试等待body加载")
                    self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                    self.logger.info("✓ body标签加载完成")
                    time.sleep(3)

                # 再次检查浏览器连接
                if not self._check_browser_connection():
                    raise Exception(f"第{page_num}页基本元素加载后浏览器连接断开")

                # 等待JavaScript执行完成
                ready_state = self.driver.execute_script("return document.readyState")
                self.logger.info(f"页面readyState: {ready_state}")
                time.sleep(2)

                # 滚动页面确保所有内容加载
                self.logger.info("滚动页面加载内容...")
                try:
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(self.scroll_pause_time)

                    # 再次滚动到顶部，确保所有内容都已渲染
                    self.driver.execute_script("window.scrollTo(0, 0);")
                    time.sleep(1)
                    self.logger.info("✓ 页面滚动完成")
                except Exception as e:
                    self.logger.warning(f"页面滚动失败: {str(e)}")
                    # 检查是否是浏览器连接问题
                    if not self._check_browser_connection():
                        raise Exception(f"第{page_num}页滚动时浏览器连接断开")

                # 获取页面源码进行检测
                try:
                    page_source = self.driver.page_source.lower()
                    self.logger.info(f"页面源码长度: {len(page_source)} 字符")

                    # 检查页面是否包含Vinted相关内容
                    if 'vinted' not in page_source:
                        self.logger.warning("页面源码中未找到'vinted'关键词，可能不是正确的页面")

                except Exception as e:
                    self.logger.error(f"获取页面源码失败: {str(e)}")
                    if not self._check_browser_connection():
                        raise Exception(f"第{page_num}页获取源码时浏览器连接断开")
                    raise

                # 首先检查是否显示"没有关注任何人"的消息
                no_following_messages = [
                    "doesn't follow anyone yet",
                    "volgt nog niemand",
                    "ne suit personne",
                    "没有关注任何人",
                    "no sigue a nadie"
                ]

                # 检查是否出现结束标志 - 更精确的检查
                self.logger.info(f"第{page_num}页：检查是否有'没有关注任何人'的消息...")
                found_no_following_msg = None
                for msg in no_following_messages:
                    if msg.lower() in page_source:
                        found_no_following_msg = msg
                        break

                if found_no_following_msg:
                    self.logger.info(f"第{page_num}页包含消息: '{found_no_following_msg}'")

                    # 更精确地检查这个消息是否真的表示没有关注任何人
                    # 先检查是否有用户容器和用户名元素
                    try:
                        user_containers = self.driver.find_elements(By.CSS_SELECTOR, "div.followed-users__body")
                        username_elements = self.driver.find_elements(By.CSS_SELECTOR, "[data-testid='profile-username']")

                        self.logger.info(f"第{page_num}页：用户容器数量: {len(user_containers)}")
                        self.logger.info(f"第{page_num}页：用户名元素数量: {len(username_elements)}")

                        if len(username_elements) > 1:  # 大于1是因为页面主用户也有用户名元素
                            self.logger.info(f"第{page_num}页：虽然包含结束消息，但发现了 {len(username_elements)} 个用户名元素，继续检测")
                        else:
                            self.logger.info(f"第{page_num}页：确认没有关注任何人，停止翻页")
                            break
                    except Exception as e:
                        self.logger.warning(f"第{page_num}页：检查用户元素时出错: {str(e)}，继续检测")
                else:
                    self.logger.info(f"第{page_num}页：未发现结束消息，继续查找用户链接")

                # 使用正确的CSS选择器来查找用户链接
                self.logger.info(f"第{page_num}页：开始查找用户链接...")
                user_links = []
                user_link_selectors = [
                    # 基于你提供的实际页面结构
                    "div.followed-users__body > div > div > a",  # 关注用户主容器中的链接
                    ".followed-users__body a[href*='/member/']",  # 关注用户容器中的成员链接
                    "[data-testid='profile-username']",  # 用户名元素（需要找到父级链接）
                    "a[href*='/member/']",  # 通用用户链接
                    ".web_ui__Cell a",  # Cell组件中的链接
                ]

                self.logger.info(f"第{page_num}页：将尝试 {len(user_link_selectors)} 个不同的选择器")

                for i, selector in enumerate(user_link_selectors, 1):
                    self.logger.info(f"第{page_num}页：尝试选择器 {i}/{len(user_link_selectors)}: '{selector}'")
                    try:
                        if selector == "[data-testid='profile-username']":
                            # 对于用户名元素，需要找到父级链接
                            username_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                            self.logger.info(f"第{page_num}页：找到 {len(username_elements)} 个用户名元素")

                            if username_elements:
                                # 输出前几个用户名用于验证
                                for j, elem in enumerate(username_elements[:3]):
                                    try:
                                        username = elem.text.strip()
                                        self.logger.info(f"第{page_num}页：用户名 {j+1}: '{username}'")
                                    except:
                                        pass

                            for username_elem in username_elements:
                                # 向上查找包含链接的父元素
                                try:
                                    link_elem = username_elem.find_element(By.XPATH, "./ancestor::a[contains(@href, '/member/')]")
                                    user_links.append(link_elem)
                                except Exception as e:
                                    self.logger.debug(f"查找父级链接失败: {str(e)}")
                                    continue

                            if user_links:
                                self.logger.info(f"第{page_num}页：通过用户名元素找到 {len(user_links)} 个用户链接")
                                break
                            else:
                                self.logger.warning(f"第{page_num}页：找到用户名元素但无法找到对应的链接")
                        else:
                            found_links = self.driver.find_elements(By.CSS_SELECTOR, selector)
                            self.logger.info(f"第{page_num}页：选择器 '{selector}' 找到 {len(found_links)} 个元素")

                            if found_links:
                                # 验证这些链接是否包含member
                                valid_links = []
                                for link in found_links:
                                    href = link.get_attribute('href') or ''
                                    if '/member/' in href:
                                        valid_links.append(link)

                                self.logger.info(f"第{page_num}页：其中 {len(valid_links)} 个是有效的member链接")

                                if valid_links:
                                    user_links = valid_links
                                    self.logger.info(f"第{page_num}页：使用选择器 '{selector}' 成功找到 {len(valid_links)} 个用户链接")
                                    break
                    except Exception as e:
                        self.logger.warning(f"第{page_num}页：选择器 '{selector}' 执行失败: {str(e)}")
                        continue

                # 如果还是没找到，尝试更宽泛的搜索
                if not user_links:
                    self.logger.warning("常规选择器未找到用户链接，尝试更宽泛的搜索...")
                    try:
                        # 查找所有包含member的链接
                        all_links = self.driver.find_elements(By.TAG_NAME, "a")
                        self.logger.info(f"页面总共有 {len(all_links)} 个链接")

                        member_links = []
                        for link in all_links:
                            href = link.get_attribute('href')
                            if href and '/member/' in href:
                                member_links.append(href)
                                if '/general/' not in href:
                                    user_links.append(link)

                        self.logger.info(f"包含/member/的链接: {len(member_links)} 个")
                        self.logger.info(f"过滤后的用户链接: {len(user_links)} 个")

                        # 打印前几个链接作为调试信息
                        if member_links:
                            self.logger.info(f"前5个member链接示例: {member_links[:5]}")

                    except Exception as e:
                        self.logger.warning(f"遍历所有链接失败: {str(e)}")

                self.logger.info(f"第{page_num}页总共找到 {len(user_links)} 个潜在用户链接")

                # 如果仍然没有找到用户链接，输出详细的页面调试信息
                if not user_links:
                    self.logger.error(f"第{page_num}页未找到任何用户链接！")

                    # 检查浏览器连接状态
                    if not self._check_browser_connection():
                        raise Exception(f"第{page_num}页用户链接检测时浏览器连接断开")

                    try:
                        current_url = self.driver.current_url
                        page_title = self.driver.title
                        self.logger.error(f"当前页面URL: {current_url}")
                        self.logger.error(f"页面标题: {page_title}")

                        # 检查关键容器是否存在
                        containers_to_check = [
                            "div.followed-users__body",
                            ".body-content__content",
                            "#content",
                            "[data-testid='profile-username']",
                            ".web_ui__Cell",
                        ]

                        for container in containers_to_check:
                            try:
                                elements = self.driver.find_elements(By.CSS_SELECTOR, container)
                                self.logger.info(f"容器 '{container}': 找到 {len(elements)} 个元素")
                                if elements:
                                    # 输出第一个元素的HTML片段
                                    html_snippet = elements[0].get_attribute('outerHTML')[:200]
                                    self.logger.debug(f"容器HTML片段: {html_snippet}...")
                            except Exception as e:
                                self.logger.debug(f"检查容器 '{container}' 失败: {str(e)}")

                        # 检查页面是否包含关键词
                        key_words = ["following", "member", "user", "profile", "volgt", "suivre", "followed-users"]
                        found_keywords = []
                        for word in key_words:
                            if word in page_source:
                                found_keywords.append(word)

                        if found_keywords:
                            self.logger.info(f"页面包含关键词: {found_keywords}")
                        else:
                            self.logger.warning("页面不包含任何预期关键词")

                        # 检查是否有任何链接
                        all_links = self.driver.find_elements(By.TAG_NAME, "a")
                        self.logger.info(f"页面总共有 {len(all_links)} 个链接")

                        # 检查包含member的链接
                        member_links = [link for link in all_links if 'member' in link.get_attribute('href') or '']
                        self.logger.info(f"包含'member'的链接有 {len(member_links)} 个")

                        if member_links:
                            for i, link in enumerate(member_links[:3]):  # 只显示前3个
                                href = link.get_attribute('href')
                                text = link.text.strip()
                                self.logger.info(f"Member链接 {i+1}: {href} (文本: '{text}')")

                    except Exception as e:
                        self.logger.error(f"获取页面调试信息失败: {str(e)}")
                        if not self._check_browser_connection():
                            raise Exception(f"第{page_num}页调试信息获取时浏览器连接断开")

                page_users = []
                for link in user_links:
                    try:
                        href = link.get_attribute('href')
                        if href and '/member/' in href and '/general/' not in href:
                            user_id = extract_user_id_from_url(href)
                            if user_id:
                                # 尝试获取用户名 - 优先使用data-testid='profile-username'
                                username = "Unknown"
                                try:
                                    # 首先尝试使用精确的用户名选择器
                                    username_element = link.find_element(By.CSS_SELECTOR, "[data-testid='profile-username']")
                                    username = clean_text(username_element.text)
                                    if username:
                                        self.logger.debug(f"使用data-testid获取用户名: {username}")
                                except NoSuchElementException:
                                    try:
                                        # 尝试其他用户名选择器
                                        username_element = link.find_element(By.CSS_SELECTOR, ".user-name, .username, [data-testid='username']")
                                        username = clean_text(username_element.text)
                                        if username:
                                            self.logger.debug(f"使用通用选择器获取用户名: {username}")
                                    except NoSuchElementException:
                                        # 如果找不到用户名元素，从链接文本中提取第一行
                                        link_text = clean_text(link.text)
                                        if link_text:
                                            # 取第一行作为用户名，过滤掉"Nog geen reviews"等
                                            lines = link_text.split('\n')
                                            for line in lines:
                                                line = line.strip()
                                                # 跳过常见的非用户名文本
                                                if line and not any(skip in line.lower() for skip in [
                                                    'nog geen reviews', 'no reviews', 'reviews',
                                                    'heel goed', 'very good', 'good', 'excellent'
                                                ]):
                                                    username = line
                                                    self.logger.debug(f"从链接文本提取用户名: {username}")
                                                    break

                                        if username == "Unknown":
                                            username = f"User_{user_id}"

                                user_info = UserInfo(
                                    user_id=user_id,
                                    username=username,
                                    profile_url=href
                                )

                                # 避免重复添加
                                if not any(u.user_id == user_id for u in page_users):
                                    page_users.append(user_info)

                    except Exception as e:
                        self.logger.warning(f"提取用户链接失败: {str(e)}")
                        continue
                
                if page_users:
                    users.extend(page_users)
                    self._update_status(f"第{page_num}页找到 {len(page_users)} 个用户，总计 {len(users)} 个用户")
                else:
                    self.logger.info(f"第{page_num}页未找到用户，停止翻页")
                    break

                # 简化的分页检测逻辑
                # 尝试构建下一页URL
                next_url = build_next_page_url(current_url)
                if next_url == current_url:
                    # URL没有变化，说明已经是最后一页
                    self.logger.info("URL没有变化，已到达最后一页")
                    break

                # 验证下一页是否存在且有内容
                self.logger.info(f"尝试访问下一页: {next_url}")
                if not self._safe_get_page(next_url):
                    self.logger.info("无法访问下一页，停止翻页")
                    break

                # 检查下一页是否有实际的用户链接（更准确的检测）
                time.sleep(2)
                page_source = self.driver.page_source.lower()

                # 检查是否有关注用户的容器和用户链接
                next_page_user_links = self.driver.find_elements(By.CSS_SELECTOR, "div.followed-users__body > div > div > a")
                next_page_username_elements = self.driver.find_elements(By.CSS_SELECTOR, "[data-testid='profile-username']")

                self.logger.info(f"下一页预检：找到 {len(next_page_user_links)} 个用户链接，{len(next_page_username_elements)} 个用户名元素")

                # 如果没有用户链接，或者用户名元素<=1（只有页面主用户），则停止
                if len(next_page_user_links) == 0 or len(next_page_username_elements) <= 1:
                    self.logger.info("下一页确认没有关注用户，停止翻页")
                    break

                # 更新当前URL并继续
                current_url = next_url
                page_num += 1
                self.logger.info(f"继续处理第{page_num}页")

            except TimeoutException:
                self.logger.error(f"关注列表页面加载超时: {current_url}")
                break
            except Exception as e:
                self.logger.error(f"提取关注列表失败: {str(e)}")
                break
        
        self._update_status(f"关注列表提取完成，共找到 {len(users)} 个用户")
        return users

    def _build_user_shop_url(self, profile_url: str) -> str:
        """
        构建用户商店页面URL

        Args:
            profile_url: 用户个人资料URL

        Returns:
            用户商店页面URL
        """
        try:
            # 从个人资料URL提取用户ID
            user_id = extract_user_id_from_url(profile_url)
            if user_id:
                # 构建商店页面URL
                base_url = profile_url.split('/member/')[0]
                shop_url = f"{base_url}/member/{user_id}"
                self.logger.info(f"构建商店URL: {profile_url} -> {shop_url}")
                return shop_url
            else:
                self.logger.warning(f"无法从URL提取用户ID: {profile_url}")
                return profile_url
        except Exception as e:
            self.logger.warning(f"构建商店URL失败: {str(e)}")
            return profile_url

    def check_user_inventory(self, user_info: UserInfo) -> UserInfo:
        """
        检查单个用户的库存状态

        Args:
            user_info: 用户信息

        Returns:
            更新后的用户信息
        """
        try:
            self._update_status(f"正在检查用户 {user_info.username} 的库存...")

            # 构建用户商店页面URL
            shop_url = self._build_user_shop_url(user_info.profile_url)
            self.logger.info(f"访问用户商店页面: {shop_url}")

            if not self._safe_get_page(shop_url):
                user_info.status = "error"
                user_info.error_message = "无法访问用户商店页面"
                return user_info

            # 等待页面加载
            time.sleep(3)

            # 滚动页面确保商品加载
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            # 先检查实际的商品元素，而不是依赖文本消息
            self.logger.info(f"开始检测用户 {user_info.username} 的库存...")

            # 获取页面源码用于调试
            page_source = self.driver.page_source.lower()
            
            # 1. 首先检查库存数量显示
            try:
                import re
                items_pattern = r'(\d+)\s+items?'
                items_matches = re.findall(items_pattern, page_source)
                if items_matches:
                    # 取第一个匹配的数字作为库存数量
                    item_count_from_text = int(items_matches[0])
                    self.logger.info(f"从页面文本检测到库存数量: {item_count_from_text}")
                else:
                    item_count_from_text = None
                    self.logger.info("未从页面文本检测到库存数量")
            except Exception as e:
                self.logger.warning(f"检测库存数量文本失败: {str(e)}")
                item_count_from_text = None

            # 2. 检查是否有空状态元素
            try:
                empty_state_selector = "#content > div > div.container > div > div:nth-child(3) > div.profile__items-wrapper > div.web_ui__EmptyState__empty-state"
                empty_elements = self.driver.find_elements(By.CSS_SELECTOR, empty_state_selector)
                has_empty_state = len(empty_elements) > 0
                self.logger.info(f"空状态元素检测: {'找到' if has_empty_state else '未找到'}")

                if has_empty_state:
                    # 确实是空状态，没有库存
                    user_info.status = "no_inventory"
                    user_info.item_count = 0
                    self.logger.info(f"用户 {user_info.username} 确认无库存（空状态）")
                    return user_info

            except Exception as e:
                self.logger.warning(f"检查空状态元素失败: {str(e)}")
                has_empty_state = False

            # 3. 查找实际的商品元素
            try:
                # 基于调试结果，优先使用有效的选择器
                item_selectors = [
                    ".feed-grid__item",  # 调试验证有效
                    ".item-box",
                    "[data-testid='item']",
                    ".catalog-item",
                    ".product-item"
                ]

                items_found = []
                used_selector = None
                for selector in item_selectors:
                    try:
                        item_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        if item_elements:
                            items_found = item_elements
                            used_selector = selector
                            self.logger.info(f"使用选择器 '{selector}' 找到 {len(item_elements)} 个商品元素")
                            break
                    except Exception as e:
                        self.logger.debug(f"选择器 '{selector}' 失败: {str(e)}")
                        continue
                
                # 4. 根据检测结果判断库存状态
                if items_found:
                    # 找到了商品元素，有库存
                    actual_item_count = len(items_found)

                    # 提取商品信息 - 改进提取逻辑
                    items = []
                    for i, item_element in enumerate(items_found[:20]):  # 限制最多20个商品
                        try:
                            # 获取商品文本内容
                            item_text = item_element.text.strip()
                            self.logger.debug(f"商品 {i+1} 原始文本: '{item_text}'")

                            if item_text:
                                # 分析文本结构，提取商品名称
                                lines = [line.strip() for line in item_text.split('\n') if line.strip()]

                                # 查找商品名称 - 通常是第一个不包含数字、价格、评级的行
                                title = "Unknown Item"
                                for line in lines:
                                    # 跳过纯数字、价格、评级等
                                    if (line and
                                        not line.isdigit() and  # 跳过纯数字
                                        '€' not in line and     # 跳过价格
                                        not any(rating in line.lower() for rating in ['heel goed', 'very good', 'good', 'excellent', 'fair']) and  # 跳过评级
                                        not any(size in line for size in ['·', '•']) and  # 跳过包含分隔符的行
                                        len(line) > 1):  # 跳过单字符
                                        title = line
                                        break

                                if title != "Unknown Item":
                                    items.append(title)
                                    self.logger.debug(f"商品 {i+1} 提取标题: '{title}'")
                                else:
                                    # 如果没找到合适的标题，使用第一行
                                    if lines:
                                        items.append(lines[0])
                                        self.logger.debug(f"商品 {i+1} 使用第一行: '{lines[0]}'")
                        except Exception as e:
                            self.logger.debug(f"提取商品 {i+1} 信息失败: {str(e)}")
                            continue

                    user_info.status = "has_inventory"
                    user_info.item_count = actual_item_count
                    user_info.items = items

                    # 验证文本检测的数量和实际元素数量
                    if item_count_from_text and item_count_from_text != actual_item_count:
                        self.logger.info(f"库存数量差异: 文本显示{item_count_from_text}，实际元素{actual_item_count}")

                    self.logger.info(f"用户 {user_info.username} 确认有库存: {actual_item_count} 个商品")

                    # 更新状态显示检查结果
                    status_msg = f"✅ {user_info.username} - 有库存 ({actual_item_count}个商品)"
                    self._update_status(status_msg)

                else:
                    # 没有找到商品元素，确认无库存
                    user_info.status = "no_inventory"
                    user_info.item_count = 0
                    self.logger.info(f"用户 {user_info.username} 确认无库存（未找到商品元素）")

                    # 更新状态显示检查结果
                    status_msg = f"❌ {user_info.username} - 无库存"
                    self._update_status(status_msg)
                
            except Exception as e:
                self.logger.warning(f"查找商品列表失败: {str(e)}")
                user_info.status = "error"
                user_info.error_message = f"商品列表解析失败: {str(e)}"
            
        except Exception as e:
            self.logger.error(f"检查用户库存失败: {str(e)}")
            user_info.status = "error"
            user_info.error_message = str(e)
        
        return user_info

    def scrape_all_users(self, following_url: str) -> ScrapingResult:
        """
        采集所有用户的库存信息

        Args:
            following_url: 关注列表URL

        Returns:
            采集结果
        """
        start_time = time.time()
        self.should_stop = False

        try:
            # 第一步：提取关注列表
            self._update_status("开始提取关注用户列表...")
            users = self.extract_following_users(following_url)

            if not users:
                raise Exception("未找到任何关注用户")

            if self.should_stop:
                raise Exception("用户取消操作")

            # 第二步：检查每个用户的库存
            self._update_status(f"开始检查 {len(users)} 个用户的库存状态...")

            users_with_inventory = []
            users_without_inventory = []
            users_with_errors = []

            for i, user in enumerate(users):
                if self.should_stop:
                    self.logger.info("用户请求停止采集")
                    break

                self._update_progress(i + 1, len(users), f"检查用户: {user.username}")

                try:
                    updated_user = self.check_user_inventory(user)

                    if updated_user.status == "has_inventory":
                        users_with_inventory.append(updated_user)
                    elif updated_user.status == "no_inventory":
                        users_without_inventory.append(updated_user)
                    else:
                        users_with_errors.append(updated_user)

                    # 添加延迟避免请求过快
                    delay = self.config.get('delay_between_requests', 1)
                    if delay > 0:
                        time.sleep(delay)

                except Exception as e:
                    self.logger.error(f"检查用户 {user.username} 失败: {str(e)}")
                    user.status = "error"
                    user.error_message = str(e)
                    users_with_errors.append(user)

            # 创建结果对象
            scraping_time = time.time() - start_time
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

            result = ScrapingResult(
                admin_url=following_url,
                total_users=len(users),
                users_with_inventory=users_with_inventory,
                users_without_inventory=users_without_inventory,
                users_with_errors=users_with_errors,
                scraping_time=scraping_time,
                timestamp=timestamp
            )

            self._update_status(f"采集完成！耗时 {scraping_time:.1f} 秒")
            self._update_progress(len(users), len(users), "采集完成")

            return result

        except Exception as e:
            self.logger.error(f"采集过程失败: {str(e)}")
            raise
