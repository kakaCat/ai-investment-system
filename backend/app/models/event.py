"""
Event Model
"""
from sqlalchemy import Column, BigInteger, String, Integer, Boolean, TIMESTAMP, Text, Index
from sqlalchemy.sql import func
from app.core.database import Base


class Event(Base):
    """Event table - 事件表"""
    __tablename__ = "events"

    event_id = Column(BigInteger, primary_key=True, autoincrement=True, comment="事件ID")
    user_id = Column(BigInteger, nullable=False, index=True, comment="用户ID")

    title = Column(String(200), nullable=False, comment="事件标题")
    category = Column(String(50), nullable=False, index=True, comment="事件类别: policy/company/market/industry")
    event_type = Column(String(50), nullable=False, comment="事件类型")

    symbol = Column(String(20), index=True, comment="关联股票代码")
    stock_name = Column(String(100), comment="股票名称")

    content = Column(Text, nullable=False, comment="事件内容")
    source_url = Column(String(500), comment="来源链接")

    event_date = Column(TIMESTAMP(timezone=True), nullable=False, index=True, comment="事件日期")

    # AI分析
    impact_level = Column(Integer, comment="影响等级 1-5")
    ai_analysis = Column(Text, comment="AI分析")

    is_read = Column(Boolean, default=False, nullable=False, comment="是否已读")
    is_deleted = Column(Boolean, default=False, nullable=False, comment="是否删除")

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False, comment="更新时间")
    deleted_at = Column(TIMESTAMP(timezone=True), comment="删除时间")

    __table_args__ = (
        Index("idx_events_user_category", "user_id", "category"),
        Index("idx_events_user_date", "user_id", "event_date"),
        Index("idx_events_symbol", "symbol"),
        Index("idx_events_category_date", "category", "event_date"),
    )

    def __repr__(self):
        return f"<Event(event_id={self.event_id}, title={self.title}, category={self.category})>"
