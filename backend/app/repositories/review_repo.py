"""
Review Repository

纯数据访问层 - 只负责user_stock_reviews表的CRUD操作，不包含任何业务逻辑
"""

from typing import Optional
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.review import Review


class ReviewRepository:
    """股票评价数据访问层（纯CRUD，无业务逻辑）"""

    async def get_by_user_symbol(self, db: AsyncSession, user_id: int, symbol: str) -> Optional[Review]:
        """
        查询用户对指定股票的评价

        Args:
            db: 数据库会话
            user_id: 用户ID
            symbol: 股票代码

        Returns:
            Review对象，不存在返回None
        """
        result = await db.execute(
            select(Review).where(and_(Review.user_id == user_id, Review.symbol == symbol, Review.is_deleted is False))
        )
        return result.scalar_one_or_none()

    async def create(self, db: AsyncSession, review_data: dict) -> Review:
        """
        创建评价

        Args:
            db: 数据库会话
            review_data: 评价数据字典

        Returns:
            创建的Review对象
        """
        review = Review(**review_data)
        db.add(review)
        await db.flush()
        await db.refresh(review)
        return review

    async def update(self, db: AsyncSession, review: Review, update_data: dict) -> Review:
        """
        更新评价

        Args:
            db: 数据库会话
            review: Review对象
            update_data: 更新数据字典

        Returns:
            更新后的Review对象
        """
        for key, value in update_data.items():
            if hasattr(review, key):
                setattr(review, key, value)

        await db.flush()
        await db.refresh(review)
        return review
