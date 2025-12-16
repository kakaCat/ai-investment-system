"""
Review Model (v3.2)
"""

from sqlalchemy import Column, BigInteger, String, Integer, NUMERIC, Boolean, TIMESTAMP, Text, Index
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.sql import func
from app.core.database import Base


class Review(Base):
    """Review table - 用户股票评价表 (v3.2)"""

    __tablename__ = "user_stock_reviews"

    review_id = Column(BigInteger, primary_key=True, autoincrement=True, comment="评价ID")
    user_id = Column(BigInteger, nullable=False, index=True, comment="用户ID")

    symbol = Column(String(20), nullable=False, index=True, comment="股票代码")
    stock_name = Column(String(100), comment="股票名称")

    rating = Column(Integer, nullable=False, comment="评分 1-5星")

    # 使用PostgreSQL ARRAY类型存储列表
    bullish_reasons = Column(ARRAY(Text), default=list, comment="看好原因列表")
    bearish_reasons = Column(ARRAY(Text), default=list, comment="风险原因列表")

    holding_logic = Column(Text, comment="持有逻辑")

    target_price = Column(NUMERIC(20, 8), comment="目标价")
    stop_loss_price = Column(NUMERIC(20, 8), comment="止损价")

    is_deleted = Column(Boolean, default=False, nullable=False, comment="是否删除")

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(
        TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False, comment="更新时间"
    )
    deleted_at = Column(TIMESTAMP(timezone=True), comment="删除时间")

    __table_args__ = (
        Index("idx_reviews_user_symbol", "user_id", "symbol", unique=True),
        Index("idx_reviews_rating", "rating"),
    )

    def __repr__(self):
        return f"<Review(review_id={self.review_id}, symbol={self.symbol}, rating={self.rating})>"
