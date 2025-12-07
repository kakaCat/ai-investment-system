"""
Event Repository

纯数据访问层 - 只负责事件表的CRUD操作，不包含任何业务逻辑
"""

from typing import List, Optional
from datetime import datetime
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.event import Event


class EventRepository:
    """事件数据访问层（纯CRUD，无业务逻辑）"""

    async def get_by_id(self, db: AsyncSession, event_id: int) -> Optional[Event]:
        """
        根据ID查询事件

        Args:
            db: 数据库会话
            event_id: 事件ID

        Returns:
            Event对象，不存在返回None
        """
        result = await db.execute(
            select(Event).where(
                and_(
                    Event.event_id == event_id,
                    Event.is_deleted == False
                )
            )
        )
        return result.scalar_one_or_none()

    async def query_by_user(
        self,
        db: AsyncSession,
        user_id: int,
        category: Optional[str] = None,
        event_type: Optional[str] = None,
        symbol: Optional[str] = None,
        is_read: Optional[bool] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        page: int = 1,
        page_size: int = 20
    ) -> tuple[List[Event], int]:
        """
        查询用户事件列表（支持多种筛选）

        Args:
            db: 数据库会话
            user_id: 用户ID
            category: 事件类别（可选）
            event_type: 事件类型（可选）
            symbol: 股票代码（可选）
            is_read: 是否已读（可选）
            start_date: 开始日期（可选）
            end_date: 结束日期（可选）
            page: 页码
            page_size: 每页数量

        Returns:
            (事件列表, 总数)
        """
        # 构建查询条件
        conditions = [
            Event.user_id == user_id,
            Event.is_deleted == False
        ]

        if category:
            conditions.append(Event.category == category)
        if event_type:
            conditions.append(Event.event_type == event_type)
        if symbol:
            conditions.append(Event.symbol == symbol)
        if is_read is not None:
            conditions.append(Event.is_read == is_read)
        if start_date:
            conditions.append(Event.event_date >= start_date)
        if end_date:
            conditions.append(Event.event_date <= end_date)

        # 查询总数
        count_query = select(Event).where(and_(*conditions))
        count_result = await db.execute(count_query)
        total = len(count_result.scalars().all())

        # 查询列表
        query = (
            select(Event)
            .where(and_(*conditions))
            .order_by(Event.event_date.desc(), Event.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )

        result = await db.execute(query)
        events = result.scalars().all()

        return list(events), total

    async def query_by_symbol(
        self,
        db: AsyncSession,
        user_id: int,
        symbol: str,
        page: int = 1,
        page_size: int = 20
    ) -> tuple[List[Event], int]:
        """
        查询某个股票的所有事件

        Args:
            db: 数据库会话
            user_id: 用户ID
            symbol: 股票代码
            page: 页码
            page_size: 每页数量

        Returns:
            (事件列表, 总数)
        """
        conditions = [
            Event.user_id == user_id,
            Event.symbol == symbol,
            Event.is_deleted == False
        ]

        # 查询总数
        count_query = select(Event).where(and_(*conditions))
        count_result = await db.execute(count_query)
        total = len(count_result.scalars().all())

        # 查询列表
        query = (
            select(Event)
            .where(and_(*conditions))
            .order_by(Event.event_date.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )

        result = await db.execute(query)
        events = result.scalars().all()

        return list(events), total

    async def create(self, db: AsyncSession, data: dict) -> Event:
        """
        创建事件

        Args:
            db: 数据库会话
            data: 事件数据字典

        Returns:
            创建的Event对象
        """
        event = Event(**data)
        db.add(event)
        await db.commit()
        await db.refresh(event)
        return event

    async def update(self, db: AsyncSession, event_id: int, data: dict) -> Optional[Event]:
        """
        更新事件

        Args:
            db: 数据库会话
            event_id: 事件ID
            data: 更新数据字典

        Returns:
            更新后的Event对象，不存在返回None
        """
        event = await self.get_by_id(db, event_id)
        if not event:
            return None

        for key, value in data.items():
            if hasattr(event, key):
                setattr(event, key, value)

        await db.commit()
        await db.refresh(event)
        return event

    async def soft_delete(self, db: AsyncSession, event_id: int) -> bool:
        """
        软删除事件

        Args:
            db: 数据库会话
            event_id: 事件ID

        Returns:
            是否删除成功
        """
        event = await self.get_by_id(db, event_id)
        if not event:
            return False

        event.is_deleted = True
        event.deleted_at = datetime.utcnow()

        await db.commit()
        return True

    async def mark_as_read(self, db: AsyncSession, event_id: int) -> bool:
        """
        标记事件为已读

        Args:
            db: 数据库会话
            event_id: 事件ID

        Returns:
            是否成功
        """
        event = await self.get_by_id(db, event_id)
        if not event:
            return False

        event.is_read = True
        await db.commit()
        return True

    async def get_unread_count(self, db: AsyncSession, user_id: int) -> int:
        """
        获取用户未读事件数量

        Args:
            db: 数据库会话
            user_id: 用户ID

        Returns:
            未读数量
        """
        result = await db.execute(
            select(Event).where(
                and_(
                    Event.user_id == user_id,
                    Event.is_read == False,
                    Event.is_deleted == False
                )
            )
        )
        return len(result.scalars().all())

    async def query_by_category(
        self,
        db: AsyncSession,
        user_id: int,
        category: str,
        page: int = 1,
        page_size: int = 20
    ) -> tuple[List[Event], int]:
        """
        查询某个类别的所有事件

        Args:
            db: 数据库会话
            user_id: 用户ID
            category: 事件类别
            page: 页码
            page_size: 每页数量

        Returns:
            (事件列表, 总数)
        """
        conditions = [
            Event.user_id == user_id,
            Event.category == category,
            Event.is_deleted == False
        ]

        # 查询总数
        count_query = select(Event).where(and_(*conditions))
        count_result = await db.execute(count_query)
        total = len(count_result.scalars().all())

        # 查询列表
        query = (
            select(Event)
            .where(and_(*conditions))
            .order_by(Event.event_date.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )

        result = await db.execute(query)
        events = result.scalars().all()

        return list(events), total
