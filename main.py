#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WebSnap 主入口
"""

import os
import logging
from app.app import create_app
from app.core.screenshot_service import ScreenshotService
from config.settings import config

# 配置日志
logging.basicConfig(
    level=getattr(logging, os.environ.get('LOG_LEVEL', 'INFO')),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建Flask应用
app = create_app(os.environ.get('FLASK_ENV', 'default'))

# 创建全局截图服务实例
screenshot_service = ScreenshotService()


def cleanup():
    """清理资源"""
    screenshot_service.close()


if __name__ == '__main__':
    try:
        config_class = config[os.environ.get('FLASK_ENV', 'default')]
        logger.info("启动WebSnap服务...")
        logger.info(f"环境: {os.environ.get('FLASK_ENV', 'default')}")
        logger.info(f"端口: {config_class.PORT}")
        
        app.run(
            host=config_class.HOST,
            port=config_class.PORT,
            debug=config_class.DEBUG
        )
    except KeyboardInterrupt:
        logger.info("服务正在关闭...")
    finally:
        cleanup()
