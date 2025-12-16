"""
Trade Model
"""

from sqlalchemy import Column, BigInteger, String, NUMERIC, Boolean, TIMESTAMP, Index
from sqlalchemy.sql import func
from app.core.database import Base


class Trade(Base):
    """Trade table - 交易记录表"""

    __tablename__ = "trades"

    trade_id = Column(BigInteger, primary_key=True, autoincrement=True, comment="交易ID")
    user_id = Column(BigInteger, nullable=False, index=True, comment="用户ID")
    account_id = Column(BigInteger, nullable=False, index=True, comment="账户ID")

    symbol = Column(String(20), nullable=False, index=True, comment="股票代码")
    stock_name = Column(String(100), nullable=False, comment="股票名称")

    trade_type = Column(String(20), nullable=False, comment="交易类型: buy/sell")

    quantity = Column(NUMERIC(20, 8), nullable=False, comment="交易数量")
    price = Column(NUMERIC(20, 8), nullable=False, comment="交易价格")
    total_amount = Column(NUMERIC(20, 8), nullable=False, comment="交易金额")

    # 费用
    commission = Column(NUMERIC(20, 8), default=0, comment="手续费")
    stamp_duty = Column(NUMERIC(20, 8), default=0, comment="印花税")
    transfer_fee = Column(NUMERIC(20, 8), default=0, comment="过户费")
    net_amount = Column(NUMERIC(20, 8), nullable=False, comment="净金额")

    trade_date = Column(TIMESTAMP(timezone=True), nullable=False, index=True, comment="交易日期")
    notes = Column(String(500), comment="备注")

    is_deleted = Column(Boolean, default=False, nullable=False, comment="是否删除")

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(
        TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False, comment="更新时间"
    )
    deleted_at = Column(TIMESTAMP(timezone=True), comment="删除时间")

    __table_args__ = (
        Index("idx_trades_user_account", "user_id", "account_id"),
        Index("idx_trades_account_symbol", "account_id", "symbol"),
        Index("idx_trades_trade_date", "trade_date"),
        Index("idx_trades_symbol_date", "symbol", "trade_date"),
    )

    def __repr__(self):
        return (
            f"<Trade(trade_id={self.trade_id}, symbol={self.symbol}, type={self.trade_type}, quantity={self.quantity})>"
        )
