"""
Strategy API

操作策略管理接口 - 使用POST-only架构
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
from app.services.strategy import (
    StrategyQueryService,
    StrategyCreateService,
    StrategyUpdateService,
    StrategyDeleteService,
    StrategyExecuteService,
)


router = APIRouter(prefix="/strategy", tags=["操作策略管理"])


# ========================================
# Request Schemas
# ========================================

class StrategyQueryRequest(BaseModel):
    """策略查询请求"""
    symbol: Optional[str] = None
    strategy_type: Optional[str] = None
    status: Optional[str] = None
    page: int = 1
    page_size: int = 20


class StrategyCreateRequest(BaseModel):
    """策略创建请求"""
    symbol: str
    stock_name: str
    strategy_type: str
    trigger_price: Optional[Decimal] = None
    target_quantity: Optional[Decimal] = None
    reason: Optional[str] = None
    notes: Optional[str] = None
    priority: str = "normal"
    is_stop_loss: bool = False
    is_take_profit: bool = False


class StrategyUpdateRequest(BaseModel):
    """策略更新请求"""
    strategy_id: int
    trigger_price: Optional[Decimal] = None
    target_quantity: Optional[Decimal] = None
    reason: Optional[str] = None
    notes: Optional[str] = None
    priority: Optional[str] = None


class StrategyDeleteRequest(BaseModel):
    """策略删除请求"""
    strategy_id: int


class StrategyExecuteRequest(BaseModel):
    """策略执行请求"""
    strategy_id: int
    executed_price: Decimal
    executed_quantity: Decimal


# ========================================
# API Endpoints
# ========================================

@router.post("/query")
async def query_strategies(
    request: StrategyQueryRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    查询策略列表

    ========================================
    接口信息
    ========================================
    接口路径: POST /api/v1/strategy/query
    对应页面: pages/stock/detail.vue - 股票详情页（操作策略模块）
    接口功能: 查询用户操作策略，支持按股票代码、策略类型、状态筛选，支持分页

    ========================================
    请求参数
    ========================================
    {
        "symbol": "600000.SH",     // 股票代码（可选）
        "strategy_type": "buy",    // 策略类型（可选）: buy/sell/hold
        "status": "pending",       // 状态（可选）: pending/completed/cancelled
        "page": 1,                 // 页码（默认1）
        "page_size": 20            // 每页数量（默认20）
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
                    "strategy_id": 1,
                    "symbol": "600000.SH",
                    "stock_name": "浦发银行",
                    "strategy_type": "buy",
                    "trigger_price": 10.5,
                    "target_quantity": 1000,
                    "reason": "技术面突破支撑位",
                    "notes": "分批买入",
                    "status": "pending",
                    "priority": "high",
                    "is_stop_loss": false,
                    "is_take_profit": false,
                    "executed_at": null,
                    "executed_price": null,
                    "executed_quantity": null,
                    "created_at": "2025-01-01T00:00:00",
                    "updated_at": "2025-01-01T00:00:00"
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
    1. 前端发起请求 POST /strategy/query
    2. Controller 获取当前用户信息
    3. Controller 调用 StrategyQueryService.execute()
    4. Service 调用 StrategyRepository 查询策略列表
    5. Service 调用 Converter 转换数据
    6. Service 调用 Builder 构建响应对象
    7. Controller 返回统一格式响应
    8. 前端渲染策略列表

    ========================================
    业务规则
    ========================================
    1. 只能查询当前用户自己的策略
    2. 支持按股票代码筛选
    3. 支持按策略类型筛选（buy/sell/hold）
    4. 支持按状态筛选（pending/completed/cancelled）
    5. 按创建时间倒序排列

    ========================================
    错误码
    ========================================
    无特殊错误码（使用通用错误码）

    ========================================
    前端调用示例
    ========================================
    const data = await post('/strategy/query', {
        symbol: '600000.SH',
        status: 'pending',
        page: 1,
        page_size: 20
    })

    ========================================
    修改记录
    ========================================
    2025-11-21: 初始版本
    """
    service = StrategyQueryService()
    data = await service.execute(
        db=db,
        user_id=current_user.user_id,
        symbol=request.symbol,
        strategy_type=request.strategy_type,
        status=request.status,
        page=request.page,
        page_size=request.page_size
    )
    return Response.success(data)


