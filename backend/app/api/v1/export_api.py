"""
Export API - POST-only架构

数据导出API - 使用POST-only + Service + Converter + Builder模式
"""

from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.common import Response
from app.services.export import ExportService


router = APIRouter(prefix="/export", tags=["数据导出"])


# ========================================
# Request Schemas
# ========================================


class ExportTradesRequest(BaseModel):
    """导出交易记录请求"""

    account_id: Optional[int] = Field(None, description="账户ID，不指定则全部账户")
    format: str = Field("xlsx", description="导出格式：xlsx/csv")
    start_date: Optional[str] = Field(None, description="开始日期 YYYY-MM-DD")
    end_date: Optional[str] = Field(None, description="结束日期 YYYY-MM-DD")
    include_summary: bool = Field(True, description="包含汇总统计")


class ExportHoldingsRequest(BaseModel):
    """导出持仓请求"""

    account_id: Optional[int] = Field(None, description="账户ID，不指定则全部账户")
    format: str = Field("xlsx", description="导出格式：xlsx/csv")
    include_stats: bool = Field(True, description="包含统计数据")


class ExportEventsRequest(BaseModel):
    """导出事件请求"""

    category: Optional[str] = Field(None, description="事件类别")
    format: str = Field("xlsx", description="导出格式：xlsx/csv")
    start_date: Optional[str] = Field(None, description="开始日期 YYYY-MM-DD")
    end_date: Optional[str] = Field(None, description="结束日期 YYYY-MM-DD")


class ExportPortfolioRequest(BaseModel):
    """导出投资组合请求"""

    account_id: Optional[int] = Field(None, description="账户ID，不指定则全部账户")
    format: str = Field("xlsx", description="导出格式：xlsx/pdf")
    include_charts: bool = Field(True, description="包含图表（仅PDF）")


# ========================================
# API Endpoints
# ========================================


@router.post("/trades")
async def export_trades(
    request: ExportTradesRequest, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """
    导出交易记录

    ========================================
    接口信息
    ========================================
    接口路径: POST /api/v1/export/trades
    对应页面: pages/trade/list.vue - 导出按钮
    接口功能: 导出Excel或CSV格式的交易记录

    ========================================
    请求参数
    ========================================
    {
        "account_id": 1,                  // 可选，账户ID
        "format": "xlsx",                 // xlsx/csv
        "start_date": "2025-01-01",      // 可选
        "end_date": "2025-12-31",        // 可选
        "include_summary": true           // 包含汇总
    }

    ========================================
    响应数据
    ========================================
    {
        "task_id": "export_abc123",
        "status": "processing",
        "export_type": "trades",
        "download_url": "/api/v1/export/download/export_abc123",
        "created_at": "2025-11-18T10:00:00Z"
    }

    ========================================
    执行流程（时序）
    ========================================
    1. 接收导出参数
    2. Service创建导出任务
    3. （TODO）后台异步生成文件
    4. 返回任务ID供轮询或下载

    ========================================
    业务规则
    ========================================
    1. 支持Excel和CSV两种格式
    2. 可以筛选账户、日期范围
    3. 异步生成文件，返回任务ID

    ========================================
    前端调用示例
    ========================================
    const task = await post('/export/trades', {
        format: 'xlsx',
        include_summary: true
    })
    // 轮询或直接下载
    window.open(task.download_url)
    """
    service = ExportService()
    result = await service.export_trades(
        db,
        current_user.user_id,
        request.account_id,
        request.format,
        request.start_date,
        request.end_date,
        request.include_summary,
    )
    return Response.success(data=result, message="导出任务已创建")


@router.post("/holdings")
async def export_holdings(
    request: ExportHoldingsRequest, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """
    导出持仓数据

    ========================================
    接口信息
    ========================================
    接口路径: POST /api/v1/export/holdings
    对应页面: pages/holding/list.vue - 导出按钮
    接口功能: 导出Excel或CSV格式的持仓数据

    ========================================
    请求参数
    ========================================
    {
        "account_id": 1,
        "format": "xlsx",
        "include_stats": true
    }

    ========================================
    前端调用示例
    ========================================
    const task = await post('/export/holdings', { format: 'xlsx' })
    """
    service = ExportService()
    result = await service.export_holdings(
        db, current_user.user_id, request.account_id, request.format, request.include_stats
    )
    return Response.success(data=result, message="导出任务已创建")


@router.post("/events")
async def export_events(
    request: ExportEventsRequest, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """
    导出事件数据

    ========================================
    接口信息
    ========================================
    接口路径: POST /api/v1/export/events
    对应页面: pages/event/list.vue - 导出按钮
    接口功能: 导出Excel或CSV格式的事件数据

    ========================================
    请求参数
    ========================================
    {
        "category": "company",
        "format": "xlsx",
        "start_date": "2025-01-01",
        "end_date": "2025-12-31"
    }

    ========================================
    前端调用示例
    ========================================
    const task = await post('/export/events', {
        category: 'company',
        format: 'xlsx'
    })
    """
    service = ExportService()
    result = await service.export_events(
        db, current_user.user_id, request.category, request.format, request.start_date, request.end_date
    )
    return Response.success(data=result, message="导出任务已创建")


@router.post("/portfolio")
async def export_portfolio(
    request: ExportPortfolioRequest, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """
    导出投资组合报告

    ========================================
    接口信息
    ========================================
    接口路径: POST /api/v1/export/portfolio
    对应页面: pages/portfolio/index.vue - 导出按钮
    接口功能: 导出完整的投资组合报告（Excel或PDF）

    ========================================
    请求参数
    ========================================
    {
        "account_id": 1,
        "format": "pdf",              // xlsx/pdf
        "include_charts": true        // 包含图表（仅PDF）
    }

    ========================================
    业务规则
    ========================================
    1. Excel格式包含详细数据表格
    2. PDF格式包含可视化图表和分析报告
    3. include_charts仅对PDF格式有效

    ========================================
    前端调用示例
    ========================================
    const task = await post('/export/portfolio', {
        format: 'pdf',
        include_charts: true
    })
    """
    service = ExportService()
    result = await service.export_portfolio(
        db, current_user.user_id, request.account_id, request.format, request.include_charts
    )
    return Response.success(data=result, message="导出任务已创建")


class DownloadRequest(BaseModel):
    """下载请求"""

    task_id: str = Field(..., description="任务ID")


@router.post("/download")
async def download_export(
    request: DownloadRequest, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """
    下载导出文件

    ========================================
    接口信息
    ========================================
    接口路径: POST /api/v1/export/download
    接口功能: 根据任务ID下载生成的导出文件

    ========================================
    请求参数
    ========================================
    {
        "task_id": "export_abc123"
    }

    ========================================
    业务规则
    ========================================
    1. 文件生成后有效期7天
    2. 只能下载本用户的导出文件
    3. 文件下载后不会删除，可重复下载

    ========================================
    前端调用示例
    ========================================
    // 方式1：直接打开下载链接
    window.open(`/api/v1/export/download?task_id=${taskId}`)

    // 方式2：通过接口下载
    const response = await post('/export/download', { task_id: taskId })
    """
    # TODO: 实现实际的文件下载
    # return FileResponse(file_path, filename=filename)
    return Response.error(code=1001, message="文件不存在或已过期")
