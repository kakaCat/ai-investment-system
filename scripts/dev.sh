#!/bin/bash

# 一键启动开发环境
# 功能:
# ✅ 并行启动前后端（不互相阻塞）
# ✅ 端口占用检测
# ✅ 健康检查等待
# ✅ 日志分离输出
# ✅ 优雅停止（Ctrl+C）
# ✅ 支持热重载

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
LOGDIR="$SCRIPT_DIR/logs"
mkdir -p "$LOGDIR"

# 端口配置
BACKEND_PORT=8000
FRONTEND_PORT=5175
DB_PORT=5432

echo ""
echo "🚀 启动开发环境..."
echo "=================================="
echo ""

# 1. 检查端口占用
check_port() {
    local port=$1
    local name=$2
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${RED}❌ 端口 $port 已被占用（$name）${NC}"
        echo "   请先停止占用进程: lsof -ti:$port | xargs kill -9"
        return 1
    else
        echo -e "${GREEN}✅ 端口 $port 可用（$name）${NC}"
        return 0
    fi
}

echo "📍 检查端口占用..."
check_port $BACKEND_PORT "后端" || exit 1
check_port $FRONTEND_PORT "前端" || exit 1
echo ""

# 2. 检查数据库
echo "📊 检查PostgreSQL数据库..."
if lsof -Pi :$DB_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${GREEN}✅ PostgreSQL已运行（端口 $DB_PORT）${NC}"
else
    echo -e "${YELLOW}⚠️  PostgreSQL未运行${NC}"
    echo "   启动PostgreSQL: brew services start postgresql@15"
    echo "   或继续启动（某些功能可能不可用）"
    echo ""
fi

# 3. 启动后端（后台运行）
echo "🔧 启动后端服务..."
cd "$PROJECT_ROOT/backend"
if [ ! -d "venv" ] && [ ! -d ".venv" ]; then
    echo -e "${YELLOW}⚠️  未发现Python虚拟环境${NC}"
fi

# 启动后端
python -m uvicorn app.main:app \
    --host 0.0.0.0 \
    --port $BACKEND_PORT \
    --reload \
    > "$LOGDIR/backend.log" 2>&1 &
BACKEND_PID=$!
echo -e "   后端PID: $BACKEND_PID"
echo -e "   日志: ${BLUE}$LOGDIR/backend.log${NC}"

# 4. 启动前端（后台运行）
echo ""
echo "🎨 启动前端服务..."
cd "$PROJECT_ROOT/frontend"
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}⚠️  未发现node_modules，请先运行: npm install${NC}"
fi

# 启动前端
npm run dev > "$LOGDIR/frontend.log" 2>&1 &
FRONTEND_PID=$!
echo -e "   前端PID: $FRONTEND_PID"
echo -e "   日志: ${BLUE}$LOGDIR/frontend.log${NC}"

# 5. 健康检查
echo ""
echo "⏳ 等待服务就绪..."
sleep 3

check_service() {
    local url=$1
    local name=$2
    local max_attempts=10
    local attempt=1

    while [ $attempt -le $max_attempts ]; do
        if curl -s -o /dev/null -w "%{http_code}" $url | grep -q "200\|404"; then
            echo -e "${GREEN}✅ $name 已就绪${NC}"
            return 0
        fi
        echo -e "   等待 $name 启动... ($attempt/$max_attempts)"
        sleep 2
        attempt=$((attempt + 1))
    done

    echo -e "${RED}❌ $name 启动超时${NC}"
    return 1
}

check_service "http://localhost:$BACKEND_PORT/health" "后端服务"
check_service "http://localhost:$FRONTEND_PORT" "前端服务"

# 6. 显示信息
echo ""
echo "========================================="
echo -e "${GREEN}✅ 开发环境启动成功！${NC}"
echo "========================================="
echo ""
echo "📍 服务地址:"
echo "   后端: ${BLUE}http://localhost:$BACKEND_PORT${NC}"
echo "   前端: ${BLUE}http://localhost:$FRONTEND_PORT${NC}"
echo "   API文档: ${BLUE}http://localhost:$BACKEND_PORT/docs${NC}"
echo ""
echo "📝 日志文件:"
echo "   后端: ${BLUE}tail -f $LOGDIR/backend.log${NC}"
echo "   前端: ${BLUE}tail -f $LOGDIR/frontend.log${NC}"
echo ""
echo "💡 提示:"
echo "   - 代码修改会自动热重载"
echo "   - 按 ${YELLOW}Ctrl+C${NC} 停止所有服务"
echo "   - 查看实时日志: ${BLUE}tail -f $LOGDIR/backend.log${NC}"
echo ""
echo "🔧 其他命令:"
echo "   停止服务: ${BLUE}./scripts/stop.sh${NC}"
echo "   重启服务: ${BLUE}./scripts/restart.sh${NC}"
echo "   架构检查: ${BLUE}python scripts/check_architecture.py${NC}"
echo ""

# 7. 优雅停止
cleanup() {
    echo ""
    echo ""
    echo "🛑 正在停止服务..."

    # 停止后端
    if kill -0 $BACKEND_PID 2>/dev/null; then
        echo "   停止后端 (PID: $BACKEND_PID)"
        kill $BACKEND_PID 2>/dev/null
    fi

    # 停止前端
    if kill -0 $FRONTEND_PID 2>/dev/null; then
        echo "   停止前端 (PID: $FRONTEND_PID)"
        kill $FRONTEND_PID 2>/dev/null
    fi

    # 等待进程结束
    sleep 1

    echo -e "${GREEN}✅ 所有服务已停止${NC}"
    echo ""
    exit 0
}

trap cleanup INT TERM

# 8. 保持运行
echo "按 ${YELLOW}Ctrl+C${NC} 停止服务..."
echo ""

# 实时显示日志（可选）
# tail -f "$LOGDIR/backend.log" "$LOGDIR/frontend.log"

# 或者只是等待
wait
