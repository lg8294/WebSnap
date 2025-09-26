#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网页截图服务核心类
"""

import time
import logging
from typing import Optional
from urllib.parse import urlparse

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

logger = logging.getLogger(__name__)


class ScreenshotService:
    """网页截图服务类"""
    
    def __init__(self, viewport_width: int = 1920, viewport_height: int = 1080):
        self.driver = None
        self.viewport_width = viewport_width
        self.viewport_height = viewport_height
        self.setup_driver()
    
    def setup_driver(self):
        """初始化Chromium WebDriver"""
        try:
            chrome_options = Options()
            chrome_options.add_argument('--headless')  # 无头模式
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--disable-web-security')
            chrome_options.add_argument('--disable-features=VizDisplayCompositor')
            chrome_options.add_argument(f'--window-size={self.viewport_width},{self.viewport_height}')
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
            
            # 使用Chromium
            chrome_options.binary_location = '/usr/bin/chromium'
            self.driver = webdriver.Chrome(options=chrome_options)
            logger.info("Chromium WebDriver 初始化成功")
            
        except Exception as e:
            logger.error(f"WebDriver 初始化失败: {e}")
            raise
    
    def take_screenshot(self, url: str, wait_time: int = 3, full_page: bool = True, 
                       viewport_width: int = None, viewport_height: int = None) -> Optional[bytes]:
        """
        截取网页截图
        
        Args:
            url: 要截图的网址
            wait_time: 等待页面加载的时间（秒）
            full_page: 是否截取完整页面
            viewport_width: 视口宽度，如果指定则临时修改
            viewport_height: 视口高度，如果指定则临时修改
            
        Returns:
            截图的字节数据，失败时返回None
        """
        try:
            # 验证URL格式
            parsed_url = urlparse(url)
            if not parsed_url.scheme:
                url = 'https://' + url
            
            logger.info(f"开始截取网页: {url}")
            
            # 如果指定了视口大小，则临时修改窗口大小
            if viewport_width is not None and viewport_height is not None:
                self.driver.set_window_size(viewport_width, viewport_height)
                logger.info(f"设置视口大小: {viewport_width}x{viewport_height}")
            
            # 访问网页
            self.driver.get(url)
            
            # 等待页面加载
            time.sleep(wait_time)
            
            # 等待页面元素加载完成
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
            except TimeoutException:
                logger.warning("页面加载超时，继续截图")
            
            # 设置窗口大小
            if full_page:
                # 获取页面总高度
                total_height = self.driver.execute_script("return document.body.scrollHeight")
                self.driver.set_window_size(1920, total_height)
                time.sleep(1)
            
            # 截取截图
            screenshot = self.driver.get_screenshot_as_png()
            logger.info(f"截图成功，大小: {len(screenshot)} bytes")
            
            return screenshot
            
        except WebDriverException as e:
            logger.error(f"WebDriver 错误: {e}")
            return None
        except Exception as e:
            logger.error(f"截图失败: {e}")
            return None
    
    def close(self):
        """关闭WebDriver"""
        if self.driver:
            self.driver.quit()
            logger.info("WebDriver 已关闭")
