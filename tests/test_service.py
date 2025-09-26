#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网页截图服务测试脚本
"""

import requests
import json
import base64
import time
from PIL import Image
from io import BytesIO


def test_screenshot_service():
    """测试截图服务"""
    base_url = "http://localhost:9000"
    
    print("🧪 开始测试网页截图服务...")
    
    # 测试1: 健康检查
    print("\n1️⃣ 测试健康检查接口...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ 健康检查通过")
            print(f"   响应: {response.json()}")
        else:
            print(f"❌ 健康检查失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 健康检查异常: {e}")
        return False
    
    # 测试2: API说明接口
    print("\n2️⃣ 测试API说明接口...")
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✅ API说明接口正常")
            data = response.json()
            print(f"   服务: {data['service']}")
            print(f"   版本: {data['version']}")
        else:
            print(f"❌ API说明接口失败: {response.status_code}")
    except Exception as e:
        print(f"❌ API说明接口异常: {e}")
    
    # 测试3: 基本截图功能
    print("\n3️⃣ 测试基本截图功能...")
    test_urls = [
        "https://platform.kangfx.com"
    ]
    
    for i, url in enumerate(test_urls, 1):
        print(f"\n   测试网址 {i}: {url}")
        try:
            response = requests.post(f"{base_url}/screenshot", json={
                "url": url,
                "wait_time": 3,
                "full_page": True,
                "format": "base64"
            })
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print(f"   ✅ 截图成功")
                    print(f"   📊 图片大小: {data.get('size', 0)} bytes")
                    
                    # 保存截图到文件
                    try:
                        screenshot_data = base64.b64decode(data['screenshot'])
                        image = Image.open(BytesIO(screenshot_data))
                        filename = f"test_screenshot_{i}_{int(time.time())}.png"
                        image.save(filename)
                        print(f"   💾 截图已保存: {filename}")
                    except Exception as e:
                        print(f"   ⚠️ 保存截图失败: {e}")
                else:
                    print(f"   ❌ 截图失败: {data.get('error', '未知错误')}")
            else:
                print(f"   ❌ 请求失败: {response.status_code}")
                print(f"   响应: {response.text}")
        except Exception as e:
            print(f"   ❌ 请求异常: {e}")
    
    # 测试4: 不同参数组合
    print("\n4️⃣ 测试不同参数组合...")
    test_cases = [
        {
            "name": "短等待时间",
            "params": {"url": "https://platform.kangfx.com", "wait_time": 1}
        },
        {
            "name": "非完整页面",
            "params": {"url": "https://platform.kangfx.com", "full_page": False}
        },
        {
            "name": "文件格式返回",
            "params": {"url": "https://platform.kangfx.com", "format": "file"}
        },
        {
            "name": "自定义视口大小",
            "params": {"url": "https://platform.kangfx.com", "viewport_width": 1280, "viewport_height": 720}
        }
    ]
    
    for case in test_cases:
        print(f"\n   测试: {case['name']}")
        try:
            response = requests.post(f"{base_url}/screenshot", json=case['params'])
            if response.status_code == 200:
                if case['params'].get('format') == 'file':
                    print(f"   ✅ 文件格式返回成功，大小: {len(response.content)} bytes")
                else:
                    data = response.json()
                    if data.get('success'):
                        print(f"   ✅ 参数测试成功")
                    else:
                        print(f"   ❌ 参数测试失败: {data.get('error')}")
            else:
                print(f"   ❌ 参数测试失败: {response.status_code}")
        except Exception as e:
            print(f"   ❌ 参数测试异常: {e}")
    
    print("\n🎉 测试完成！")
    return True


if __name__ == "__main__":
    print("=" * 50)
    print("网页截图服务测试")
    print("=" * 50)
    print("请确保服务已启动: python main.py")
    print("=" * 50)
    
    # 等待用户确认
    input("按回车键开始测试...")
    
    test_screenshot_service()
