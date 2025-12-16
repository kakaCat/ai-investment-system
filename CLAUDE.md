# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI-driven personal investment management system with multi-account support, AI-powered analysis, and event-driven insights.

**Current Status**: Active development - documentation complete, scaffolding implemented, feature development in progress.

**Tech Stack**:
- Frontend: Vue 3 + TypeScript + Vite + TailwindCSS
- Backend: FastAPI + Python 3.11+
- Database: PostgreSQL 15+
- ORM: SQLAlchemy 2.0 (async)
- AI: DeepSeek API (deepseek-chat)
- Data Sources:
  - News: Third-party APIs (e.g., Tushare, AkShare for CN stocks)
  - Market Data: Real-time quote APIs
  - Web Search: Optional integration for event discovery

## Team Structure

This project follows the [global team structure standard](~/.claude/CLAUDE.md#-项目团队结构规范), where each top-level directory represents a team role:

| Directory | Role | Responsibility |
|-----------|------|----------------|
| `backend/` | Backend Engineer | API, business logic, database operations |
| `frontend/` | Frontend Engineer | UI, user interaction, frontend logic |
| `tests/` | QA Engineer | Quality assurance, automated testing |
| `docs/` | PM + Architect | Requirements, technical design |
| `management/` | Project Manager | Task management, progress tracking |
| `deploy/` | DevOps Engineer | Deployment, monitoring, operations |
| `scripts/` | Shared by all | Development tools, automation scripts |

## Architecture Guard

**CRITICAL**: Before developing any code, you MUST read the architecture constraints:

- [Backend Architecture Constraints](backend/ARCHITECTURE.md) ⭐ **Required reading before backend dev**
- [Frontend Architecture Constraints](frontend/ARCHITECTURE.md) ⭐ **Required reading before frontend dev**
- Architecture Check: `python scripts/check_architecture.py`

**Enforcement**:
- Local check: Run `python scripts/check_architecture.py` before committing
- CI/CD: Automated check on every PR
- Code Review: Architecture compliance is a merge requirement

## Quick Start

### Start Development Environment
```bash
./scripts/dev.sh
```
This will:
- Start backend on http://localhost:8000
- Start frontend on http://localhost:5175
- Auto-reload on code changes
- Separate log files in `scripts/logs/`

### Stop Services
```bash
./scripts/stop.sh
```

### Architecture Check
```bash
python scripts/check_architecture.py
```

### Backend Commands
```bash
# Install dependencies
cd backend
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "description"

# Run backend tests
pytest

# Run specific test file
pytest tests/unit/backend/test_specific.py
```

### Frontend Commands
```bash
# Install dependencies
cd frontend
npm install

# Run linting
npm run lint

# Build for production
npm run build

# Run frontend tests
npm run test
```

### Current Tasks
See [management/sprints/current.md](management/sprints/current.md) for current sprint tasks.

## Documentation Structure

This project follows a strict documentation management standard based on the **pyramid principle**. All documentation lives in `/docs` with the following structure:

```
docs/
├── README.md                          # Main documentation index
├── prd/v3/                            # Product requirements (v3.1)
│   ├── main.md                        # Complete PRD (~8000 lines)
│   └── sections/                      # Large sections broken out
├── design/
│   ├── database/schema-v1.md          # Complete DB schema with ENUMs, constraints
│   ├── features/events/               # Event analysis system design
│   └── ui/wireframes/                 # UI wireframes
├── guides/setup/                      # MCP setup, API keys configuration
├── standards/                         # Document management standards
└── archive/                           # Deprecated docs
```

**Critical**:
- Root directory contains ONLY `CLAUDE.md` - all other docs go in `/docs`
- Every directory must have a `README.md` with index and description
- Files use kebab-case naming: `event-analysis-design.md`
- Large files (>2000 lines) split into `sections/` subdirectory
- Version files use suffix: `schema-v1.md`, `prd-v2.md`

See [~/.claude/CLAUDE.md](~/.claude/CLAUDE.md) for complete global documentation standards.

## Core Features (from PRD v3.1)

1. **Multi-Account Portfolio Management** - Track multiple brokerage accounts (A-share, HK, US markets)
2. **Stock Data Management** - Real-time quotes, historical data, company fundamentals
3. **AI Investment Analysis** - Single stock analysis, portfolio analysis, strategy generation
4. **Event Analysis & Tracking** (v3.1) - 4 major categories (policy/company/market/industry), 16 subtypes
   - AI-powered event impact assessment
   - Event timeline visualization
   - Smart alerts for critical events

## Key Documentation

| Document | Purpose | Lines |
|----------|---------|-------|
| [docs/prd/v3/main.md](docs/prd/v3/main.md) | Complete product requirements v3.1 | ~8000 |
| [docs/design/database/schema-v1.md](docs/design/database/schema-v1.md) | Full PostgreSQL schema with design principles | ~1500 |
| [docs/design/features/events/](docs/design/features/events/) | Event system architecture (requirements, implementation, AI integration) | Multi-file |
| [docs/guides/setup/](docs/guides/setup/) | MCP server configuration, API key management | - |
| [docs/standards/](docs/standards/) | Document management standards and reorganization history | - |

## Database Design Principles

From [docs/design/database/schema-v1.md:1-14](docs/design/database/schema-v1.md):

- **Strict account isolation**: All core tables carry `user_id + account_id` (except public market data)
- **Numeric primary keys**: `BIGSERIAL/BIGINT` for all IDs (no UUIDs)
- **Virtual foreign keys**: No DB-level FKs - use NOT NULL + indexes + soft delete
- **Idempotency**: Event/import tables use `idempotency_key` unique constraint
- **Audit trail**: Transaction tables store raw events, never computed fields
- **Enums for discrete values**: PostgreSQL ENUM types for status, types, tiers
- **Soft delete**: `is_deleted`/`deleted_at` instead of hard deletes
- **UTC timestamps**: All times stored as `TIMESTAMPTZ`
- **Precise decimals**: `NUMERIC(20,8)` for amounts, never FLOAT

## Implementation Architecture

### Backend Structure

The backend follows a strict layered architecture (see [backend/ARCHITECTURE.md](backend/ARCHITECTURE.md)):

```
backend/app/
├── api/v1/          # Controllers (POST-only endpoints)
├── services/        # Business logic organized by scenario
│   └── {module}/    # e.g., account/, holding/, trade/
│       └── {action}_service.py  # Contains Service + Converter + Builder
├── repositories/    # Pure database CRUD operations
├── models/          # SQLAlchemy ORM models
├── schemas/         # Pydantic request/response models
└── core/            # Configuration, security, dependencies
```

**Key Architectural Rules**:
- All APIs use POST method only (no GET/PUT/DELETE)
- Service files contain: Service class + Converter class (static) + Builder class (static)
- Business logic ONLY in Converter classes
- Repositories contain NO business logic
- Every API endpoint requires 8-section documentation

### Frontend Structure

The frontend uses Vue 3 Composition API (see [frontend/ARCHITECTURE.md](frontend/ARCHITECTURE.md)):

```
frontend/src/
├── views/           # Page components (by module)
├── components/      # Reusable components
├── api/             # API service functions (POST-only)
├── stores/          # Pinia state management
├── router/          # Vue Router configuration
├── types/           # TypeScript type definitions
└── utils/           # Utility functions
```

**Key Frontend Rules**:
- Use Composition API only (no Options API)
- All API calls through centralized service functions
- Complete error handling with ElMessage
- TypeScript types for all props and data
- Loading states for all async operations

## Working with Documentation

### Creating New Documentation

When adding design docs:

```bash
# Create design doc in appropriate location
# For new feature design:
docs/design/features/{feature-name}/
  ├── README.md           # Feature overview and index
  ├── requirements.md     # Requirements and scope
  ├── implementation.md   # Technical design
  └── integration.md      # Integration points (if needed)

# For API design:
docs/design/api/{api-name}-api.md

# For architectural decisions:
docs/design/architecture/{decision-name}.md
```

### Documentation Standards

When creating or updating docs:

1. **Determine correct location** - Follow the structure in `docs/README.md`
2. **Create/update README** - Every directory needs an index
3. **Use standard naming** - kebab-case, version suffixes where appropriate
4. **Split large files** - Files >2000 lines go to `sections/` subdirectory
5. **Update parent indexes** - Add links in parent directory's README
6. **Use relative paths** - All internal links use relative paths

### Document Types & Locations

| Type | Location | Example |
|------|----------|---------|
| PRD | `docs/prd/v{n}/` | `main.md`, `sections/02.9-events.md` |
| DB Schema | `docs/design/database/` | `schema-v1.md` |
| Feature Design | `docs/design/features/{name}/` | `events/requirements.md` |
| Architecture | `docs/design/architecture/` | `system-architecture.md` |
| Setup Guide | `docs/guides/setup/` | `mcp-setup.md` |
| UI Design | `docs/design/ui/wireframes/` | `01-dashboard.md` |
| Standards | `docs/standards/` | `DOCUMENT-MANAGEMENT-STANDARD.md` |
| Archive | `docs/archive/` | Old/deprecated docs |

## Data Sources & API Integration

**Stock Data APIs** (for Chinese market):
- **Tushare**: Professional financial data (requires token) - primary choice
- **AkShare**: Free alternative for A-share/HK/US market data
- **East Money API**: Real-time quotes (optional)

**AI Integration**:
- **DeepSeek API**: deepseek-chat model for investment analysis
- **API Endpoint**: https://api.deepseek.com/v1
- **Key Features**: Long context (64K), cost-effective, Chinese optimization
- **Configuration**: API key stored in environment variables

**Web Search** (optional):
- For event discovery and news analysis
- Can integrate search APIs if needed for event tracking

## Event System Architecture

One of the key v3.1 features - comprehensive design in [docs/design/features/events/](docs/design/features/events/):

**Event Categories**:
- Policy Events (政策事件): Monetary, fiscal, regulatory, international
- Company Events (公司事件): Earnings, dividends, M&A, governance
- Market Events (市场事件): Index volatility, sector rotation, sentiment shifts
- Industry Events (行业事件): Tech changes, regulatory shifts, competitive dynamics

**AI Integration**:
- Automated event impact assessment (1-5 scale)
- Multi-dimensional analysis (short/mid/long term)
- Confidence scoring
- Portfolio impact correlation

## Backend Architecture Requirements

**CRITICAL**: All backend code MUST follow the architecture defined in [docs/design/architecture/backend-architecture.md](docs/design/architecture/backend-architecture.md)

### Core Design Principles (Non-Negotiable)

1. **POST-Only API Protocol**
   - ALL endpoints use POST method (no GET/PUT/DELETE)
   - URL format: `POST /api/v1/{module}/{action}`
   - Example: `POST /api/v1/account/query`, `POST /api/v1/account/create`

2. **Service Layer Structure**
   - Organize by business scenario, NOT by module
   - One file per business scenario: `{action}_service.py`
   - Each file contains: Service + Converter + Builder classes

3. **Required Layers** (in order)
   ```
   Controller (API) → Service → Converter + Builder → Repository → Database
   ```

4. **Layer Responsibilities**
   - **Controller**: Receive request, get user, call Service, return response
   - **Service**: Permission check, orchestration, transaction management
   - **Converter**: ALL business logic & calculations (static methods only)
   - **Builder**: Complex object construction (static methods only)
   - **Repository**: Pure CRUD operations, no business logic

### Directory Structure (MUST Follow)

```
backend/app/
├── api/v1/
│   └── {module}_api.py          # Controller only
│
├── services/
│   └── {module}/                # Business scenarios folder
│       ├── {action}_service.py  # Contains:
│       │                        #  - {Action}Service class
│       │                        #  - {Action}Converter class (static)
│       │                        #  - {Action}Builder class (static)
│       └── ...
│
├── repositories/
│   └── {table}_repo.py          # Pure data access
│
└── models/
    └── {table}.py               # SQLAlchemy models
```

### Code Requirements

**Service Class**:
```python
class AccountDetailService:
    def __init__(self):
        self.account_repo = AccountRepository()
        # ...

    async def execute(self, request: dict, user_id: int) -> dict:
        # 1. Permission check
        # 2. Call repositories
        # 3. Call Converter
        # 4. Return data
```

**Converter Class** (Static - Business Logic):
```python
class AccountDetailConverter:
    @staticmethod
    def convert(account, holdings) -> dict:
        # All business calculations here
        total_value = AccountDetailConverter._calculate_total(holdings)
        return AccountDetailBuilder.build_response(...)

    @staticmethod
    def _calculate_total(holdings) -> float:
        # Business logic implementation
```

**Builder Class** (Static - Data Construction):
```python
class AccountDetailBuilder:
    @staticmethod
    def build_response(account, **kwargs) -> dict:
        return {"account": {...}, "stats": {...}}
```

**Repository Class** (No Business Logic):
```python
class AccountRepository:
    async def get_by_id(self, id: int) -> Account:
        # Pure database query only

    async def query_by_user(self, user_id: int) -> List[Account]:
        # Pure database query only
```

### API Documentation Requirements

Every Controller endpoint MUST have complete documentation:

```python
@router.post("/detail")
async def get_account_detail(request: dict, user: User = Depends(get_current_user)):
    """
    接口标题

    ========================================
    接口信息
    ========================================
    接口路径: POST /api/v1/account/detail
    对应页面: pages/account/detail.vue
    接口功能: [描述]

    ========================================
    请求参数
    ========================================
    {request example with types and descriptions}

    ========================================
    响应数据
    ========================================
    {response example}

    ========================================
    执行流程（时序）
    ========================================
    1. Step 1
    2. Step 2
    ...

    ========================================
    业务规则
    ========================================
    1. Rule 1
    2. Rule 2

    ========================================
    错误码
    ========================================
    1001: Error description

    ========================================
    前端调用示例
    ========================================
    const data = await post('/account/detail', {...})

    ========================================
    修改记录
    ========================================
    YYYY-MM-DD: 初始版本
    """
```

### Validation Checklist

Before committing any backend code, verify:

- [ ] All APIs use POST method only
- [ ] Service files in `services/{module}/{action}_service.py`
- [ ] Each service file has Service + Converter + Builder
- [ ] Converter uses @staticmethod for all methods
- [ ] Builder uses @staticmethod for all methods
- [ ] Repository has no business logic
- [ ] Controller has complete 8-section documentation
- [ ] No business logic in Controller or Repository

**Reference**: See complete architecture in [docs/design/architecture/backend-architecture.md](docs/design/architecture/backend-architecture.md)

---

## Code Standards (for when implementation begins)

From [CLAUDE.md:164-169](CLAUDE.md):

- TypeScript Strict Mode
- ESLint + Prettier
- Git commits: `<type>(<scope>): <subject>` format
- Git Flow branching strategy

## Development Phases

**Current Phase**: Phase 2 - Core Feature Implementation

- [x] PRD v3.1 complete
- [x] Database schema designed
- [x] Event system designed
- [x] UI wireframes created
- [x] Documentation standards established
- [x] Project initialization complete (FastAPI + Vue 3)
- [x] Basic framework setup
- [ ] Feature implementation in progress

See full roadmap in [docs/prd/v3/main.md](docs/prd/v3/main.md) (search for "里程碑" or "milestone").

## When Working in This Codebase

1. **Before writing code**: Review PRD and relevant design docs
2. **Before creating docs**: Check documentation standards and existing structure
3. **Database changes**: Must align with schema design principles in schema-v1.md
4. **New features**: Create design doc first following the template structure
5. **Large PRD updates**: Use sections/ subdirectory for files >2000 lines

## Resources

- [Claude API Docs](https://docs.anthropic.com/)
- [MCP Protocol](https://modelcontextprotocol.io/)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Vue 3 Docs](https://vuejs.org/)
- [PostgreSQL Docs](https://www.postgresql.org/docs/)

## Global Standards

This project follows all standards defined in `~/.claude/CLAUDE.md`:

- [Team Structure Standards](~/.claude/CLAUDE.md#-项目团队结构规范) - Role-to-directory mapping
- [Document Management Standards](~/.claude/CLAUDE.md#-文档管理规范金字塔原理) - Pyramid principle, naming conventions
- [Architecture Guard Standards](~/.claude/CLAUDE.md#️-架构守卫规范) - ARCHITECTURE.md, templates, automated checks
- [Development Workflow Standards](~/.claude/CLAUDE.md#-开发流程规范) - dev.sh, stop.sh, work flows
- [AI Assistant Behavior Standards](~/.claude/CLAUDE.md#-ai-助手行为规范) - Code/doc creation rules

---

**Last Updated**: 2025-12-08
**Version**: v2.1
