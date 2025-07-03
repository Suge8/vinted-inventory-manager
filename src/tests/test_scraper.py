#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vinted采集器测试模块
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.core.vinted_scraper import VintedScraper, UserInfo, ScrapingResult


class TestUserInfo(unittest.TestCase):
    """用户信息测试类"""
    
    def test_user_info_creation(self):
        """测试用户信息创建"""
        user = UserInfo(
            user_id="12345",
            username="test_user",
            profile_url="https://www.vinted.nl/member/12345"
        )
        
        self.assertEqual(user.user_id, "12345")
        self.assertEqual(user.username, "test_user")
        self.assertEqual(user.status, "unknown")
        self.assertEqual(user.item_count, 0)
        self.assertEqual(user.items, [])
    
    def test_user_info_with_items(self):
        """测试带商品的用户信息"""
        items = ["Item 1", "Item 2", "Item 3"]
        user = UserInfo(
            user_id="12345",
            username="test_user",
            profile_url="https://www.vinted.nl/member/12345",
            status="has_inventory",
            item_count=3,
            items=items
        )
        
        self.assertEqual(user.status, "has_inventory")
        self.assertEqual(user.item_count, 3)
        self.assertEqual(len(user.items), 3)


class TestVintedScraper(unittest.TestCase):
    """Vinted采集器测试类"""
    
    def setUp(self):
        """测试前设置"""
        self.mock_driver = Mock()
        self.config = {
            'element_wait_timeout': 10,
            'page_load_timeout': 15,
            'scroll_pause_time': 2,
            'delay_between_requests': 1
        }
        self.scraper = VintedScraper(self.mock_driver, self.config)
    
    def test_init(self):
        """测试初始化"""
        self.assertEqual(self.scraper.driver, self.mock_driver)
        self.assertEqual(self.scraper.config, self.config)
        self.assertFalse(self.scraper.should_stop)
    
    def test_set_callbacks(self):
        """测试设置回调函数"""
        progress_callback = Mock()
        status_callback = Mock()
        
        self.scraper.set_callbacks(progress_callback, status_callback)
        
        self.assertEqual(self.scraper.progress_callback, progress_callback)
        self.assertEqual(self.scraper.status_callback, status_callback)
    
    def test_stop_scraping(self):
        """测试停止采集"""
        self.assertFalse(self.scraper.should_stop)
        
        self.scraper.stop_scraping()
        
        self.assertTrue(self.scraper.should_stop)
    
    @patch('src.core.vinted_scraper.WebDriverWait')
    @patch('src.core.vinted_scraper.time.sleep')
    def test_safe_get_page_success(self, mock_sleep, mock_wait):
        """测试安全访问页面成功"""
        # 模拟WebDriverWait
        mock_wait_instance = Mock()
        mock_wait.return_value = mock_wait_instance
        mock_wait_instance.until.return_value = True
        
        result = self.scraper._safe_get_page("https://example.com")
        
        self.assertTrue(result)
        self.mock_driver.get.assert_called_once_with("https://example.com")
    
    def test_safe_get_page_failure(self):
        """测试安全访问页面失败"""
        from selenium.common.exceptions import TimeoutException
        
        self.mock_driver.get.side_effect = TimeoutException("Timeout")
        
        result = self.scraper._safe_get_page("https://example.com")
        
        self.assertFalse(result)
    
    def test_update_progress(self):
        """测试更新进度"""
        progress_callback = Mock()
        self.scraper.set_callbacks(progress_callback=progress_callback)
        
        self.scraper._update_progress(5, 10, "测试消息")
        
        progress_callback.assert_called_once_with(5, 10, "测试消息")
    
    def test_update_status(self):
        """测试更新状态"""
        status_callback = Mock()
        self.scraper.set_callbacks(status_callback=status_callback)
        
        self.scraper._update_status("测试状态")
        
        status_callback.assert_called_once_with("测试状态")
    
    @patch('src.core.vinted_scraper.time.sleep')
    def test_check_user_inventory_no_items(self, mock_sleep):
        """测试检查用户库存 - 无商品"""
        user = UserInfo(
            user_id="12345",
            username="test_user",
            profile_url="https://www.vinted.nl/member/12345"
        )
        
        # 模拟页面内容包含"没有商品"消息
        self.mock_driver.page_source = "Dit lid heeft geen artikelen te koop"
        
        with patch.object(self.scraper, '_safe_get_page', return_value=True):
            result = self.scraper.check_user_inventory(user)
        
        self.assertEqual(result.status, "no_inventory")
        self.assertEqual(result.item_count, 0)
    
    def test_check_user_inventory_with_items(self):
        """测试检查用户库存 - 有商品"""
        user = UserInfo(
            user_id="12345",
            username="test_user",
            profile_url="https://www.vinted.nl/member/12345"
        )
        
        # 模拟页面内容不包含"没有商品"消息
        self.mock_driver.page_source = "Some other content"
        
        # 模拟找到商品元素
        mock_item_elements = [Mock(), Mock(), Mock()]
        for i, element in enumerate(mock_item_elements):
            title_element = Mock()
            title_element.text = f"Item {i+1}"
            element.find_element.return_value = title_element
        
        self.mock_driver.find_elements.return_value = mock_item_elements
        
        with patch.object(self.scraper, '_safe_get_page', return_value=True):
            result = self.scraper.check_user_inventory(user)
        
        self.assertEqual(result.status, "has_inventory")
        self.assertEqual(result.item_count, 3)
        self.assertEqual(len(result.items), 3)
    
    def test_check_user_inventory_error(self):
        """测试检查用户库存 - 访问错误"""
        user = UserInfo(
            user_id="12345",
            username="test_user",
            profile_url="https://www.vinted.nl/member/12345"
        )
        
        with patch.object(self.scraper, '_safe_get_page', return_value=False):
            result = self.scraper.check_user_inventory(user)
        
        self.assertEqual(result.status, "error")
        self.assertEqual(result.error_message, "无法访问用户主页")


class TestScrapingResult(unittest.TestCase):
    """采集结果测试类"""
    
    def test_scraping_result_creation(self):
        """测试采集结果创建"""
        users_with_inventory = [
            UserInfo("1", "user1", "url1", "has_inventory", 5),
            UserInfo("2", "user2", "url2", "has_inventory", 3)
        ]
        
        users_without_inventory = [
            UserInfo("3", "user3", "url3", "no_inventory", 0)
        ]
        
        users_with_errors = [
            UserInfo("4", "user4", "url4", "error", 0, error_message="Connection failed")
        ]
        
        result = ScrapingResult(
            admin_url="https://example.com/following",
            total_users=4,
            users_with_inventory=users_with_inventory,
            users_without_inventory=users_without_inventory,
            users_with_errors=users_with_errors,
            scraping_time=120.5,
            timestamp="2025-06-02 14:30:00"
        )
        
        self.assertEqual(result.total_users, 4)
        self.assertEqual(len(result.users_with_inventory), 2)
        self.assertEqual(len(result.users_without_inventory), 1)
        self.assertEqual(len(result.users_with_errors), 1)
        self.assertEqual(result.scraping_time, 120.5)


if __name__ == '__main__':
    unittest.main()
