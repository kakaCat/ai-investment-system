# 技术栈选型

**版本**: v1.1
**日期**: 2025-01-15
**状态**: 已确定并与 PRD v3.1 同步

---

## 整体架构

```
┌─────────────────────────────────────────────────────┐
│                   Client Browser                     │
│              Vue 3 + TypeScript + Vite               │
│                   TailwindCSS                        │
└──────────────────┬──────────────────────────────────┘
                   │ HTTP/WebSocket
                   │
┌──────────────────▼──────────────────────────────────┐
│              FastAPI Backend                         │
│         (Python 3.11+ / Async)                       │
├──────────────────────────────────────────────────────┤
│  Business Logic │ AI Service │ Data Adapters         │
│                 │  DeepSeek  │  Tushare/AkShare     │
└──────────┬──────┴────────────┴──────────────────────┘
           │ SQLAlchemy 2.0 (Async)
           │
┌──────────▼──────────────────────────────────────────┐
│              PostgreSQL 15+                          │
│       (Multi-user / Multi-account)                   │
└──────────────────────────────────────────────────────┘
```

---

## 前端技术栈

### Vue 3 + TypeScript + Vite

**选择原因**:
1. **Vue 3 组合式 API**: 更好的逻辑复用和类型推断
2. **TypeScript**: 类型安全，减少运行时错误
3. **Vite**: 极快的开发服务器和构建速度（基于 ESBuild）
4. **生态成熟**: 大量高质量组件库（Element Plus, Ant Design Vue）

**关键依赖**:
```json
{
  "vue": "^3.4.0",
  "vue-router": "^4.2.0",
  "pinia": "^2.1.0",
  "vite": "^5.0.0",
  "typescript": "^5.3.0"
}
```

### UI 组件库

**待选方案**:
- **Element Plus**: 企业级组件库，中文友好，表格/表单组件强大
- **Ant Design Vue**: 蚂蚁金服设计体系，适合金融场景
- **Naive UI**: TypeScript 优先，组件质量高

**推荐**: Element Plus（考虑到投资管理系统需要大量表格和表单）

### 状态管理

**Pinia**: Vue 3 官方推荐，替代 Vuex
- 更好的 TypeScript 支持
- 模块化设计，自动代码分割
- DevTools 支持

### 样式方案

**TailwindCSS**:
- 原子化 CSS，开发效率高
- 配合组件库使用，快速定制样式
- 生产环境自动移除未使用的样式

---

## 后端技术栈

### FastAPI + Python 3.11+

**选择原因**:
1. **现代 Python**: 使用最新的类型提示和异步特性
2. **高性能**: 基于 Starlette 和 Pydantic，性能接近 Node.js/Go
3. **自动文档**: 基于 OpenAPI 自动生成交互式 API 文档
4. **异步支持**: 原生 async/await，适合 I/O 密集型应用
5. **类型安全**: Pydantic 模型自动验证和序列化
6. **生态丰富**: 数据分析库（pandas, numpy）、金融库丰富

**关键依赖**:
```python
fastapi = "^0.104.0"
uvicorn[standard] = "^0.24.0"
sqlalchemy = "^2.0.0"
asyncpg = "^0.29.0"  # PostgreSQL async driver
pydantic = "^2.5.0"
pydantic-settings = "^2.1.0"
```

### 数据库 ORM

**SQLAlchemy 2.0 (Async)**:
- **异步支持**: 使用 asyncpg 驱动，充分利用 Python async
- **类型提示**: 2.0 版本改进了类型推断
- **灵活性**: 支持复杂查询和原生 SQL
- **迁移工具**: Alembic 自动管理数据库版本

**替代方案考虑**:
- ~~Tortoise ORM~~: 功能较少，生态不如 SQLAlchemy
- ~~Django ORM~~: 需要整个 Django 框架，过重

---

## 数据库

### PostgreSQL 15+

