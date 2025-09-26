# 故障排除指南

## 常见问题及解决方案

### 1. 服务启动问题

#### 问题：Chrome/Chromium启动失败

**症状**：
- 服务启动时报错：`WebDriver 初始化失败`
- 日志显示：`Chrome/Chromium not found`

**解决方案**：
```bash
# 检查Chrome/Chromium是否安装
which chromium
which google-chrome

# 在Docker容器中检查
docker exec -it websnap-service /bin/bash
which chromium

# 如果未安装，重新构建镜像
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

**预防措施**：
- 确保Dockerfile中包含Chrome/Chromium安装
- 检查系统资源是否充足（内存至少512MB）

#### 问题：端口被占用

**症状**：
- 启动时报错：`Address already in use`
- 端口9000被其他服务占用

**解决方案**：
```bash
# 查看端口占用情况
netstat -tulpn | grep :9000
lsof -i :9000

# 停止占用端口的进程
sudo kill -9 <PID>

# 或修改docker-compose.yml中的端口映射
ports:
  - "9001:9000"  # 改为其他端口
```

#### 问题：权限不足

**症状**：
- 无法创建日志文件或截图文件
- 权限被拒绝错误

**解决方案**：
```bash
# 检查目录权限
ls -la logs/
ls -la screenshots/

# 修改权限
chmod 755 logs/
chmod 755 screenshots/
chown -R 1000:1000 logs/ screenshots/

# 在Docker中检查用户权限
docker exec -it websnap-service id
```

### 2. 截图功能问题

#### 问题：截图失败或返回空白

**症状**：
- API返回成功但截图为空
- 截图文件损坏或无法打开

**可能原因及解决方案**：

1. **网络连接问题**
```bash
# 测试网络连接
curl -I https://platform.kangfx.com
ping platform.kangfx.com

# 检查DNS解析
nslookup platform.kangfx.com
```

2. **页面加载超时**
```bash
# 增加等待时间
curl -X POST http://localhost:9000/screenshot \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://platform.kangfx.com",
    "wait_time": 10,
    "full_page": true,
    "format": "base64"
  }'
```

3. **JavaScript渲染问题**
```bash
# 检查Chrome控制台错误
docker exec -it websnap-service /bin/bash
google-chrome --headless --disable-gpu --dump-dom https://platform.kangfx.com
```

4. **内存不足**
```bash
# 检查内存使用
docker stats websnap-service

# 增加内存限制
deploy:
  resources:
    limits:
      memory: 2G
```

#### 问题：特定网站无法截图

**症状**：
- 某些网站截图失败
- 返回403或404错误

**解决方案**：

1. **检查User-Agent**
```python
# 在screenshot_service.py中修改User-Agent
chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
```

2. **处理反爬虫机制**
```python
# 添加更多Chrome选项
chrome_options.add_argument('--disable-blink-features=AutomationControlled')
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)
```

3. **处理Cookie和Session**
```python
# 如果需要登录，可以添加Cookie
driver.add_cookie({'name': 'session', 'value': 'your-session-value'})
```

### 3. 性能问题

#### 问题：响应时间过长

**症状**：
- 截图请求响应时间超过30秒
- 服务响应缓慢

**解决方案**：

1. **优化Chrome参数**
```python
chrome_options.add_argument('--disable-images')  # 禁用图片加载
chrome_options.add_argument('--disable-javascript')  # 禁用JavaScript（如果不需要）
chrome_options.add_argument('--disable-plugins')  # 禁用插件
```

2. **调整资源限制**
```yaml
deploy:
  resources:
    limits:
      memory: 2G
      cpus: "1.0"
```

3. **使用缓存**
```python
# 实现截图缓存
import redis
import hashlib

def get_cached_screenshot(url, params):
    cache_key = hashlib.md5(f"{url}:{params}".encode()).hexdigest()
    return redis_client.get(cache_key)
```

#### 问题：内存泄漏

**症状**：
- 服务运行时间越长，内存使用越高
- 最终导致OOM错误

**解决方案**：

1. **定期重启服务**
```bash
# 设置自动重启
restart: unless-stopped

