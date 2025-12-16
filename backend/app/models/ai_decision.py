"""
AI Decision Model (v3.2)
"""

from sqlalchemy import Column, BigInteger, String, Integer, NUMERIC, Boolean, TIMESTAMP, Text, Index, JSON
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.sql import func
from app.core.database import Base


class AIDecision(Base):
    """AI Decision table - AI决策记录表 (v3.2)"""

    __tablename__ = "ai_decisions"

    decision_id = Column(BigInteger, primary_key=True, autoincrement=True, comment="决策ID")
    user_id = Column(BigInteger, nullable=False, index=True, comment="用户ID")

    symbol = Column(String(20), nullable=False, index=True, comment="股票代码")
    stock_name = Column(String(100), comment="股票名称")

    analysis_type = Column(String(50), nullable=False, comment="分析类型: daily/single/portfolio")

    # AI评分 (存储为JSON)
    ai_score = Column(JSON, comment="AI评分详情 {fundamental_score, technical_score, valuation_score, overall_score}")

    ai_suggestion = Column(Text, nullable=False, comment="AI建议")

    # AI策略 (存储为JSON)
    ai_strategy = Column(
        JSON, comment="AI策略 {target_price, recommended_position, risk_level, holding_period, stop_loss_price}"
    )

    # AI理由列表
    ai_reasons = Column(ARRAY(Text), default=list, comment="AI理由列表")

    confidence_level = Column(NUMERIC(10, 4), comment="置信度 (0-100)")

    is_deleted = Column(Boolean, default=False, nullable=False, comment="是否删除")

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(
        TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False, comment="更新时间"
    )
    deleted_at = Column(TIMESTAMP(timezone=True), comment="删除时间")

    __table_args__ = (
        Index("idx_ai_decisions_user_symbol", "user_id", "symbol"),
        Index("idx_ai_decisions_analysis_type", "analysis_type"),
        Index("idx_ai_decisions_created_date", "created_at"),
    )

    def __repr__(self):
        return f"<AIDecision(decision_id={self.decision_id}, symbol={self.symbol}, type={self.analysis_type})>"


class AIConversation(Base):
    """AI Conversation table - AI对话记录表 (v3.2)"""

    __tablename__ = "ai_conversations"

    conversation_id = Column(BigInteger, primary_key=True, autoincrement=True, comment="会话ID")
    user_id = Column(BigInteger, nullable=False, index=True, comment="用户ID")

    context_symbol = Column(String(20), comment="上下文股票代码")
    context_type = Column(String(50), comment="上下文类型")

    # 对话消息 (存储为JSON数组)
    messages = Column(JSON, nullable=False, comment="消息列表 [{role, content, timestamp}]")

    total_tokens = Column(Integer, default=0, comment="消耗Token总数")

    is_deleted = Column(Boolean, default=False, nullable=False, comment="是否删除")

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(
        TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False, comment="更新时间"
    )
    deleted_at = Column(TIMESTAMP(timezone=True), comment="删除时间")

    __table_args__ = (
        Index("idx_ai_conversations_user", "user_id"),
        Index("idx_ai_conversations_context_symbol", "context_symbol"),
    )

    def __repr__(self):
        return f"<AIConversation(conversation_id={self.conversation_id}, user_id={self.user_id})>"