@router.post("/create")
async def create_strategy(
    request: StrategyCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    创建操作策略

    ========================================
    接口信息
    ========================================
    接口路径: POST /api/v1/strategy/create
    对应页面: pages/stock/detail.vue - 股票详情页（添加策略）
    接口功能: 创建买入、卖出或持有策略

    ========================================
    请求参数
    ========================================
    {
        "symbol": "600000.SH",               // 股票代码（必填）
        "stock_name": "浦发银行",            // 股票名称（必填）
        "strategy_type": "buy",              // 策略类型（必填）: buy/sell/hold
        "trigger_price": 10.5,               // 触发价格（可选）
        "target_quantity": 1000,             // 目标数量（可选）
        "reason": "技术面突破支撑位",        // 策略原因（可选）
        "notes": "分批买入",                 // 备注（可选）
        "priority": "high",                  // 优先级（可选，默认normal）: urgent/high/normal/low
        "is_stop_loss": false,               // 是否止损策略（可选，默认false）
        "is_take_profit": false              // 是否止盈策略（可选，默认false）
    }

    ========================================
    响应数据
    ========================================
    {
        "code": 0,
        "message": "success",
        "data": {
            "strategy_id": 1,
            "symbol": "600000.SH",
            "stock_name": "浦发银行",
            "strategy_type": "buy",
            "trigger_price": 10.5,
            "target_quantity": 1000,
            "reason": "技术面突破支撑位",
            "notes": "分批买入",
            "status": "pending",
            "priority": "high",
            "is_stop_loss": false,
            "is_take_profit": false,
            "created_at": "2025-01-01T00:00:00"
        }
    }

    ========================================
    执行流程（时序）
    ========================================
    1. 前端发起请求 POST /strategy/create
    2. Controller 获取当前用户信息
    3. Controller 调用 StrategyCreateService.execute()
    4. Service 调用 Converter.validate() 验证数据
    5. Service 调用 Converter.prepare_data() 准备数据
    6. Service 调用 StrategyRepository.create() 创建策略
    7. Service 调用 Builder.build_response() 构建响应
    8. Controller 返回统一格式响应
    9. 前端提示创建成功并刷新列表

    ========================================
    业务规则
    ========================================
    1. 股票代码和名称必填
    2. 策略类型必须是 buy/sell/hold 之一
    3. 触发价格和目标数量如果提供必须大于0
    4. 优先级必须是 urgent/high/normal/low 之一
    5. 新创建的策略状态默认为 pending

    ========================================
    错误码
    ========================================
    1001: 股票代码不能为空
    1002: 股票名称不能为空
    1003: 策略类型无效
    1004: 触发价格必须大于0
    1005: 目标数量必须大于0
    1006: 优先级无效

    ========================================
    前端调用示例
    ========================================
    const data = await post('/strategy/create', {
        symbol: '600000.SH',
        stock_name: '浦发银行',
        strategy_type: 'buy',
        trigger_price: 10.5,
        target_quantity: 1000,
        reason: '技术面突破支撑位',
        priority: 'high'
    })

    ========================================
    修改记录
    ========================================
    2025-11-21: 初始版本
    """
    service = StrategyCreateService()
    data = await service.execute(
        db=db,
        user_id=current_user.user_id,
        symbol=request.symbol,
        stock_name=request.stock_name,
        strategy_type=request.strategy_type,
        trigger_price=request.trigger_price,
        target_quantity=request.target_quantity,
        reason=request.reason,
        notes=request.notes,
        priority=request.priority,
        is_stop_loss=request.is_stop_loss,
        is_take_profit=request.is_take_profit
    )
    return Response.success(data)


@router.post("/update")
async def update_strategy(
    request: StrategyUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    更新操作策略

    ========================================
    接口信息
    ========================================
    接口路径: POST /api/v1/strategy/update
    对应页面: pages/stock/detail.vue - 股票详情页（编辑策略）
    接口功能: 更新策略的触发价格、目标数量、原因、备注、优先级

    ========================================
    请求参数
    ========================================
    {
        "strategy_id": 1,                    // 策略ID（必填）
        "trigger_price": 10.8,               // 触发价格（可选）
        "target_quantity": 1200,             // 目标数量（可选）
        "reason": "调整买入价格",            // 策略原因（可选）
        "notes": "分批买入，加仓",           // 备注（可选）
        "priority": "urgent"                 // 优先级（可选）: urgent/high/normal/low
    }

    ========================================
    响应数据
    ========================================
    {
        "code": 0,
        "message": "success",
        "data": {
            "strategy_id": 1,
            "symbol": "600000.SH",
            "stock_name": "浦发银行",
            "strategy_type": "buy",
            "trigger_price": 10.8,
            "target_quantity": 1200,
            "reason": "调整买入价格",
            "notes": "分批买入，加仓",
            "status": "pending",
            "priority": "urgent",
            "is_stop_loss": false,
            "is_take_profit": false,
            "created_at": "2025-01-01T00:00:00",
            "updated_at": "2025-01-02T00:00:00"
        }
    }

    ========================================
    执行流程（时序）
    ========================================
    1. 前端发起请求 POST /strategy/update
    2. Controller 获取当前用户信息
    3. Controller 调用 StrategyUpdateService.execute()
    4. Service 调用 StrategyRepository.get_by_id() 检查策略存在性
    5. Service 检查策略归属（权限校验）
    6. Service 调用 Converter.validate() 验证数据
    7. Service 调用 Converter.prepare_data() 准备更新数据
    8. Service 调用 StrategyRepository.update() 更新策略
    9. Service 调用 Builder.build_response() 构建响应
    10. Controller 返回统一格式响应
    11. 前端提示更新成功并刷新列表

    ========================================
    业务规则
    ========================================
    1. 只能更新当前用户自己的策略
    2. 只更新提供的字段（部分更新）
    3. 触发价格和目标数量如果提供必须大于0
    4. 优先级如果提供必须是 urgent/high/normal/low 之一

    ========================================
    错误码
    ========================================
    2001: 策略不存在
    2002: 无权访问该策略
    2003: 触发价格必须大于0
    2004: 目标数量必须大于0
    2005: 优先级无效

    ========================================
    前端调用示例
    ========================================
    const data = await post('/strategy/update', {
        strategy_id: 1,
        trigger_price: 10.8,
        priority: 'urgent'
    })

    ========================================
    修改记录
    ========================================
    2025-11-21: 初始版本
    """
    service = StrategyUpdateService()
    data = await service.execute(
        db=db,
        user_id=current_user.user_id,
        strategy_id=request.strategy_id,
        trigger_price=request.trigger_price,
        target_quantity=request.target_quantity,
        reason=request.reason,
        notes=request.notes,
        priority=request.priority
    )
    return Response.success(data)


@router.post("/delete")
async def delete_strategy(
    request: StrategyDeleteRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    删除操作策略

    ========================================
    接口信息
    ========================================
    接口路径: POST /api/v1/strategy/delete
    对应页面: pages/stock/detail.vue - 股票详情页（删除策略）
    接口功能: 软删除操作策略

    ========================================
    请求参数
    ========================================
    {
        "strategy_id": 1  // 策略ID（必填）
    }

    ========================================
    响应数据
    ========================================
    {
        "code": 0,
        "message": "success",
        "data": {
            "success": true,
            "strategy_id": 1,
            "message": "策略已删除"
        }
    }

    ========================================
    执行流程（时序）
    ========================================
    1. 前端发起请求 POST /strategy/delete
    2. Controller 获取当前用户信息
    3. Controller 调用 StrategyDeleteService.execute()
    4. Service 调用 StrategyRepository.get_by_id() 检查策略存在性
    5. Service 检查策略归属（权限校验）
    6. Service 调用 StrategyRepository.soft_delete() 软删除策略
    7. Service 调用 Builder.build_response() 构建响应
    8. Controller 返回统一格式响应
    9. 前端提示删除成功并刷新列表

    ========================================
    业务规则
    ========================================
    1. 只能删除当前用户自己的策略
    2. 使用软删除（is_deleted=true）
    3. 删除后不影响历史数据

    ========================================
    错误码
    ========================================
    3001: 策略不存在
    3002: 无权访问该策略

    ========================================
    前端调用示例
    ========================================
    const data = await post('/strategy/delete', {
        strategy_id: 1
    })

    ========================================
    修改记录
    ========================================
    2025-11-21: 初始版本
    """
    service = StrategyDeleteService()
    data = await service.execute(
        db=db,
        user_id=current_user.user_id,
        strategy_id=request.strategy_id
    )
    return Response.success(data)


@router.post("/execute")
async def execute_strategy(
    request: StrategyExecuteRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    执行操作策略

    ========================================
    接口信息
    ========================================
    接口路径: POST /api/v1/strategy/execute
    对应页面: pages/stock/detail.vue - 股票详情页（标记策略已执行）
    接口功能: 标记策略为已执行，记录实际执行价格和数量

    ========================================
    请求参数
    ========================================
    {
        "strategy_id": 1,                    // 策略ID（必填）
        "executed_price": 10.6,              // 实际执行价格（必填）
        "executed_quantity": 1000            // 实际执行数量（必填）
    }

    ========================================
    响应数据
    ========================================
    {
        "code": 0,
        "message": "success",
        "data": {
            "strategy_id": 1,
            "symbol": "600000.SH",
            "stock_name": "浦发银行",
            "strategy_type": "buy",
            "trigger_price": 10.5,
            "target_quantity": 1000,
            "reason": "技术面突破支撑位",
            "notes": "分批买入",
            "status": "completed",
            "priority": "high",
            "is_stop_loss": false,
            "is_take_profit": false,
            "executed_at": "2025-01-02T10:30:00",
            "executed_price": 10.6,
            "executed_quantity": 1000,
            "created_at": "2025-01-01T00:00:00",
            "updated_at": "2025-01-02T10:30:00"
        }
    }

    ========================================
    执行流程（时序）
    ========================================
    1. 前端发起请求 POST /strategy/execute
    2. Controller 获取当前用户信息
    3. Controller 调用 StrategyExecuteService.execute()
    4. Service 调用 StrategyRepository.get_by_id() 检查策略存在性
    5. Service 检查策略归属（权限校验）
    6. Service 调用 Converter.validate() 验证执行数据
    7. Service 调用 StrategyRepository.execute_strategy() 更新执行信息
    8. Service 调用 Builder.build_response() 构建响应
    9. Controller 返回统一格式响应
    10. 前端提示执行成功并刷新列表

    ========================================
    业务规则
    ========================================
    1. 只能执行当前用户自己的策略
    2. 执行价格和数量必须大于0
    3. 执行后策略状态变为 completed
    4. 记录执行时间为当前时间
    5. 执行后不可再次执行（状态已变更）

    ========================================
    错误码
    ========================================
    4001: 策略不存在
    4002: 无权访问该策略
    4003: 执行价格必须大于0
    4004: 执行数量必须大于0

    ========================================
    前端调用示例
    ========================================
    const data = await post('/strategy/execute', {
        strategy_id: 1,
        executed_price: 10.6,
        executed_quantity: 1000
    })

    ========================================
    修改记录
    ========================================
    2025-11-21: 初始版本
    """
    service = StrategyExecuteService()
    data = await service.execute(
        db=db,
        user_id=current_user.user_id,
        strategy_id=request.strategy_id,
        executed_price=request.executed_price,
        executed_quantity=request.executed_quantity
    )
    return Response.success(data)
