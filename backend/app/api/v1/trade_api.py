"""
Trade API - POST-only架构

交易管理API - 使用POST-only + Service + Converter + Builder模式
"""

from typing import Optional
from decimal import Decimal
from datetime import date
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.common import Response
from app.services.trade import (
    TradeQueryService,
    TradeDetailService,
    TradeCreateService,
    TradeUpdateService,
    TradeDeleteService,
)


router = APIRouter(prefix="/trade", tags=["交易管理"])


# ========================================
# Request Schemas
# ========================================

class TradeQueryRequest(BaseModel):
    """交易查询请求"""
    account_id: Optional[int] = Field(None, description="账户ID筛选")
    symbol: Optional[str] = Field(None, description="股票代码筛选")
    trade_type: Optional[str] = Field(None, description="交易类型筛选（buy/sell）")
    start_date: Optional[date] = Field(None, description="开始日期")
    end_date: Optional[date] = Field(None, description="结束日期")
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(20, ge=1, le=100, description="每页数量")


class TradeDetailRequest(BaseModel):
    """交易详情请求"""
    trade_id: int = Field(..., description="交易ID")


class TradeCreateRequest(BaseModel):
    """交易创建请求"""
    account_id: int = Field(..., description="账户ID")
    symbol: str = Field(..., description="股票代码")
    stock_name: str = Field(..., description="股票名称")
    trade_type: str = Field(..., description="交易类型（buy/sell）")
    quantity: Decimal = Field(..., gt=0, description="数量")
    price: Decimal = Field(..., gt=0, description="价格")
    trade_date: date = Field(..., description="交易日期")
    commission: Optional[Decimal] = Field(None, ge=0, description="手续费")
    tax: Optional[Decimal] = Field(None, ge=0, description="税费")
    profit_loss: Optional[Decimal] = Field(None, description="盈亏（卖出时）")
    notes: Optional[str] = Field(None, description="备注")


class TradeUpdateRequest(BaseModel):
    """交易更新请求"""
    trade_id: int = Field(..., description="交易ID")
    symbol: Optional[str] = Field(None, description="股票代码")
    stock_name: Optional[str] = Field(None, description="股票名称")
    trade_type: Optional[str] = Field(None, description="交易类型（buy/sell）")
    quantity: Optional[Decimal] = Field(None, gt=0, description="数量")
    price: Optional[Decimal] = Field(None, gt=0, description="价格")
    trade_date: Optional[date] = Field(None, description="交易日期")
    commission: Optional[Decimal] = Field(None, ge=0, description="手续费")
    tax: Optional[Decimal] = Field(None, ge=0, description="税费")
    profit_loss: Optional[Decimal] = Field(None, description="盈亏")
    notes: Optional[str] = Field(None, description="备注")


class TradeDeleteRequest(BaseModel):
    """交易删除请求"""
    trade_id: int = Field(..., description="交易ID")


# ========================================
# API Endpoints
# ========================================

