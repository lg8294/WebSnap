# 使用官方Python运行时作为基础镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

# 安装系统依赖和Chromium
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    ca-certificates \
    fonts-liberation \
    fonts-liberation-sans-narrow \
    fonts-dejavu \
    fonts-dejavu-core \
    fonts-dejavu-extra \
    fonts-wqy-zenhei \
    fonts-wqy-microhei \
    fonts-noto-cjk \
    fonts-noto-cjk-extra \
    fonts-noto-color-emoji \
    fonts-roboto \
    fonts-roboto-unhinted \
    fonts-open-sans \
    fonts-lato \
    fonts-droid-fallback \
    fonts-freefont-ttf \
    fonts-arphic-ukai \
    fonts-arphic-uming \
    fonts-unfonts-core \
    fonts-unfonts-extra \
    fonts-takao \
    fonts-takao-gothic \
    fonts-takao-mincho \
    fonts-sil-gentium \
    fonts-sil-gentium-basic \
    fonts-cantarell \
    fonts-croscore \
    fonts-crosextra-caladea \
    fonts-crosextra-carlito \
    libasound2 \
    libatk-bridge2.0-0 \
    libdrm2 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libxss1 \
    libnss3 \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# 复制requirements文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 复制字体配置文件
COPY fonts.conf /etc/fonts/local.conf

# 下载并安装Microsoft YaHei字体
RUN mkdir -p /usr/share/fonts/truetype/microsoft \
    && wget -O /tmp/msyh.ttf "https://github.com/adobe-fonts/source-han-sans/raw/release/OTF/SimplifiedChinese/SourceHanSansSC-Regular.otf" \
    && mv /tmp/msyh.ttf /usr/share/fonts/truetype/microsoft/msyh.ttf \
    && chmod 644 /usr/share/fonts/truetype/microsoft/msyh.ttf \
    && rm -f /tmp/msyh.ttf

# 更新字体缓存
RUN fc-cache -fv

# 创建非root用户
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# 暴露端口
EXPOSE 9000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:9000/health || exit 1

# 启动命令
CMD ["python", "main.py"]
