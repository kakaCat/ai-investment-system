"""
Holding Model
"""

from sqlalchemy import Column, BigInteger, String, NUMERIC, Boolean, TIMESTAMP, Index
from sqlalchemy.sql import func
from app.core.database import Base


class Holding(Base):
    """Holding table - 持仓表"""

    __tablename__ = "holdings"

    holding_id = Column(BigInteger, primary_key=True, autoincrement=True, comment="持仓ID")
    user_id = Column(BigInteger, nullable=False, index=True, comment="用户ID")
    account_id = Column(BigInteger, nullable=False, index=True, comment="账户ID")

    symbol = Column(String(20), nullable=False, index=True, comment="股票代码")
    stock_name = Column(String(100), nullable=False, comment="股票名称")

    # 持仓数量
    quantity = Column(NUMERIC(20, 8), default=0, nullable=False, comment="持仓数量")
    available_quantity = Column(NUMERIC(20, 8), default=0, nullable=False, comment="可用数量")

    # 成本和价格
    avg_cost = Column(NUMERIC(20, 8), nullable=False, comment="持仓成本")
    current_price = Column(NUMERIC(20, 8), default=0, comment="当前价格")

    # 市值
    market_value = Column(NUMERIC(20, 8), default=0, comment="市值")

    # 盈亏
    profit = Column(NUMERIC(20, 8), default=0, comment="盈亏金额")
    profit_rate = Column(NUMERIC(10, 4), default=0, comment="盈亏率 (%)")
    today_profit = Column(NUMERIC(20, 8), default=0, comment="今日盈亏")
    today_profit_rate = Column(NUMERIC(10, 4), default=0, comment="今日盈亏率 (%)")

    # 仓位
    position_ratio = Column(NUMERIC(10, 4), default=0, comment="仓位占比 (%)")

    first_buy_date = Column(TIMESTAMP(timezone=True), comment="首次买入日期")
    last_update_time = Column(TIMESTAMP(timezone=True), comment="最后更新时间")

    is_deleted = Column(Boolean, default=False, nullable=False, comment="是否删除")

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(
        TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False, comment="更新时间"
    )
    deleted_at = Column(TIMESTAMP(timezone=True), comment="删除时间")

    __table_args__ = (
        Index("idx_holdings_user_account", "user_id", "account_id"),
        Index("idx_holdings_account_symbol", "account_id", "symbol"),
        Index("idx_holdings_symbol", "symbol"),
    )

    def __repr__(self):
        return f"<Holding(holding_id={self.holding_id}, symbol={self.symbol}, quantity={self.quantity})>"
