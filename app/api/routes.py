#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API路由定义
"""

import time
import base64
import logging
from io import BytesIO
from typing import Optional

from flask import Blueprint, request, jsonify, send_file

from app.core.screenshot_service import ScreenshotService

logger = logging.getLogger(__name__)

# 创建蓝图
api_bp = Blueprint('api', __name__)

# 创建全局截图服务实例
screenshot_service = ScreenshotService()


@api_bp.route('/screenshot', methods=['POST'])
def take_screenshot():
    """
    截图API接口
    
    请求参数:
    - url: 要截图的网址（必需）
    - wait_time: 等待时间，默认3秒（可选）
    - full_page: 是否截取完整页面，默认true（可选）
    - format: 返回格式，'base64'或'file'，默认'base64'（可选）
    - viewport_width: 视口宽度，默认1920（可选）
    - viewport_height: 视口高度，默认1080（可选）
    """
    try:
        data = request.get_json()
        
        if not data or 'url' not in data:
            return jsonify({
                'success': False,
                'error': '缺少必需参数: url'
            }), 400
        
        url = data['url']
        wait_time = data.get('wait_time', 3)
        full_page = data.get('full_page', True)
        return_format = data.get('format', 'base64')
        viewport_width = data.get('viewport_width')
        viewport_height = data.get('viewport_height')
        
        # 截取截图
        screenshot_data = screenshot_service.take_screenshot(
            url, wait_time, full_page, viewport_width, viewport_height
        )
        
        if screenshot_data is None:
            return jsonify({
                'success': False,
                'error': '截图失败，请检查网址是否正确'
            }), 500
        
        if return_format == 'base64':
            # 返回base64编码的图片
            screenshot_base64 = base64.b64encode(screenshot_data).decode('utf-8')
            return jsonify({
                'success': True,
                'screenshot': screenshot_base64,
                'url': url,
                'size': len(screenshot_data)
            })
        else:
            # 返回文件
            return send_file(
                BytesIO(screenshot_data),
                mimetype='image/png',
                as_attachment=True,
                download_name=f'screenshot_{int(time.time())}.png'
            )
            
    except Exception as e:
        logger.error(f"API错误: {e}")
        return jsonify({
            'success': False,
            'error': f'服务器内部错误: {str(e)}'
        }), 500


@api_bp.route('/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        'status': 'healthy',
        'service': 'screenshot_service',
        'timestamp': time.time()
    })


@api_bp.route('/', methods=['GET'])
def index():
    """首页，显示API使用说明"""
    return jsonify({
        'service': '网页截图服务',
        'version': '1.0.0',
        'endpoints': {
            'POST /screenshot': '截取网页截图',
            'GET /health': '健康检查',
            'GET /': 'API说明'
        },
        'usage': {
            'url': '要截图的网址（必需）',
            'wait_time': '等待时间，默认3秒（可选）',
            'full_page': '是否截取完整页面，默认true（可选）',
            'format': '返回格式，base64或file，默认base64（可选）',
            'viewport_width': '视口宽度，默认1920（可选）',
            'viewport_height': '视口高度，默认1080（可选）'
        },
        'example': {
            'url': 'https://platform.kangfx.com',
            'wait_time': 3,
            'full_page': True,
            'format': 'base64',
            'viewport_width': 1920,
            'viewport_height': 1080
        }
    })
