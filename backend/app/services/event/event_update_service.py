"""
Event Update Service

事件更新业务服务 - Service + Converter + Builder
"""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.event_repo import EventRepository
from app.exceptions import ResourceNotFound, PermissionDenied, ValidationError


class EventUpdateService:
    """
    事件更新业务类

    职责：权限校验、编排流程、事务管理
    """

    def __init__(self):
        self.event_repo = EventRepository()

    async def execute(
        self,
        db: AsyncSession,
        event_id: int,
        user_id: int,
        title: Optional[str] = None,
        content: Optional[str] = None,
        impact_level: Optional[int] = None,
        impact_analysis: Optional[str] = None,
        tags: Optional[list] = None,
    ) -> dict:
        """
        执行事件更新业务逻辑

        Args:
            db: 数据库会话
            event_id: 事件ID
            user_id: 用户ID
            title: 标题（可选）
            content: 内容（可选）
            impact_level: 影响等级（可选）
            impact_analysis: 影响分析（可选）
            tags: 标签列表（可选）

        Returns:
            更新后的事件数据

        Raises:
            ResourceNotFound: 事件不存在
            PermissionDenied: 无权访问
            ValidationError: 数据验证失败
        """
        # 1. 权限校验 - 查询事件
        event = await self.event_repo.get_by_id(db, event_id)
        if not event:
            raise ResourceNotFound(f"事件ID {event_id} 不存在")

        if event.user_id != user_id:
            raise PermissionDenied(f"无权访问事件ID {event_id}")

        # 2. 调用 Converter 验证和准备数据
        update_data = EventUpdateConverter.prepare_update_data(
            title=title, content=content, impact_level=impact_level, impact_analysis=impact_analysis, tags=tags
        )

        # 3. 更新事件
        updated_event = await self.event_repo.update(db, event_id, update_data)

        # 4. 调用 Builder 构建响应
        return EventUpdateBuilder.build_response(updated_event)


class EventUpdateConverter:
    """
    事件更新转换器（静态类）

    职责：数据验证、业务逻辑处理
    """

    @staticmethod
    def prepare_update_data(
        title: Optional[str],
        content: Optional[str],
        impact_level: Optional[int],
        impact_analysis: Optional[str],
        tags: Optional[list],
    ) -> dict:
        """
        准备更新数据（只更新提供的字段）

        Args:
            title: 标题
            content: 内容
            impact_level: 影响等级
            impact_analysis: 影响分析
            tags: 标签列表

        Returns:
            准备好的更新数据字典

        Raises:
            ValidationError: 验证失败
        """
        update_data = {}

        # 验证并添加标题
        if title is not None:
            if not title or len(title.strip()) == 0:
                raise ValidationError("标题不能为空")
            if len(title) > 200:
                raise ValidationError("标题长度不能超过200个字符")
            update_data["title"] = title.strip()

        # 验证并添加内容
        if content is not None:
            if not content or len(content.strip()) == 0:
                raise ValidationError("内容不能为空")
            update_data["content"] = content.strip()

        # 验证并添加影响等级
        if impact_level is not None:
            if impact_level < 1 or impact_level > 5:
                raise ValidationError("影响等级必须在1-5之间")
            update_data["impact_level"] = impact_level

        # 添加影响分析
        if impact_analysis is not None:
            update_data["impact_analysis"] = impact_analysis.strip() if impact_analysis else None

        # 添加标签
        if tags is not None:
            update_data["tags"] = tags

        return update_data


class EventUpdateBuilder:
    """
    事件更新数据构建器（静态类）

    职责：构建响应对象
    """

    @staticmethod
    def build_response(event) -> dict:
        """
        构建事件更新响应

        Args:
            event: 更新后的事件对象

        Returns:
            事件数据字典
        """
        return {
            "event_id": event.event_id,
            "symbol": event.symbol,
            "stock_name": event.stock_name,
            "category": event.category,
            "subcategory": event.subcategory,
            "title": event.title,
            "content": event.content,
            "event_date": event.event_date.isoformat() if event.event_date else None,
            "impact_level": event.impact_level,
            "impact_analysis": event.impact_analysis,
            "tags": event.tags,
            "is_read": event.is_read,
            "created_at": event.created_at.isoformat() if event.created_at else None,
            "updated_at": event.updated_at.isoformat() if event.updated_at else None,
        }
