# 网页截图服务 Docker 部署指南

## 快速开始

### 1. 使用 Docker Compose 部署（推荐）

```bash
# 构建并启动服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f screenshot-service

# 停止服务
docker-compose down
```

### 2. 使用 Docker 命令部署

```bash
# 构建镜像
docker build -t screenshot-service .

# 运行容器
docker run -d \
  --name screenshot-service \
  -p 9000:9000 \
  -v $(pwd)/screenshots:/app/screenshots \
  -v $(pwd)/logs:/app/logs \
  screenshot-service

# 查看容器状态
docker ps

# 查看日志
docker logs -f screenshot-service

# 停止容器
docker stop screenshot-service
docker rm screenshot-service
```

## 服务配置

### 环境变量

| 变量名           | 默认值     | 说明                         |
| ---------------- | ---------- | ---------------------------- |
| FLASK_ENV        | production | Flask运行环境                |
| PYTHONUNBUFFERED | 1          | Python输出缓冲设置           |
| CORS_ORIGINS     | *          | 允许的跨域源，多个用逗号分隔 |

### 端口配置

- **服务端口**: 9000
- **健康检查**: http://localhost:9000/health

### 目录挂载

- `./screenshots:/app/screenshots` - 截图输出目录
- `./logs:/app/logs` - 日志输出目录

## API 使用

### 基本截图

```bash
curl -X POST http://localhost:9000/screenshot \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://platform.kangfx.com",
    "wait_time": 3,
    "full_page": true,
    "format": "base64"
  }'
```

### 自定义视口大小

```bash
curl -X POST http://localhost:9000/screenshot \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://platform.kangfx.com",
    "viewport_width": 1280,
    "viewport_height": 720,
    "wait_time": 3,
    "full_page": true,
    "format": "base64"
  }'
```

### 健康检查

```bash
curl http://localhost:9000/health
```

## 监控和维护

### 查看服务状态

```bash
# 使用 docker-compose
docker-compose ps

# 使用 docker
docker ps | grep screenshot-service
```

### 查看日志

```bash
# 使用 docker-compose
docker-compose logs -f screenshot-service

# 使用 docker
docker logs -f screenshot-service
```

### 重启服务

```bash
# 使用 docker-compose
docker-compose restart screenshot-service

# 使用 docker
docker restart screenshot-service
```

### 更新服务

```bash
# 使用 docker-compose
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# 使用 docker
docker stop screenshot-service
docker rm screenshot-service
docker build -t screenshot-service .
docker run -d --name screenshot-service -p 9000:9000 screenshot-service
```

## 故障排除

### 常见问题

1. **Chrome启动失败**
   - 检查系统资源是否充足
   - 查看容器日志中的错误信息

2. **端口冲突**
   - 修改 docker-compose.yml 中的端口映射
   - 或使用 `docker run -p 其他端口:9000`

3. **权限问题**
   - 确保挂载目录有正确的读写权限
   - 检查容器内的用户权限

### 调试模式

```bash
# 进入容器调试
docker exec -it screenshot-service /bin/bash

# 查看Chrome版本
google-chrome --version

# 查看ChromeDriver版本
chromedriver --version
```

## 生产环境最佳实践

### 1. 高可用部署

#### 负载均衡配置
```yaml
# docker-compose.prod.yml
version: "3.8"

services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - screenshot-service-1
      - screenshot-service-2
      - screenshot-service-3

  screenshot-service-1:
    build: .
    container_name: screenshot-service-1
    environment:
      - FLASK_ENV=production
      - PYTHONUNBUFFERED=1
    volumes:
      - ./logs:/app/logs
      - ./screenshots:/app/screenshots
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: "0.5"

  screenshot-service-2:
    build: .
    container_name: screenshot-service-2
    environment:
      - FLASK_ENV=production
      - PYTHONUNBUFFERED=1
    volumes:
      - ./logs:/app/logs
      - ./screenshots:/app/screenshots
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: "0.5"

  screenshot-service-3:
    build: .
    container_name: screenshot-service-3
    environment:
      - FLASK_ENV=production
      - PYTHONUNBUFFERED=1
    volumes:
      - ./logs:/app/logs
      - ./screenshots:/app/screenshots
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: "0.5"
```

#### Nginx负载均衡配置
```nginx
upstream screenshot_backend {
    server screenshot-service-1:9000;
    server screenshot-service-2:9000;
    server screenshot-service-3:9000;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    
    # 安全头
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";
    
    # 请求限制
    limit_req_zone $binary_remote_addr zone=screenshot:10m rate=5r/s;
    limit_req zone=screenshot burst=10 nodelay;
    
    location / {
        proxy_pass http://screenshot_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 超时设置
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
        
        # 健康检查
        proxy_next_upstream error timeout invalid_header http_500 http_502 http_503;
    }
    
    location /health {
        access_log off;
        proxy_pass http://screenshot_backend;
    }
}
```

### 2. 监控和告警

#### Prometheus监控配置
```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'screenshot-service'
    static_configs:
      - targets: ['screenshot-service-1:9000', 'screenshot-service-2:9000', 'screenshot-service-3:9000']
    metrics_path: '/metrics'
    scrape_interval: 30s
```

