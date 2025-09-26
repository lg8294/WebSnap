# 网页截图服务

一个基于Flask和Selenium的网页截图服务，支持自定义视口大小和多种输出格式。

## 项目结构

```
screenshot-service/
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
   docker build -t screenshot-service .
   docker run -d -p 9000:9000 screenshot-service
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

## 部署说明

详细的部署说明请参考 [DEPLOYMENT.md](DEPLOYMENT.md)

## 许可证

MIT License