# 或使用cron定期重启
0 2 * * * docker restart websnap-service
```

2. **优化Chrome内存使用**
```python
chrome_options.add_argument('--memory-pressure-off')
chrome_options.add_argument('--max_old_space_size=512')
```

### 4. 网络问题

#### 问题：无法访问外部网站

**症状**：
- 截图外部网站失败
- 网络超时错误

**解决方案**：

1. **检查防火墙设置**
```bash
# 检查防火墙状态
sudo ufw status

# 允许HTTP/HTTPS流量
sudo ufw allow out 80/tcp
sudo ufw allow out 443/tcp
```

2. **检查代理设置**
```bash
# 如果使用代理，配置Chrome代理
chrome_options.add_argument('--proxy-server=http://proxy:port')
```

3. **DNS问题**
```bash
# 检查DNS配置
cat /etc/resolv.conf

# 使用公共DNS
echo "nameserver 8.8.8.8" >> /etc/resolv.conf
```

### 5. 日志分析

#### 问题：如何分析日志

**日志位置**：
- Docker容器：`/app/logs/`
- 宿主机：`./logs/`

**重要日志信息**：
```bash
# 查看错误日志
docker logs websnap-service 2>&1 | grep ERROR

# 查看特定时间段的日志
docker logs --since="2024-01-01T00:00:00" screenshot-service

# 实时监控日志
docker logs -f screenshot-service
```

**日志级别调整**：
```bash
# 设置更详细的日志级别
export LOG_LEVEL=DEBUG
docker-compose up -d
```

### 6. 监控和告警

#### 问题：如何监控服务状态

**健康检查**：
```bash
# 检查服务健康状态
curl http://localhost:9000/health

# 设置监控脚本
#!/bin/bash
if ! curl -f http://localhost:9000/health > /dev/null 2>&1; then
    echo "Service is down, restarting..."
    docker restart websnap-service
fi
```

**性能监控**：
```bash
# 监控资源使用
docker stats websnap-service

# 监控API响应时间
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:9000/health
```

### 7. 常见错误码

| 错误码 | 含义           | 解决方案                |
| ------ | -------------- | ----------------------- |
| 400    | 参数错误       | 检查请求参数格式        |
| 500    | 服务器内部错误 | 查看服务日志            |
| 503    | 服务不可用     | 检查Chrome/Chromium状态 |
| 504    | 网关超时       | 增加等待时间或检查网络  |

### 8. 调试技巧

#### 启用调试模式
```bash
# 设置调试环境变量
export FLASK_ENV=development
export LOG_LEVEL=DEBUG

# 重新启动服务
docker-compose down
docker-compose up -d
```

#### 进入容器调试
```bash
# 进入运行中的容器
docker exec -it websnap-service /bin/bash

# 手动测试Chrome
google-chrome --headless --disable-gpu --dump-dom https://example.com

# 检查Chrome版本
google-chrome --version
```

#### 网络调试
```bash
# 测试网络连接
curl -v https://platform.kangfx.com

# 检查DNS解析
nslookup platform.kangfx.com

# 测试端口连通性
telnet platform.kangfx.com 443
```

### 9. 预防措施

1. **定期更新**：
   - 定期更新Docker镜像
   - 更新Chrome/Chromium版本
   - 更新Python依赖包

2. **资源监控**：
   - 监控内存和CPU使用
   - 设置资源限制
   - 配置告警机制

3. **备份策略**：
   - 定期备份配置文件
   - 备份重要数据
   - 测试恢复流程

4. **安全加固**：
   - 定期更新安全补丁
   - 配置防火墙规则
   - 监控异常访问

### 10. 获取帮助

如果以上解决方案都无法解决问题，请：

1. **收集信息**：
   - 错误日志
   - 系统信息
   - 复现步骤

2. **联系支持**：
   - 提交Issue到GitHub
   - 发送邮件到技术支持
   - 加入社区讨论

3. **提供信息**：
   - 操作系统版本
   - Docker版本
   - 错误截图
   - 完整日志文件
