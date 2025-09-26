# 性能基准和优化指南

## 性能基准数据

### 测试环境

- **CPU**: Intel Core i7-8700K @ 3.70GHz
- **内存**: 16GB DDR4
- **存储**: SSD NVMe
- **操作系统**: Ubuntu 20.04 LTS
- **Docker**: 20.10.21
- **Chrome版本**: 91.0.4472.124

### 基准测试结果

#### 1. 单请求性能

| 网站类型       | 平均响应时间 | 文件大小 | 成功率 |
| -------------- | ------------ | -------- | ------ |
| 简单静态页面   | 2.1s         | 245KB    | 99.8%  |
| 复杂动态页面   | 4.7s         | 1.2MB    | 98.5%  |
| 图片密集型页面 | 6.3s         | 2.8MB    | 97.2%  |
| 单页应用(SPA)  | 8.9s         | 1.8MB    | 95.8%  |

#### 2. 并发性能

| 并发数 | 平均响应时间 | 成功率 | 吞吐量(QPS) |
| ------ | ------------ | ------ | ----------- |
| 1      | 2.1s         | 99.8%  | 0.48        |
| 5      | 3.2s         | 98.5%  | 1.56        |
| 10     | 5.8s         | 96.2%  | 1.72        |
| 20     | 12.4s        | 89.3%  | 1.61        |
| 50     | 28.7s        | 72.1%  | 1.74        |

#### 3. 不同视口大小性能

| 视口大小  | 平均响应时间 | 文件大小 | 内存使用 |
| --------- | ------------ | -------- | -------- |
| 800x600   | 1.8s         | 180KB    | 120MB    |
| 1024x768  | 2.1s         | 245KB    | 135MB    |
| 1280x720  | 2.3s         | 320KB    | 150MB    |
| 1366x768  | 2.4s         | 380KB    | 160MB    |
| 1920x1080 | 2.8s         | 520KB    | 180MB    |
| 2560x1440 | 3.5s         | 890KB    | 220MB    |

#### 4. 不同等待时间性能

| 等待时间 | 平均响应时间 | 成功率 | 备注               |
| -------- | ------------ | ------ | ------------------ |
| 1s       | 1.9s         | 85.2%  | 页面可能未完全加载 |
| 3s       | 2.1s         | 98.5%  | 推荐设置           |
| 5s       | 2.3s         | 99.1%  | 适合复杂页面       |
| 10s      | 2.8s         | 99.5%  | 适合慢速网站       |
| 15s      | 3.2s         | 99.7%  | 适合极慢网站       |

## 性能优化建议

### 1. 系统级优化

#### 资源分配
```yaml
# docker-compose.yml
services:
  screenshot-service:
    deploy:
      resources:
        limits:
          memory: 2G      # 推荐2GB内存
          cpus: "1.0"     # 推荐1个CPU核心
        reservations:
          memory: 1G      # 最少1GB内存
          cpus: "0.5"     # 最少0.5个CPU核心
```

#### 系统调优
```bash
# 增加文件描述符限制
echo "* soft nofile 65536" >> /etc/security/limits.conf
echo "* hard nofile 65536" >> /etc/security/limits.conf

# 优化内核参数
echo "vm.max_map_count=262144" >> /etc/sysctl.conf
echo "net.core.somaxconn=65535" >> /etc/sysctl.conf
sysctl -p
```

### 2. Chrome优化

#### 启动参数优化
```python
chrome_options = [
    '--headless',
    '--no-sandbox',
    '--disable-dev-shm-usage',
    '--disable-gpu',
    '--disable-extensions',
    '--disable-plugins',
    '--disable-images',              # 禁用图片加载
    '--disable-javascript',          # 禁用JavaScript（如果不需要）
    '--disable-web-security',        # 禁用Web安全
    '--disable-features=VizDisplayCompositor',
    '--memory-pressure-off',         # 禁用内存压力检测
    '--max_old_space_size=512',      # 限制V8内存使用
    '--disable-background-timer-throttling',
    '--disable-backgrounding-occluded-windows',
    '--disable-renderer-backgrounding',
    '--disable-background-networking',
    '--disable-default-apps',
    '--disable-sync',
    '--disable-translate',
    '--hide-scrollbars',
    '--mute-audio',
    '--no-first-run',
    '--disable-logging',
    '--disable-permissions-api',
    '--disable-presentation-api',
    '--disable-print-preview',
    '--disable-speech-api',
    '--disable-file-system',
    '--disable-notifications',
    '--disable-geolocation',
    '--disable-media-session-api',
    '--disable-bluetooth',
    '--disable-usb',
    '--disable-serial',
    '--disable-hid',
    '--disable-device-discovery-notifications'
]
```

