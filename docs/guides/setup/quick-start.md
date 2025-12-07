# 快速开始指南

**版本**: v1.0
**日期**: 2025-11-14
**技术栈**: Vue 3 + FastAPI + PostgreSQL + DeepSeek

---

## 前置要求

确保已安装以下工具：

| 工具 | 版本要求 | 用途 |
|------|---------|------|
| Python | 3.11+ | 后端运行环境 |
| Node.js | 18+ | 前端开发环境 |
| pnpm | 8+ | Node 包管理器 |
| Docker | 20+ | 容器化服务（PostgreSQL/Redis） |
| Poetry | 1.5+ | Python 依赖管理 |

### 安装指南

**Poetry** (Python 依赖管理):
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

**pnpm** (Node 包管理器):
```bash
npm install -g pnpm
```

**Docker Desktop**:
- macOS/Windows: https://www.docker.com/products/docker-desktop
- Linux: 使用系统包管理器安装

---

## 一键初始化

### 1. 运行初始化脚本

```bash
cd /path/to/stock
./scripts/setup/init-project.sh
```

脚本会自动：
- ✅ 检查开发环境
- ✅ 创建项目目录结构
- ✅ 初始化 Python 项目（Poetry）
- ✅ 创建配置文件模板
- ✅ 创建 Docker Compose 配置

### 2. 启动基础服务

```bash
# 启动 PostgreSQL + Redis
docker-compose up -d

# 检查服务状态
docker-compose ps
```

预期输出：
```
NAME                IMAGE               STATUS
investment-db       postgres:15-alpine  Up (healthy)
investment-redis    redis:7-alpine      Up (healthy)
```

---

## 后端设置

### 1. 配置环境变量

```bash
cd backend
cp .env.example .env
```

编辑 `.env` 文件，填入真实的 API Keys:

```env
# DeepSeek API
DEEPSEEK_API_KEY=sk-your-actual-deepseek-api-key

# Tushare API
TUSHARE_TOKEN=your-tushare-token

# 生成安全的 SECRET_KEY
SECRET_KEY=$(openssl rand -hex 32)
```

**获取 API Keys**:
- DeepSeek: https://platform.deepseek.com/ (注册后在控制台获取)
- Tushare: https://tushare.pro/register (注册后在个人中心查看)

### 2. 安装 Python 依赖

```bash
cd backend

# 使用 Poetry 安装
poetry install

# 或者使用传统 pip（如果没有 Poetry）
pip install -r requirements.txt  # 需要先从 pyproject.toml 生成
```

### 3. 初始化数据库

```bash
# 创建数据库迁移
poetry run alembic revision --autogenerate -m "Initial schema"

# 执行迁移
poetry run alembic upgrade head

# （可选）填充测试数据
poetry run python -m app.db.seed
```

### 4. 启动后端服务

```bash
# 开发模式（热重载）
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 或使用简化命令
poetry run dev
```

访问 API 文档：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## 前端设置

### 1. 初始化 Vue 项目（首次）

```bash
# 使用 Vite 创建 Vue 3 + TypeScript 项目
pnpm create vite frontend -- --template vue-ts

cd frontend
pnpm install
```

### 2. 安装额外依赖

```bash
# UI 组件库（选择 Element Plus）
pnpm add element-plus @element-plus/icons-vue

# 路由和状态管理
pnpm add vue-router pinia

# HTTP 客户端
pnpm add axios

# TailwindCSS
pnpm add -D tailwindcss postcss autoprefixer
npx tailwindcss init -p

# 开发工具
pnpm add -D @types/node
```

### 3. 配置前端环境变量

创建 `frontend/.env.development`:

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_APP_TITLE=投资管理系统
```

### 4. 启动前端服务

```bash
cd frontend
pnpm dev
```

访问应用：http://localhost:5173

---

## 验证安装

### 健康检查

```bash
# 检查后端 API
curl http://localhost:8000/health

# 预期响应
{"status": "ok", "database": "connected"}
```

### 测试 DeepSeek API

```bash
# 在后端项目中运行测试
poetry run python -c "
from openai import OpenAI
import os

client = OpenAI(
    api_key=os.getenv('DEEPSEEK_API_KEY'),
    base_url='https://api.deepseek.com/v1'
)

response = client.chat.completions.create(
    model='deepseek-chat',
    messages=[{'role': 'user', 'content': '你好'}]
)

print(response.choices[0].message.content)
"
```

### 测试数据库连接

```bash
# PostgreSQL
docker exec -it investment-db psql -U postgres -d investment -c "SELECT version();"

# Redis
docker exec -it investment-redis redis-cli PING
# 预期输出: PONG
```

---

## 开发工作流

### 日常开发

```bash
# 1. 启动基础服务（首次或重启后）
docker-compose up -d

# 2. 启动后端（终端 1）
cd backend
poetry run uvicorn app.main:app --reload

# 3. 启动前端（终端 2）
cd frontend
pnpm dev

# 4. 开始编码！
```

### 代码质量检查

**后端**:
```bash
cd backend

# 格式化代码
poetry run black .

# Linting
poetry run ruff check .

# 类型检查
poetry run mypy app/

# 运行测试
poetry run pytest
```

**前端**:
```bash
cd frontend

# Linting
pnpm lint

# 格式化
pnpm format

# 运行测试
pnpm test:unit
```

---

## 常见问题

### Q1: PostgreSQL 连接失败

**问题**: `FATAL: password authentication failed for user "postgres"`

**解决**:
```bash
# 重置数据库
docker-compose down -v
docker-compose up -d
```

### Q2: 前端无法连接后端 API

**问题**: CORS 错误

**解决**:
确保 `backend/.env` 中配置了正确的 CORS 源：
```env
CORS_ORIGINS=["http://localhost:5173", "http://localhost:3000"]
```

### Q3: DeepSeek API 调用失败

**问题**: `AuthenticationError: Invalid API Key`

**解决**:
1. 检查 `.env` 文件中 `DEEPSEEK_API_KEY` 是否正确
2. 验证 API Key: https://platform.deepseek.com/api_keys
3. 确保账户有余额

### Q4: Poetry 安装依赖慢

**解决**:
```bash
# 使用国内镜像源
poetry source add --priority=primary tsinghua https://pypi.tuna.tsinghua.edu.cn/simple/
```

---

## 下一步

- [ ] 阅读 [PRD v3.1](../../prd/v3/main.md) 了解产品功能
- [ ] 查看 [数据库设计](../../design/database/schema-v1.md)
- [ ] 了解 [技术栈选型](../../design/architecture/tech-stack.md)
- [ ] 开始实现核心功能！

---

## 有用的命令

### Docker

```bash
# 查看日志
docker-compose logs -f postgres
docker-compose logs -f redis

# 进入容器
docker exec -it investment-db bash
docker exec -it investment-redis sh

# 清理重启
docker-compose down && docker-compose up -d
```

### 数据库迁移

```bash
# 创建迁移
poetry run alembic revision --autogenerate -m "描述"

# 应用迁移
poetry run alembic upgrade head

# 回滚
poetry run alembic downgrade -1

# 查看历史
poetry run alembic history
```

### 后端快捷命令（可配置）

在 `backend/pyproject.toml` 中添加：
```toml
[tool.poetry.scripts]
dev = "uvicorn app.main:app --reload"
migrate = "alembic upgrade head"
test = "pytest"
```

---

**祝开发顺利！** 如遇问题请查看项目文档或提交 Issue。
