# WebSnap

一个基于Flask和Selenium的网页截图服务，支持自定义视口大小和多种输出格式。

## 项目结构

```
WebSnap/
├── app/                    # 应用主目录
│   ├── __init__.py
│   ├── app.py             # Flask应用工厂
│   ├── api/               # API模块
│   │   ├── __init__.py
│   │   └── routes.py      # API路由定义
│   ├── core/              # 核心模块
│   │   ├── __init__.py
│   │   └── screenshot_service.py  # 截图服务核心类
│   ├── services/          # 服务模块
│   │   └── __init__.py
│   └── utils/             # 工具模块
│       ├── __init__.py
│       └── validators.py  # 数据验证工具
├── config/                # 配置模块
│   ├── __init__.py
│   └── settings.py        # 应用配置
├── tests/                 # 测试模块
│   ├── __init__.py
│   └── test_service.py    # 测试脚本
├── scripts/               # 脚本目录
│   ├── __init__.py
│   └── start.sh          # 启动脚本
├── docs/                  # 文档目录
├── main.py               # 主入口文件
├── requirements.txt      # Python依赖
├── Dockerfile           # Docker镜像构建文件
├── docker-compose.yml   # Docker Compose配置
├── .dockerignore        # Docker忽略文件
└── README.md           # 项目说明
```

## 系统要求

### 最低要求
- **Python**: 3.11+ 
- **内存**: 512MB RAM（推荐1GB+）
- **CPU**: 1核心（推荐2核心+）
- **磁盘**: 100MB可用空间
- **网络**: 能够访问目标网页

### 浏览器要求
- **Chromium**: 91.0+ （自动安装）
- **ChromeDriver**: 与Chromium版本匹配（自动安装）

### 操作系统支持
- ✅ **Linux**: Ubuntu 18.04+, CentOS 7+, Debian 9+
- ✅ **macOS**: 10.14+
- ✅ **Windows**: Windows 10+ (WSL2推荐)

### Docker环境
- **Docker**: 20.10+
- **Docker Compose**: 2.0+

## 功能特性

- ✅ **网页截图**: 支持任意网页的截图功能
- ✅ **自定义视口**: 可指定截图时的视口大小
- ✅ **多种格式**: 支持base64和文件两种返回格式
- ✅ **完整页面**: 支持截取完整页面或可见区域
- ✅ **等待时间**: 可配置页面加载等待时间
- ✅ **Docker支持**: 完整的Docker化部署方案
- ✅ **健康检查**: 内置健康检查接口
- ✅ **日志记录**: 完整的日志记录系统
- ✅ **配置管理**: 支持多环境配置
- ✅ **CORS支持**: 完整的跨域资源共享支持
- ✅ **安全配置**: 生产环境安全最佳实践

## 快速开始

### 本地开发

1. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

2. **启动服务**
   ```bash
   python main.py
   ```

3. **运行测试**
   ```bash
   python tests/test_service.py
   ```

### Docker部署

1. **使用Docker Compose（推荐）**
   ```bash
   docker-compose up -d
   ```

2. **使用Docker命令**
   ```bash
   docker build -t websnap .
   docker run -d -p 9000:9000 websnap
   ```

## API使用

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

## API详细说明

### POST /screenshot

截取网页截图的主要接口。

#### 请求参数

| 参数名            | 类型    | 必需 | 默认值   | 说明                                    |
| ----------------- | ------- | ---- | -------- | --------------------------------------- |
| `url`             | string  | ✅    | -        | 要截图的网址，支持http/https协议        |
| `wait_time`       | integer | ❌    | 3        | 页面加载等待时间（秒），范围：1-60      |
| `full_page`       | boolean | ❌    | true     | 是否截取完整页面，false时只截取可见区域 |
| `format`          | string  | ❌    | "base64" | 返回格式："base64" 或 "file"            |
| `viewport_width`  | integer | ❌    | 1920     | 视口宽度（像素），范围：320-4096        |
| `viewport_height` | integer | ❌    | 1080     | 视口高度（像素），范围：240-4096        |

