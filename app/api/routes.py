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
from flask_restx import Api, Resource, fields, Namespace

from app.core.screenshot_service import ScreenshotService

logger = logging.getLogger(__name__)

# 创建蓝图
api_bp = Blueprint('api', __name__)

# 创建RESTX API
api = Api(
    api_bp,
    version='1.0',
    title='WebSnap API',
    description='一个基于Flask和Selenium的网页截图服务',
    doc='/docs/',  # Swagger UI路径
    prefix='/api/v1'
)

# 创建命名空间
screenshot_ns = Namespace('screenshot', description='截图相关接口')
health_ns = Namespace('health', description='健康检查接口')
info_ns = Namespace('info', description='服务信息接口')

# 添加命名空间到API
api.add_namespace(screenshot_ns)
api.add_namespace(health_ns)
api.add_namespace(info_ns)

# 创建全局截图服务实例
screenshot_service = ScreenshotService()

# 定义数据模型
screenshot_request_model = api.model('ScreenshotRequest', {
    'url': fields.String(required=True, description='要截图的网址', example='https://platform.kangfx.com'),
    'wait_time': fields.Integer(min=1, max=60, default=3, description='页面加载等待时间（秒）'),
    'full_page': fields.Boolean(default=True, description='是否截取完整页面'),
    'format': fields.String(enum=['base64', 'file'], default='base64', description='返回格式'),
    'viewport_width': fields.Integer(min=320, max=4096, default=1920, description='视口宽度（像素）'),
    'viewport_height': fields.Integer(min=240, max=4096, default=1080, description='视口高度（像素）')
})

screenshot_response_model = api.model('ScreenshotResponse', {
    'success': fields.Boolean(description='请求是否成功'),
    'screenshot': fields.String(description='Base64编码的截图数据'),
    'url': fields.String(description='截图的网址'),
    'size': fields.Integer(description='截图数据大小（字节）')
})

error_response_model = api.model('ErrorResponse', {
    'success': fields.Boolean(description='请求是否成功'),
    'error': fields.String(description='错误信息')
})

health_response_model = api.model('HealthResponse', {
    'status': fields.String(description='服务状态'),
    'service': fields.String(description='服务名称'),
    'timestamp': fields.Float(description='时间戳')
})


# 截图接口
@screenshot_ns.route('/screenshot')
class ScreenshotResource(Resource):
    @screenshot_ns.expect(screenshot_request_model)
    def post(self):
        """
        截取网页截图
        
        支持自定义视口大小、等待时间和输出格式
        """
        try:
            data = request.get_json()
            
            if not data or 'url' not in data:
                return {
                    'success': False,
                    'error': '缺少必需参数: url'
                }, 400
            
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
                return {
                    'success': False,
                    'error': '截图失败，请检查网址是否正确'
                }, 500
            
            if return_format == 'base64':
                # 返回base64编码的图片
                screenshot_base64 = base64.b64encode(screenshot_data).decode('utf-8')
                return {
                    'success': True,
                    'screenshot': screenshot_base64,
                    'url': url,
                    'size': len(screenshot_data)
                }
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
            return {
                'success': False,
                'error': f'服务器内部错误: {str(e)}'
            }, 500


# 健康检查接口
@health_ns.route('/health')
class HealthResource(Resource):
    @health_ns.marshal_with(health_response_model)
    def get(self):
        """健康检查接口"""
        return {
            'status': 'healthy',
            'service': 'websnap',
            'timestamp': time.time()
        }


# API信息接口
@info_ns.route('/')
class InfoResource(Resource):
    def get(self):
        """首页，显示API使用说明"""
        return {
            'service': 'WebSnap',
            'version': '1.0.0',
            'endpoints': {
                'POST /api/v1/screenshot/screenshot': '截取网页截图',
                'GET /api/v1/health/health': '健康检查',
                'GET /api/v1/info/': 'API说明',
                'GET /docs/': 'Swagger API文档'
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
        }


# 兼容性路由（保持向后兼容）
@api_bp.route('/screenshot', methods=['POST'])
def take_screenshot_legacy():
    """兼容性截图接口"""
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
def health_check_legacy():
    """兼容性健康检查接口"""
    return HealthResource().get()


@api_bp.route('/', methods=['GET'])
def index_legacy():
    """兼容性首页接口"""
    return InfoResource().get()


@api_bp.route('/test', methods=['POST'])
def test_screenshot():
    """测试截图接口"""
    try:
        data = request.get_json()
        print(f"Received data: {data}")
        
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
        
        print(f"Taking screenshot of: {url}")
        
        # 截取截图
        screenshot_data = screenshot_service.take_screenshot(
            url, wait_time, full_page, viewport_width, viewport_height
        )
        
        print(f"Screenshot data size: {len(screenshot_data) if screenshot_data else 'None'}")
        
        if screenshot_data is None:
            return jsonify({
                'success': False,
                'error': '截图失败，请检查网址是否正确'
            }), 500
        
        if return_format == 'base64':
            # 返回base64编码的图片
            screenshot_base64 = base64.b64encode(screenshot_data).decode('utf-8')
            result = {
                'success': True,
                'screenshot': screenshot_base64,
                'url': url,
                'size': len(screenshot_data)
            }
            print(f"Returning result with size: {len(screenshot_data)}")
            return jsonify(result)
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
        print(f"Exception: {e}")
        return jsonify({
            'success': False,
            'error': f'服务器内部错误: {str(e)}'
        }), 500
