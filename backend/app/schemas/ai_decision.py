"""
AI Decision Schemas (v3.2)
"""
from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal
from datetime import datetime


class AIScoreDetail(BaseModel):
    """AI score detail"""
    fundamental_score: int = Field(..., ge=0, le=100, description="基本面得分")
    technical_score: int = Field(..., ge=0, le=100, description="技术面得分")
    valuation_score: int = Field(..., ge=0, le=100, description="估值得分")
    overall_score: int = Field(..., ge=0, le=100, description="综合得分")


class AIStrategyDetail(BaseModel):
    """AI strategy detail"""
    target_price: Optional[Decimal] = Field(None, description="目标价")
    recommended_position: Optional[Decimal] = Field(None, description="建议仓位 (%)")
    risk_level: Optional[str] = Field(None, description="风险等级: low/medium/high")
    holding_period: Optional[str] = Field(None, description="持有周期")
    stop_loss_price: Optional[Decimal] = Field(None, description="止损价")


class AIDecisionBase(BaseModel):
    """Base AI decision schema"""
    symbol: str = Field(..., max_length=20, description="股票代码")
    analysis_type: str = Field(..., description="分析类型: daily/single/portfolio")


class AIDecisionCreate(AIDecisionBase):
    """AI decision creation schema"""
    user_id: int = Field(..., description="用户ID")
    ai_score: AIScoreDetail = Field(..., description="AI评分")
    ai_suggestion: str = Field(..., description="AI建议")
    ai_strategy: Optional[AIStrategyDetail] = Field(None, description="AI策略")
    ai_reasons: list[str] = Field(default_factory=list, description="AI理由列表")
    confidence_level: Optional[Decimal] = Field(None, ge=0, le=100, description="置信度")


class AIDecisionResponse(AIDecisionBase):
    """AI decision response schema"""
    decision_id: int = Field(..., description="决策ID")
    user_id: int = Field(..., description="用户ID")
    stock_name: Optional[str] = Field(None, description="股票名称")
    ai_score: AIScoreDetail = Field(..., description="AI评分")
    ai_suggestion: str = Field(..., description="AI建议")
    ai_strategy: Optional[AIStrategyDetail] = Field(None, description="AI策略")
    ai_reasons: list[str] = Field(..., description="AI理由列表")
    confidence_level: Optional[Decimal] = Field(None, description="置信度")
    created_at: datetime = Field(..., description="创建时间")

    class Config:
        from_attributes = True


class DailyAnalysisRequest(BaseModel):
    """Daily analysis request"""
    user_id: int = Field(..., description="用户ID")
    stock_symbols: list[str] = Field(..., min_length=1, description="股票代码列表")
    include_holdings: bool = Field(default=True, description="包含持仓股票")
    include_watchlist: bool = Field(default=False, description="包含自选股票")


class DailyAnalysisTask(BaseModel):
    """Daily analysis task response"""
    task_id: str = Field(..., description="任务ID")
    status: str = Field(..., description="任务状态: pending/processing/completed/failed")
    total_stocks: int = Field(..., description="总股票数")
    processed_stocks: int = Field(..., description="已处理股票数")
    estimated_tokens: int = Field(..., description="预估消耗Token数")
    created_at: datetime = Field(..., description="创建时间")


class DailyAnalysisResult(BaseModel):
    """Daily analysis result"""
    task_id: str = Field(..., description="任务ID")
    status: str = Field(..., description="任务状态")
    results: list[AIDecisionResponse] = Field(..., description="分析结果列表")
    total_tokens_used: int = Field(..., description="实际消耗Token数")
    completed_at: Optional[datetime] = Field(None, description="完成时间")


class AIConversationMessage(BaseModel):
    """AI conversation message"""
    role: str = Field(..., description="角色: user/assistant/system")
    content: str = Field(..., description="消息内容")
    timestamp: datetime = Field(..., description="时间戳")


class AIConversationRequest(BaseModel):
    """AI conversation request"""
    user_id: int = Field(..., description="用户ID")
    message: str = Field(..., min_length=1, max_length=2000, description="用户消息")
    context_symbol: Optional[str] = Field(None, description="上下文股票代码")
    conversation_id: Optional[int] = Field(None, description="会话ID (继续对话)")


class AIConversationResponse(BaseModel):
    """AI conversation response"""
    conversation_id: int = Field(..., description="会话ID")
    message: AIConversationMessage = Field(..., description="AI回复消息")
    is_streaming: bool = Field(default=False, description="是否流式返回")