#### 响应格式

**成功响应 (200)**:
```json
{
  "success": true,
  "screenshot": "iVBORw0KGgoAAAANSUhEUgAA...",
  "url": "https://platform.kangfx.com",
  "size": 123456
}
```

**错误响应**:
```json
{
  "success": false,
  "error": "错误描述信息"
}
```

#### 错误码说明

| HTTP状态码 | 错误类型   | 说明                       | 解决方案                 |
| ---------- | ---------- | -------------------------- | ------------------------ |
| 400        | 参数错误   | 缺少必需参数或参数格式错误 | 检查请求参数格式         |
| 500        | 服务器错误 | 截图失败或服务内部错误     | 检查目标URL是否可访问    |
| 503        | 服务不可用 | Chrome/Chromium启动失败    | 检查系统资源和Chrome安装 |

### GET /health

服务健康检查接口。

#### 响应格式

```json
{
  "status": "healthy",
  "service": "websnap",
  "timestamp": 1640995200.123
}
```

### GET /

API使用说明接口。

#### 响应格式

```json
{
  "service": "WebSnap",
  "version": "1.0.0",
  "endpoints": {
    "POST /screenshot": "截取网页截图",
    "GET /health": "健康检查",
    "GET /": "API说明"
  },
  "usage": {
    "url": "要截图的网址（必需）",
    "wait_time": "等待时间，默认3秒（可选）",
    "full_page": "是否截取完整页面，默认true（可选）",
    "format": "返回格式，base64或file，默认base64（可选）",
    "viewport_width": "视口宽度，默认1920（可选）",
    "viewport_height": "视口高度，默认1080（可选）"
  }
}
```

#### 请求限制

- **请求超时**: 30秒
- **最大请求大小**: 16MB
- **并发限制**: 建议不超过10个并发请求
- **频率限制**: 建议每秒不超过5个请求

## 配置说明

### 环境变量

| 变量名                  | 默认值  | 说明          |
| ----------------------- | ------- | ------------- |
| FLASK_ENV               | default | Flask运行环境 |
| HOST                    | 0.0.0.0 | 服务监听地址  |
| PORT                    | 9000    | 服务端口      |
| LOG_LEVEL               | INFO    | 日志级别      |
| DEFAULT_VIEWPORT_WIDTH  | 1920    | 默认视口宽度  |
| DEFAULT_VIEWPORT_HEIGHT | 1080    | 默认视口高度  |

### 配置类

- `DevelopmentConfig`: 开发环境配置
- `ProductionConfig`: 生产环境配置
- `TestingConfig`: 测试环境配置

## Base64图片显示

### HTML中显示base64图片

```html
<!-- 基本用法 -->
<img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA..." alt="截图">

<!-- 完整示例 -->
<img src="data:image/png;base64,你的base64数据" 
     alt="网页截图" 
     style="max-width: 100%; height: auto;">
```

### JavaScript中处理base64图片

```javascript
// 创建img元素并显示
function displayBase64Image(base64Data) {
    const img = document.createElement('img');
    img.src = 'data:image/png;base64,' + base64Data;
    document.body.appendChild(img);
}

// 在现有img元素中显示
function updateImage(imgElement, base64Data) {
    imgElement.src = 'data:image/png;base64,' + base64Data;
}
```

### Python中处理base64图片

```python
import base64
from PIL import Image
from io import BytesIO

# 保存base64图片为文件
def save_base64_image(base64_data, filename):
    image_data = base64.b64decode(base64_data)
    with open(filename, 'wb') as f:
        f.write(image_data)

# 转换为PIL Image对象
def base64_to_pil_image(base64_data):
    image_data = base64.b64decode(base64_data)
    return Image.open(BytesIO(image_data))
```

### 演示页面

我们提供了完整的HTML演示页面，展示了如何使用截图服务：