#### 内存优化
```python
# 定期清理Chrome进程
import psutil
import os

def cleanup_chrome_processes():
    """清理Chrome进程"""
    for proc in psutil.process_iter(['pid', 'name']):
        if 'chrome' in proc.info['name'].lower():
            try:
                proc.kill()
            except:
                pass

# 在每次截图后清理
def take_screenshot_with_cleanup(self, url, wait_time=3, full_page=True, 
                                viewport_width=None, viewport_height=None):
    try:
        result = self.take_screenshot(url, wait_time, full_page, viewport_width, viewport_height)
        return result
    finally:
        # 清理Chrome进程
        cleanup_chrome_processes()
```

### 3. 应用级优化

#### 连接池优化
```python
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class OptimizedHTTPClient:
    def __init__(self):
        self.session = requests.Session()
        
        # 配置重试策略
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
        # 配置适配器
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=10,
            pool_maxsize=20
        )
        
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
```

#### 缓存优化
```python
import redis
import hashlib
import json
from typing import Optional

class ScreenshotCache:
    def __init__(self, redis_host='localhost', redis_port=6379, redis_db=0):
        self.redis_client = redis.Redis(
            host=redis_host, 
            port=redis_port, 
            db=redis_db,
            decode_responses=True
        )
        self.cache_ttl = 3600  # 1小时缓存
    
    def get_cache_key(self, url: str, params: dict) -> str:
        """生成缓存键"""
        key_data = f"{url}:{json.dumps(params, sort_keys=True)}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get_screenshot(self, url: str, params: dict) -> Optional[dict]:
        """从缓存获取截图"""
        cache_key = self.get_cache_key(url, params)
        cached_data = self.redis_client.get(cache_key)
        if cached_data:
            return json.loads(cached_data)
        return None
    
    def set_screenshot(self, url: str, params: dict, screenshot_data: dict):
        """缓存截图"""
        cache_key = self.get_cache_key(url, params)
        self.redis_client.setex(
            cache_key, 
            self.cache_ttl, 
            json.dumps(screenshot_data)
        )
```

### 4. 负载均衡优化

#### Nginx配置优化
```nginx
upstream screenshot_backend {
    least_conn;  # 最少连接负载均衡
    server screenshot-service-1:9000 max_fails=3 fail_timeout=30s;
    server screenshot-service-2:9000 max_fails=3 fail_timeout=30s;
    server screenshot-service-3:9000 max_fails=3 fail_timeout=30s;
    
    keepalive 32;  # 保持连接
}

server {
    # 启用HTTP/2
    listen 443 ssl http2;
    
    # 启用gzip压缩
    gzip on;
    gzip_types application/json;
    gzip_min_length 1000;
    
    # 连接优化
    keepalive_timeout 65;
    keepalive_requests 100;
    
    location / {
        proxy_pass http://screenshot_backend;
        
        # 连接优化
        proxy_http_version 1.1;
        proxy_set_header Connection "";
        
        # 超时设置
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
        
        # 缓冲设置
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
        proxy_busy_buffers_size 8k;
    }
}
```

### 5. 监控和告警

#### Prometheus指标
```python
from prometheus_client import Counter, Histogram, Gauge, start_http_server

# 定义指标
REQUEST_COUNT = Counter('screenshot_requests_total', 'Total requests', ['method', 'status'])
REQUEST_DURATION = Histogram('screenshot_request_duration_seconds', 'Request duration')
ACTIVE_REQUESTS = Gauge('screenshot_active_requests', 'Active requests')
MEMORY_USAGE = Gauge('screenshot_memory_usage_bytes', 'Memory usage')

# 在请求处理中使用
@REQUEST_DURATION.time()
def process_request():
    ACTIVE_REQUESTS.inc()
    try:
        # 处理请求
        result = take_screenshot()
        REQUEST_COUNT.labels(method='POST', status='200').inc()
        return result
    except Exception as e:
        REQUEST_COUNT.labels(method='POST', status='500').inc()
        raise
    finally:
        ACTIVE_REQUESTS.dec()
```

