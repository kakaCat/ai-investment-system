"""
Event Mark Read Service

事件标记已读业务服务 - Service + Converter + Builder
"""

from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.event_repo import EventRepository
from app.exceptions import ResourceNotFound, PermissionDenied


class EventMarkReadService:
    """
    事件标记已读业务类

    职责：权限校验、编排流程、事务管理
    """

    def __init__(self):
        self.event_repo = EventRepository()

    async def execute(
        self,
        db: AsyncSession,
        event_id: int,
        user_id: int,
        is_read: bool = True
    ) -> dict:
        """
        执行事件标记已读/未读业务逻辑

        Args:
            db: 数据库会话
            event_id: 事件ID
            user_id: 用户ID
            is_read: 是否已读（默认True）

        Returns:
            标记结果

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

        # 2. 标记已读/未读
        success = await self.event_repo.mark_as_read(db, event_id, is_read)

        # 3. 调用 Builder 构建响应
        return EventMarkReadBuilder.build_response(success, event_id, is_read)


class EventMarkReadBuilder:
    """
    事件标记已读数据构建器（静态类）

    职责：构建响应对象
    """

    @staticmethod
    def build_response(success: bool, event_id: int, is_read: bool) -> dict:
        """
        构建事件标记已读响应

        Args:
            success: 是否成功
            event_id: 事件ID
            is_read: 是否已读

        Returns:
            标记结果字典
        """
        status = "已读" if is_read else "未读"
        return {
            "success": success,
            "event_id": event_id,
            "is_read": is_read,
            "message": f"事件已标记为{status}" if success else "标记失败"
        }