- **演示页面**: `docs/screenshot_demo.html` - 包含实时服务健康状态显示
- **CORS测试页面**: `docs/cors_test.html` - 包含健康状态监控的跨域测试
- **JavaScript示例**: `docs/base64_image_examples.js`
- **Python示例**: `docs/python_base64_examples.py`

### 实时健康状态监控

所有演示页面都包含实时服务健康状态监控功能：

- ✅ **实时状态显示**: 绿色圆点表示服务在线，红色表示离线
- ✅ **自动检查**: 每30秒自动检查服务状态
- ✅ **手动刷新**: 提供手动刷新按钮
- ✅ **详细信息**: 显示服务名称、状态和时间戳
- ✅ **错误提示**: 服务离线时显示具体错误信息

### CORS跨域支持

服务已配置CORS跨域支持，允许前端页面直接调用API：

- ✅ **完全跨域**: 支持所有域名的跨域请求
- ✅ **多种方法**: 支持GET、POST、OPTIONS等方法
- ✅ **标准头信息**: 支持Content-Type、Authorization等标准头
- ✅ **预检请求**: 自动处理OPTIONS预检请求

## 安全配置

### 生产环境安全建议

#### 1. 网络安全
- **防火墙配置**: 限制9000端口只允许必要的IP访问
- **反向代理**: 使用Nginx/Apache作为反向代理，配置SSL/TLS
- **CORS配置**: 生产环境应限制CORS_ORIGINS为具体域名
- **请求限制**: 配置请求频率限制和大小限制

#### 2. 容器安全
- **非root用户**: 容器内使用非root用户运行（已配置）
- **资源限制**: 设置内存和CPU限制防止资源耗尽
- **安全选项**: 启用no-new-privileges安全选项
- **镜像扫描**: 定期扫描Docker镜像漏洞

#### 3. 应用安全
- **密钥管理**: 生产环境使用强密钥替换默认SECRET_KEY
- **日志安全**: 避免在日志中记录敏感信息
- **输入验证**: 严格验证URL格式和参数范围
- **错误处理**: 避免在错误信息中泄露内部信息

#### 4. 监控和告警
- **健康检查**: 配置自动健康检查和重启
- **日志监控**: 监控异常日志和错误率
- **资源监控**: 监控CPU、内存使用情况
- **安全事件**: 监控异常请求和攻击行为

### 安全配置示例

#### Nginx反向代理配置
```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:9000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 安全头
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";
    }
}
```

#### 环境变量安全配置
```bash
# 生产环境变量
export SECRET_KEY="your-very-secure-secret-key-here"
export CORS_ORIGINS="https://yourdomain.com,https://app.yourdomain.com"
export LOG_LEVEL="WARNING"
export FLASK_ENV="production"
```

## 开发指南

### 添加新功能

1. 在 `app/core/` 中添加核心业务逻辑
2. 在 `app/api/` 中添加API接口
3. 在 `app/utils/` 中添加工具函数
4. 在 `tests/` 中添加测试用例

### 代码规范

- 使用类型提示
- 遵循PEP 8代码风格
- 添加适当的文档字符串
- 编写单元测试

### 安全开发规范

- **输入验证**: 所有用户输入必须验证
- **错误处理**: 避免泄露敏感信息
- **日志记录**: 记录安全相关事件
- **依赖管理**: 定期更新依赖包

## 文档目录

- 📖 [部署指南](DEPLOYMENT.md) - 详细的部署说明和最佳实践
- 🔧 [故障排除](docs/TROUBLESHOOTING.md) - 常见问题及解决方案
- 📊 [性能指南](docs/PERFORMANCE.md) - 性能基准和优化建议
- 📋 [API规范](docs/api_spec.yaml) - OpenAPI/Swagger API文档

## 快速链接

- 🚀 **Swagger UI**: http://localhost:9000/docs/
- 🏥 **健康检查**: http://localhost:9000/health
- 📝 **API说明**: http://localhost:9000/
- 🧪 **性能测试**: `python tests/performance_test.py`

## 许可证

MIT License