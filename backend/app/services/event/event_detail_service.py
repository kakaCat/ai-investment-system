"""
Event Detail Service

事件详情业务服务 - Service + Converter + Builder
"""

from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.event_repo import EventRepository
from app.exceptions import ResourceNotFound, PermissionDenied


class EventDetailService:
    """
    事件详情业务类

    职责：权限校验、编排流程、事务管理
    """

    def __init__(self):
        self.event_repo = EventRepository()

    async def execute(self, db: AsyncSession, event_id: int, user_id: int) -> dict:
        """
        执行事件详情查询业务逻辑

        Args:
            db: 数据库会话
            event_id: 事件ID
            user_id: 用户ID

        Returns:
            事件详情数据

        Raises:
            ResourceNotFound: 事件不存在
            PermissionDenied: 无权访问
        """
        # 1. 权限校验 - 查询事件
        event = await self.event_repo.get_by_id(db, event_id)
        if not event:
            raise ResourceNotFound(f"事件ID {event_id} 不存在")

        if event.user_id != user_id:
            raise PermissionDenied(f"无权访问事件ID {event_id}")

        # 2. 调用 Converter 转换数据
        return EventDetailConverter.convert(event)


class EventDetailConverter:
    """
    事件详情转换器（静态类）

    职责：业务逻辑计算
    """

    @staticmethod
    def convert(event) -> dict:
        """
        将事件对象转换为详情数据

        Args:
            event: 事件对象

        Returns:
            事件详情字典
        """
        return {
            "event_id": event.event_id,
            "user_id": event.user_id,
            "symbol": event.symbol,
            "stock_name": event.stock_name,
            "category": event.category,
            "subcategory": event.subcategory,
            "title": event.title,
            "content": event.content,
            "source": event.source,
            "source_url": event.source_url,
            "event_date": event.event_date.isoformat() if event.event_date else None,
            "impact_level": event.impact_level,
            "impact_analysis": event.impact_analysis,
            "tags": event.tags,
            "is_read": event.is_read,
            "created_at": event.created_at.isoformat() if event.created_at else None,
            "updated_at": event.updated_at.isoformat() if event.updated_at else None,
        }
