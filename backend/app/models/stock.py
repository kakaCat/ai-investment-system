"""
Stock Model
"""
from sqlalchemy import Column, BigInteger, String, Boolean, TIMESTAMP, Date, Index
from sqlalchemy.sql import func
from app.core.database import Base


class Stock(Base):
    """Stock table - 股票基础信息表"""
    __tablename__ = "stocks"

    stock_id = Column(BigInteger, primary_key=True, autoincrement=True, comment="股票ID")

    symbol = Column(String(20), unique=True, nullable=False, index=True, comment="股票代码")
    name = Column(String(100), nullable=False, comment="股票名称")
    market = Column(String(20), nullable=False, comment="市场类型: A股/港股/美股")

    # 基本信息
    industry = Column(String(100), comment="所属行业")
    sector = Column(String(100), comment="所属板块")
    list_date = Column(Date, comment="上市日期")

    # 搜索字段
    pinyin = Column(String(50), index=True, comment="拼音首字母")

    is_delisted = Column(Boolean, default=False, nullable=False, comment="是否退市")
    is_deleted = Column(Boolean, default=False, nullable=False, comment="是否删除")

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False, comment="更新时间")
    deleted_at = Column(TIMESTAMP(timezone=True), comment="删除时间")

    __table_args__ = (
        Index("idx_stocks_market", "market"),
        Index("idx_stocks_name", "name"),
    )

    def __repr__(self):
        return f"<Stock(symbol={self.symbol}, name={self.name}, market={self.market})>"
