"""
Trade Schemas
"""

from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal
from datetime import datetime


class TradeBase(BaseModel):
    """Base trade schema"""

    symbol: str = Field(..., max_length=20, description="股票代码")
    stock_name: str = Field(..., max_length=100, description="股票名称")
    trade_type: str = Field(..., description="交易类型: buy/sell")
    quantity: Decimal = Field(..., gt=0, description="交易数量")
    price: Decimal = Field(..., gt=0, description="交易价格")
    trade_date: datetime = Field(..., description="交易日期")


class TradeCreate(TradeBase):
    """Trade creation schema"""

    account_id: int = Field(..., description="账户ID")
    commission: Optional[Decimal] = Field(Decimal("0"), description="手续费")
    stamp_duty: Optional[Decimal] = Field(Decimal("0"), description="印花税")
    transfer_fee: Optional[Decimal] = Field(Decimal("0"), description="过户费")
    notes: Optional[str] = Field(None, max_length=500, description="备注")


class TradeUpdate(BaseModel):
    """Trade update schema"""

    price: Optional[Decimal] = Field(None, gt=0)
    quantity: Optional[Decimal] = Field(None, gt=0)
    notes: Optional[str] = Field(None, max_length=500)


class TradeResponse(TradeBase):
    """Trade response schema"""

    trade_id: int = Field(..., description="交易ID")
    account_id: int = Field(..., description="账户ID")
    total_amount: Decimal = Field(..., description="交易金额")
    commission: Decimal = Field(..., description="手续费")
    stamp_duty: Decimal = Field(..., description="印花税")
    transfer_fee: Decimal = Field(..., description="过户费")
    net_amount: Decimal = Field(..., description="净金额")
    notes: Optional[str] = Field(None, description="备注")
    created_at: datetime = Field(..., description="创建时间")

    class Config:
        from_attributes = True


class TradeListResponse(BaseModel):
    """Trade list response"""

    total: int = Field(..., description="总数量")
    trades: list[TradeResponse] = Field(..., description="交易列表")


class TradeStats(BaseModel):
    """Trade statistics"""

    total_trades: int = Field(..., description="总交易次数")
    buy_count: int = Field(..., description="买入次数")
    sell_count: int = Field(..., description="卖出次数")
    total_buy_amount: Decimal = Field(..., description="总买入金额")
    total_sell_amount: Decimal = Field(..., description="总卖出金额")
    total_commission: Decimal = Field(..., description="总手续费")
    avg_buy_price: Optional[Decimal] = Field(None, description="平均买入价")
    avg_sell_price: Optional[Decimal] = Field(None, description="平均卖出价")
