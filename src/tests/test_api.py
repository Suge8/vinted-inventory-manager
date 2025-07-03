#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
比特浏览器API测试模块
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.core.bitbrowser_api import BitBrowserAPI, BitBrowserManager


class TestBitBrowserAPI(unittest.TestCase):
    """比特浏览器API测试类"""
    
    def setUp(self):
        """测试前设置"""
        self.api = BitBrowserAPI("http://127.0.0.1:54345")
    
    def test_init(self):
        """测试初始化"""
        self.assertEqual(self.api.api_url, "http://127.0.0.1:54345")
        self.assertEqual(self.api.timeout, 30)
    
    @patch('requests.Session.get')
    def test_test_connection_success(self, mock_get):
        """测试连接成功"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        success, message = self.api.test_connection()
        
        self.assertTrue(success)
        self.assertEqual(message, "API连接成功")
    
    @patch('requests.Session.get')
    def test_test_connection_failure(self, mock_get):
        """测试连接失败"""
        import requests
        mock_get.side_effect = requests.exceptions.ConnectionError("Connection failed")

        success, message = self.api.test_connection()

        self.assertFalse(success)
        self.assertIn("无法连接到比特浏览器API", message)
    
    @patch('requests.Session.get')
    def test_get_browser_list_success(self, mock_get):
        """测试获取浏览器列表成功"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'data': [
                {'id': '1', 'name': 'test_browser'},
                {'id': '2', 'name': 'another_browser'}
            ]
        }
        mock_get.return_value = mock_response
        
        browsers = self.api.get_browser_list()
        
        self.assertEqual(len(browsers), 2)
        self.assertEqual(browsers[0]['name'], 'test_browser')
    
    @patch('requests.Session.post')
    def test_create_browser_window_success(self, mock_post):
        """测试创建浏览器窗口成功"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'success': True,
            'data': {'id': 'new_browser_id', 'name': 'test_window'}
        }
        mock_post.return_value = mock_response
        
        result = self.api.create_browser_window('test_window')
        
        self.assertIsNotNone(result)
        self.assertEqual(result['name'], 'test_window')
    
    def test_find_browser_by_name(self):
        """测试根据名称查找浏览器"""
        with patch.object(self.api, 'get_browser_list') as mock_get_list:
            mock_get_list.return_value = [
                {'id': '1', 'name': 'test_browser'},
                {'id': '2', 'name': 'another_browser'}
            ]
            
            result = self.api.find_browser_by_name('test_browser')
            
            self.assertIsNotNone(result)
            self.assertEqual(result['id'], '1')
            
            # 测试未找到的情况
            result = self.api.find_browser_by_name('nonexistent')
            self.assertIsNone(result)


class TestBitBrowserManager(unittest.TestCase):
    """比特浏览器管理器测试类"""
    
    def setUp(self):
        """测试前设置"""
        self.config = {
            'api_url': 'http://127.0.0.1:54345',
            'timeout': 30
        }
        self.manager = BitBrowserManager(self.config)
    
    def test_init(self):
        """测试初始化"""
        self.assertEqual(self.manager.config, self.config)
        self.assertIsNotNone(self.manager.api)
        self.assertIsNone(self.manager.driver)
        self.assertIsNone(self.manager.browser_info)
    
    def test_is_ready(self):
        """测试就绪状态检查"""
        # 初始状态应该是未就绪
        self.assertFalse(self.manager.is_ready())
        
        # 模拟设置driver和browser_info
        self.manager.driver = Mock()
        self.manager.browser_info = {'id': 'test'}
        
        self.assertTrue(self.manager.is_ready())
    
    @patch('src.core.bitbrowser_api.webdriver.Chrome')
    def test_initialize_success(self, mock_chrome):
        """测试初始化成功"""
        # 模拟API调用
        with patch.object(self.manager.api, 'test_connection') as mock_test, \
             patch.object(self.manager.api, 'find_browser_by_name') as mock_find, \
             patch.object(self.manager.api, 'open_browser') as mock_open:
            
            mock_test.return_value = (True, "连接成功")
            mock_find.return_value = {'id': 'browser_id', 'name': 'test_window'}
            mock_open.return_value = {'http': '9222'}
            
            # 模拟WebDriver
            mock_driver = Mock()
            mock_chrome.return_value = mock_driver
            
            success, message = self.manager.initialize('test_window')
            
            self.assertTrue(success)
            self.assertEqual(message, "浏览器环境初始化成功")
            self.assertEqual(self.manager.driver, mock_driver)
    
    def test_cleanup(self):
        """测试清理资源"""
        # 设置模拟对象
        mock_driver = Mock()
        mock_browser_info = {'id': 'test_id'}
        
        self.manager.driver = mock_driver
        self.manager.browser_info = mock_browser_info
        
        with patch.object(self.manager.api, 'close_browser') as mock_close:
            self.manager.cleanup()
            
            # 验证清理操作
            mock_driver.quit.assert_called_once()
            mock_close.assert_called_once_with('test_id')
            self.assertIsNone(self.manager.driver)
            self.assertIsNone(self.manager.browser_info)


if __name__ == '__main__':
    unittest.main()
