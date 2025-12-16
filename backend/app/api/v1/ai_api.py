"""
AI API - POST-only架构

AI分析、对话、复盘相关API - 使用POST-only + Service + Converter + Builder模式
"""

from typing import Optional, List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.common import Response
from app.services.ai import (
    DailyAnalysisService,
    SingleAnalysisService,
    DailyReviewService,
    AIChatService,
)


router = APIRouter(prefix="/ai", tags=["AI分析"])


# ========================================
# Request Schemas
# ========================================


class DailyAnalysisRequest(BaseModel):
    """批量分析请求"""

    stock_symbols: List[str] = Field(..., description="股票代码列表")


class DailyAnalysisResultRequest(BaseModel):
    """批量分析结果查询请求"""

    task_id: str = Field(..., description="任务ID")


class SingleAnalysisRequest(BaseModel):
    """单股分析请求"""

    symbol: str = Field(..., description="股票代码")
    analysis_type: str = Field("comprehensive", description="分析类型")
    include_fundamentals: bool = Field(True, description="包含基本面分析")
    include_technicals: bool = Field(True, description="包含技术面分析")
    include_valuation: bool = Field(True, description="包含估值分析")


class AISuggestionsRequest(BaseModel):
    """AI建议查询请求"""

    priority: Optional[str] = Field(None, description="优先级筛选：urgent/medium/low")
    action: Optional[str] = Field(None, description="操作类型筛选：buy/sell/hold/observe")
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)


class DailyReviewGenerateRequest(BaseModel):
    """生成复盘请求"""

    date: Optional[str] = Field(None, description="复盘日期 YYYY-MM-DD")


class DailyReviewGetRequest(BaseModel):
    """获取复盘请求"""

    date: Optional[str] = Field(None, description="复盘日期 YYYY-MM-DD，默认最新")


class ChatSessionRequest(BaseModel):
    """创建对话会话请求"""

    context_symbol: Optional[str] = Field(None, description="上下文股票代码")
    context_type: Optional[str] = Field(None, description="上下文类型")


class ChatMessageRequest(BaseModel):
    """发送消息请求"""

    session_id: str = Field(..., description="会话ID")
    message: str = Field(..., description="消息内容")


class ChatHistoryRequest(BaseModel):
    """获取对话历史请求"""

    session_id: str = Field(..., description="会话ID")
    limit: int = Field(50, ge=1, le=200)


class ChatDeleteRequest(BaseModel):
    """删除会话请求"""

    session_id: str = Field(..., description="会话ID")


# ========================================
# API Endpoints - Daily Analysis (批量分析)
# ========================================