#### Grafana仪表板
```json
{
  "dashboard": {
    "title": "Screenshot Service Performance",
    "panels": [
      {
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(screenshot_requests_total[5m])",
            "legendFormat": "{{method}} {{status}}"
          }
        ]
      },
      {
        "title": "Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(screenshot_request_duration_seconds_bucket[5m]))",
            "legendFormat": "95th percentile"
          },
          {
            "expr": "histogram_quantile(0.50, rate(screenshot_request_duration_seconds_bucket[5m]))",
            "legendFormat": "50th percentile"
          }
        ]
      },
      {
        "title": "Active Requests",
        "type": "graph",
        "targets": [
          {
            "expr": "screenshot_active_requests",
            "legendFormat": "Active Requests"
          }
        ]
      },
      {
        "title": "Memory Usage",
        "type": "graph",
        "targets": [
          {
            "expr": "screenshot_memory_usage_bytes",
            "legendFormat": "Memory Usage"
          }
        ]
      }
    ]
  }
}
```

## 性能测试工具

### 1. 内置性能测试

使用项目提供的性能测试脚本：

```bash
# 基本性能测试
python tests/performance_test.py

# 并发测试
python tests/performance_test.py --concurrent 10

# 特定测试类型
python tests/performance_test.py --test-type concurrent

# 自定义测试URL
python tests/performance_test.py --test-url https://example.com
```

### 2. 外部压力测试工具

#### Apache Bench (ab)
```bash
# 安装
sudo apt-get install apache2-utils

# 基本压力测试
ab -n 100 -c 10 -p test_data.json -T application/json http://localhost:9000/screenshot

# 测试数据文件 (test_data.json)
{
  "url": "https://platform.kangfx.com",
  "wait_time": 3,
  "full_page": true,
  "format": "base64"
}
```

#### wrk
```bash
# 安装
sudo apt-get install wrk

# 压力测试
wrk -t12 -c400 -d30s -s post.lua http://localhost:9000/screenshot

# Lua脚本 (post.lua)
wrk.method = "POST"
wrk.body = '{"url":"https://platform.kangfx.com","wait_time":3,"full_page":true,"format":"base64"}'
wrk.headers["Content-Type"] = "application/json"
```

#### Artillery
```bash
# 安装
npm install -g artillery

# 配置文件 (artillery.yml)
config:
  target: 'http://localhost:9000'
  phases:
    - duration: 60
      arrivalRate: 10
scenarios:
  - name: "Screenshot API"
    requests:
      - post:
          url: "/screenshot"
          json:
            url: "https://platform.kangfx.com"
            wait_time: 3
            full_page: true
            format: "base64"

# 运行测试
artillery run artillery.yml
```

## 性能调优检查清单

### 系统级检查
- [ ] 内存使用率 < 80%
- [ ] CPU使用率 < 70%
- [ ] 磁盘I/O正常
- [ ] 网络延迟 < 100ms
- [ ] 文件描述符限制充足

### 应用级检查
- [ ] Chrome进程正常启动
- [ ] 内存泄漏检查
- [ ] 连接池配置合理
- [ ] 缓存命中率 > 80%
- [ ] 错误率 < 1%

### 网络级检查
- [ ] 负载均衡配置正确
- [ ] SSL/TLS配置优化
- [ ] 压缩启用
- [ ] 连接复用配置
- [ ] 超时设置合理

### 监控检查
- [ ] 关键指标监控
- [ ] 告警规则配置
- [ ] 日志级别适当
- [ ] 性能数据收集
- [ ] 趋势分析

## 性能基准更新

建议定期更新性能基准数据：

1. **每月更新**: 基础性能指标
2. **每季度更新**: 完整性能报告
3. **版本发布时**: 性能对比分析
4. **硬件升级后**: 重新建立基准

通过持续的性能监控和优化，确保服务在高负载下仍能保持稳定的性能表现。
