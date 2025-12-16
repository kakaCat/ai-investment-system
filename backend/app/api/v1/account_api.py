"""
Account API

账户管理接口 - 使用POST-only架构
"""

from typing import Optional
from decimal import Decimal
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.schemas.common import Response
from app.models.user import User
from app.services.account import (
    AccountQueryService,
    AccountDetailService,
    AccountCreateService,
    AccountUpdateService,
    AccountDeleteService,
)


router = APIRouter(prefix="/account", tags=["账户管理"])


# ========================================
# Request Schemas
# ========================================


class AccountQueryRequest(BaseModel):
    """账户查询请求"""

    market: Optional[str] = None
    status: Optional[str] = None
    page: int = 1
    page_size: int = 20


class AccountDetailRequest(BaseModel):
    """账户详情请求"""

    account_id: int


class AccountCreateRequest(BaseModel):
    """账户创建请求"""

    account_name: str
    market: str
    broker: Optional[str] = None
    account_number: Optional[str] = None
    initial_capital: Optional[Decimal] = None


class AccountUpdateRequest(BaseModel):
    """账户更新请求"""

    account_id: int
    account_name: Optional[str] = None
    broker: Optional[str] = None
    account_number: Optional[str] = None
    status: Optional[str] = None
    current_capital: Optional[Decimal] = None


class AccountDeleteRequest(BaseModel):
    """账户删除请求"""

    account_id: int


# ========================================
# API Endpoints
# ========================================


