"""
Strategy Model - 操作策略模型
"""

from sqlalchemy import Column, BigInteger, String, NUMERIC, Boolean, TIMESTAMP, Index, Text
from sqlalchemy.sql import func
from app.core.database import Base


class Strategy(Base):
    """Strategy table - 操作策略表"""

    __tablename__ = "strategies"

    strategy_id = Column(BigInteger, primary_key=True, autoincrement=True, comment="策略ID")
    user_id = Column(BigInteger, nullable=False, index=True, comment="用户ID")

    symbol = Column(String(20), nullable=False, index=True, comment="股票代码")
    stock_name = Column(String(100), nullable=False, comment="股票名称")

    strategy_type = Column(String(20), nullable=False, comment="策略类型: buy/sell/hold")
    trigger_price = Column(NUMERIC(20, 8), comment="触发价格")
    target_quantity = Column(NUMERIC(20, 8), comment="目标数量")

    reason = Column(Text, comment="策略原因/理由")
    notes = Column(String(500), comment="备注")

    # 策略状态
    status = Column(String(20), default="pending", nullable=False, comment="状态: pending/completed/cancelled")
    priority = Column(String(20), default="normal", comment="优先级: urgent/high/normal/low")

    # 止损止盈标记
    is_stop_loss = Column(Boolean, default=False, comment="是否止损策略")
    is_take_profit = Column(Boolean, default=False, comment="是否止盈策略")

    # 执行信息
    executed_at = Column(TIMESTAMP(timezone=True), comment="执行时间")
    executed_price = Column(NUMERIC(20, 8), comment="实际执行价格")
    executed_quantity = Column(NUMERIC(20, 8), comment="实际执行数量")

    is_deleted = Column(Boolean, default=False, nullable=False, comment="是否删除")

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(
        TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False, comment="更新时间"
    )
    deleted_at = Column(TIMESTAMP(timezone=True), comment="删除时间")

    __table_args__ = (
        Index("idx_strategies_user_id", "user_id"),
        Index("idx_strategies_symbol", "symbol"),
        Index("idx_strategies_status", "status"),
        Index("idx_strategies_user_symbol", "user_id", "symbol"),
    )

    def __repr__(self):
        return f"<Strategy(strategy_id={self.strategy_id}, symbol={self.symbol}, type={self.strategy_type}, status={self.status})>"
