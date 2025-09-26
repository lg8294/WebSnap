#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
应用配置
"""

import os
from typing import Dict, Any


class Config:
    """基础配置类"""
    
    # Flask配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = False
    TESTING = False
    
    # 服务配置
    HOST = os.environ.get('HOST', '0.0.0.0')
    PORT = int(os.environ.get('PORT', 9000))
    
    # 截图服务配置
    DEFAULT_VIEWPORT_WIDTH = int(os.environ.get('DEFAULT_VIEWPORT_WIDTH', 1920))
    DEFAULT_VIEWPORT_HEIGHT = int(os.environ.get('DEFAULT_VIEWPORT_HEIGHT', 1080))
    DEFAULT_WAIT_TIME = int(os.environ.get('DEFAULT_WAIT_TIME', 3))
    MAX_WAIT_TIME = int(os.environ.get('MAX_WAIT_TIME', 60))
    
    # Chrome配置
    CHROME_OPTIONS = [
        '--headless',
        '--no-sandbox',
        '--disable-dev-shm-usage',
        '--disable-gpu',
        '--disable-extensions',
        '--disable-plugins',
        '--disable-images',  # 可选：禁用图片加载以提高速度
        '--disable-javascript',  # 可选：禁用JavaScript
    ]
    
    # 日志配置
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # 安全配置
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    REQUEST_TIMEOUT = 30  # 30秒
    
    # CORS配置
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')
    CORS_METHODS = ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
    CORS_HEADERS = ['Content-Type', 'Authorization', 'X-Requested-With']


class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'


class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    LOG_LEVEL = 'WARNING'


class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    DEBUG = True
    LOG_LEVEL = 'DEBUG'


# 配置字典
config: Dict[str, Any] = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
