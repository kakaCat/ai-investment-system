"""
Strategy Repository

纯数据访问层 - 只负责策略表的CRUD操作，不包含任何业务逻辑
"""

from typing import List, Optional
from datetime import datetime
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.strategy import Strategy


class StrategyRepository:
    """策略数据访问层（纯CRUD，无业务逻辑）"""

    async def get_by_id(self, db: AsyncSession, strategy_id: int) -> Optional[Strategy]:
        """
        根据ID查询策略

        Args:
            db: 数据库会话
            strategy_id: 策略ID

        Returns:
            Strategy对象，不存在返回None
        """
        result = await db.execute(
            select(Strategy).where(and_(Strategy.strategy_id == strategy_id, Strategy.is_deleted is False))
        )
        return result.scalar_one_or_none()

    async def query_by_user(
        self,
        db: AsyncSession,
        user_id: int,
        symbol: Optional[str] = None,
        strategy_type: Optional[str] = None,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[List[Strategy], int]:
        """
        查询用户策略列表（支持分页、筛选）

        Args:
            db: 数据库会话
            user_id: 用户ID
            symbol: 股票代码（可选）
            strategy_type: 策略类型（可选）
            status: 策略状态（可选）
            page: 页码
            page_size: 每页数量

        Returns:
            (策略列表, 总数)
        """
        # 构建查询条件
        conditions = [Strategy.user_id == user_id, Strategy.is_deleted is False]

        if symbol:
            conditions.append(Strategy.symbol == symbol)
        if strategy_type:
            conditions.append(Strategy.strategy_type == strategy_type)
        if status:
            conditions.append(Strategy.status == status)

        # 查询总数
        count_query = select(Strategy).where(and_(*conditions))
        count_result = await db.execute(count_query)
        total = len(count_result.scalars().all())

        # 查询列表
        query = (
            select(Strategy)
            .where(and_(*conditions))
            .order_by(Strategy.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )

        result = await db.execute(query)
        strategies = result.scalars().all()

        return list(strategies), total

    async def query_by_symbol(
        self, db: AsyncSession, user_id: int, symbol: str, status: Optional[str] = None
    ) -> List[Strategy]:
        """
        查询某个股票的所有策略

        Args:
            db: 数据库会话
            user_id: 用户ID
            symbol: 股票代码
            status: 策略状态（可选）

        Returns:
            策略列表
        """
        conditions = [Strategy.user_id == user_id, Strategy.symbol == symbol, Strategy.is_deleted is False]

        if status:
            conditions.append(Strategy.status == status)

        query = select(Strategy).where(and_(*conditions)).order_by(Strategy.created_at.desc())

        result = await db.execute(query)
        return list(result.scalars().all())

    async def query_active_strategies(self, db: AsyncSession, user_id: int) -> List[Strategy]:
        """
        查询所有待执行的策略

        Args:
            db: 数据库会话
            user_id: 用户ID

        Returns:
            待执行策略列表
        """
        result = await db.execute(
            select(Strategy)
            .where(and_(Strategy.user_id == user_id, Strategy.status == "pending", Strategy.is_deleted is False))
            .order_by(Strategy.priority.desc(), Strategy.created_at.desc())
        )
        return list(result.scalars().all())

    async def create(self, db: AsyncSession, data: dict) -> Strategy:
        """
        创建策略

        Args:
            db: 数据库会话
            data: 策略数据字典

        Returns:
            创建的Strategy对象
        """
        strategy = Strategy(**data)
        db.add(strategy)
        await db.commit()
        await db.refresh(strategy)
        return strategy

    async def update(self, db: AsyncSession, strategy_id: int, data: dict) -> Optional[Strategy]:
        """
        更新策略

        Args:
            db: 数据库会话
            strategy_id: 策略ID
            data: 更新数据字典

        Returns:
            更新后的Strategy对象，不存在返回None
        """
        strategy = await self.get_by_id(db, strategy_id)
        if not strategy:
            return None

        for key, value in data.items():
            if hasattr(strategy, key):
                setattr(strategy, key, value)

        await db.commit()
        await db.refresh(strategy)
        return strategy

    async def soft_delete(self, db: AsyncSession, strategy_id: int) -> bool:
        """
        软删除策略

        Args:
            db: 数据库会话
            strategy_id: 策略ID

        Returns:
            是否删除成功
        """
        strategy = await self.get_by_id(db, strategy_id)
        if not strategy:
            return False

        strategy.is_deleted = True
        strategy.deleted_at = datetime.utcnow()

        await db.commit()
        return True

    async def execute_strategy(
        self, db: AsyncSession, strategy_id: int, executed_price: float, executed_quantity: float
    ) -> Optional[Strategy]:
        """
        执行策略（更新执行信息）

        Args:
            db: 数据库会话
            strategy_id: 策略ID
            executed_price: 实际执行价格
            executed_quantity: 实际执行数量

        Returns:
            更新后的Strategy对象，不存在返回None
        """
        strategy = await self.get_by_id(db, strategy_id)
        if not strategy:
            return None

        strategy.status = "completed"
        strategy.executed_at = datetime.utcnow()
        strategy.executed_price = executed_price
        strategy.executed_quantity = executed_quantity

        await db.commit()
        await db.refresh(strategy)
        return strategy

    async def cancel_strategy(self, db: AsyncSession, strategy_id: int) -> Optional[Strategy]:
        """
        取消策略

        Args:
            db: 数据库会话
            strategy_id: 策略ID

        Returns:
            更新后的Strategy对象，不存在返回None
        """
        strategy = await self.get_by_id(db, strategy_id)
        if not strategy:
            return None

        strategy.status = "cancelled"

        await db.commit()
        await db.refresh(strategy)
        return strategy
