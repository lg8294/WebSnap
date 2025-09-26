#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据验证工具
"""

import re
from urllib.parse import urlparse
from typing import Optional, Tuple


def validate_url(url: str) -> Tuple[bool, Optional[str]]:
    """
    验证URL格式
    
    Args:
        url: 要验证的URL
        
    Returns:
        (是否有效, 错误信息)
    """
    if not url:
        return False, "URL不能为空"
    
    # 如果没有协议，添加https://
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    try:
        parsed = urlparse(url)
        if not parsed.netloc:
            return False, "URL格式不正确"
        
        # 简单的域名格式验证
        domain_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$'
        if not re.match(domain_pattern, parsed.netloc):
            return False, "域名格式不正确"
            
        return True, None
    except Exception as e:
        return False, f"URL解析失败: {str(e)}"


def validate_viewport_size(width: int, height: int) -> Tuple[bool, Optional[str]]:
    """
    验证视口大小
    
    Args:
        width: 宽度
        height: 高度
        
    Returns:
        (是否有效, 错误信息)
    """
    if width <= 0 or height <= 0:
        return False, "视口大小必须大于0"
    
    if width > 4096 or height > 4096:
        return False, "视口大小不能超过4096像素"
    
    return True, None


def validate_wait_time(wait_time: int) -> Tuple[bool, Optional[str]]:
    """
    验证等待时间
    
    Args:
        wait_time: 等待时间（秒）
        
    Returns:
        (是否有效, 错误信息)
    """
    if wait_time < 0:
        return False, "等待时间不能为负数"
    
    if wait_time > 60:
        return False, "等待时间不能超过60秒"
    
    return True, None
