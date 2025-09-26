#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Python中处理base64图片的示例
"""

import base64
import requests
from PIL import Image
from io import BytesIO
import os


def save_base64_image(base64_data, filename):
    """
    将base64数据保存为图片文件
    
    Args:
        base64_data: base64编码的图片数据
        filename: 保存的文件名
    """
    try:
        # 解码base64数据
        image_data = base64.b64decode(base64_data)
        
        # 保存为文件
        with open(filename, 'wb') as f:
            f.write(image_data)
        
        print(f"图片已保存: {filename}")
        return True
    except Exception as e:
        print(f"保存图片失败: {e}")
        return False


def base64_to_pil_image(base64_data):
    """
    将base64数据转换为PIL Image对象
    
    Args:
        base64_data: base64编码的图片数据
        
    Returns:
        PIL Image对象
    """
    try:
        image_data = base64.b64decode(base64_data)
        image = Image.open(BytesIO(image_data))
        return image
    except Exception as e:
        print(f"转换图片失败: {e}")
        return None


def pil_image_to_base64(image, format='PNG'):
    """
    将PIL Image对象转换为base64数据
    
    Args:
        image: PIL Image对象
        format: 图片格式
        
    Returns:
        base64编码的图片数据
    """
    try:
        buffer = BytesIO()
        image.save(buffer, format=format)
        image_data = buffer.getvalue()
        base64_data = base64.b64encode(image_data).decode('utf-8')
        return base64_data
    except Exception as e:
        print(f"转换base64失败: {e}")
        return None


def fetch_screenshot_as_base64(url, **kwargs):
    """
    获取网页截图并返回base64数据
    
    Args:
        url: 要截图的网址
        **kwargs: 其他参数
        
    Returns:
        base64编码的图片数据
    """
    try:
        response = requests.post('http://localhost:9000/screenshot', json={
            'url': url,
            'wait_time': kwargs.get('wait_time', 3),
            'full_page': kwargs.get('full_page', True),
            'viewport_width': kwargs.get('viewport_width', 1920),
            'viewport_height': kwargs.get('viewport_height', 1080),
            'format': 'base64'
        })
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                return data.get('screenshot')
            else:
                print(f"截图失败: {data.get('error')}")
                return None
        else:
            print(f"请求失败: {response.status_code}")
            return None
    except Exception as e:
        print(f"请求异常: {e}")
        return None


def create_html_with_base64_image(base64_data, title="截图"):
    """
    创建包含base64图片的HTML文件
    
    Args:
        base64_data: base64编码的图片数据
        title: 页面标题
        
    Returns:
        HTML内容
    """
    html_content = f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title}</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }}
            .container {{
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                text-align: center;
            }}
            img {{
                max-width: 100%;
                height: auto;
                border: 1px solid #ddd;
                border-radius: 5px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }}
            .info {{
                margin-top: 20px;
                color: #666;
                font-size: 14px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>{title}</h1>
            <img src="data:image/png;base64,{base64_data}" alt="{title}">
            <div class="info">
                <p>生成时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p>图片大小: {len(base64_data)} 字符</p>
            </div>
        </div>
    </body>
    </html>
    """
    return html_content


def batch_screenshots(urls, output_dir='screenshots'):
    """
    批量截图并保存
    
    Args:
        urls: 网址列表
        output_dir: 输出目录
    """
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    results = []
    
    for i, url in enumerate(urls, 1):
        print(f"正在截图 {i}/{len(urls)}: {url}")
        
        # 获取截图
        base64_data = fetch_screenshot_as_base64(url)
        
        if base64_data:
            # 保存为PNG文件
            filename = f"screenshot_{i}_{url.replace('https://', '').replace('/', '_')}.png"
            filepath = os.path.join(output_dir, filename)
            
            if save_base64_image(base64_data, filepath):
                results.append({
                    'url': url,
                    'filename': filepath,
                    'success': True
                })
            else:
                results.append({
                    'url': url,
                    'filename': None,
                    'success': False
                })
        else:
            results.append({
                'url': url,
                'filename': None,
                'success': False
            })
    
    return results


def main():
    """主函数 - 演示各种用法"""
    print("=== Base64图片处理示例 ===\n")
    
    # 示例1: 获取截图
    print("1. 获取网页截图...")
    url = "https://platform.kangfx.com"
    base64_data = fetch_screenshot_as_base64(url)
    
    if base64_data:
        print(f"✅ 截图成功，base64数据长度: {len(base64_data)}")
        
        # 示例2: 保存为文件
        print("\n2. 保存为PNG文件...")
        save_base64_image(base64_data, "example_screenshot.png")
        
        # 示例3: 转换为PIL Image
        print("\n3. 转换为PIL Image...")
        image = base64_to_pil_image(base64_data)
        if image:
            print(f"✅ 图片尺寸: {image.size}")
            
            # 示例4: 调整图片大小
            print("\n4. 调整图片大小...")
            resized_image = image.resize((800, 600))
            resized_base64 = pil_image_to_base64(resized_image)
            
            if resized_base64:
                save_base64_image(resized_base64, "resized_screenshot.png")
                print("✅ 调整大小后的图片已保存")
        
        # 示例5: 创建HTML文件
        print("\n5. 创建HTML文件...")
        html_content = create_html_with_base64_image(base64_data, "网页截图")
        with open("screenshot.html", "w", encoding="utf-8") as f:
            f.write(html_content)
        print("✅ HTML文件已创建: screenshot.html")
        
    else:
        print("❌ 截图失败")
    
    # 示例6: 批量截图
    print("\n6. 批量截图示例...")
    test_urls = [
        "https://platform.kangfx.com",
        "https://www.baidu.com",
        "https://www.github.com"
    ]
    
    results = batch_screenshots(test_urls)
    
    print("\n批量截图结果:")
    for result in results:
        status = "✅ 成功" if result['success'] else "❌ 失败"
        print(f"  {result['url']}: {status}")


if __name__ == "__main__":
    main()
