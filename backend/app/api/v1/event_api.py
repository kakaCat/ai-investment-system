"""
Event API - POST-only架构

事件管理API - 使用POST-only + Service + Converter + Builder模式
"""

from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.common import Response
from app.services.event import (
    EventQueryService,
    EventDetailService,
    EventCreateService,
    EventUpdateService,
    EventMarkReadService,
)


router = APIRouter(prefix="/event", tags=["事件管理"])


# ========================================
# Request Schemas
# ========================================

class EventQueryRequest(BaseModel):
    """事件查询请求"""
    symbol: Optional[str] = Field(None, description="股票代码筛选")
    category: Optional[str] = Field(None, description="事件类别筛选")
    is_read: Optional[bool] = Field(None, description="是否已读筛选")
    start_date: Optional[date] = Field(None, description="开始日期")
    end_date: Optional[date] = Field(None, description="结束日期")
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(20, ge=1, le=100, description="每页数量")


class EventDetailRequest(BaseModel):
    """事件详情请求"""
    event_id: int = Field(..., description="事件ID")


class EventCreateRequest(BaseModel):
    """事件创建请求"""
    symbol: str = Field(..., description="股票代码")
    stock_name: str = Field(..., description="股票名称")
    category: str = Field(..., description="事件类别（policy/company/market/industry）")
    subcategory: str = Field(..., description="事件子类别")
    title: str = Field(..., max_length=200, description="标题")
    content: str = Field(..., description="内容")
    event_date: date = Field(..., description="事件日期")
    source: Optional[str] = Field(None, description="来源")
    source_url: Optional[str] = Field(None, description="来源URL")
    impact_level: Optional[int] = Field(None, ge=1, le=5, description="影响等级1-5")
    impact_analysis: Optional[str] = Field(None, description="影响分析")
    tags: Optional[list[str]] = Field(None, description="标签列表")


class EventUpdateRequest(BaseModel):
    """事件更新请求"""
    event_id: int = Field(..., description="事件ID")
    title: Optional[str] = Field(None, max_length=200, description="标题")
    content: Optional[str] = Field(None, description="内容")
    impact_level: Optional[int] = Field(None, ge=1, le=5, description="影响等级1-5")
    impact_analysis: Optional[str] = Field(None, description="影响分析")
    tags: Optional[list[str]] = Field(None, description="标签列表")


class EventMarkReadRequest(BaseModel):
    """事件标记已读请求"""
    event_id: int = Field(..., description="事件ID")
    is_read: bool = Field(True, description="是否已读（默认True）")


# ========================================
# API Endpoints
# ========================================