**选择原因**:
1. **ACID 保证**: 金融数据必须保证事务一致性
2. **JSON 支持**: 存储 AI 分析结果、事件元数据
3. **时序优化**: 支持分区表，优化历史行情查询
4. **丰富扩展**:
   - `pg_stat_statements`: 性能分析
   - `pgcrypto`: 加密支持
   - `uuid-ossp`: UUID 生成（备选）
5. **全文搜索**: 支持中文分词（可选 zhparser 插件）

**版本要求**: 15+ （支持 MERGE 语句，优化的 JSON 性能）

---

## AI 集成

### DeepSeek API

**选择原因**:
1. **成本优势**: 相比 GPT-4/Claude，价格更低
   - Input: ¥1/M tokens
   - Output: ¥2/M tokens
2. **中文优化**: 对中文金融术语理解更好
3. **长上下文**: 支持 64K context，可一次分析更多数据
4. **OpenAI 兼容**: 可使用 OpenAI SDK，迁移成本低

**模型选择**:
- **deepseek-chat**: 通用对话模型，适合投资分析
- **deepseek-coder**: 如需代码生成（策略回测脚本）

**API 集成方式**:
```python
# 使用 OpenAI SDK 兼容接口
from openai import OpenAI

client = OpenAI(
    api_key="<DeepSeek API Key>",
    base_url="https://api.deepseek.com/v1"
)

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[...],
    temperature=0.7,
    max_tokens=2000
)
```

**成本控制**:
- 实现结果缓存（Redis）
- 批量分析优化
- Token 使用量监控
- 用户 Token 配额管理

---

## 数据源集成

### 股票行情数据

#### Tushare Pro（主要数据源）

**优势**:
- 数据质量高，覆盖全面（A股/港股/美股）
- 支持实时行情、历史数据、财务数据
- Python SDK 成熟
- 提供因子数据、指数数据

**限制**:
- 需要积分（免费账户有限制）
- API 调用频率限制

**使用场景**:
- 日线级别历史数据
- 财务报表数据
- 公司基本信息
- 行业分类数据

#### AkShare（备选/补充）

**优势**:
- 完全免费
- 数据来源多样（东方财富、新浪财经等）
- 支持期货、期权、基金等

**限制**:
- 数据质量参差不齐
- 部分接口不稳定
- 需要爬虫逻辑，可能受网站变更影响

**使用场景**:
- Tushare 配额不足时的降级方案
- 获取实时资讯、公告

### 新闻与事件数据

**方案**:
1. **主动爬取**: 定时爬取财经网站（东方财富、新浪财经）
2. **RSS 订阅**: 订阅相关主题 RSS
3. **API 服务**: 使用第三方新闻 API（如有预算）

**处理流程**:
```
新闻采集 → 去重 → 存储 → AI 分析（DeepSeek） → 事件分类 → 影响评估
```

---

## 开发工具链

### 代码质量

**Python**:
- **Black**: 代码格式化（统一风格）
- **Ruff**: 超快的 Linter（替代 Flake8/isort）
- **MyPy**: 类型检查
- **Pytest**: 单元测试

**TypeScript/Vue**:
- **ESLint**: 代码检查
- **Prettier**: 格式化
- **Vitest**: 单元测试（Vite 原生支持）
- **Vue Test Utils**: 组件测试

### 依赖管理

**Python**:
- **Poetry**: 现代化依赖管理工具
  - `pyproject.toml` 统一配置
  - 自动解析依赖冲突
  - 虚拟环境管理

**Node.js**:
- **pnpm**: 更快的包管理器，节省磁盘空间

### API 文档

**FastAPI 自动生成**:
- Swagger UI: `/docs`
- ReDoc: `/redoc`
- OpenAPI Schema: `/openapi.json`

---

## 部署方案（待详细设计）

### 开发环境

```
Docker Compose:
  - PostgreSQL 15
  - Redis 7 (缓存)
  - FastAPI (uvicorn --reload)
  - Vite Dev Server
```

### 生产环境（初步）

