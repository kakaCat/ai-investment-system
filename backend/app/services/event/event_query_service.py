"""
Event Query Service

事件查询业务服务 - Service + Converter + Builder
"""

from typing import Optional
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.event_repo import EventRepository
from app.schemas.common import PaginationResponse


class EventQueryService:
    """
    事件查询业务类

    职责：权限校验、编排流程、事务管理
    """

    def __init__(self):
        self.event_repo = EventRepository()

    async def execute(
        self,
        db: AsyncSession,
        user_id: int,
        symbol: Optional[str] = None,
        category: Optional[str] = None,
        is_read: Optional[bool] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        page: int = 1,
        page_size: int = 20
    ) -> dict:
        """
        执行事件查询业务逻辑

        Args:
            db: 数据库会话
            user_id: 用户ID
            symbol: 股票代码筛选（可选）
            category: 事件类别筛选（可选）
            is_read: 是否已读筛选（可选）
            start_date: 开始日期（可选）
            end_date: 结束日期（可选）
            page: 页码
            page_size: 每页数量

        Returns:
            分页的事件列表数据
        """
        # 1. 查询事件列表
        events, total = await self.event_repo.query_by_user(
            db=db,
            user_id=user_id,
            symbol=symbol,
            category=category,
            is_read=is_read,
            start_date=start_date,
            end_date=end_date,
            page=page,
            page_size=page_size
        )

        # 2. 调用 Converter 转换数据
        items = EventQueryConverter.convert(events)

        # 3. 调用 Builder 构建响应
        return EventQueryBuilder.build_response(items, total, page, page_size)


class EventQueryConverter:
    """
    事件查询转换器（静态类）

    职责：业务逻辑计算
    """

    @staticmethod
    def convert(events: list) -> list:
        """
        将事件列表转换为业务数据

        Args:
            events: 事件对象列表

        Returns:
            转换后的事件数据列表
        """
        result = []
        for event in events:
            event_data = {
                "event_id": event.event_id,
                "user_id": event.user_id,
                "symbol": event.symbol,
                "stock_name": event.stock_name,
                "category": event.category,
                "subcategory": event.subcategory,
                "title": event.title,
                "content": event.content,
                "source": event.source,
                "event_date": event.event_date.isoformat() if event.event_date else None,
                "impact_level": event.impact_level,
                "impact_analysis": event.impact_analysis,
                "is_read": event.is_read,
                "created_at": event.created_at.isoformat() if event.created_at else None,
                "updated_at": event.updated_at.isoformat() if event.updated_at else None,
            }
            result.append(event_data)

        return result


class EventQueryBuilder:
    """
    事件查询数据构建器（静态类）

    职责：构建响应对象
    """

    @staticmethod
    def build_response(items: list, total: int, page: int, page_size: int) -> dict:
        """
        构建分页响应

        Args:
            items: 事件数据列表
            total: 总记录数
            page: 当前页码
            page_size: 每页数量

        Returns:
            分页响应字典
        """
        pagination = PaginationResponse.create(
            items=items,
            total=total,
            page=page,
            page_size=page_size
        )
        return pagination.dict()
