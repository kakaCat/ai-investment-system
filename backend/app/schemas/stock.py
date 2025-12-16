"""
Stock Schemas
"""

from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal
from datetime import datetime


class StockBase(BaseModel):
    """Base stock schema"""

    symbol: str = Field(..., max_length=20, description="股票代码")
    name: str = Field(..., max_length=100, description="股票名称")
    market: str = Field(..., description="市场类型: A股/港股/美股")


class StockQuote(StockBase):
    """Stock quote schema"""

    current_price: Decimal = Field(..., description="当前价格")
    change_amount: Decimal = Field(..., description="涨跌额")
    change_rate: Decimal = Field(..., description="涨跌幅 (%)")
    open_price: Optional[Decimal] = Field(None, description="开盘价")
    high_price: Optional[Decimal] = Field(None, description="最高价")
    low_price: Optional[Decimal] = Field(None, description="最低价")
    prev_close: Optional[Decimal] = Field(None, description="昨收价")
    volume: Optional[Decimal] = Field(None, description="成交量")
    turnover: Optional[Decimal] = Field(None, description="成交额")
    amplitude: Optional[Decimal] = Field(None, description="振幅 (%)")
    turnover_rate: Optional[Decimal] = Field(None, description="换手率 (%)")
    pe_ratio: Optional[Decimal] = Field(None, description="市盈率")
    pb_ratio: Optional[Decimal] = Field(None, description="市净率")
    market_cap: Optional[Decimal] = Field(None, description="总市值")
    circulating_market_cap: Optional[Decimal] = Field(None, description="流通市值")
    quote_time: datetime = Field(..., description="行情时间")


class StockInfo(StockBase):
    """Stock basic information"""

    stock_id: int = Field(..., description="股票ID")
    industry: Optional[str] = Field(None, description="所属行业")
    sector: Optional[str] = Field(None, description="所属板块")
    list_date: Optional[datetime] = Field(None, description="上市日期")
    is_delisted: bool = Field(default=False, description="是否退市")

    class Config:
        from_attributes = True


class StockSearch(BaseModel):
    """Stock search result"""

    symbol: str = Field(..., description="股票代码")
    name: str = Field(..., description="股票名称")
    market: str = Field(..., description="市场类型")
    pinyin: Optional[str] = Field(None, description="拼音首字母")


class StockSearchResponse(BaseModel):
    """Stock search response"""

    total: int = Field(..., description="总数量")
    stocks: list[StockSearch] = Field(..., description="股票列表")


class StockHistoryPrice(BaseModel):
    """Stock historical price"""

    trade_date: datetime = Field(..., description="交易日期")
    open_price: Decimal = Field(..., description="开盘价")
    high_price: Decimal = Field(..., description="最高价")
    low_price: Decimal = Field(..., description="最低价")
    close_price: Decimal = Field(..., description="收盘价")
    volume: Decimal = Field(..., description="成交量")
    turnover: Decimal = Field(..., description="成交额")
    change_rate: Decimal = Field(..., description="涨跌幅 (%)")
