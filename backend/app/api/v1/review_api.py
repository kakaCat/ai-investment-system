"""
Review API - POST-only架构

股票评价API - 使用POST-only + Service + Converter + Builder模式
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field
from typing import Optional, List
from decimal import Decimal

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.common import Response
from app.services.review import ReviewService


router = APIRouter(prefix="/review", tags=["股票评价"])


# ========================================
# Request Schemas
# ========================================

class ReviewGetRequest(BaseModel):
    """获取评价请求"""
    symbol: str = Field(..., description="股票代码")


class ReviewCreateRequest(BaseModel):
    """创建/更新评价请求"""
    symbol: str = Field(..., description="股票代码")
    stock_name: Optional[str] = Field(None, description="股票名称")
    rating: int = Field(..., ge=0, le=10, description="评分 0-10")
    bullish_reasons: List[str] = Field(default=[], description="看好理由列表")
    bearish_reasons: List[str] = Field(default=[], description="风险理由列表")
    holding_logic: Optional[str] = Field(None, description="持有逻辑")
    target_price: Optional[Decimal] = Field(None, description="目标价")
    stop_loss_price: Optional[Decimal] = Field(None, description="止损价")


# ========================================
# API Endpoints
# ========================================

@router.post("/get")
async def get_review(
    request: ReviewGetRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取股票评价

    ========================================
    接口信息
    ========================================
    接口路径: POST /api/v1/review/get
    对应页面: pages/stock/detail.vue - 股票详情页评价tab
    接口功能: 获取用户对指定股票的评价，不存在则返回空模板

    ========================================
    请求参数
    ========================================
    {
        "symbol": "600600"  // 股票代码
    }

    ========================================
    响应数据
    ========================================
    {
        "review_id": 1,
        "user_id": 1001,
        "symbol": "600600",
        "stock_name": "青岛啤酒",
        "rating": 8,                          // 评分 0-10
        "bullish_reasons": ["理由1", "理由2"],
        "bearish_reasons": ["风险1"],
        "holding_logic": "长期持有",
        "target_price": 120.0,
        "stop_loss_price": 85.0,
        "created_at": "2025-11-18T10:00:00Z",
        "updated_at": "2025-11-18T12:00:00Z"
    }

    ========================================
    执行流程（时序）
    ========================================
    1. 接收symbol
    2. Service调用Repository查询评价
    3. Converter转换数据（不存在返回空模板）
    4. 返回响应

    ========================================
    业务规则
    ========================================
    1. 每个用户对每只股票只能有一条评价
    2. 不存在时返回review_id=0的空模板
    3. rating范围0-10

    ========================================
    前端调用示例
    ========================================
    const review = await post('/review/get', { symbol: '600600' })
    """
    service = ReviewService()
    result = await service.get_review(db, current_user.user_id, request.symbol)
    return Response.success(data=result)


@router.post("/save")
async def save_review(
    request: ReviewCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    保存股票评价

    ========================================
    接口信息
    ========================================
    接口路径: POST /api/v1/review/save
    对应页面: pages/stock/detail.vue - 股票详情页评价表单
    接口功能: 创建或更新用户对股票的评价

    ========================================
    请求参数
    ========================================
    {
        "symbol": "600600",
        "stock_name": "青岛啤酒",
        "rating": 8,
        "bullish_reasons": ["财务稳健", "品牌力强"],
        "bearish_reasons": ["行业增长放缓"],
        "holding_logic": "长期持有，分红稳定",
        "target_price": 120.0,
        "stop_loss_price": 85.0
    }

    ========================================
    响应数据
    ========================================
    {
        "review_id": 1,
        "user_id": 1001,
        "symbol": "600600",
        ...
    }

    ========================================
    执行流程（时序）
    ========================================
    1. 接收评价数据
    2. Service查询是否存在评价
    3. 存在则更新，不存在则创建
    4. Builder构建数据
    5. Repository保存到数据库
    6. Converter转换响应

    ========================================
    业务规则
    ========================================
    1. 自动判断create or update
    2. rating必填，范围0-10
    3. bullish_reasons和bearish_reasons可为空数组

    ========================================
    前端调用示例
    ========================================
    const review = await post('/review/save', {
        symbol: '600600',
        rating: 8,
        bullish_reasons: ['理由1']
    })
    """
    service = ReviewService()
    result = await service.create_or_update(
        db,
        current_user.user_id,
        request.symbol,
        request.dict(exclude={'symbol'})
    )
    return Response.success(data=result, message="评价已保存")