@router.post("/query")
async def query_trades(
    request: TradeQueryRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    查询交易列表

    ========================================
    接口信息
    ========================================
    接口路径: POST /api/v1/trade/query
    对应页面: pages/trade/list.vue - 交易记录列表页
    接口功能: 查询用户所有交易记录，支持账户、股票、类型、日期范围筛选，支持分页

    ========================================
    请求参数
    ========================================
    {
        "account_id": 1,                    // 账户ID筛选（可选）
        "symbol": "600519",                 // 股票代码筛选（可选）
        "trade_type": "buy",                // 交易类型筛选（可选）buy/sell
        "start_date": "2025-01-01",         // 开始日期（可选）
        "end_date": "2025-01-31",           // 结束日期（可选）
        "page": 1,                          // 页码（默认1）
        "page_size": 20                     // 每页数量（默认20）
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
                    "trade_id": 1,
                    "account_id": 1,
                    "symbol": "600519",
                    "stock_name": "贵州茅台",
                    "trade_type": "buy",
                    "quantity": 100.0,
                    "price": 1800.50,
                    "total_amount": 180050.0,
                    "commission": 5.0,
                    "tax": 1.8,
                    "profit_loss": null,
                    "trade_date": "2025-01-15",
                    "notes": "建仓",
                    "created_at": "2025-01-15T10:30:00"
                }
            ],
            "total": 50,
            "page": 1,
            "page_size": 20,
            "total_pages": 3
        }
    }

    ========================================
    执行流程（时序）
    ========================================
    1. API接收请求 → 验证JWT Token → 获取user_id
    2. 调用 TradeQueryService.execute()
       2.1 调用 TradeRepository.query_by_user() 查询交易列表（含筛选条件）
       2.2 调用 TradeQueryConverter.convert() 转换为业务数据
           - 计算交易总金额（数量 × 价格）
           - 提取盈亏信息（卖出交易）
       2.3 调用 TradeQueryBuilder.build_response() 构建分页响应
    3. 返回统一响应格式

    ========================================
    业务规则
    ========================================
    1. 权限规则：
       - 只能查询当前登录用户的交易
       - TradeRepository自动过滤user_id

    2. 筛选规则：
       - account_id: 筛选指定账户的交易
       - symbol: 筛选指定股票的交易
       - trade_type: 筛选交易类型（buy/sell）
       - start_date/end_date: 筛选日期范围

    3. 数据计算：
       - total_amount = quantity × price
       - profit_loss: 仅卖出交易显示

    4. 分页规则：
       - 默认页码1，每页20条
       - 最大每页100条
       - 按交易日期倒序

    ========================================
    错误码
    ========================================
    - 0: 成功
    - 1001: 无权访问（PermissionDenied）
    - 1003: 数据验证失败（ValidationError）
    - 1000: 服务器内部错误

    ========================================
    前端调用示例
    ========================================
    ```javascript
    // pages/trade/list.vue
    const queryTrades = async (filters) => {
      const response = await api.post('/api/v1/trade/query', {
        account_id: filters.accountId,
        symbol: filters.symbol,
        trade_type: filters.tradeType,
        start_date: filters.startDate,
        end_date: filters.endDate,
        page: filters.page,
        page_size: 20
      });

      if (response.data.code === 0) {
        trades.value = response.data.data.items;
        pagination.value = {
          total: response.data.data.total,
          page: response.data.data.page,
          pageSize: response.data.data.page_size,
          totalPages: response.data.data.total_pages
        };
      }
    };
    ```

    ========================================
    修改记录
    ========================================
    2025-01-17: 重构为POST-only架构，使用Service+Converter+Builder模式
    """
    service = TradeQueryService()
    data = await service.execute(
        db=db,
        user_id=current_user.user_id,
        account_id=request.account_id,
        symbol=request.symbol,
        trade_type=request.trade_type,
        start_date=request.start_date,
        end_date=request.end_date,
        page=request.page,
        page_size=request.page_size
    )
    return Response.success(data)


@router.post("/detail")
async def get_trade_detail(
    request: TradeDetailRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    查询交易详情

    ========================================
    接口信息
    ========================================
    接口路径: POST /api/v1/trade/detail
    对应页面: pages/trade/detail.vue - 交易详情页
    接口功能: 查询单个交易的详细信息，包含完整的费用和盈亏计算

    ========================================
    请求参数
    ========================================
    {
        "trade_id": 1                       // 交易ID（必需）
    }

    ========================================
    响应数据
    ========================================
    {
        "code": 0,
        "message": "success",
        "data": {
            "trade_id": 1,
            "account_id": 1,
            "user_id": 1,
            "symbol": "600519",
            "stock_name": "贵州茅台",
            "trade_type": "buy",
            "quantity": 100.0,
            "price": 1800.50,
            "total_amount": 180050.0,
            "commission": 5.0,
            "tax": 1.8,
            "actual_amount": 180056.8,      // 实际金额（含手续费税费）
            "profit_loss": null,
            "trade_date": "2025-01-15",
            "notes": "建仓",
            "created_at": "2025-01-15T10:30:00",
            "updated_at": "2025-01-15T10:30:00"
        }
    }

    ========================================
    执行流程（时序）
    ========================================
    1. API接收请求 → 验证JWT Token → 获取user_id
    2. 调用 TradeDetailService.execute()
       2.1 调用 TradeRepository.get_by_id() 查询交易
       2.2 权限校验：检查trade.user_id == user_id
       2.3 调用 TradeDetailConverter.convert() 转换为详情数据
           - 计算交易总金额（数量 × 价格）
           - 计算实际金额：
             买入: 总金额 + 手续费 + 税费
             卖出: 总金额 - 手续费 - 税费
    3. 返回统一响应格式

    ========================================
    业务规则
    ========================================
    1. 权限规则：
       - 只能查询当前登录用户的交易
       - 如果交易不属于当前用户，返回1001错误

    2. 数据计算：
       - total_amount = quantity × price
       - actual_amount（买入）= total_amount + commission + tax
       - actual_amount（卖出）= total_amount - commission - tax

    ========================================
    错误码
    ========================================
    - 0: 成功
    - 1001: 无权访问（PermissionDenied）
    - 1002: 交易不存在（ResourceNotFound）
    - 1000: 服务器内部错误

    ========================================
    前端调用示例
    ========================================
    ```javascript
    // pages/trade/detail.vue
    const getTradeDetail = async (tradeId) => {
      const response = await api.post('/api/v1/trade/detail', {
        trade_id: tradeId
      });

      if (response.data.code === 0) {
        trade.value = response.data.data;
      } else if (response.data.code === 1002) {
        showError('交易不存在');
      } else if (response.data.code === 1001) {
        showError('无权访问该交易');
      }
    };
    ```

    ========================================
    修改记录
    ========================================
    2025-01-17: 重构为POST-only架构，使用Service+Converter+Builder模式
    """
    service = TradeDetailService()
    data = await service.execute(
        db=db,
        trade_id=request.trade_id,
        user_id=current_user.user_id
    )
    return Response.success(data)


