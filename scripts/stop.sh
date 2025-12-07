#!/bin/bash

# 停止所有开发服务

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

echo ""
echo "🛑 停止所有服务..."
echo ""

# 停止后端 (uvicorn)
if pkill -f "uvicorn app.main:app" 2>/dev/null; then
    echo -e "${GREEN}✅ 后端服务已停止${NC}"
else
    echo "   后端服务未运行"
fi

# 停止前端 (Vite)
if pkill -f "vite" 2>/dev/null; then
    echo -e "${GREEN}✅ 前端服务已停止${NC}"
else
    echo "   前端服务未运行"
fi

echo ""
echo -e "${GREEN}✅ 所有服务已停止${NC}"
echo ""