@router.post("/query")
async def query_events(
    request: EventQueryRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    查询事件列表

    ========================================
    接口信息
    ========================================
    接口路径: POST /api/v1/event/query
    对应页面: pages/event/list.vue - 事件列表页
    接口功能: 查询用户关注的所有投资事件，支持多维度筛选和分页

    ========================================
    请求参数
    ========================================
    {
        "symbol": "600519",                 // 股票代码筛选（可选）
        "category": "company",              // 事件类别筛选（可选）
        "is_read": false,                   // 是否已读筛选（可选）
        "start_date": "2025-01-01",         // 开始日期（可选）
        "end_date": "2025-01-31",           // 结束日期（可选）
        "page": 1,                          // 页码（默认1）
        "page_size": 20                     // 每页数量（默认20）
    }

    ========================================
    响应数据
    ========================================
    {
        "code": 0,
        "message": "success",
        "data": {
            "items": [
                {
                    "event_id": 1,
                    "user_id": 1,
                    "symbol": "600519",
                    "stock_name": "贵州茅台",
                    "category": "company",
                    "subcategory": "earnings",
                    "title": "贵州茅台发布2024年Q4财报",
                    "content": "营收同比增长15%，净利润...",
                    "source": "东方财富",
                    "event_date": "2025-01-15",
                    "impact_level": 4,
                    "impact_analysis": "超预期业绩，短期利好...",
                    "is_read": false,
                    "created_at": "2025-01-15T10:00:00",
                    "updated_at": "2025-01-15T10:00:00"
                }
            ],
            "total": 50,
            "page": 1,
            "page_size": 20,
            "total_pages": 3
        }
    }

    ========================================
    执行流程（时序）
    ========================================
    1. API接收请求 → 验证JWT Token → 获取user_id
    2. 调用 EventQueryService.execute()
       2.1 调用 EventRepository.query_by_user() 查询事件列表
       2.2 调用 EventQueryConverter.convert() 转换为业务数据
       2.3 调用 EventQueryBuilder.build_response() 构建分页响应
    3. 返回统一响应格式

    ========================================
    业务规则
    ========================================
    1. 权限规则：
       - 只能查询当前登录用户的事件
       - EventRepository自动过滤user_id

    2. 筛选规则：
       - symbol: 筛选指定股票的事件
       - category: 筛选事件类别（policy/company/market/industry）
       - is_read: 筛选已读/未读事件
       - start_date/end_date: 筛选日期范围

    3. 事件类别：
       - policy: 政策事件（monetary/fiscal/regulatory/international）
       - company: 公司事件（earnings/dividend/merger/governance）
       - market: 市场事件（volatility/rotation/sentiment/liquidity）
       - industry: 行业事件（technology/regulation/competition/cycle）

    4. 影响等级：
       - 1-5级，5为最高影响

    5. 分页规则：
       - 默认页码1，每页20条
       - 最大每页100条
       - 按事件日期倒序

    ========================================
    错误码
    ========================================
    - 0: 成功
    - 1001: 无权访问（PermissionDenied）
    - 1003: 数据验证失败（ValidationError）
    - 1000: 服务器内部错误

    ========================================
    前端调用示例
    ========================================
    ```javascript
    // pages/event/list.vue
    const queryEvents = async (filters) => {
      const response = await api.post('/api/v1/event/query', {
        symbol: filters.symbol,
        category: filters.category,
        is_read: filters.isRead,
        start_date: filters.startDate,
        end_date: filters.endDate,
        page: filters.page,
        page_size: 20
      });

      if (response.data.code === 0) {
        events.value = response.data.data.items;
        pagination.value = {
          total: response.data.data.total,
          page: response.data.data.page,
          pageSize: response.data.data.page_size,
          totalPages: response.data.data.total_pages
        };
      }
    };
    ```

    ========================================
    修改记录
    ========================================
    2025-01-17: 重构为POST-only架构，使用Service+Converter+Builder模式
    """
    service = EventQueryService()
    data = await service.execute(
        db=db,
        user_id=current_user.user_id,
        symbol=request.symbol,
        category=request.category,
        is_read=request.is_read,
        start_date=request.start_date,
        end_date=request.end_date,
        page=request.page,
        page_size=request.page_size
    )
    return Response.success(data)


@router.post("/detail")
async def get_event_detail(
    request: EventDetailRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    查询事件详情

    ========================================
    接口信息
    ========================================
    接口路径: POST /api/v1/event/detail
    对应页面: pages/event/detail.vue - 事件详情页
    接口功能: 查询单个事件的详细信息

    ========================================
    请求参数
    ========================================
    {
        "event_id": 1                       // 事件ID（必需）
    }

    ========================================
    响应数据
    ========================================
    {
        "code": 0,
        "message": "success",
        "data": {
            "event_id": 1,
            "user_id": 1,
            "symbol": "600519",
            "stock_name": "贵州茅台",
            "category": "company",
            "subcategory": "earnings",
            "title": "贵州茅台发布2024年Q4财报",
            "content": "营收同比增长15%，净利润增长12%...",
            "source": "东方财富",
            "source_url": "https://...",
            "event_date": "2025-01-15",
            "impact_level": 4,
            "impact_analysis": "超预期业绩，短期利好股价...",
            "tags": ["财报", "超预期"],
            "is_read": false,
            "created_at": "2025-01-15T10:00:00",
            "updated_at": "2025-01-15T10:00:00"
        }
    }

    ========================================
    执行流程（时序）
    ========================================
    1. API接收请求 → 验证JWT Token → 获取user_id
    2. 调用 EventDetailService.execute()
       2.1 调用 EventRepository.get_by_id() 查询事件
       2.2 权限校验：检查event.user_id == user_id
       2.3 调用 EventDetailConverter.convert() 转换为详情数据
    3. 返回统一响应格式

    ========================================
    业务规则
    ========================================
    1. 权限规则：
       - 只能查询当前登录用户的事件
       - 如果事件不属于当前用户，返回1001错误

    ========================================
    错误码
    ========================================
    - 0: 成功
    - 1001: 无权访问（PermissionDenied）
    - 1002: 事件不存在（ResourceNotFound）
    - 1000: 服务器内部错误

    ========================================
    前端调用示例
    ========================================
    ```javascript
    // pages/event/detail.vue
    const getEventDetail = async (eventId) => {
      const response = await api.post('/api/v1/event/detail', {
        event_id: eventId
      });

      if (response.data.code === 0) {
        event.value = response.data.data;
      } else if (response.data.code === 1002) {
        showError('事件不存在');
      } else if (response.data.code === 1001) {
        showError('无权访问该事件');
      }
    };
    ```

    ========================================
    修改记录
    ========================================
    2025-01-17: 重构为POST-only架构，使用Service+Converter+Builder模式
    """
    service = EventDetailService()
    data = await service.execute(
        db=db,
        event_id=request.event_id,
        user_id=current_user.user_id
    )
    return Response.success(data)


@router.post("/create")
async def create_event(
    request: EventCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    创建事件

    ========================================
    接口信息
    ========================================
    接口路径: POST /api/v1/event/create
    对应页面: pages/event/create.vue - 创建事件页
    接口功能: 创建新的投资事件记录

    ========================================
    请求参数
    ========================================
    {
        "symbol": "600519",                 // 股票代码（必需）
        "stock_name": "贵州茅台",           // 股票名称（必需）
        "category": "company",              // 事件类别（必需）
        "subcategory": "earnings",          // 事件子类别（必需）
        "title": "贵州茅台发布Q4财报",      // 标题（必需）
        "content": "营收同比增长15%...",    // 内容（必需）
        "event_date": "2025-01-15",         // 事件日期（必需）
        "source": "东方财富",               // 来源（可选）
        "source_url": "https://...",        // 来源URL（可选）
        "impact_level": 4,                  // 影响等级1-5（可选）
        "impact_analysis": "超预期...",     // 影响分析（可选）
        "tags": ["财报", "超预期"]          // 标签列表（可选）
    }

    ========================================
    响应数据
    ========================================
    {
        "code": 0,
        "message": "success",
        "data": {
            "event_id": 1,
            "symbol": "600519",
            "stock_name": "贵州茅台",
            "category": "company",
            "subcategory": "earnings",
            "title": "贵州茅台发布Q4财报",
            "content": "营收同比增长15%...",
            "event_date": "2025-01-15",
            "impact_level": 4,
            "is_read": false,
            "created_at": "2025-01-15T10:00:00"
        }
    }

    ========================================
    执行流程（时序）
    ========================================
    1. API接收请求 → 验证JWT Token → 获取user_id
    2. 调用 EventCreateService.execute()
       2.1 调用 EventCreateConverter.validate() 验证数据
           - 类别和子类别必须匹配
           - 影响等级1-5
       2.2 调用 EventCreateConverter.prepare_data() 准备数据
       2.3 调用 EventRepository.create() 创建事件
       2.4 调用 EventCreateBuilder.build_response() 构建响应
    3. 返回统一响应格式

    ========================================
    业务规则
    ========================================
    1. 类别和子类别对应关系：
       - policy: monetary, fiscal, regulatory, international
       - company: earnings, dividend, merger, governance
       - market: volatility, rotation, sentiment, liquidity
       - industry: technology, regulation, competition, cycle

    2. 验证规则：
       - symbol/stock_name: 不能为空
       - category/subcategory: 必须是预定义值
       - title: 不能为空，最长200字符
       - content: 不能为空
       - impact_level: 如提供，必须1-5

    3. 默认值：
       - is_read: 默认false

    ========================================
    错误码
    ========================================
    - 0: 成功
    - 1003: 数据验证失败（ValidationError）
    - 1000: 服务器内部错误

    ========================================
    前端调用示例
    ========================================
    ```javascript
    // pages/event/create.vue
    const createEvent = async (formData) => {
      const response = await api.post('/api/v1/event/create', {
        symbol: formData.symbol,
        stock_name: formData.stockName,
        category: formData.category,
        subcategory: formData.subcategory,
        title: formData.title,
        content: formData.content,
        event_date: formData.eventDate,
        source: formData.source,
        source_url: formData.sourceUrl,
        impact_level: formData.impactLevel,
        impact_analysis: formData.impactAnalysis,
        tags: formData.tags
      });

      if (response.data.code === 0) {
        showSuccess('事件创建成功');
        router.push('/event/list');
      } else if (response.data.code === 1003) {
        showError(response.data.message);
      }
    };
    ```

    ========================================
    修改记录
    ========================================
    2025-01-17: 重构为POST-only架构，使用Service+Converter+Builder模式
    """
    service = EventCreateService()
    data = await service.execute(
        db=db,
        user_id=current_user.user_id,
        symbol=request.symbol,
        stock_name=request.stock_name,
        category=request.category,
        subcategory=request.subcategory,
        title=request.title,
        content=request.content,
        event_date=request.event_date,
        source=request.source,
        source_url=request.source_url,
        impact_level=request.impact_level,
        impact_analysis=request.impact_analysis,
        tags=request.tags
    )
    return Response.success(data)


@router.post("/update")
async def update_event(
    request: EventUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    更新事件

    ========================================
    接口信息
    ========================================
    接口路径: POST /api/v1/event/update
    对应页面: pages/event/edit.vue - 编辑事件页
    接口功能: 更新已有事件的信息（支持部分更新）

    ========================================
    请求参数
    ========================================
    {
        "event_id": 1,                      // 事件ID（必需）
        "title": "新标题",                  // 标题（可选）
        "content": "新内容",                // 内容（可选）
        "impact_level": 5,                  // 影响等级（可选）
        "impact_analysis": "新分析",        // 影响分析（可选）
        "tags": ["新标签"]                  // 标签列表（可选）
    }

    ========================================
    响应数据
    ========================================
    {
        "code": 0,
        "message": "success",
        "data": {
            "event_id": 1,
            "symbol": "600519",
            "stock_name": "贵州茅台",
            "category": "company",
            "subcategory": "earnings",
            "title": "新标题",
            "content": "新内容",
            "event_date": "2025-01-15",
            "impact_level": 5,
            "impact_analysis": "新分析",
            "tags": ["新标签"],
            "is_read": false,
            "created_at": "2025-01-15T10:00:00",
            "updated_at": "2025-01-15T11:00:00"
        }
    }

    ========================================
    执行流程（时序）
    ========================================
    1. API接收请求 → 验证JWT Token → 获取user_id
    2. 调用 EventUpdateService.execute()
       2.1 调用 EventRepository.get_by_id() 查询事件
       2.2 权限校验：检查event.user_id == user_id
       2.3 调用 EventUpdateConverter.prepare_update_data() 准备更新数据
       2.4 调用 EventRepository.update() 更新事件
       2.5 调用 EventUpdateBuilder.build_response() 构建响应
    3. 返回统一响应格式

    ========================================
    业务规则
    ========================================
    1. 权限规则：
       - 只能更新当前登录用户的事件

    2. 更新规则：
       - 支持部分更新（只更新提供的字段）
       - 未提供的字段保持原值不变
       - 不能修改：symbol, stock_name, category, subcategory, event_date

    ========================================
    错误码
    ========================================
    - 0: 成功
    - 1001: 无权访问（PermissionDenied）
    - 1002: 事件不存在（ResourceNotFound）
    - 1003: 数据验证失败（ValidationError）
    - 1000: 服务器内部错误

    ========================================
    前端调用示例
    ========================================
    ```javascript
    // pages/event/edit.vue
    const updateEvent = async (eventId, formData) => {
      const response = await api.post('/api/v1/event/update', {
        event_id: eventId,
        title: formData.title,
        content: formData.content,
        impact_level: formData.impactLevel,
        impact_analysis: formData.impactAnalysis,
        tags: formData.tags
      });

      if (response.data.code === 0) {
        showSuccess('事件更新成功');
        router.push('/event/list');
      }
    };
    ```

    ========================================
    修改记录
    ========================================
    2025-01-17: 重构为POST-only架构，使用Service+Converter+Builder模式
    """
    service = EventUpdateService()
    data = await service.execute(
        db=db,
        event_id=request.event_id,
        user_id=current_user.user_id,
        title=request.title,
        content=request.content,
        impact_level=request.impact_level,
        impact_analysis=request.impact_analysis,
        tags=request.tags
    )
    return Response.success(data)


@router.post("/mark_read")
async def mark_event_read(
    request: EventMarkReadRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    标记事件已读/未读

    ========================================
    接口信息
    ========================================
    接口路径: POST /api/v1/event/mark_read
    对应页面: pages/event/list.vue - 事件列表页（标记操作）
    接口功能: 标记事件为已读或未读状态

    ========================================
    请求参数
    ========================================
    {
        "event_id": 1,                      // 事件ID（必需）
        "is_read": true                     // 是否已读（默认true）
    }

    ========================================
    响应数据
    ========================================
    {
        "code": 0,
        "message": "success",
        "data": {
            "success": true,
            "event_id": 1,
            "is_read": true,
            "message": "事件已标记为已读"
        }
    }

    ========================================
    执行流程（时序）
    ========================================
    1. API接收请求 → 验证JWT Token → 获取user_id
    2. 调用 EventMarkReadService.execute()
       2.1 调用 EventRepository.get_by_id() 查询事件
       2.2 权限校验：检查event.user_id == user_id
       2.3 调用 EventRepository.mark_as_read() 标记已读/未读
       2.4 调用 EventMarkReadBuilder.build_response() 构建响应
    3. 返回统一响应格式

    ========================================
    业务规则
    ========================================
    1. 权限规则：
       - 只能标记当前登录用户的事件

    2. 标记规则：
       - is_read=true: 标记为已读
       - is_read=false: 标记为未读

    ========================================
    错误码
    ========================================
    - 0: 成功
    - 1001: 无权访问（PermissionDenied）
    - 1002: 事件不存在（ResourceNotFound）
    - 1000: 服务器内部错误

    ========================================
    前端调用示例
    ========================================
    ```javascript
    // pages/event/list.vue
    const markEventRead = async (eventId, isRead = true) => {
      const response = await api.post('/api/v1/event/mark_read', {
        event_id: eventId,
        is_read: isRead
      });

      if (response.data.code === 0) {
        showSuccess(response.data.data.message);
        // 刷新列表
        await queryEvents(currentFilters.value);
      }
    };

    // 批量标记已读
    const markAllRead = async (eventIds) => {
      for (const id of eventIds) {
        await markEventRead(id, true);
      }
    };
    ```

    ========================================
    修改记录
    ========================================
    2025-01-17: 重构为POST-only架构，使用Service+Converter+Builder模式
    """
    service = EventMarkReadService()
    data = await service.execute(
        db=db,
        event_id=request.event_id,
        user_id=current_user.user_id,
        is_read=request.is_read
    )
    return Response.success(data)