```
服务器: 阿里云/腾讯云
  - FastAPI: Uvicorn + Gunicorn (多进程)
  - Vue: Nginx 静态托管
  - PostgreSQL: 云数据库 RDS
  - Redis: 云缓存
  - 反向代理: Nginx (HTTPS)
```

---

## 关键技术决策

### 1. 为什么选择 FastAPI 而不是 Flask/Django？

| 特性 | FastAPI | Flask | Django |
|------|---------|-------|--------|
| 性能 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| 异步支持 | ✅ 原生 | ⚠️ 插件 | ⚠️ 3.1+ |
| 类型检查 | ✅ Pydantic | ❌ | ❌ |
| API 文档 | ✅ 自动 | ❌ | ⚠️ DRF |
| 学习曲线 | 中 | 低 | 高 |
| 适用场景 | API 服务 | 小型应用 | 全栈应用 |

**结论**: 本项目是前后端分离的 API 服务，FastAPI 性能和开发效率最优。

### 2. 为什么用 SQLAlchemy 而不是 Django ORM？

- Django ORM 绑定整个 Django 框架，无法单独使用
- SQLAlchemy 2.0 的异步支持更成熟
- 更灵活的查询构建，适合复杂金融数据分析

### 3. 为什么用 DeepSeek 而不是 Claude/GPT-4？

| 模型 | 输入成本 | 输出成本 | 上下文 | 中文能力 |
|------|----------|----------|--------|----------|
| DeepSeek | ¥1/M | ¥2/M | 64K | ⭐⭐⭐⭐⭐ |
| GPT-4 Turbo | $10/M | $30/M | 128K | ⭐⭐⭐⭐ |
| Claude Sonnet | $3/M | $15/M | 200K | ⭐⭐⭐⭐ |

**结论**:
- DeepSeek 成本仅为 GPT-4 的 1/10，Claude 的 1/5
- 中文金融场景下表现优秀
- 个人项目预算有限，DeepSeek 最合适

### 4. 为什么用 Vue 3 而不是 React？

- Vue 3 组合式 API 更符合直觉
- 更少的样板代码
- 官方生态完整（Router, State, Build）
- 中文文档和社区支持好

---

## 风险与对策

### 1. DeepSeek API 稳定性

**风险**: DeepSeek 是国内服务，可能有限流或中断

**对策**:
- 实现 AI 服务抽象层，支持多提供商切换
- 关键分析结果缓存
- 降级方案：规则引擎 + 历史数据

### 2. Tushare 数据配额

**风险**: 免费账户积分有限

**对策**:
- 使用 AkShare 作为备选
- 优化数据获取策略（批量、缓存）
- 考虑付费升级（500 积分/年 ≈ ¥200）

### 3. 数据库性能

**风险**: 大量历史行情数据查询慢

**对策**:
- 使用分区表（按时间/股票代码）
- 时序数据建立复合索引
- 考虑使用 TimescaleDB 扩展

---

## 后续技术评估

### 可选技术组件

1. **消息队列**: Celery + Redis（异步任务）
   - 场景：定时数据采集、批量 AI 分析

2. **缓存层**: Redis
   - 场景：行情数据缓存、API 限流、Session 存储

3. **时序数据库**: TimescaleDB（PostgreSQL 扩展）
   - 场景：海量历史行情数据

4. **监控**: Prometheus + Grafana
   - 场景：API 性能监控、AI Token 消耗监控

5. **日志**: ELK Stack (Elasticsearch + Logstash + Kibana)
   - 场景：集中日志管理和分析

---

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| v1.1 | 2025-01-15 | 确认技术栈与 CLAUDE.md、PRD v3.1 一致 |
| v1.0 | 2025-11-14 | 初始技术选型：FastAPI + Vue 3 + DeepSeek |

---

## 相关文档

- **PRD v3.1**: [../../prd/v3/main.md](../../prd/v3/main.md)
- **项目配置**: [../../../CLAUDE.md](../../../CLAUDE.md)
- **数据库设计**: [../database/schema-v1.md](../database/schema-v1.md)

---

**下一步**: 创建项目初始化脚本，搭建开发环境
