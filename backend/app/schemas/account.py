"""
Account Schemas
"""

from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal


class AccountBase(BaseModel):
    """Base account schema"""

    account_name: str = Field(..., max_length=100, description="账户名称")
    account_number: str = Field(..., max_length=50, description="账户号码")
    market: str = Field(..., description="市场类型: A股/港股/美股")
    broker: str = Field(..., max_length=100, description="券商名称")


class AccountCreate(AccountBase):
    """Account creation schema"""

    user_id: int = Field(..., description="用户ID")
    initial_cash: Decimal = Field(default=Decimal("0"), description="初始资金")


class AccountUpdate(BaseModel):
    """Account update schema"""

    account_name: Optional[str] = Field(None, max_length=100)
    status: Optional[str] = Field(None, description="账户状态")


class AccountResponse(AccountBase):
    """Account response schema"""

    account_id: int = Field(..., description="账户ID")
    total_value: Decimal = Field(..., description="总资产")
    available_cash: Decimal = Field(..., description="可用资金")
    invested_value: Decimal = Field(..., description="持仓市值")
    today_profit: Decimal = Field(..., description="今日盈亏")
    today_profit_rate: Decimal = Field(..., description="今日盈亏率 (%)")
    total_profit: Decimal = Field(..., description="累计盈亏")
    total_profit_rate: Decimal = Field(..., description="累计盈亏率 (%)")
    status: str = Field(..., description="账户状态")

    class Config:
        from_attributes = True


class AccountListResponse(BaseModel):
    """Account list response"""

    total: int = Field(..., description="总数量")
    accounts: list[AccountResponse] = Field(..., description="账户列表")
