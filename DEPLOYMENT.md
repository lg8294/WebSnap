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

## 生产环境建议

1. **资源限制**: 已在 docker-compose.yml 中设置了内存和CPU限制
2. **安全设置**: 启用了 no-new-privileges 安全选项
3. **健康检查**: 配置了自动健康检查
4. **日志管理**: 建议配置日志轮转和监控
5. **备份策略**: 定期备份截图和日志数据

## 性能优化

1. **调整资源限制**: 根据实际使用情况调整内存和CPU限制
2. **优化Chrome参数**: 根据需要在Dockerfile中调整Chrome启动参数
3. **缓存策略**: 考虑添加Redis等缓存层
4. **负载均衡**: 对于高并发场景，考虑使用多个容器实例
