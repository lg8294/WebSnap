#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flask应用工厂
"""

import logging
import os
from flask import Flask
from flask_cors import CORS

from app.api.routes import api_bp
from config.settings import config


def create_app(config_name: str = 'default'):
    """
    创建Flask应用实例
    
    Args:
        config_name: 配置名称
        
    Returns:
        Flask应用实例
    """
    app = Flask(__name__)
    
    # 加载配置
    config_class = config[config_name]
    app.config.from_object(config_class)
    
    # 配置日志
    logging.basicConfig(
        level=getattr(logging, config_class.LOG_LEVEL),
        format=config_class.LOG_FORMAT
    )
    
    # 配置CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": config_class.CORS_ORIGINS,
            "methods": config_class.CORS_METHODS,
            "allow_headers": config_class.CORS_HEADERS
        },
        r"/screenshot": {
            "origins": config_class.CORS_ORIGINS,
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": config_class.CORS_HEADERS
        },
        r"/health": {
            "origins": config_class.CORS_ORIGINS,
            "methods": ["GET", "OPTIONS"],
            "allow_headers": config_class.CORS_HEADERS
        },
        r"/": {
            "origins": config_class.CORS_ORIGINS,
            "methods": ["GET", "OPTIONS"],
            "allow_headers": config_class.CORS_HEADERS
        }
    })
    
    # 注册蓝图
    app.register_blueprint(api_bp)
    
    return app
