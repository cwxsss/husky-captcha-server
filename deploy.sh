#!/usr/bin/env bash
# ==============================================================
# Husky Captcha Server 一键部署脚本
# 适用于 Ubuntu / Debian / CentOS / Aliyun Linux
# ==============================================================

set -e

echo "=== 正在启动 Husky Captcha Server 部署程序 ==="

# 1. 检查 Docker 是否安装
if ! command -v docker &> /dev/null; then
    echo "未检测到 Docker，正在自动安装 Docker..."
    curl -fsSL https://get.docker.com | bash -s docker
    systemctl enable --now docker
fi

# 2. 检查 Docker Compose
if ! docker compose version &> /dev/null; then
    echo "正在安装 Docker Compose 插件..."
    apt-get update && apt-get install -y docker-compose-plugin || true
fi

# 3. 构建并启动容器
echo "=== 正在构建并启动容器 (端口 7070) ==="
docker compose down || true
docker compose up -d --build

echo ""
echo "=========================================================="
echo "🎉 部署成功！Husky Captcha Server 已在后台运行。"
echo "访问仪表盘测试：http://$(curl -s ifconfig.me):7070"
echo "配套油猴脚本在：http://$(curl -s ifconfig.me):7070/userscript/husky-captcha.user.js"
echo "=========================================================="
