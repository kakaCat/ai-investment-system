"""
Review Schemas (v3.2)
"""

from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal
from datetime import datetime


class ReviewBase(BaseModel):
    """Base review schema"""

    symbol: str = Field(..., max_length=20, description="股票代码")
    rating: int = Field(..., ge=1, le=5, description="评分 1-5星")


class ReviewCreate(ReviewBase):
    """Review creation schema"""

    user_id: int = Field(..., description="用户ID")
    bullish_reasons: list[str] = Field(default_factory=list, description="看好原因列表")
    bearish_reasons: list[str] = Field(default_factory=list, description="风险原因列表")
    holding_logic: Optional[str] = Field(None, max_length=2000, description="持有逻辑")
    target_price: Optional[Decimal] = Field(None, description="目标价")
    stop_loss_price: Optional[Decimal] = Field(None, description="止损价")


class ReviewUpdate(BaseModel):
    """Review update schema"""

    rating: Optional[int] = Field(None, ge=1, le=5)
    bullish_reasons: Optional[list[str]] = None
    bearish_reasons: Optional[list[str]] = None
    holding_logic: Optional[str] = Field(None, max_length=2000)
    target_price: Optional[Decimal] = None
    stop_loss_price: Optional[Decimal] = None


class ReviewResponse(ReviewBase):
    """Review response schema"""

    review_id: int = Field(..., description="评价ID")
    user_id: int = Field(..., description="用户ID")
    stock_name: Optional[str] = Field(None, description="股票名称")
    bullish_reasons: list[str] = Field(..., description="看好原因列表")
    bearish_reasons: list[str] = Field(..., description="风险原因列表")
    holding_logic: Optional[str] = Field(None, description="持有逻辑")
    target_price: Optional[Decimal] = Field(None, description="目标价")
    stop_loss_price: Optional[Decimal] = Field(None, description="止损价")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    class Config:
        from_attributes = True


class ReviewListResponse(BaseModel):
    """Review list response"""

    total: int = Field(..., description="总数量")
    reviews: list[ReviewResponse] = Field(..., description="评价列表")


class ReviewStats(BaseModel):
    """Review statistics"""

    total_reviews: int = Field(..., description="总评价数")
    avg_rating: Decimal = Field(..., description="平均评分")
    five_star_count: int = Field(..., description="5星数量")
    four_star_count: int = Field(..., description="4星数量")
    three_star_count: int = Field(..., description="3星数量")
    two_star_count: int = Field(..., description="2星数量")
    one_star_count: int = Field(..., description="1星数量")
