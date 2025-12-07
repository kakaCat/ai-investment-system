# AI Investment System - Backend

基于 FastAPI + PostgreSQL + SQLAlchemy 的异步后端服务

## 📁 项目结构

```
backend/
├── app/
│   ├── main.py                 # FastAPI 主应用
│   ├── __init__.py
│   ├── api/                    # API 路由
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── auth.py         # 认证接口
│   │       ├── accounts.py     # 账户管理
│   │       ├── holdings.py     # 持仓管理
│   │       ├── trades.py       # 交易记录
│   │       ├── stocks.py       # 股票数据
│   │       ├── events.py       # 事件管理
│   │       ├── ai_analysis.py  # AI分析
│   │       ├── reviews.py      # 用户评价 (v3.2)
│   │       ├── daily_review.py # 每日复盘 (v3.2)
│   │       ├── ai_chat.py      # AI对话 (v3.2)
│   │       └── settings.py     # 系统设置
│   ├── core/                   # 核心模块
│   │   ├── __init__.py
│   │   ├── config.py           # 配置管理
│   │   ├── database.py         # 数据库配置
│   │   ├── security.py         # 安全工具（JWT、密码）
│   │   └── dependencies.py     # 依赖注入
│   ├── models/                 # SQLAlchemy 模型
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── account.py
│   │   ├── holding.py
│   │   ├── trade.py
│   │   ├── stock.py
│   │   ├── event.py
│   │   ├── ai_decision.py      # v3.2
│   │   └── review.py           # v3.2
│   ├── schemas/                # Pydantic 模型
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── account.py
│   │   ├── holding.py
│   │   ├── trade.py
│   │   ├── stock.py
│   │   ├── event.py
│   │   ├── ai_decision.py      # v3.2
│   │   └── review.py           # v3.2
│   ├── services/               # 业务逻辑
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── account_service.py
│   │   ├── holding_service.py
│   │   ├── trade_service.py
│   │   ├── stock_service.py
│   │   ├── event_service.py
│   │   ├── ai_service.py       # AI分析服务
│   │   └── deepseek_client.py  # DeepSeek API客户端
│   └── utils/                  # 工具函数
│       ├── __init__.py
│       ├── logger.py
│       └── helpers.py
├── alembic/                    # 数据库迁移
│   ├── versions/
│   ├── env.py
│   └── script.py.mako
├── tests/                      # 测试
│   ├── __init__.py
│   ├── conftest.py
│   └── api/
│       └── v1/
│           ├── test_auth.py
│           ├── test_accounts.py
│           └── ...
├── logs/                       # 日志目录
├── .env                        # 环境变量（不提交）
├── .env.example                # 环境变量示例
├── requirements.txt            # Python依赖
├── alembic.ini                 # Alembic配置
├── pytest.ini                  # Pytest配置
└── README.md                   # 本文件
```

## 🚀 快速开始

### 1. 环境准备

```bash
# Python 3.11+
python --version

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，填入实际配置
```

### 3. 数据库初始化

```bash
# 创建PostgreSQL数据库
createdb investment_db

# 运行迁移
alembic upgrade head
```

### 4. 启动服务

```bash
# 开发模式
python -m app.main

# 或使用 uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. 访问API文档

- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

## 📡 API接口

### P0 核心接口（已实现）

| 接口 | 说明 | 状态 |
|------|------|------|
| POST /api/v1/auth/login | 用户登录 | ✅ |
| GET /api/v1/accounts | 获取账户列表 | ✅ |
| GET /api/v1/holdings | 获取持仓列表 | ✅ |
| GET /api/v1/trades | 获取交易记录 | ✅ |
| POST /api/v1/trades | 记录交易 | ✅ |
| GET /api/v1/stocks/{symbol}/quote | 获取股票行情 | ✅ |
| GET /api/v1/events | 获取事件列表 | ✅ |
| GET /api/v1/reviews/{symbol} | 获取股票评价 | ✅ |
| POST /api/v1/reviews/{symbol} | 保存股票评价 | ✅ |
| POST /api/v1/ai/daily-analysis | 批量AI分析 | ✅ |
| GET /api/v1/ai/daily-analysis/{task_id}/results | 获取分析结果 | ✅ |

完整接口文档请查看: [API文档](../docs/design/api/)

## 🔧 技术栈

- **FastAPI**: 现代、高性能的Web框架
- **SQLAlchemy 2.0**: 异步ORM
- **PostgreSQL 15+**: 关系型数据库
- **Alembic**: 数据库迁移工具
- **Pydantic**: 数据验证
- **JWT**: 身份认证
- **Redis**: 缓存和任务队列
- **Celery**: 后台任务处理
- **DeepSeek API**: AI分析

## 📝 开发规范

### 代码风格

```bash
# 格式化代码
black app/

# 代码检查
flake8 app/

# 类型检查
mypy app/
```

### 提交规范

```
<type>(<scope>): <subject>

feat(api): 添加用户评价接口
fix(db): 修复持仓计算错误
docs(api): 更新API文档
```

## 🧪 测试

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/api/v1/test_auth.py

# 查看覆盖率
pytest --cov=app tests/
```

## 📦 数据库迁移

```bash
# 创建新迁移
alembic revision --autogenerate -m "描述"

# 应用迁移
alembic upgrade head

# 回滚迁移
alembic downgrade -1
```

## 🔐 安全

- JWT Token认证
- 密码bcrypt加密
- SQL注入防护（使用ORM参数化查询）
- CORS配置
- 速率限制

## 📊 监控

- 日志记录（Loguru）
- 性能监控
- 错误追踪

## 🚧 待实现功能

### P1 功能
- [ ] 账户详情接口
- [ ] 股票搜索接口
- [ ] 事件详情接口
- [ ] 单股AI分析接口
- [ ] 每日复盘接口
- [ ] AI对话接口

### P2 功能
- [ ] 批量导入交易
- [ ] 财务数据接口
- [ ] 数据导出功能
- [ ] WebSocket实时推送

## 📚 相关文档

- [API接口文档](../docs/design/api/complete-api-list.md)
- [数据库设计](../docs/design/database/schema-v1.md)
- [PRD文档](../docs/prd/v3/main.md)

## 🤝 贡献

1. Fork 项目
2. 创建功能分支
3. 提交代码
4. 创建 Pull Request

## 📄 许可证

MIT License