@router.post("/create")
async def create_trade(
    request: TradeCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    创建交易记录

    ========================================
    接口信息
    ========================================
    接口路径: POST /api/v1/trade/create
    对应页面: pages/trade/create.vue - 创建交易页
    接口功能: 创建新的交易记录（买入/卖出）

    ========================================
    请求参数
    ========================================
    {
        "account_id": 1,                    // 账户ID（必需）
        "symbol": "600519",                 // 股票代码（必需）
        "stock_name": "贵州茅台",           // 股票名称（必需）
        "trade_type": "buy",                // 交易类型（必需）buy/sell
        "quantity": 100,                    // 数量（必需，>0）
        "price": 1800.50,                   // 价格（必需，>0）
        "trade_date": "2025-01-15",         // 交易日期（必需）
        "commission": 5.0,                  // 手续费（可选，>=0）
        "tax": 1.8,                         // 税费（可选，>=0）
        "profit_loss": null,                // 盈亏（可选，卖出时）
        "notes": "建仓"                     // 备注（可选）
    }

    ========================================
    响应数据
    ========================================
    {
        "code": 0,
        "message": "success",
        "data": {
            "trade_id": 1,
            "account_id": 1,
            "symbol": "600519",
            "stock_name": "贵州茅台",
            "trade_type": "buy",
            "quantity": 100.0,
            "price": 1800.50,
            "total_amount": 180050.0,
            "commission": 5.0,
            "tax": 1.8,
            "profit_loss": null,
            "trade_date": "2025-01-15",
            "notes": "建仓",
            "created_at": "2025-01-15T10:30:00"
        }
    }

    ========================================
    执行流程（时序）
    ========================================
    1. API接收请求 → 验证JWT Token → 获取user_id
    2. 调用 TradeCreateService.execute()
       2.1 调用 AccountRepository.get_by_id() 查询账户
       2.2 权限校验：检查account.user_id == user_id
       2.3 调用 TradeCreateConverter.validate() 验证数据
           - 股票代码和名称不为空
           - 交易类型必须是buy或sell
           - 数量和价格必须>0
           - 手续费和税费必须>=0
       2.4 调用 TradeCreateConverter.prepare_data() 准备数据
           - 股票代码转大写
           - 手续费和税费默认0
       2.5 调用 TradeRepository.create() 创建交易
       2.6 调用 TradeCreateBuilder.build_response() 构建响应
    3. 返回统一响应格式

    ========================================
    业务规则
    ========================================
    1. 权限规则：
       - 只能在当前登录用户的账户下创建交易
       - 如果账户不属于当前用户，返回1001错误

    2. 验证规则：
       - symbol: 不能为空
       - stock_name: 不能为空
       - trade_type: 必须是buy或sell
       - quantity: 必须>0
       - price: 必须>0
       - commission: 如提供，必须>=0
       - tax: 如提供，必须>=0

    3. 默认值：
       - commission: 默认0
       - tax: 默认0
       - symbol: 自动转大写

    ========================================
    错误码
    ========================================
    - 0: 成功
    - 1001: 无权访问账户（PermissionDenied）
    - 1002: 账户不存在（ResourceNotFound）
    - 1003: 数据验证失败（ValidationError）
    - 1000: 服务器内部错误

    ========================================
    前端调用示例
    ========================================
    ```javascript
    // pages/trade/create.vue
    const createTrade = async (formData) => {
      const response = await api.post('/api/v1/trade/create', {
        account_id: formData.accountId,
        symbol: formData.symbol,
        stock_name: formData.stockName,
        trade_type: formData.tradeType,
        quantity: formData.quantity,
        price: formData.price,
        trade_date: formData.tradeDate,
        commission: formData.commission || 0,
        tax: formData.tax || 0,
        profit_loss: formData.profitLoss,
        notes: formData.notes
      });

      if (response.data.code === 0) {
        showSuccess('交易记录创建成功');
        router.push('/trade/list');
      } else if (response.data.code === 1003) {
        showError(response.data.message);
      }
    };
    ```

    ========================================
    修改记录
    ========================================
    2025-01-17: 重构为POST-only架构，使用Service+Converter+Builder模式
    """
    service = TradeCreateService()
    data = await service.execute(
        db=db,
        user_id=current_user.user_id,
        account_id=request.account_id,
        symbol=request.symbol,
        stock_name=request.stock_name,
        trade_type=request.trade_type,
        quantity=request.quantity,
        price=request.price,
        trade_date=request.trade_date,
        commission=request.commission,
        tax=request.tax,
        profit_loss=request.profit_loss,
        notes=request.notes
    )
    return Response.success(data)


@router.post("/update")
async def update_trade(
    request: TradeUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    更新交易记录

    ========================================
    接口信息
    ========================================
    接口路径: POST /api/v1/trade/update
    对应页面: pages/trade/edit.vue - 编辑交易页
    接口功能: 更新已有交易记录的信息（支持部分更新）

    ========================================
    请求参数
    ========================================
    {
        "trade_id": 1,                      // 交易ID（必需）
        "symbol": "600519",                 // 股票代码（可选）
        "stock_name": "贵州茅台",           // 股票名称（可选）
        "trade_type": "buy",                // 交易类型（可选）
        "quantity": 100,                    // 数量（可选，>0）
        "price": 1800.50,                   // 价格（可选，>0）
        "trade_date": "2025-01-15",         // 交易日期（可选）
        "commission": 5.0,                  // 手续费（可选，>=0）
        "tax": 1.8,                         // 税费（可选，>=0）
        "profit_loss": null,                // 盈亏（可选）
        "notes": "调整建仓"                 // 备注（可选）
    }

    ========================================
    响应数据
    ========================================
    {
        "code": 0,
        "message": "success",
        "data": {
            "trade_id": 1,
            "account_id": 1,
            "symbol": "600519",
            "stock_name": "贵州茅台",
            "trade_type": "buy",
            "quantity": 100.0,
            "price": 1800.50,
            "total_amount": 180050.0,
            "commission": 5.0,
            "tax": 1.8,
            "profit_loss": null,
            "trade_date": "2025-01-15",
            "notes": "调整建仓",
            "created_at": "2025-01-15T10:30:00",
            "updated_at": "2025-01-15T11:00:00"
        }
    }

    ========================================
    执行流程（时序）
    ========================================
    1. API接收请求 → 验证JWT Token → 获取user_id
    2. 调用 TradeUpdateService.execute()
       2.1 调用 TradeRepository.get_by_id() 查询交易
       2.2 权限校验：检查trade.user_id == user_id
       2.3 调用 TradeUpdateConverter.prepare_update_data() 准备更新数据
           - 只更新提供的字段
           - 验证每个字段的合法性
       2.4 调用 TradeRepository.update() 更新交易
       2.5 调用 TradeUpdateBuilder.build_response() 构建响应
    3. 返回统一响应格式

    ========================================
    业务规则
    ========================================
    1. 权限规则：
       - 只能更新当前登录用户的交易
       - 如果交易不属于当前用户，返回1001错误

    2. 更新规则：
       - 支持部分更新（只更新提供的字段）
       - 未提供的字段保持原值不变

    3. 验证规则：
       - symbol: 如提供，不能为空
       - stock_name: 如提供，不能为空
       - trade_type: 如提供，必须是buy或sell
       - quantity: 如提供，必须>0
       - price: 如提供，必须>0
       - commission: 如提供，必须>=0
       - tax: 如提供，必须>=0

    ========================================
    错误码
    ========================================
    - 0: 成功
    - 1001: 无权访问（PermissionDenied）
    - 1002: 交易不存在（ResourceNotFound）
    - 1003: 数据验证失败（ValidationError）
    - 1000: 服务器内部错误

    ========================================
    前端调用示例
    ========================================
    ```javascript
    // pages/trade/edit.vue
    const updateTrade = async (tradeId, formData) => {
      const response = await api.post('/api/v1/trade/update', {
        trade_id: tradeId,
        symbol: formData.symbol,
        stock_name: formData.stockName,
        trade_type: formData.tradeType,
        quantity: formData.quantity,
        price: formData.price,
        trade_date: formData.tradeDate,
        commission: formData.commission,
        tax: formData.tax,
        profit_loss: formData.profitLoss,
        notes: formData.notes
      });

      if (response.data.code === 0) {
        showSuccess('交易记录更新成功');
        router.push('/trade/list');
      } else if (response.data.code === 1003) {
        showError(response.data.message);
      }
    };
    ```

    ========================================
    修改记录
    ========================================
    2025-01-17: 重构为POST-only架构，使用Service+Converter+Builder模式
    """
    service = TradeUpdateService()
    data = await service.execute(
        db=db,
        trade_id=request.trade_id,
        user_id=current_user.user_id,
        symbol=request.symbol,
        stock_name=request.stock_name,
        trade_type=request.trade_type,
        quantity=request.quantity,
        price=request.price,
        trade_date=request.trade_date,
        commission=request.commission,
        tax=request.tax,
        profit_loss=request.profit_loss,
        notes=request.notes
    )
    return Response.success(data)


@router.post("/delete")
async def delete_trade(
    request: TradeDeleteRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    删除交易记录

    ========================================
    接口信息
    ========================================
    接口路径: POST /api/v1/trade/delete
    对应页面: pages/trade/list.vue - 交易列表页（删除操作）
    接口功能: 软删除交易记录（标记为已删除，不实际删除数据）

    ========================================
    请求参数
    ========================================
    {
        "trade_id": 1                       // 交易ID（必需）
    }

    ========================================
    响应数据
    ========================================
    {
        "code": 0,
        "message": "success",
        "data": {
            "success": true,
            "trade_id": 1,
            "message": "交易已删除"
        }
    }

    ========================================
    执行流程（时序）
    ========================================
    1. API接收请求 → 验证JWT Token → 获取user_id
    2. 调用 TradeDeleteService.execute()
       2.1 调用 TradeRepository.get_by_id() 查询交易
       2.2 权限校验：检查trade.user_id == user_id
       2.3 调用 TradeRepository.soft_delete() 软删除交易
           - 设置is_deleted=True
           - 设置deleted_at=当前时间
       2.4 调用 TradeDeleteBuilder.build_response() 构建响应
    3. 返回统一响应格式

    ========================================
    业务规则
    ========================================
    1. 权限规则：
       - 只能删除当前登录用户的交易
       - 如果交易不属于当前用户，返回1001错误

    2. 删除规则：
       - 软删除（is_deleted=True）
       - 不实际删除数据库记录
       - 查询时自动过滤已删除记录

    ========================================
    错误码
    ========================================
    - 0: 成功
    - 1001: 无权访问（PermissionDenied）
    - 1002: 交易不存在（ResourceNotFound）
    - 1000: 服务器内部错误

    ========================================
    前端调用示例
    ========================================
    ```javascript
    // pages/trade/list.vue
    const deleteTrade = async (tradeId) => {
      if (!confirm('确认删除此交易记录？')) return;

      const response = await api.post('/api/v1/trade/delete', {
        trade_id: tradeId
      });

      if (response.data.code === 0) {
        showSuccess('交易记录已删除');
        refreshTradeList();
      } else if (response.data.code === 1002) {
        showError('交易不存在');
      } else if (response.data.code === 1001) {
        showError('无权删除该交易');
      }
    };
    ```

    ========================================
    修改记录
    ========================================
    2025-01-17: 重构为POST-only架构，使用Service+Converter+Builder模式
    """
    service = TradeDeleteService()
    data = await service.execute(
        db=db,
        trade_id=request.trade_id,
        user_id=current_user.user_id
    )
    return Response.success(data)
