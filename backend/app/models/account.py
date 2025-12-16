"""
Account Model
"""

from sqlalchemy import Column, BigInteger, String, NUMERIC, Boolean, TIMESTAMP, Index
from sqlalchemy.sql import func
from app.core.database import Base


class Account(Base):
    """Account table - 账户表"""

    __tablename__ = "accounts"

    account_id = Column(BigInteger, primary_key=True, autoincrement=True, comment="账户ID")
    user_id = Column(BigInteger, nullable=False, index=True, comment="用户ID")

    account_name = Column(String(100), nullable=False, comment="账户名称")
    account_number = Column(String(50), nullable=True, comment="账户号码")
    market = Column(String(20), nullable=False, comment="市场类型: A股/港股/美股")
    broker = Column(String(100), nullable=True, comment="券商名称")

    # 资金字段
    total_value = Column(NUMERIC(20, 8), default=0, nullable=False, comment="总资产")
    available_cash = Column(NUMERIC(20, 8), default=0, nullable=False, comment="可用资金")
    invested_value = Column(NUMERIC(20, 8), default=0, nullable=False, comment="持仓市值")

    # 盈亏字段
    today_profit = Column(NUMERIC(20, 8), default=0, comment="今日盈亏")
    today_profit_rate = Column(NUMERIC(10, 4), default=0, comment="今日盈亏率 (%)")
    total_profit = Column(NUMERIC(20, 8), default=0, comment="累计盈亏")
    total_profit_rate = Column(NUMERIC(10, 4), default=0, comment="累计盈亏率 (%)")

    status = Column(String(20), default="active", nullable=False, comment="账户状态: active/inactive/closed")

    is_deleted = Column(Boolean, default=False, nullable=False, comment="是否删除")

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(
        TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False, comment="更新时间"
    )
    deleted_at = Column(TIMESTAMP(timezone=True), comment="删除时间")

    __table_args__ = (
        Index("idx_accounts_user_market", "user_id", "market"),
        Index("idx_accounts_user_status", "user_id", "status"),
    )

    def __repr__(self):
        return f"<Account(account_id={self.account_id}, account_name={self.account_name}, market={self.market})>"
