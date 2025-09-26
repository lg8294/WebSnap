#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网页截图服务性能测试脚本
"""

import requests
import time
import statistics
import concurrent.futures
import json
import base64
from typing import List, Dict, Any
import argparse
import sys


class PerformanceTester:
    """性能测试类"""
    
    def __init__(self, base_url: str = "http://localhost:9000"):
        self.base_url = base_url
        self.results = []
    
    def test_single_request(self, url: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """测试单个请求"""
        start_time = time.time()
        try:
            response = requests.post(f"{self.base_url}/screenshot", json=params, timeout=60)
            end_time = time.time()
            
            result = {
                'url': url,
                'status_code': response.status_code,
                'response_time': end_time - start_time,
                'success': response.status_code == 200,
                'error': None,
                'size': 0
            }
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    result['size'] = data.get('size', 0)
                else:
                    result['error'] = data.get('error', 'Unknown error')
                    result['success'] = False
            else:
                result['error'] = f"HTTP {response.status_code}"
                
        except requests.exceptions.Timeout:
            end_time = time.time()
            result = {
                'url': url,
                'status_code': 0,
                'response_time': end_time - start_time,
                'success': False,
                'error': 'Request timeout',
                'size': 0
            }
        except Exception as e:
            end_time = time.time()
            result = {
                'url': url,
                'status_code': 0,
                'response_time': end_time - start_time,
                'success': False,
                'error': str(e),
                'size': 0
            }
        
        return result
    
    def test_concurrent_requests(self, url: str, params: Dict[str, Any], 
                                concurrent_count: int = 5) -> List[Dict[str, Any]]:
        """测试并发请求"""
        print(f"测试并发请求: {concurrent_count} 个请求到 {url}")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_count) as executor:
            futures = [
                executor.submit(self.test_single_request, url, params)
                for _ in range(concurrent_count)
            ]
            
            results = []
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                results.append(result)
                print(f"  请求完成: {result['response_time']:.2f}s, 状态: {result['status_code']}")
        
        return results
    
    def test_different_websites(self, websites: List[str], params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """测试不同网站"""
        print(f"测试不同网站: {len(websites)} 个网站")
        
        results = []
        for i, website in enumerate(websites, 1):
            print(f"  测试网站 {i}/{len(websites)}: {website}")
            test_params = params.copy()
            test_params['url'] = website
            
            result = self.test_single_request(website, test_params)
            results.append(result)
            
            print(f"    响应时间: {result['response_time']:.2f}s")
            print(f"    状态: {result['status_code']}")
            print(f"    大小: {result['size']} bytes")
            
            # 避免请求过于频繁
            time.sleep(1)
        
        return results
    
    def test_different_viewport_sizes(self, url: str, viewport_sizes: List[tuple]) -> List[Dict[str, Any]]:
        """测试不同视口大小"""
        print(f"测试不同视口大小: {len(viewport_sizes)} 种配置")
        
        results = []
        for i, (width, height) in enumerate(viewport_sizes, 1):
            print(f"  测试视口 {i}/{len(viewport_sizes)}: {width}x{height}")
            
            params = {
                'url': url,
                'viewport_width': width,
                'viewport_height': height,
                'wait_time': 3,
                'full_page': True,
                'format': 'base64'
            }
            
            result = self.test_single_request(url, params)
            result['viewport'] = f"{width}x{height}"
            results.append(result)
            
            print(f"    响应时间: {result['response_time']:.2f}s")
            print(f"    状态: {result['status_code']}")
            print(f"    大小: {result['size']} bytes")
        
        return results
    
    def test_different_wait_times(self, url: str, wait_times: List[int]) -> List[Dict[str, Any]]:
        """测试不同等待时间"""
        print(f"测试不同等待时间: {len(wait_times)} 种配置")
        
        results = []
        for i, wait_time in enumerate(wait_times, 1):
            print(f"  测试等待时间 {i}/{len(wait_times)}: {wait_time}s")
            
            params = {
                'url': url,
                'wait_time': wait_time,
                'full_page': True,
                'format': 'base64'
            }
            
            result = self.test_single_request(url, params)
            result['wait_time'] = wait_time
            results.append(result)
            
            print(f"    响应时间: {result['response_time']:.2f}s")
            print(f"    状态: {result['status_code']}")
            print(f"    大小: {result['size']} bytes")
        
        return results
    
    def analyze_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析测试结果"""
        if not results:
            return {}
        
        successful_results = [r for r in results if r['success']]
        failed_results = [r for r in results if not r['success']]
        
        if not successful_results:
            return {
                'total_requests': len(results),
                'successful_requests': 0,
                'failed_requests': len(failed_results),
                'success_rate': 0.0,
                'error_summary': {}
            }
        
        response_times = [r['response_time'] for r in successful_results]
        sizes = [r['size'] for r in successful_results]
        
        # 统计错误
        error_summary = {}
        for result in failed_results:
            error = result.get('error', 'Unknown error')
            error_summary[error] = error_summary.get(error, 0) + 1
        
        return {
            'total_requests': len(results),
            'successful_requests': len(successful_results),
            'failed_requests': len(failed_results),
            'success_rate': len(successful_results) / len(results) * 100,
            'response_time_stats': {
                'min': min(response_times),
                'max': max(response_times),
                'mean': statistics.mean(response_times),
                'median': statistics.median(response_times),
                'std_dev': statistics.stdev(response_times) if len(response_times) > 1 else 0
            },
            'size_stats': {
                'min': min(sizes),
                'max': max(sizes),
                'mean': statistics.mean(sizes),
                'median': statistics.median(sizes),
                'std_dev': statistics.stdev(sizes) if len(sizes) > 1 else 0
            },
            'error_summary': error_summary
        }
    
    def print_summary(self, analysis: Dict[str, Any]):
        """打印测试摘要"""
        print("\n" + "="*60)
        print("性能测试摘要")
        print("="*60)
        
        print(f"总请求数: {analysis['total_requests']}")
        print(f"成功请求数: {analysis['successful_requests']}")
        print(f"失败请求数: {analysis['failed_requests']}")
        print(f"成功率: {analysis['success_rate']:.1f}%")
        
        if analysis['successful_requests'] > 0:
            print("\n响应时间统计:")
            rt_stats = analysis['response_time_stats']
            print(f"  最小: {rt_stats['min']:.2f}s")
            print(f"  最大: {rt_stats['max']:.2f}s")
            print(f"  平均: {rt_stats['mean']:.2f}s")
            print(f"  中位数: {rt_stats['median']:.2f}s")
            print(f"  标准差: {rt_stats['std_dev']:.2f}s")
            
            print("\n文件大小统计:")
            size_stats = analysis['size_stats']
            print(f"  最小: {size_stats['min']:,} bytes")
            print(f"  最大: {size_stats['max']:,} bytes")
            print(f"  平均: {size_stats['mean']:,.0f} bytes")
            print(f"  中位数: {size_stats['median']:,.0f} bytes")
            print(f"  标准差: {size_stats['std_dev']:,.0f} bytes")
        
        if analysis['error_summary']:
            print("\n错误统计:")
            for error, count in analysis['error_summary'].items():
                print(f"  {error}: {count} 次")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='网页截图服务性能测试')
    parser.add_argument('--url', default='http://localhost:9000', help='服务URL')
    parser.add_argument('--test-url', default='https://platform.kangfx.com', help='测试目标URL')
    parser.add_argument('--concurrent', type=int, default=5, help='并发请求数')
    parser.add_argument('--test-type', choices=['concurrent', 'websites', 'viewport', 'wait-time', 'all'], 
                       default='all', help='测试类型')
    
    args = parser.parse_args()
    
    print("网页截图服务性能测试")
    print("="*60)
    print(f"服务URL: {args.url}")
    print(f"测试目标: {args.test_url}")
    print(f"并发数: {args.concurrent}")
    print(f"测试类型: {args.test_type}")
    print("="*60)
    
    # 检查服务是否可用
    try:
        response = requests.get(f"{args.url}/health", timeout=10)
        if response.status_code != 200:
            print(f"❌ 服务健康检查失败: {response.status_code}")
            sys.exit(1)
        print("✅ 服务健康检查通过")
    except Exception as e:
        print(f"❌ 无法连接到服务: {e}")
        sys.exit(1)
    
    tester = PerformanceTester(args.url)
    all_results = []
    
    # 基本参数
    base_params = {
        'url': args.test_url,
        'wait_time': 3,
        'full_page': True,
        'format': 'base64'
    }
    
    if args.test_type in ['concurrent', 'all']:
        print("\n1. 并发性能测试")
        print("-" * 40)
        concurrent_results = tester.test_concurrent_requests(
            args.test_url, base_params, args.concurrent
        )
        all_results.extend(concurrent_results)
    
    if args.test_type in ['websites', 'all']:
        print("\n2. 不同网站测试")
        print("-" * 40)
        test_websites = [
            'https://www.google.com',
            'https://www.github.com',
            'https://www.stackoverflow.com',
            'https://platform.kangfx.com'
        ]
        website_results = tester.test_different_websites(test_websites, base_params)
        all_results.extend(website_results)
    
    if args.test_type in ['viewport', 'all']:
        print("\n3. 不同视口大小测试")
        print("-" * 40)
        viewport_sizes = [
            (1920, 1080),  # Full HD
            (1366, 768),   # HD
            (1280, 720),   # HD Ready
            (1024, 768),   # XGA
            (800, 600)     # SVGA
        ]
        viewport_results = tester.test_different_viewport_sizes(args.test_url, viewport_sizes)
        all_results.extend(viewport_results)
    
    if args.test_type in ['wait-time', 'all']:
        print("\n4. 不同等待时间测试")
        print("-" * 40)
        wait_times = [1, 3, 5, 10, 15]
        wait_time_results = tester.test_different_wait_times(args.test_url, wait_times)
        all_results.extend(wait_time_results)
    
    # 分析结果
    print("\n5. 结果分析")
    print("-" * 40)
    analysis = tester.analyze_results(all_results)
    tester.print_summary(analysis)
    
    # 保存结果
    timestamp = int(time.time())
    result_file = f"performance_test_results_{timestamp}.json"
    
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump({
            'test_info': {
                'service_url': args.url,
                'test_url': args.test_url,
                'concurrent_count': args.concurrent,
                'test_type': args.test_type,
                'timestamp': timestamp
            },
            'results': all_results,
            'analysis': analysis
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n测试结果已保存到: {result_file}")
    
    # 性能建议
    print("\n6. 性能建议")
    print("-" * 40)
    
    if analysis['success_rate'] < 95:
        print("⚠️  成功率较低，建议检查:")
        print("   - 网络连接稳定性")
        print("   - 服务资源使用情况")
        print("   - 目标网站可访问性")
    
    if analysis['successful_requests'] > 0:
        avg_response_time = analysis['response_time_stats']['mean']
        if avg_response_time > 10:
            print("⚠️  平均响应时间较长，建议:")
            print("   - 优化Chrome启动参数")
            print("   - 增加服务资源")
            print("   - 考虑使用缓存")
        elif avg_response_time < 3:
            print("✅ 响应时间表现良好")
        
        avg_size = analysis['size_stats']['mean']
        if avg_size > 1024 * 1024:  # 1MB
            print("⚠️  截图文件较大，建议:")
            print("   - 优化图片压缩")
            print("   - 调整视口大小")
            print("   - 禁用不必要的资源加载")


if __name__ == "__main__":
    main()
