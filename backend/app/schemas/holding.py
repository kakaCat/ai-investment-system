"""
Holding Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal
from datetime import datetime


class HoldingBase(BaseModel):
    """Base holding schema"""
    symbol: str = Field(..., max_length=20, description="股票代码")
    stock_name: str = Field(..., max_length=100, description="股票名称")


class HoldingResponse(HoldingBase):
    """Holding response schema"""
    holding_id: int = Field(..., description="持仓ID")
    account_id: int = Field(..., description="账户ID")
    quantity: Decimal = Field(..., description="持仓数量")
    available_quantity: Decimal = Field(..., description="可用数量")
    avg_cost: Decimal = Field(..., description="持仓成本")
    current_price: Decimal = Field(..., description="当前价格")
    market_value: Decimal = Field(..., description="市值")
    profit: Decimal = Field(..., description="盈亏金额")
    profit_rate: Decimal = Field(..., description="盈亏率 (%)")
    today_profit: Decimal = Field(..., description="今日盈亏")
    today_profit_rate: Decimal = Field(..., description="今日盈亏率 (%)")
    position_ratio: Decimal = Field(..., description="仓位占比 (%)")
    first_buy_date: Optional[datetime] = Field(None, description="首次买入日期")
    last_update_time: datetime = Field(..., description="最后更新时间")

    class Config:
        from_attributes = True


class HoldingListResponse(BaseModel):
    """Holding list response"""
    total: int = Field(..., description="总数量")
    total_market_value: Decimal = Field(..., description="总市值")
    total_profit: Decimal = Field(..., description="总盈亏")
    total_profit_rate: Decimal = Field(..., description="总盈亏率 (%)")
    holdings: list[HoldingResponse] = Field(..., description="持仓列表")


class HoldingStats(BaseModel):
    """Holding statistics"""
    total_stocks: int = Field(..., description="持仓股票数")
    total_market_value: Decimal = Field(..., description="总市值")
    today_profit: Decimal = Field(..., description="今日盈亏")
    total_profit: Decimal = Field(..., description="累计盈亏")
    max_profit_stock: Optional[str] = Field(None, description="最赚股票")
    max_loss_stock: Optional[str] = Field(None, description="最亏股票")
