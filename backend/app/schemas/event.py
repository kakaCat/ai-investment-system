"""
Event Schemas
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class EventBase(BaseModel):
    """Base event schema"""

    title: str = Field(..., max_length=200, description="事件标题")
    category: str = Field(..., description="事件类别: policy/company/market/industry")
    event_type: str = Field(..., description="事件类型")
    event_date: datetime = Field(..., description="事件日期")


class EventCreate(EventBase):
    """Event creation schema"""

    user_id: int = Field(..., description="用户ID")
    symbol: Optional[str] = Field(None, max_length=20, description="关联股票代码")
    content: str = Field(..., description="事件内容")
    source_url: Optional[str] = Field(None, max_length=500, description="来源链接")
    impact_level: Optional[int] = Field(None, ge=1, le=5, description="影响等级 1-5")
    ai_analysis: Optional[str] = Field(None, description="AI分析")


class EventUpdate(BaseModel):
    """Event update schema"""

    title: Optional[str] = Field(None, max_length=200)
    content: Optional[str] = Field(None)
    impact_level: Optional[int] = Field(None, ge=1, le=5)
    is_read: Optional[bool] = Field(None)


class EventResponse(EventBase):
    """Event response schema"""

    event_id: int = Field(..., description="事件ID")
    symbol: Optional[str] = Field(None, description="关联股票代码")
    stock_name: Optional[str] = Field(None, description="股票名称")
    content: str = Field(..., description="事件内容")
    source_url: Optional[str] = Field(None, description="来源链接")
    impact_level: Optional[int] = Field(None, description="影响等级")
    ai_analysis: Optional[str] = Field(None, description="AI分析")
    is_read: bool = Field(..., description="是否已读")
    created_at: datetime = Field(..., description="创建时间")

    class Config:
        from_attributes = True


class EventListResponse(BaseModel):
    """Event list response"""

    total: int = Field(..., description="总数量")
    unread_count: int = Field(..., description="未读数量")
    events: list[EventResponse] = Field(..., description="事件列表")


class EventStats(BaseModel):
    """Event statistics"""

    total_events: int = Field(..., description="总事件数")
    policy_count: int = Field(..., description="政策事件数")
    company_count: int = Field(..., description="公司事件数")
    market_count: int = Field(..., description="市场事件数")
    industry_count: int = Field(..., description="行业事件数")
    high_impact_count: int = Field(..., description="高影响事件数")
    unread_count: int = Field(..., description="未读事件数")
