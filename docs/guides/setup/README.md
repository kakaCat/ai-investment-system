# 环境配置指南

> Vue 3 + FastAPI + PostgreSQL + DeepSeek 技术栈配置

---

## 📦 配置文档

### 环境配置

| 文档 | 用途 |
|------|------|
| [快速开始](quick-start.md) | 🌟 **从这里开始** - 完整的项目初始化指南 |
| [API 密钥](api-keys.md) | 获取 DeepSeek API Key 和 Tushare Token |
| [MCP 配置](mcp-setup.md) | Model Context Protocol 服务器配置 |

### 前端开发 ⭐

| 文档 | 用途 |
|------|------|
| [前端项目初始化](frontend-setup.md) | Vue 3 + TypeScript 项目完整配置指南 |
| [Mock 数据方案](mock-data-guide.md) | 前端开发阶段 Mock 数据配置 |
| [组件开发指南](component-guide.md) | 核心页面和公共组件开发示例 |

---

## ⚡ 快速开始

### 1. 运行项目初始化脚本

```bash
cd /path/to/stock
./scripts/setup/init-project.sh
```

脚本会自动：
- ✅ 检查开发环境（Python, Node.js, Docker 等）
- ✅ 创建项目目录结构（backend/, frontend/）
- ✅ 初始化 Python 项目（Poetry）
- ✅ 创建配置文件模板（.env, docker-compose.yml）

### 2. 启动数据库服务

```bash
docker-compose up -d
```

启动 PostgreSQL 和 Redis 容器。

### 3. 配置环境变量

```bash
cp backend/.env.example backend/.env
# 编辑 .env 文件，填入真实的 API Keys
```

**需要的 API Keys**:
- **DeepSeek API Key**: https://platform.deepseek.com/
- **Tushare Token**: https://tushare.pro/register

查看详细说明: [API 密钥获取指南](api-keys.md)

### 4. 安装依赖并启动

**后端**:
```bash
cd backend
poetry install
poetry run uvicorn app.main:app --reload
```

**前端**:
```bash
cd frontend
pnpm install
pnpm dev
```

访问:
- 前端: http://localhost:5173
- 后端 API: http://localhost:8000/docs

---

## 🛠️ 技术栈

### 后端
- **Python 3.11+**: 后端运行环境
- **FastAPI**: 现代 Python Web 框架
- **SQLAlchemy 2.0**: 异步 ORM
- **PostgreSQL 15+**: 关系型数据库
- **Redis**: 缓存（可选）

### 前端
- **Vue 3**: 渐进式前端框架
- **TypeScript**: 类型安全
- **Vite**: 快速构建工具
- **TailwindCSS**: 原子化 CSS
- **Element Plus**: UI 组件库（推荐）

### AI & 数据
- **DeepSeek API**: 投资分析 AI 模型
- **Tushare**: 股票数据 API（主要）
- **AkShare**: 备选数据源（免费）

---

## 📂 项目结构

初始化后的目录结构：

```
stock/
├── backend/                  # FastAPI 后端
│   ├── app/
│   │   ├── api/             # API 路由
│   │   ├── core/            # 核心配置
│   │   ├── db/              # 数据库连接
│   │   ├── models/          # SQLAlchemy 模型
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── services/        # 业务逻辑
│   │   └── utils/           # 工具函数
│   ├── tests/               # 单元测试
│   ├── alembic/             # 数据库迁移
│   ├── pyproject.toml       # Poetry 配置
│   └── .env                 # 环境变量
│
├── frontend/                # Vue 3 前端
│   ├── src/
│   │   ├── api/            # API 客户端
│   │   ├── components/     # Vue 组件
│   │   ├── pages/          # 页面组件
│   │   ├── router/         # 路由配置
│   │   ├── stores/         # Pinia 状态管理
│   │   ├── types/          # TypeScript 类型
│   │   └── utils/          # 工具函数
│   ├── package.json
│   └── vite.config.ts
│
├── docs/                    # 项目文档
├── data/                    # 数据文件
├── logs/                    # 日志文件
├── docker-compose.yml       # Docker 配置
└── .gitignore              # Git 忽略规则
```

---

## 🔑 环境变量说明

### 后端 `backend/.env`

```env
# 应用配置
APP_NAME=Investment Management System
APP_ENV=development
DEBUG=True

# 服务器
HOST=0.0.0.0
PORT=8000

# 数据库
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/investment

# Redis（可选）
REDIS_URL=redis://localhost:6379/0

# JWT 认证
SECRET_KEY=your-secret-key-change-this
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# DeepSeek API
DEEPSEEK_API_KEY=sk-your-actual-key
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
DEEPSEEK_MODEL=deepseek-chat

# Tushare API
TUSHARE_TOKEN=your-tushare-token

# CORS
CORS_ORIGINS=["http://localhost:5173"]
```

### 前端 `frontend/.env.development`

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_APP_TITLE=投资管理系统
```

---

## 🧪 验证安装

### 检查后端

```bash
# 健康检查
curl http://localhost:8000/health

# 预期响应
{"status": "ok", "database": "connected"}
```

### 检查数据库

```bash
# 连接 PostgreSQL
docker exec -it investment-db psql -U postgres -d investment

# 列出所有表
\dt

# 退出
\q
```

### 检查 DeepSeek API

```bash
cd backend
poetry run python -c "
from openai import OpenAI
import os

client = OpenAI(
    api_key=os.getenv('DEEPSEEK_API_KEY'),
    base_url='https://api.deepseek.com/v1'
)

response = client.chat.completions.create(
    model='deepseek-chat',
    messages=[{'role': 'user', 'content': '你好'}],
    max_tokens=50
)

print('✓ DeepSeek API 工作正常')
print('响应:', response.choices[0].message.content)
"
```

---

## 📖 后续步骤

1. 阅读 [技术栈选型文档](../../design/architecture/tech-stack.md) 了解技术决策
2. 查看 [数据库设计](../../design/database/schema-v1.md) 了解数据模型
3. 阅读 [PRD v3.1](../../prd/v3/main.md) 了解产品需求
4. 开始开发第一个功能！

---

## ❓ 常见问题

### Q: Poetry 安装失败
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

### Q: Docker 服务启动失败
```bash
# 清理并重启
docker-compose down -v
docker-compose up -d
```

### Q: 前端无法连接后端（CORS 错误）
检查 `backend/.env` 中 `CORS_ORIGINS` 配置是否包含前端地址。

### Q: Tushare 积分不足
使用 AkShare 作为备选数据源（免费）。

---

## 🔗 相关资源

- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [Vue 3 文档](https://cn.vuejs.org/)
- [DeepSeek API 文档](https://platform.deepseek.com/docs)
- [Tushare 文档](https://tushare.pro/document/2)
- [项目 GitHub](https://github.com/your-username/stock)

---

**🎉 配置完成后，您就可以开始开发了！**

有任何问题请查看 [快速开始指南](quick-start.md) 或提交 Issue。
