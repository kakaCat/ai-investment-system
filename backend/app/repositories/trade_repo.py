"""
Trade Repository

纯数据访问层 - 只负责交易表的CRUD操作，不包含任何业务逻辑
"""

from typing import List, Optional
from datetime import datetime
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.trade import Trade


class TradeRepository:
    """交易数据访问层（纯CRUD，无业务逻辑）"""

    async def get_by_id(self, db: AsyncSession, trade_id: int) -> Optional[Trade]:
        """
        根据ID查询交易记录

        Args:
            db: 数据库会话
            trade_id: 交易ID

        Returns:
            Trade对象，不存在返回None
        """
        result = await db.execute(select(Trade).where(and_(Trade.trade_id == trade_id, Trade.is_deleted is False)))
        return result.scalar_one_or_none()

    async def query_by_account(
        self,
        db: AsyncSession,
        account_id: int,
        symbol: Optional[str] = None,
        trade_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[List[Trade], int]:
        """
        查询账户交易记录列表（支持分页、筛选）

        Args:
            db: 数据库会话
            account_id: 账户ID
            symbol: 股票代码（可选）
            trade_type: 交易类型（可选）
            start_date: 开始日期（可选）
            end_date: 结束日期（可选）
            page: 页码
            page_size: 每页数量

        Returns:
            (交易记录列表, 总数)
        """
        # 构建查询条件
        conditions = [Trade.account_id == account_id, Trade.is_deleted is False]

        if symbol:
            conditions.append(Trade.symbol == symbol)
        if trade_type:
            conditions.append(Trade.trade_type == trade_type)
        if start_date:
            conditions.append(Trade.trade_date >= start_date)
        if end_date:
            conditions.append(Trade.trade_date <= end_date)

        # 查询总数
        count_query = select(Trade).where(and_(*conditions))
        count_result = await db.execute(count_query)
        total = len(count_result.scalars().all())

        # 查询列表
        query = (
            select(Trade)
            .where(and_(*conditions))
            .order_by(Trade.trade_date.desc(), Trade.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )

        result = await db.execute(query)
        trades = result.scalars().all()

        return list(trades), total

    async def query_by_user(
        self,
        db: AsyncSession,
        user_id: int,
        account_id: Optional[int] = None,
        symbol: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[List[Trade], int]:
        """
        查询用户所有交易记录（跨账户）

        Args:
            db: 数据库会话
            user_id: 用户ID
            account_id: 账户ID（可选）
            symbol: 股票代码（可选）
            page: 页码
            page_size: 每页数量

        Returns:
            (交易记录列表, 总数)
        """
        # 构建查询条件
        conditions = [Trade.user_id == user_id, Trade.is_deleted is False]

        if account_id:
            conditions.append(Trade.account_id == account_id)
        if symbol:
            conditions.append(Trade.symbol == symbol)

        # 查询总数
        count_query = select(Trade).where(and_(*conditions))
        count_result = await db.execute(count_query)
        total = len(count_result.scalars().all())

        # 查询列表
        query = (
            select(Trade)
            .where(and_(*conditions))
            .order_by(Trade.trade_date.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )

        result = await db.execute(query)
        trades = result.scalars().all()

        return list(trades), total

    async def create(self, db: AsyncSession, data: dict) -> Trade:
        """
        创建交易记录

        Args:
            db: 数据库会话
            data: 交易数据字典

        Returns:
            创建的Trade对象
        """
        trade = Trade(**data)
        db.add(trade)
        await db.commit()
        await db.refresh(trade)
        return trade

    async def update(self, db: AsyncSession, trade_id: int, data: dict) -> Optional[Trade]:
        """
        更新交易记录

        Args:
            db: 数据库会话
            trade_id: 交易ID
            data: 更新数据字典

        Returns:
            更新后的Trade对象，不存在返回None
        """
        trade = await self.get_by_id(db, trade_id)
        if not trade:
            return None

        for key, value in data.items():
            if hasattr(trade, key):
                setattr(trade, key, value)

        await db.commit()
        await db.refresh(trade)
        return trade

    async def soft_delete(self, db: AsyncSession, trade_id: int) -> bool:
        """
        软删除交易记录

        Args:
            db: 数据库会话
            trade_id: 交易ID

        Returns:
            是否删除成功
        """
        trade = await self.get_by_id(db, trade_id)
        if not trade:
            return False

        trade.is_deleted = True
        trade.deleted_at = datetime.utcnow()

        await db.commit()
        return True

    async def query_by_symbol(
        self, db: AsyncSession, user_id: int, symbol: str, page: int = 1, page_size: int = 20
    ) -> tuple[List[Trade], int]:
        """
        查询某个股票的所有交易记录

        Args:
            db: 数据库会话
            user_id: 用户ID
            symbol: 股票代码
            page: 页码
            page_size: 每页数量

        Returns:
            (交易记录列表, 总数)
        """
        conditions = [Trade.user_id == user_id, Trade.symbol == symbol, Trade.is_deleted is False]

        # 查询总数
        count_query = select(Trade).where(and_(*conditions))
        count_result = await db.execute(count_query)
        total = len(count_result.scalars().all())

        # 查询列表
        query = (
            select(Trade)
            .where(and_(*conditions))
            .order_by(Trade.trade_date.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )

        result = await db.execute(query)
        trades = result.scalars().all()

        return list(trades), total