#### Grafana仪表板配置
```json
{
  "dashboard": {
    "title": "Screenshot Service Dashboard",
    "panels": [
      {
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])",
            "legendFormat": "{{instance}}"
          }
        ]
      },
      {
        "title": "Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "95th percentile"
          }
        ]
      },
      {
        "title": "Error Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total{status=~\"5..\"}[5m])",
            "legendFormat": "5xx errors"
          }
        ]
      }
    ]
  }
}
```

### 3. 日志管理

#### ELK Stack配置
```yaml
# docker-compose.logging.yml
version: "3.8"

services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:7.15.0
    environment:
      - discovery.type=single-node
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data
    ports:
      - "9200:9200"

  logstash:
    image: docker.elastic.co/logstash/logstash:7.15.0
    volumes:
      - ./logstash.conf:/usr/share/logstash/pipeline/logstash.conf
      - ./logs:/var/log/screenshot-service
    depends_on:
      - elasticsearch

  kibana:
    image: docker.elastic.co/kibana/kibana:7.15.0
    ports:
      - "5601:5601"
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
    depends_on:
      - elasticsearch

volumes:
  elasticsearch_data:
```

#### 日志轮转配置
```bash
# /etc/logrotate.d/screenshot-service
/var/log/screenshot-service/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 root root
    postrotate
        docker restart screenshot-service-1 screenshot-service-2 screenshot-service-3
    endscript
}
```

### 4. 备份和恢复

#### 自动备份脚本
```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/backup/screenshot-service"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="screenshot-backup-$DATE.tar.gz"

# 创建备份目录
mkdir -p $BACKUP_DIR

# 备份截图文件
tar -czf $BACKUP_DIR/$BACKUP_FILE \
    /var/lib/docker/volumes/screenshot-service_screenshots \
    /var/lib/docker/volumes/screenshot-service_logs

# 清理7天前的备份
find $BACKUP_DIR -name "screenshot-backup-*.tar.gz" -mtime +7 -delete

# 上传到云存储（可选）
# aws s3 cp $BACKUP_DIR/$BACKUP_FILE s3://your-backup-bucket/
```

#### 恢复脚本
```bash
#!/bin/bash
# restore.sh

BACKUP_FILE=$1
BACKUP_DIR="/backup/screenshot-service"

if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: $0 <backup-file>"
    exit 1
fi

# 停止服务
docker-compose down

# 恢复文件
tar -xzf $BACKUP_DIR/$BACKUP_FILE -C /

# 重启服务
docker-compose up -d
```

### 5. 安全加固

#### 防火墙配置
```bash
# UFW防火墙规则
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
ufw deny 9000/tcp   # 禁止直接访问应用端口
ufw enable
```

#### SSL证书自动更新
```bash
#!/bin/bash
# ssl-renew.sh

# 使用Let's Encrypt自动更新证书
certbot renew --quiet

# 重新加载Nginx配置
nginx -s reload
```

### 6. 性能优化

#### 缓存策略
```python
# 添加Redis缓存支持
import redis
import json
import hashlib

class ScreenshotCache:
    def __init__(self):
        self.redis_client = redis.Redis(host='redis', port=6379, db=0)
        self.cache_ttl = 3600  # 1小时缓存
    
    def get_cache_key(self, url, params):
        """生成缓存键"""
        key_data = f"{url}:{json.dumps(params, sort_keys=True)}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get_screenshot(self, url, params):
        """从缓存获取截图"""
        cache_key = self.get_cache_key(url, params)
        cached_data = self.redis_client.get(cache_key)
        if cached_data:
            return json.loads(cached_data)
        return None
    
    def set_screenshot(self, url, params, screenshot_data):
        """缓存截图"""
        cache_key = self.get_cache_key(url, params)
        self.redis_client.setex(
            cache_key, 
            self.cache_ttl, 
            json.dumps(screenshot_data)
        )
```

#### 资源优化
```yaml
# docker-compose.optimized.yml
version: "3.8"

services:
  screenshot-service:
    build: .
    environment:
      - FLASK_ENV=production
      - PYTHONUNBUFFERED=1
      - CHROME_OPTIONS=--memory-pressure-off --max_old_space_size=512
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: "1.0"
        reservations:
          memory: 1G
          cpus: "0.5"
    ulimits:
      nofile:
        soft: 65536
        hard: 65536
```

## 生产环境建议

1. **资源限制**: 已在 docker-compose.yml 中设置了内存和CPU限制
2. **安全设置**: 启用了 no-new-privileges 安全选项
3. **健康检查**: 配置了自动健康检查
4. **日志管理**: 建议配置日志轮转和监控
5. **备份策略**: 定期备份截图和日志数据
6. **负载均衡**: 使用多个实例提高可用性
7. **监控告警**: 配置Prometheus + Grafana监控
8. **缓存优化**: 添加Redis缓存减少重复请求
9. **SSL/TLS**: 配置HTTPS和证书自动更新
10. **防火墙**: 限制网络访问提高安全性

## 性能优化

1. **调整资源限制**: 根据实际使用情况调整内存和CPU限制
2. **优化Chrome参数**: 根据需要在Dockerfile中调整Chrome启动参数
3. **缓存策略**: 考虑添加Redis等缓存层
4. **负载均衡**: 对于高并发场景，考虑使用多个容器实例
5. **连接池**: 优化数据库和外部服务连接
6. **压缩**: 启用gzip压缩减少传输大小
7. **CDN**: 使用CDN加速静态资源访问
