#!/bin/bash

# 投资管理系统 - 项目初始化脚本
# 用途：创建项目目录结构并初始化前后端项目

set -e  # 遇到错误立即退出

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$PROJECT_ROOT"

echo "======================================"
echo "  投资管理系统 - 项目初始化"
echo "======================================"
echo ""

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# 检查必要的工具
echo "1. 检查开发环境..."
echo ""

check_command() {
    if command -v $1 &> /dev/null; then
        print_success "$1 已安装"
        return 0
    else
        print_error "$1 未安装"
        return 1
    fi
}

MISSING_TOOLS=0

check_command "python3" || MISSING_TOOLS=1
check_command "node" || MISSING_TOOLS=1
check_command "pnpm" || {
    print_warning "pnpm 未安装，可以用 npm 替代"
}
check_command "docker" || {
    print_warning "docker 未安装，无法使用 Docker Compose"
}
check_command "poetry" || {
    print_warning "poetry 未安装，推荐安装: curl -sSL https://install.python-poetry.org | python3 -"
}

if [ $MISSING_TOOLS -eq 1 ]; then
    print_error "缺少必要的开发工具，请先安装"
    exit 1
fi

echo ""
echo "2. 创建项目目录结构..."
echo ""

# 创建后端目录
mkdir -p backend/{app/{api,core,db,models,schemas,services,utils},tests,alembic/versions}
print_success "创建后端目录: backend/"

# 创建前端目录
mkdir -p frontend/{src/{api,assets,components,composables,layouts,pages,router,stores,types,utils},public}
print_success "创建前端目录: frontend/"

# 创建其他目录
mkdir -p {data,logs,uploads}
print_success "创建数据目录: data/, logs/, uploads/"

echo ""
echo "3. 初始化 Python 后端项目..."
echo ""

cd backend

if [ -f "pyproject.toml" ]; then
    print_warning "pyproject.toml 已存在，跳过初始化"
else
    if command -v poetry &> /dev/null; then
        poetry init --no-interaction \
            --name "investment-backend" \
            --description "AI-driven Investment Management System - Backend" \
            --author "Your Name <your.email@example.com>" \
            --python "^3.11" \
            --dependency fastapi --dependency "uvicorn[standard]" \
            --dependency sqlalchemy --dependency asyncpg \
            --dependency pydantic --dependency pydantic-settings \
            --dependency alembic --dependency python-jose \
            --dependency passlib --dependency bcrypt \
            --dependency python-multipart --dependency aiofiles

        print_success "后端项目初始化完成"
    else
        print_warning "未安装 poetry，请手动创建 pyproject.toml"
    fi
fi

cd "$PROJECT_ROOT"

echo ""
echo "4. 初始化 Vue 前端项目..."
echo ""

if [ -f "frontend/package.json" ]; then
    print_warning "frontend/package.json 已存在，跳过初始化"
else
    print_warning "请手动执行: pnpm create vite frontend -- --template vue-ts"
    echo "  然后运行: cd frontend && pnpm install"
fi

echo ""
echo "5. 创建配置文件..."
echo ""

# 创建后端环境变量模板
cat > backend/.env.example << 'EOF'
# 应用配置
APP_NAME=Investment Management System
APP_ENV=development
DEBUG=True

# 服务器配置
HOST=0.0.0.0
PORT=8000

# 数据库配置
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/investment
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20

# Redis 配置
REDIS_URL=redis://localhost:6379/0

# JWT 配置
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# DeepSeek API
DEEPSEEK_API_KEY=your-deepseek-api-key
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
DEEPSEEK_MODEL=deepseek-chat

# Tushare API
TUSHARE_TOKEN=your-tushare-token

# CORS 配置
CORS_ORIGINS=["http://localhost:5173", "http://localhost:3000"]
EOF

print_success "创建 backend/.env.example"

# 创建 Docker Compose 配置
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: investment-db
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: investment
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: investment-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
  redis_data:
EOF

print_success "创建 docker-compose.yml"

# 创建 .gitignore
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv/
*.egg-info/
dist/
build/

# Node.js
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
pnpm-debug.log*
.pnpm-store/

# 环境变量
.env
.env.local
.env.*.local

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# 操作系统
.DS_Store
Thumbs.db

# 项目特定
data/
logs/
uploads/
*.log

# 数据库
*.db
*.sqlite

# 前端构建
frontend/dist/
frontend/.vite/
frontend/.nuxt/

# 测试覆盖率
.coverage
htmlcov/
.pytest_cache/
EOF

print_success "创建 .gitignore"

echo ""
echo "======================================"
echo "  初始化完成！"
echo "======================================"
echo ""
echo "下一步操作："
echo ""
echo "1. 启动数据库服务："
echo "   ${GREEN}docker-compose up -d${NC}"
echo ""
echo "2. 配置后端环境变量："
echo "   ${GREEN}cp backend/.env.example backend/.env${NC}"
echo "   然后编辑 backend/.env 填入真实的 API Keys"
echo ""
echo "3. 安装后端依赖："
echo "   ${GREEN}cd backend && poetry install${NC}"
echo ""
echo "4. 初始化前端项目（如果还没有）："
echo "   ${GREEN}pnpm create vite frontend -- --template vue-ts${NC}"
echo "   ${GREEN}cd frontend && pnpm install${NC}"
echo ""
echo "5. 运行数据库迁移："
echo "   ${GREEN}cd backend && poetry run alembic upgrade head${NC}"
echo ""
echo "6. 启动开发服务器："
echo "   后端: ${GREEN}cd backend && poetry run uvicorn app.main:app --reload${NC}"
echo "   前端: ${GREEN}cd frontend && pnpm dev${NC}"
echo ""
print_success "Happy Coding!"
