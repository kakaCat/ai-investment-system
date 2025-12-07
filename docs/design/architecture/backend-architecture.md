# 后端架构设计文档

**版本**: v1.0
**日期**: 2025-01-15
**状态**: 设计完成，待实现
**技术栈**: FastAPI + Python 3.11+ + PostgreSQL 15+ + SQLAlchemy 2.0 Async

---

## 目录

- [1. 架构概览](#1-架构概览)
- [2. 目录结构](#2-目录结构)
- [3. 分层设计](#3-分层设计)
- [4. 代码规范](#4-代码规范)
- [5. 接口规范](#5-接口规范)
- [6. 数据库访问](#6-数据库访问)
- [7. 异常处理](#7-异常处理)
- [8. 依赖注入](#8-依赖注入)
- [9. 示例代码](#9-示例代码)

---

## 1. 架构概览

### 1.1 整体架构

```
┌─────────────────────────────────────────────┐
│           前端 (Vue 3 + TypeScript)          │
│                                             │
└──────────────────┬──────────────────────────┘
                   │ HTTP POST (JSON)
                   │
┌──────────────────▼──────────────────────────┐
│          Controller (FastAPI Router)        │
│  - 接收请求参数                               │
│  - 获取登录人信息                             │
│  - 调用 Service                             │
│  - 返回统一响应格式                           │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│          Service (业务编排层)                │
│  - 权限校验                                  │
│  - 事务管理                                  │
│  - 调用 Converter + Repository              │
└──────┬────────────────┬──────────────────────┘
       │                │
       ▼                ▼
┌──────────────┐  ┌──────────────┐
│  Converter   │  │  Repository  │
│  (领域层)     │  │  (数据访问)   │
│              │  │              │
│ - 数据转换   │  │ - 纯CRUD     │
│ - 业务计算   │  │ - SQL封装    │
│ - 业务规则   │  │              │
│              │  │              │
│ + Builder    │  │              │
│  (辅助构建)   │  │              │
└──────────────┘  └──────┬───────┘
                         │
                    ┌────▼─────┐
                    │PostgreSQL│
                    └──────────┘
```

### 1.2 核心设计原则

1. **POST-Only API**: 所有接口统一使用 POST 协议
2. **按业务分文件夹**: Service 下按业务模块组织
3. **一个接口一套业务**: Service + Converter + Builder 在同一文件
4. **Converter 是领域层**: 包含所有业务逻辑和计算
5. **静态方法**: Converter 和 Builder 全部使用静态方法
6. **事务在 Service**: 由 Service 层统一管理事务
7. **Repository 纯粹**: 只负责数据库 CRUD，不含业务逻辑

---

## 2. 目录结构

```
backend/
├── app/
│   ├── main.py                          # FastAPI 启动入口
│   │
│   ├── api/                             # Controller 层
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── account_api.py           # 账户接口
│   │       ├── trade_api.py             # 交易接口
│   │       ├── stock_api.py             # 股票接口
│   │       ├── holding_api.py           # 持仓接口
│   │       ├── watchlist_api.py         # 关注列表接口
│   │       ├── ai_api.py                # AI分析接口
│   │       └── event_api.py             # 事件接口
│   │
│   ├── services/                        # Service 层（按业务分文件夹）
│   │   ├── account/                     # 账户业务
│   │   │   ├── __init__.py
│   │   │   ├── account_detail_service.py       # 账户详情（Service+Converter+Builder）
│   │   │   ├── account_list_service.py         # 账户列表
│   │   │   ├── account_create_service.py       # 创建账户
│   │   │   ├── account_update_service.py       # 更新账户
│   │   │   └── account_delete_service.py       # 删除账户
│   │   │
│   │   ├── trade/                       # 交易业务
│   │   │   ├── __init__.py
│   │   │   ├── trade_create_service.py         # 创建交易
│   │   │   ├── trade_list_service.py           # 交易列表
│   │   │   └── trade_detail_service.py         # 交易详情
│   │   │
│   │   ├── stock/                       # 股票业务
│   │   │   ├── __init__.py
│   │   │   ├── stock_search_service.py         # 搜索股票
│   │   │   ├── stock_detail_service.py         # 股票详情
│   │   │   └── stock_price_service.py          # 获取价格
│   │   │
│   │   ├── holding/                     # 持仓业务
│   │   │   ├── __init__.py
│   │   │   ├── holding_list_service.py
│   │   │   └── holding_update_tags_service.py
│   │   │
│   │   ├── watchlist/                   # 关注列表业务
│   │   │   ├── __init__.py
│   │   │   ├── watchlist_add_service.py
│   │   │   └── watchlist_remove_service.py
│   │   │
│   │   ├── ai/                          # AI分析业务
│   │   │   ├── __init__.py
│   │   │   ├── ai_analyze_stock_service.py
│   │   │   └── ai_analyze_event_service.py
│   │   │
│   │   └── event/                       # 事件业务
│   │       ├── __init__.py
│   │       ├── event_list_service.py
│   │       └── event_detail_service.py
│   │
│   ├── repositories/                    # Repository 层（数据访问）
│   │   ├── __init__.py
│   │   ├── account_repo.py              # 账户数据访问
│   │   ├── trade_repo.py                # 交易数据访问
│   │   ├── holding_repo.py              # 持仓数据访问
│   │   ├── watchlist_repo.py            # 关注列表数据访问
│   │   ├── stock_repo.py                # 股票数据访问
│   │   ├── price_snapshot_repo.py       # 价格快照数据访问
│   │   ├── event_repo.py                # 事件数据访问
│   │   └── ai_token_repo.py             # AI Token数据访问
│   │
│   ├── models/                          # SQLAlchemy Models（数据库表）
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── account.py
│   │   ├── holding.py
│   │   ├── watchlist.py
│   │   ├── trade.py
│   │   ├── stock.py
│   │   ├── event.py
│   │   └── ai_token.py
│   │
│   ├── schemas/                         # Pydantic Schemas（请求/响应）
│   │   ├── __init__.py
│   │   ├── common.py                    # 通用响应格式
│   │   ├── account.py
│   │   ├── trade.py
│   │   └── stock.py
│   │
│   ├── core/                            # 核心配置
│   │   ├── __init__.py
│   │   ├── config.py                    # 配置类
│   │   ├── database.py                  # 数据库连接
│   │   └── security.py                  # 安全相关（JWT等）
│   │
│   ├── dependencies.py                  # 依赖注入
│   ├── exceptions.py                    # 自定义异常
│   └── utils/                           # 工具函数
│       ├── __init__.py
│       └── helpers.py
│
├── alembic/                             # 数据库迁移
│   ├── versions/
│   └── env.py
│
├── tests/                               # 测试
│   ├── unit/
│   └── integration/
│
├── scripts/                             # 脚本工具
│   └── init_db.py
│
├── requirements.txt                     # 依赖
├── pyproject.toml                       # Poetry配置
├── .env.example                         # 环境变量示例
└── README.md
```

---

## 3. 分层设计

### 3.1 Controller 层（API路由）

**职责**:
- 接收前端请求参数
- 获取当前登录用户信息
- 调用对应的 Service
- 返回统一格式响应

**命名规范**:
- 文件名: `{模块}_api.py`，如 `account_api.py`
- 函数名: 动词开头，如 `create_account()`, `get_account_detail()`

**代码示例**:

```python
# app/api/v1/account_api.py

from fastapi import APIRouter, Depends
from app.services.account.account_detail_service import AccountDetailService
from app.schemas.common import Response
from app.dependencies import get_current_user

router = APIRouter(prefix="/account", tags=["账户管理"])

@router.post("/detail")
async def get_account_detail(
    request: dict,
    current_user: User = Depends(get_current_user)
):
    """获取账户详情 - 完整注释见代码规范章节"""
    service = AccountDetailService()
    data = await service.execute(request, current_user.id)
    return Response.success(data)
```

### 3.2 Service 层（业务编排）

**职责**:
- 权限校验
- 业务流程编排
- 事务管理
- 调用 Converter 和 Repository

**命名规范**:
- 文件名: `{业务场景}_service.py`，如 `account_detail_service.py`
- 类名: `{业务场景}Service`，如 `AccountDetailService`
- 方法名: `execute(request, user_id)` 统一入口

**代码示例**:

```python
# app/services/account/account_detail_service.py

class AccountDetailService:
    """账户详情业务类"""

    def __init__(self):
        self.account_repo = AccountRepository()
        self.holding_repo = HoldingRepository()
        self.watchlist_repo = WatchlistRepository()

    async def execute(self, request: dict, user_id: int) -> dict:
        """执行业务逻辑"""
        # 1. 权限校验
        account = await self.account_repo.get_by_id(request['account_id'])
        if account.user_id != user_id:
            raise PermissionError("无权访问")

        # 2. 查询数据
        holdings = await self.holding_repo.get_by_account(account.id)
        watchlist = await self.watchlist_repo.get_by_account(account.id)

        # 3. Converter 转换
        return AccountDetailConverter.convert(account, holdings, watchlist)
```

### 3.3 Converter 层（领域层 - 核心业务逻辑）

**职责**:
- 数据格式转换（前端 ↔ 数据库）
- 业务逻辑计算
- 业务规则校验

**命名规范**:
- 类名: `{业务场景}Converter`，如 `AccountDetailConverter`
- 方法: 全部使用 `@staticmethod`
- 主方法: `convert()` 或 `from_request()` / `to_response()`

**代码示例**:

```python
class AccountDetailConverter:
    """账户详情转换器（静态类）- 核心业务逻辑"""

    @staticmethod
    def convert(account, holdings, watchlist) -> dict:
        """转换 + 计算业务逻辑"""
        # 转换数据
        holdings_data = [
            AccountDetailConverter._convert_holding(h)
            for h in holdings
        ]

        # 业务计算
        total_value = AccountDetailConverter._calculate_total_value(holdings)
        total_pnl = AccountDetailConverter._calculate_total_pnl(holdings)

        # 使用 Builder 构建响应
        return AccountDetailBuilder.build_response(...)

    @staticmethod
    def _calculate_total_value(holdings) -> float:
        """业务逻辑：计算总市值"""
        return sum(h.quantity * h.current_price for h in holdings)
```

### 3.4 Builder 类（辅助构建对象）

**职责**:
- 辅助 Converter 构建复杂数据结构
- 提高代码复用性

**命名规范**:
- 类名: `{业务场景}Builder`
- 方法: 全部使用 `@staticmethod`
- 方法名: `build_xxx()`

**代码示例**:

```python
class AccountDetailBuilder:
    """账户详情数据构建器"""

    @staticmethod
    def build_response(account, holdings, watchlist, **stats) -> dict:
        """构建响应对象"""
        return {
            "account_info": {...},
            "holdings": {"total": len(holdings), "list": holdings},
            "watchlist": {"total": len(watchlist), "list": watchlist},
            "statistics": stats
        }
```

### 3.5 Repository 层（数据访问）

**职责**:
- 纯粹的数据库 CRUD 操作
- SQL 封装
- **不包含任何业务逻辑**

**命名规范**:
- 文件名: `{表名}_repo.py`
- 类名: `{表名}Repository`
- 方法名: `create()`, `get_by_id()`, `update()`, `delete()`, `query_by_xxx()`

**代码示例**:

```python
# app/repositories/account_repo.py

class AccountRepository:
    """账户数据访问（只负责数据库操作）"""

    async def get_by_id(self, account_id: int) -> Account:
        """根据ID查询"""
        async with get_db() as db:
            result = await db.execute(
                select(Account).where(Account.id == account_id)
            )
            return result.scalar_one_or_none()

    async def create(self, data: dict) -> Account:
        """创建账户"""
        async with get_db() as db:
            account = Account(**data)
            db.add(account)
            await db.commit()
            await db.refresh(account)
            return account

    async def query_by_user(
        self,
        user_id: int,
        status: str = None,
        page: int = 1,
        page_size: int = 20
    ) -> List[Account]:
        """查询用户账户列表"""
        async with get_db() as db:
            query = select(Account).where(Account.user_id == user_id)

            if status:
                query = query.where(Account.status == status)

            query = query.order_by(Account.created_at.desc())
            query = query.offset((page - 1) * page_size).limit(page_size)

            result = await db.execute(query)
            return result.scalars().all()
```

---

## 4. 代码规范

### 4.1 Controller 接口注释规范

每个接口必须包含以下注释：

```python
@router.post("/detail")
async def get_account_detail(request: dict, current_user: User = Depends(get_current_user)):
    """
    获取账户详情

    ========================================
    接口信息
    ========================================
    接口路径: POST /api/v1/account/detail
    对应页面: pages/account/detail.vue - 账户详情页
    接口功能: 获取账户基本信息、持仓列表、关注列表、汇总统计

    ========================================
    请求参数
    ========================================
    {
        "account_id": 123  // 账户ID（必填）
    }

    ========================================
    响应数据
    ========================================
    {
        "code": 0,
        "message": "success",
        "data": {...}
    }

    ========================================
    执行流程（时序）
    ========================================
    1. 前端发起请求 POST /account/detail
    2. Controller 调用 AccountDetailService.execute()
    3. Service 查询账户、持仓、关注列表（Repository）
    4. Service 调用 Converter 转换数据（业务计算）
    5. Controller 返回响应
    6. 前端渲染数据

    ========================================
    业务规则
    ========================================
    1. 只能查看自己的账户
    2. 持仓盈亏 = 数量 × (当前价 - 成本价)

    ========================================
    错误码
    ========================================
    1001: 无权访问该账户
    1002: 账户不存在

    ========================================
    前端调用示例
    ========================================
    const data = await post('/account/detail', { account_id: 123 })

    ========================================
    修改记录
    ========================================
    2025-01-15: 初始版本
    """
    service = AccountDetailService()
    data = await service.execute(request, current_user.id)
    return Response.success(data)
```

### 4.2 Service/Converter 注释规范

```python
class AccountDetailService:
    """
    账户详情业务类

    职责：
    1. 权限校验
    2. 数据查询
    3. 调用 Converter 转换数据
    """

    async def execute(self, request: dict, user_id: int) -> dict:
        """
        执行业务逻辑

        Args:
            request: 请求参数 {"account_id": 123}
            user_id: 当前登录用户ID

        Returns:
            dict: 账户详情数据

        Raises:
            PermissionError: 无权访问该账户
            ValueError: 账户不存在
        """
        pass


class AccountDetailConverter:
    """
    账户详情转换器（静态类）

    职责：
    1. 数据格式转换
    2. 业务逻辑计算
    3. 组装响应数据

    核心业务逻辑：
    - 持仓盈亏 = (当前价 - 成本价) × 数量
    - 总盈亏率 = 总盈亏 / 总成本 × 100%
    """

    @staticmethod
    def _calculate_total_value(holdings) -> float:
        """
        计算总市值 - 业务逻辑

        公式：Σ(持仓数量 × 当前价)

        Args:
            holdings: 持仓列表

        Returns:
            float: 总市值
        """
        pass
```

### 4.3 命名规范

| 类型 | 规范 | 示例 |
|------|------|------|
| **文件名** | 小写下划线 | `account_detail_service.py` |
| **类名** | 大驼峰 | `AccountDetailService` |
| **函数/方法** | 小写下划线 | `get_account_detail()` |
| **常量** | 大写下划线 | `MAX_ACCOUNTS = 10` |
| **私有方法** | 下划线开头 | `_calculate_total()` |
| **变量** | 小写下划线 | `account_id`, `user_name` |

### 4.4 类型提示

所有函数必须有类型提示：

```python
async def execute(self, request: dict, user_id: int) -> dict:
    pass

@staticmethod
def convert(account: Account, holdings: List[Holding]) -> dict:
    pass
```

---

## 5. 接口规范

### 5.1 统一 POST 协议

所有接口使用 POST 方法：

```python
# ✅ 正确
POST /api/v1/account/query      # 查询
POST /api/v1/account/create     # 创建
POST /api/v1/account/update     # 更新
POST /api/v1/account/delete     # 删除

# ❌ 错误（不使用 RESTful）
GET    /api/v1/accounts/{id}
PUT    /api/v1/accounts/{id}
DELETE /api/v1/accounts/{id}
```

### 5.2 统一响应格式

```python
# app/schemas/common.py

from pydantic import BaseModel
from typing import Optional, Any, Generic, TypeVar
from datetime import datetime

T = TypeVar('T')

class Response(BaseModel, Generic[T]):
    """统一响应格式"""
    code: int = 0              # 0=成功，非0=失败
    message: str = "success"
    data: Optional[T] = None
    timestamp: str = datetime.now().isoformat()

    @classmethod
    def success(cls, data: Any = None, message: str = "success"):
        """成功响应"""
        return cls(code=0, message=message, data=data)

    @classmethod
    def error(cls, code: int, message: str, data: Any = None):
        """错误响应"""
        return cls(code=code, message=message, data=data)
```

### 5.3 URL 规范

```
/api/v1/{模块}/{操作}

示例：
/api/v1/account/query
/api/v1/account/create
/api/v1/trade/create
/api/v1/ai/analyze_stock
```

---

## 6. 数据库访问

### 6.1 数据库配置

```python
# app/core/database.py

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from contextlib import asynccontextmanager

DATABASE_URL = "postgresql+asyncpg://user:pass@localhost/dbname"

engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()

@asynccontextmanager
async def get_db():
    """获取数据库会话"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
```

### 6.2 事务管理

在 Service 层统一管理事务：

```python
class TradeCreateService:
    async def execute(self, request: dict, user_id: int) -> dict:
        # ... 前置逻辑

        # 事务开始
        async with get_db() as db:
            async with db.begin():  # 开启事务
                # 1. 创建交易记录
                trade = await self.trade_repo.create(trade_data)

                # 2. 更新持仓
                await self.holding_repo.upsert(holding_data)

                # 自动提交或回滚

        return TradeCreateConverter.to_response(trade)
```

### 6.3 Model 定义

```python
# app/models/account.py

from sqlalchemy import Column, BigInteger, String, TIMESTAMP, JSON
from app.core.database import Base

class Account(Base):
    __tablename__ = "accounts"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    account_name = Column(String(50), nullable=False)
    type = Column(String(20), nullable=False)
    status = Column(String(20), default="active")
    fee_config = Column(JSON)
    created_at = Column(TIMESTAMP, server_default="NOW()")
    updated_at = Column(TIMESTAMP, server_default="NOW()", onupdate="NOW()")
```

---

## 7. 异常处理

### 7.1 自定义异常

```python
# app/exceptions.py

class APIException(Exception):
    """API 异常基类"""
    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message

class BusinessException(APIException):
    """业务异常"""
    def __init__(self, message: str):
        super().__init__(code=1000, message=message)

class PermissionDenied(APIException):
    """权限异常"""
    def __init__(self, message: str = "无权访问"):
        super().__init__(code=1001, message=message)

class ResourceNotFound(APIException):
    """资源不存在"""
    def __init__(self, message: str = "资源不存在"):
        super().__init__(code=1002, message=message)
```

### 7.2 全局异常处理

```python
# app/main.py

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.exceptions import APIException
from app.schemas.common import Response

app = FastAPI()

@app.exception_handler(APIException)
async def api_exception_handler(request: Request, exc: APIException):
    """统一处理 API 异常"""
    return JSONResponse(
        status_code=200,  # HTTP 状态码始终返回 200
        content=Response.error(code=exc.code, message=exc.message).dict()
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理"""
    return JSONResponse(
        status_code=200,
        content=Response.error(code=9999, message=f"系统错误: {str(exc)}").dict()
    )
```

---

## 8. 依赖注入

### 8.1 获取当前用户

```python
# app/dependencies.py

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from app.core.security import decode_token

security = HTTPBearer()

async def get_current_user(token: str = Depends(security)):
    """获取当前登录用户"""
    try:
        payload = decode_token(token.credentials)
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="无效的token")

        # 这里可以从数据库查询用户信息
        # user = await user_repo.get_by_id(user_id)

        return {"id": user_id}  # 简化版，返回用户ID
    except Exception:
        raise HTTPException(status_code=401, detail="认证失败")
```

### 8.2 在 Controller 中使用

```python
@router.post("/detail")
async def get_account_detail(
    request: dict,
    current_user: dict = Depends(get_current_user)  # 依赖注入
):
    service = AccountDetailService()
    data = await service.execute(request, current_user['id'])
    return Response.success(data)
```

---

## 9. 示例代码

### 9.1 完整的业务文件示例

见附录：[account_detail_service.py 完整示例](./examples/account_detail_service.py)

### 9.2 Repository 示例

见附录：[account_repo.py 完整示例](./examples/account_repo.py)

### 9.3 Controller 示例

见附录：[account_api.py 完整示例](./examples/account_api.py)

---

## 10. 开发流程

### 10.1 新增接口的步骤

1. **设计接口**
   - 确定接口路径：`POST /api/v1/{module}/{action}`
   - 确定对应页面
   - 定义请求/响应格式

2. **创建 Service 文件**
   - 在 `services/{module}/` 下创建 `{action}_service.py`
   - 包含：Service 类 + Converter 类 + Builder 类

3. **创建 Repository（如需要）**
   - 在 `repositories/` 下创建或使用已有 Repository

4. **创建 Controller**
   - 在 `api/v1/{module}_api.py` 中添加路由
   - 添加完整注释

5. **测试**
   - 编写单元测试
   - 集成测试

### 10.2 项目初始化

```bash
# 1. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置环境变量
cp .env.example .env
# 编辑 .env 文件

# 4. 初始化数据库
alembic upgrade head

# 5. 启动开发服务器
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## 11. 相关文档

- [技术栈选型](./tech-stack.md)
- [数据库设计](../database/schema-v1.md)
- [API 接口文档](../api/api-design.md)（待创建）
- [PRD v3.1](../../prd/v3/main.md)

---

## 12. 修改记录

| 版本 | 日期 | 变更 |
|------|------|------|
| v1.0 | 2025-01-15 | 初始版本：完整的后端架构设计 |

---

**创建者**: Claude Code
**审核**: 待审核
**状态**: 设计完成