@router.post("/daily-analysis/create")
async def create_daily_analysis(
    request: DailyAnalysisRequest, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """
    创建每日批量分析任务

    ========================================
    接口信息
    ========================================
    接口路径: POST /api/v1/ai/daily-analysis/create
    对应页面: pages/ai/daily-analysis.vue - AI批量分析页
    接口功能: 创建AI批量分析任务，异步处理多只股票的分析

    ========================================
    请求参数
    ========================================
    {
        "stock_symbols": ["600600", "000858", "600519"]  // 股票代码列表
    }

    ========================================
    响应数据
    ========================================
    {
        "task_id": "uuid-string",           // 任务ID
        "status": "pending",                 // 任务状态
        "total_stocks": 3,                   // 股票总数
        "processed_stocks": 0,               // 已处理数量
        "estimated_tokens": 4500,            // 预估token消耗
        "estimated_time_seconds": 9,         // 预估耗时（秒）
        "created_at": "2025-11-18T10:00:00Z"
    }

    ========================================
    执行流程（时序）
    ========================================
    1. 接收请求，提取用户ID和股票列表
    2. 调用Service生成任务ID和任务信息
    3. （TODO）创建Celery异步任务
    4. 返回任务信息供前端轮询

    ========================================
    业务规则
    ========================================
    1. 股票代码列表不能为空
    2. 单次最多支持100只股票
    3. 任务状态：pending/processing/completed/failed
    4. 预估每只股票消耗1500 tokens，耗时3秒

    ========================================
    错误码
    ========================================
    1001: 股票列表为空
    1002: 超出最大股票数量限制

    ========================================
    前端调用示例
    ========================================
    const result = await post('/ai/daily-analysis/create', {
        stock_symbols: ['600600', '000858']
    })

    ========================================
    修改记录
    ========================================
    2025-11-18: 初始版本 - 重构为POST-only架构
    """
    service = DailyAnalysisService()
    result = await service.create_task(db=db, user_id=current_user.user_id, stock_symbols=request.stock_symbols)
    return Response.success(data=result)


@router.post("/daily-analysis/results")
async def get_daily_analysis_results(
    request: DailyAnalysisResultRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    获取批量分析结果

    ========================================
    接口信息
    ========================================
    接口路径: POST /api/v1/ai/daily-analysis/results
    对应页面: pages/ai/daily-analysis.vue - 结果展示区域
    接口功能: 根据任务ID获取AI批量分析的结果

    ========================================
    请求参数
    ========================================
    {
        "task_id": "uuid-string"  // 任务ID（由create接口返回）
    }

    ========================================
    响应数据
    ========================================
    {
        "task_id": "uuid-string",
        "status": "completed",
        "total_count": 10,
        "results": [
            {
                "decision_id": 1,
                "symbol": "600600",
                "stock_name": "青岛啤酒",
                "ai_score": {
                    "fundamental_score": 75,
                    "technical_score": 68,
                    "valuation_score": 82,
                    "overall_score": 75
                },
                "ai_suggestion": "建议持有",
                "confidence_level": 78.5,
                "created_at": "2025-11-18T10:05:00Z"
            }
        ],
        "total_tokens_used": 12000,
        "completed_at": "2025-11-18T10:05:30Z"
    }

    ========================================
    执行流程（时序）
    ========================================
    1. 接收task_id
    2. Service查询任务状态（TODO: 从Redis）
    3. 从数据库获取AI决策记录
    4. Converter转换数据格式
    5. Builder构建响应

    ========================================
    业务规则
    ========================================
    1. 只能查询本用户的任务结果
    2. 任务状态为completed时返回完整结果
    3. 任务状态为processing时返回进度信息

    ========================================
    前端调用示例
    ========================================
    const results = await post('/ai/daily-analysis/results', {
        task_id: 'task-uuid-123'
    })
    """
    service = DailyAnalysisService()
    result = await service.get_results(db=db, user_id=current_user.user_id, task_id=request.task_id)
    return Response.success(data=result)


# ========================================
# API Endpoints - Single Analysis (单股分析)
# ========================================


@router.post("/single-analysis")
async def analyze_single_stock(
    request: SingleAnalysisRequest, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """
    单股AI深度分析

    ========================================
    接口信息
    ========================================
    接口路径: POST /api/v1/ai/single-analysis
    对应页面: pages/stock/detail.vue - 股票详情页AI分析tab
    接口功能: 对单只股票进行全面AI分析（基本面+技术面+估值）

    ========================================
    请求参数
    ========================================
    {
        "symbol": "600600",                   // 股票代码
        "analysis_type": "comprehensive",     // 分析类型（comprehensive/quick）
        "include_fundamentals": true,         // 包含基本面分析
        "include_technicals": true,           // 包含技术面分析
        "include_valuation": true             // 包含估值分析
    }

    ========================================
    响应数据
    ========================================
    {
        "decision_id": 1,
        "symbol": "600600",
        "stock_name": "青岛啤酒",
        "ai_score": {...},                    // AI评分（各维度）
        "ai_suggestion": "建议持有",          // 投资建议
        "ai_strategy": {...},                 // 具体策略（目标价、仓位等）
        "ai_reasons": [...],                  // 分析理由列表
        "confidence_level": 78.5,             // 置信度
        "created_at": "2025-11-18T10:00:00Z"
    }

    ========================================
    执行流程（时序）
    ========================================
    1. 接收股票代码和分析选项
    2. Service查询股票基本信息
    3. （TODO）调用DeepSeek API进行分析
    4. Converter生成分析结果
    5. Repository保存AI决策到数据库
    6. Builder构建响应

    ========================================
    业务规则
    ========================================
    1. 每只股票的分析结果保存到ai_decisions表
    2. analysis_type为single
    3. 包含完整的评分、建议、策略信息

    ========================================
    前端调用示例
    ========================================
    const analysis = await post('/ai/single-analysis', {
        symbol: '600600',
        analysis_type: 'comprehensive'
    })
    """
    service = SingleAnalysisService()
    result = await service.analyze_stock(
        db=db,
        user_id=current_user.user_id,
        symbol=request.symbol,
        analysis_type=request.analysis_type,
        include_fundamentals=request.include_fundamentals,
        include_technicals=request.include_technicals,
        include_valuation=request.include_valuation,
    )
    return Response.success(data=result)


@router.post("/suggestions")
async def get_ai_suggestions(
    request: AISuggestionsRequest, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """
    获取AI投资建议列表

    ========================================
    接口信息
    ========================================
    接口路径: POST /api/v1/ai/suggestions
    对应页面: pages/ai/suggestions.vue - AI建议页
    接口功能: 获取AI生成的投资操作建议，支持优先级和操作类型筛选

    ========================================
    请求参数
    ========================================
    {
        "priority": "urgent",        // 优先级筛选（可选）: urgent/medium/low
        "action": "buy",             // 操作类型筛选（可选）: buy/sell/hold/observe
        "page": 1,
        "page_size": 20
    }

    ========================================
    响应数据
    ========================================
    {
        "total": 15,
        "page": 1,
        "page_size": 20,
        "suggestions": [
            {
                "decision_id": 1,
                "symbol": "600600",
                "stock_name": "青岛啤酒",
                "action": "buy",
                "priority": "urgent",
                "suggestion": "建议买入",
                "confidence_level": 85.0,
                "created_at": "2025-11-18T10:00:00Z"
            }
        ]
    }

    ========================================
    执行流程（时序）
    ========================================
    1. 接收筛选条件
    2. Service查询AI决策记录
    3. Converter过滤和转换数据（提取action和priority）
    4. Builder构建分页响应

    ========================================
    业务规则
    ========================================
    1. priority从confidence_level提取（>=80: urgent, >=60: medium, <60: low）
    2. action从ai_suggestion文本提取（买入/卖出/持有）
    3. 按创建时间倒序排列

    ========================================
    前端调用示例
    ========================================
    const suggestions = await post('/ai/suggestions', {
        priority: 'urgent',
        page: 1
    })
    """
    service = SingleAnalysisService()
    result = await service.get_ai_suggestions(
        db=db,
        user_id=current_user.user_id,
        priority=request.priority,
        action=request.action,
        page=request.page,
        page_size=request.page_size,
    )
    return Response.success(data=result)


# ========================================
# API Endpoints - Daily Review (每日复盘)
# ========================================


@router.post("/review/stocks")
async def get_analyzable_stocks(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """
    获取可分析股票列表

    ========================================
    接口信息
    ========================================
    接口路径: POST /api/v1/ai/review/stocks
    对应页面: pages/ai/daily-review.vue - 股票选择区域
    接口功能: 获取用户的持仓股票和自选股票列表

    ========================================
    请求参数
    ========================================
    无

    ========================================
    响应数据
    ========================================
    {
        "holdings": [...],      // 持仓股票
        "watchlist": [...],     // 自选股票
        "total": 10
    }

    ========================================
    前端调用示例
    ========================================
    const stocks = await post('/ai/review/stocks', {})
    """
    service = DailyReviewService()
    result = await service.get_analyzable_stocks(db, current_user.user_id)
    return Response.success(data=result)


@router.post("/review/generate")
async def generate_daily_review(
    request: DailyReviewGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """生成每日复盘报告"""
    service = DailyReviewService()
    result = await service.generate_review(db, current_user.user_id, request.date)
    return Response.success(data=result, message="复盘报告生成中")


@router.post("/review/get")
async def get_daily_review(
    request: DailyReviewGetRequest, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """获取每日复盘报告"""
    service = DailyReviewService()
    result = await service.get_review(db, current_user.user_id, request.date)
    return Response.success(data=result)


# ========================================
# API Endpoints - AI Chat (AI对话)
# ========================================


# 简化版本Request Schema
class SimpleChatRequest(BaseModel):
    """简化AI对话请求（无会话管理）"""

    message: str = Field(..., description="用户消息")
    context: Optional[List[dict]] = Field(default=[], description="对话上下文")
    symbol: Optional[str] = Field(None, description="股票代码")
    stock_name: Optional[str] = Field(None, description="股票名称")


@router.post("/chat")
async def simple_chat(
    request: SimpleChatRequest, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """
    简化AI对话（无会话管理）

    ========================================
    接口信息
    ========================================
    接口路径: POST /api/v1/ai/chat
    对应页面: components/AIChat.vue
    接口功能: 直接与AI对话，支持上下文和股票信息

    ========================================
    请求参数
    ========================================
    {
        "message": "什么是价值投资？",
        "context": [
            {"role": "user", "content": "..."},
            {"role": "assistant", "content": "..."}
        ],
        "symbol": "600519",        // 可选
        "stock_name": "贵州茅台"    // 可选
    }

    ========================================
    响应数据
    ========================================
    {
        "reply": "价值投资是...",
        "created_at": "2025-11-20T10:00:00Z"
    }
    """
    from app.utils.ai_client import ai_client
    from datetime import datetime

    # 构建消息列表
    messages = []

    # 添加系统提示
    system_prompt = (
        "你是一位专业的投资分析师助手，擅长分析股票、解读市场数据，并提供投资建议。请用专业但易懂的语言回答问题。"
    )
    if request.symbol and request.stock_name:
        system_prompt += f"\n\n当前讨论的股票是：{request.stock_name}（{request.symbol}）"

    messages.append({"role": "system", "content": system_prompt})

    # 添加上下文
    if request.context:
        for msg in request.context:
            messages.append({"role": msg.get("role", "user"), "content": msg.get("content", "")})

    # 添加当前消息
    messages.append({"role": "user", "content": request.message})

    # 调用AI
    reply = await ai_client.chat_completion(messages)

    return Response.success(data={"reply": reply, "created_at": datetime.utcnow().isoformat() + "Z"})


@router.post("/chat/session/create")
async def create_chat_session(
    request: ChatSessionRequest, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """创建AI对话会话"""
    service = AIChatService()
    result = await service.create_session(db, current_user.user_id, request.context_symbol, request.context_type)
    return Response.success(data=result, message="会话创建成功")


@router.post("/chat/message/send")
async def send_chat_message(
    request: ChatMessageRequest, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """发送消息并获取AI回复"""
    service = AIChatService()
    result = await service.send_message(db, current_user.user_id, request.session_id, request.message)
    return Response.success(data=result)


@router.post("/chat/history")
async def get_chat_history(
    request: ChatHistoryRequest, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """获取对话历史"""
    service = AIChatService()
    result = await service.get_history(db, current_user.user_id, request.session_id, request.limit)
    return Response.success(data=result)


@router.post("/chat/session/delete")
async def delete_chat_session(
    request: ChatDeleteRequest, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """删除对话会话"""
    service = AIChatService()
    result = await service.delete_session(db, current_user.user_id, request.session_id)
    return Response.success(data=result)
