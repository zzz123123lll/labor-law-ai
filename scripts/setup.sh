#!/bin/bash
set -e
echo "=== 劳动法智能维权AI - 环境初始化 ==="

# 后端
echo "[1/4] 安装后端依赖..."
cd fastapi-server
pip install -e ".[dev]"
cd ..

# 前端
echo "[2/4] 构建Web前端..."
cd web-app && npm install && npm run build && cd ..

echo "[3/4] 构建管理后台..."
cd admin-panel && npm install && npm run build && cd ..

# SSL目录
mkdir -p ssl

echo "[4/4] 初始化完成！"
echo ""
echo "本地启动："
echo "  cd fastapi-server && uvicorn app.main:app --reload"
echo "  cd web-app && npm run dev"
echo ""
echo "Docker部署："
echo "  docker compose up -d"