@router.post("/query")
async def query_accounts(
    request: AccountQueryRequest, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """
    查询账户列表

    ========================================
    接口信息
    ========================================
    接口路径: POST /api/v1/account/query
    对应页面: pages/account/list.vue - 账户列表页
    接口功能: 查询用户所有账户，支持市场和状态筛选，支持分页

    ========================================
    请求参数
    ========================================
    {
        "market": "A-share",      // 市场筛选（可选）: A-share/HK/US
        "status": "active",       // 状态筛选（可选）: active/inactive/closed
        "page": 1,                // 页码（默认1）
        "page_size": 20           // 每页数量（默认20）
    }

    ========================================
    响应数据
    ========================================
    {
        "code": 0,
        "message": "success",
        "data": {
            "items": [
                {
                    "account_id": 1,
                    "account_name": "我的A股账户",
                    "market": "A-share",
                    "status": "active",
                    "broker": "华泰证券",
                    "initial_capital": 100000.0,
                    "current_capital": 95000.0,
                    "total_value": 108000.0,      // 持仓总市值
                    "total_cost": 105000.0,       // 持仓总成本
                    "total_pnl": 3000.0,          // 总盈亏
                    "total_pnl_rate": 2.86,       // 总盈亏率(%)
                    "holding_count": 5,           // 持仓数量
                    "created_at": "2025-01-01T00:00:00"
                }
            ],
            "total": 10,
            "page": 1,
            "page_size": 20,
            "total_pages": 1
        }
    }

    ========================================
    执行流程（时序）
    ========================================
    1. 前端发起请求 POST /account/query
    2. Controller 获取当前用户信息
    3. Controller 调用 AccountQueryService.execute()
    4. Service 调用 AccountRepository 查询账户列表
    5. Service 调用 HoldingRepository 查询持仓数据
    6. Service 调用 Converter 计算业务数据（市值、盈亏等）
    7. Service 调用 Builder 构建响应对象
    8. Controller 返回统一格式响应
    9. 前端渲染账户列表

    ========================================
    业务规则
    ========================================
    1. 只能查询当前用户自己的账户
    2. 支持按市场类型筛选（A-share/HK/US）
    3. 支持按状态筛选（active/inactive/closed）
    4. 返回账户基本信息 + 持仓统计数据
    5. 按创建时间倒序排列

    ========================================
    错误码
    ========================================
    无特殊错误码（使用通用错误码）

    ========================================
    前端调用示例
    ========================================
    const data = await post('/account/query', {
        market: 'A-share',
        status: 'active',
        page: 1,
        page_size: 20
    })

    ========================================
    修改记录
    ========================================
    2025-01-17: 重构为POST-only架构，使用Service+Converter+Builder模式
    """
    service = AccountQueryService()
    data = await service.execute(
        db=db,
        user_id=current_user.user_id,
        market=request.market,
        status=request.status,
        page=request.page,
        page_size=request.page_size,
    )
    return Response.success(data)


@router.post("/detail")
async def get_account_detail(
    request: AccountDetailRequest, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """
    获取账户详情

    ========================================
    接口信息
    ========================================
    接口路径: POST /api/v1/account/detail
    对应页面: pages/account/detail.vue - 账户详情页
    接口功能: 获取账户基本信息、持仓列表、汇总统计

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
        "data": {
            "account_info": {
                "account_id": 123,
                "account_name": "我的A股账户",
                "market": "A-share",
                "status": "active",
                "broker": "华泰证券",
                "account_number": "1234567890",
                "initial_capital": 100000.0,
                "current_capital": 95000.0,
                "created_at": "2025-01-01T00:00:00",
                "updated_at": "2025-01-17T00:00:00"
            },
            "holdings": [
                {
                    "holding_id": 1,
                    "symbol": "600000.SH",
                    "stock_name": "浦发银行",
                    "quantity": 1000,
                    "available_quantity": 1000,
                    "cost_price": 10.5,
                    "current_price": 10.8,
                    "market_value": 10800.0,
                    "total_cost": 10500.0,
                    "pnl": 300.0,
                    "pnl_rate": 2.86,
                    "updated_at": "2025-01-17T00:00:00"
                }
            ],
            "statistics": {
                "total_value": 108000.0,       // 持仓总市值
                "total_cost": 105000.0,        // 持仓总成本
                "total_pnl": 3000.0,           // 总盈亏
                "total_pnl_rate": 2.86,        // 总盈亏率(%)
                "holding_count": 5,            // 持仓数量
                "available_capital": 95000.0,  // 可用资金
                "total_assets": 203000.0       // 总资产（持仓+资金）
            }
        }
    }

    ========================================
    执行流程（时序）
    ========================================
    1. 前端发起请求 POST /account/detail
    2. Controller 调用 AccountDetailService.execute()
    3. Service 校验账户权限（是否属于当前用户）
    4. Service 查询账户信息（Repository）
    5. Service 查询持仓列表（Repository）
    6. Service 调用 Converter 计算统计数据
    7. Service 调用 Builder 构建响应
    8. Controller 返回响应
    9. 前端渲染账户详情和持仓列表

    ========================================
    业务规则
    ========================================
    1. 只能查看自己的账户
    2. 持仓盈亏 = 数量 × (当前价 - 成本价)
    3. 盈亏率 = 盈亏 / 成本 × 100%
    4. 总资产 = 持仓总市值 + 可用资金

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
    2025-01-17: 重构为POST-only架构，使用Service+Converter+Builder模式
    """
    service = AccountDetailService()
    data = await service.execute(db=db, account_id=request.account_id, user_id=current_user.user_id)
    return Response.success(data)


@router.post("/create")
async def create_account(
    request: AccountCreateRequest, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """
    创建账户

    ========================================
    接口信息
    ========================================
    接口路径: POST /api/v1/account/create
    对应页面: pages/account/create.vue - 创建账户页
    接口功能: 创建新账户

    ========================================
    请求参数
    ========================================
    {
        "account_name": "我的A股账户",      // 账户名称（必填，最长100字符）
        "market": "A-share",               // 市场类型（必填）: A-share/HK/US
        "broker": "华泰证券",              // 券商名称（可选）
        "account_number": "1234567890",   // 账户号（可选）
        "initial_capital": 100000.0       // 初始资金（可选，默认0）
    }

    ========================================
    响应数据
    ========================================
    {
        "code": 0,
        "message": "success",
        "data": {
            "account_id": 123,
            "account_name": "我的A股账户",
            "market": "A-share",
            "status": "active",
            "broker": "华泰证券",
            "account_number": "1234567890",
            "initial_capital": 100000.0,
            "current_capital": 100000.0,
            "created_at": "2025-01-17T00:00:00"
        }
    }

    ========================================
    执行流程（时序）
    ========================================
    1. 前端发起请求 POST /account/create
    2. Controller 调用 AccountCreateService.execute()
    3. Service 调用 Converter 验证数据
    4. Service 检查账户名称是否重复
    5. Service 调用 Converter 准备数据
    6. Service 调用 Repository 创建账户
    7. Service 调用 Builder 构建响应
    8. Controller 返回响应
    9. 前端跳转到账户详情页

    ========================================
    业务规则
    ========================================
    1. 账户名称不能为空，最长100字符
    2. 同一用户下账户名称不能重复
    3. 市场类型必须是: A-share/HK/US
    4. 初始资金不能为负数
    5. 新账户默认状态为active
    6. current_capital初始等于initial_capital

    ========================================
    错误码
    ========================================
    1003: 数据验证失败
    1004: 账户名称已存在

    ========================================
    前端调用示例
    ========================================
    const data = await post('/account/create', {
        account_name: '我的A股账户',
        market: 'A-share',
        broker: '华泰证券',
        initial_capital: 100000
    })

    ========================================
    修改记录
    ========================================
    2025-01-17: 重构为POST-only架构，使用Service+Converter+Builder模式
    """
    service = AccountCreateService()
    data = await service.execute(
        db=db,
        user_id=current_user.user_id,
        account_name=request.account_name,
        market=request.market,
        broker=request.broker,
        account_number=request.account_number,
        initial_capital=request.initial_capital,
    )
    return Response.success(data)


@router.post("/update")
async def update_account(
    request: AccountUpdateRequest, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """
    更新账户

    ========================================
    接口信息
    ========================================
    接口路径: POST /api/v1/account/update
    对应页面: pages/account/edit.vue - 编辑账户页
    接口功能: 更新账户信息

    ========================================
    请求参数
    ========================================
    {
        "account_id": 123,                 // 账户ID（必填）
        "account_name": "新账户名称",       // 账户名称（可选）
        "broker": "中信证券",              // 券商名称（可选）
        "account_number": "9876543210",   // 账户号（可选）
        "status": "inactive",             // 账户状态（可选）: active/inactive/closed
        "current_capital": 95000.0        // 当前资金（可选）
    }

    ========================================
    响应数据
    ========================================
    {
        "code": 0,
        "message": "success",
        "data": {
            "account_id": 123,
            "account_name": "新账户名称",
            "market": "A-share",
            "status": "inactive",
            "broker": "中信证券",
            "account_number": "9876543210",
            "initial_capital": 100000.0,
            "current_capital": 95000.0,
            "created_at": "2025-01-01T00:00:00",
            "updated_at": "2025-01-17T00:00:00"
        }
    }

    ========================================
    执行流程（时序）
    ========================================
    1. 前端发起请求 POST /account/update
    2. Controller 调用 AccountUpdateService.execute()
    3. Service 校验账户权限
    4. Service 调用 Converter 验证和准备数据
    5. Service 调用 Repository 更新账户
    6. Service 调用 Builder 构建响应
    7. Controller 返回响应
    8. 前端更新显示

    ========================================
    业务规则
    ========================================
    1. 只能更新自己的账户
    2. 只更新提供的字段（部分更新）
    3. 账户名称不能为空
    4. 状态必须是: active/inactive/closed
    5. 当前资金不能为负数
    6. market和initial_capital不允许修改

    ========================================
    错误码
    ========================================
    1001: 无权访问该账户
    1002: 账户不存在
    1003: 数据验证失败

    ========================================
    前端调用示例
    ========================================
    const data = await post('/account/update', {
        account_id: 123,
        account_name: '新账户名称',
        status: 'inactive'
    })

    ========================================
    修改记录
    ========================================
    2025-01-17: 重构为POST-only架构，使用Service+Converter+Builder模式
    """
    service = AccountUpdateService()
    data = await service.execute(
        db=db,
        account_id=request.account_id,
        user_id=current_user.user_id,
        account_name=request.account_name,
        broker=request.broker,
        account_number=request.account_number,
        status=request.status,
        current_capital=request.current_capital,
    )
    return Response.success(data)


@router.post("/delete")
async def delete_account(
    request: AccountDeleteRequest, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """
    删除账户

    ========================================
    接口信息
    ========================================
    接口路径: POST /api/v1/account/delete
    对应页面: pages/account/list.vue - 账户列表页（删除按钮）
    接口功能: 软删除账户

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
        "data": {
            "success": true,
            "account_id": 123,
            "message": "账户已删除"
        }
    }

    ========================================
    执行流程（时序）
    ========================================
    1. 前端发起请求 POST /account/delete
    2. Controller 调用 AccountDeleteService.execute()
    3. Service 校验账户权限
    4. Service 调用 Converter 检查是否有持仓
    5. Service 调用 Repository 软删除账户
    6. Service 调用 Builder 构建响应
    7. Controller 返回响应
    8. 前端刷新账户列表

    ========================================
    业务规则
    ========================================
    1. 只能删除自己的账户
    2. 账户有持仓时不能删除
    3. 使用软删除，不物理删除数据
    4. 删除后is_deleted=true, deleted_at记录时间

    ========================================
    错误码
    ========================================
    1001: 无权访问该账户
    1002: 账户不存在
    1006: 账户有持仓不能删除

    ========================================
    前端调用示例
    ========================================
    const data = await post('/account/delete', { account_id: 123 })

    ========================================
    修改记录
    ========================================
    2025-01-17: 重构为POST-only架构，使用Service+Converter+Builder模式
    """
    service = AccountDeleteService()
    data = await service.execute(db=db, account_id=request.account_id, user_id=current_user.user_id)
    return Response.success(data)
