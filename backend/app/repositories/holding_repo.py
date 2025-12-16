"""
Holding Repository

纯数据访问层 - 只负责持仓表的CRUD操作，不包含任何业务逻辑
"""

from typing import List, Optional
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.holding import Holding


class HoldingRepository:
    """持仓数据访问层（纯CRUD，无业务逻辑）"""

    async def get_by_id(self, db: AsyncSession, holding_id: int) -> Optional[Holding]:
        """
        根据ID查询持仓记录

        Args:
            db: 数据库会话
            holding_id: 持仓ID

        Returns:
            Holding对象，不存在返回None
        """
        result = await db.execute(
            select(Holding).where(and_(Holding.holding_id == holding_id, Holding.is_deleted is False))
        )
        return result.scalar_one_or_none()

    async def get_by_account_symbol(self, db: AsyncSession, account_id: int, symbol: str) -> Optional[Holding]:
        """
        根据账户和股票代码查询持仓（用于更新持仓）

        Args:
            db: 数据库会话
            account_id: 账户ID
            symbol: 股票代码

        Returns:
            Holding对象，不存在返回None
        """
        result = await db.execute(
            select(Holding).where(
                and_(Holding.account_id == account_id, Holding.symbol == symbol, Holding.is_deleted is False)
            )
        )
        return result.scalar_one_or_none()

    async def query_by_account(self, db: AsyncSession, account_id: int, symbol: Optional[str] = None) -> List[Holding]:
        """
        查询账户所有持仓

        Args:
            db: 数据库会话
            account_id: 账户ID
            symbol: 股票代码（可选，用于筛选）

        Returns:
            持仓列表
        """
        conditions = [Holding.account_id == account_id, Holding.is_deleted is False]

        if symbol:
            conditions.append(Holding.symbol == symbol)

        query = select(Holding).where(and_(*conditions)).order_by(Holding.created_at.desc())

        result = await db.execute(query)
        return list(result.scalars().all())

    async def query_by_user(self, db: AsyncSession, user_id: int, symbol: Optional[str] = None) -> List[Holding]:
        """
        查询用户所有持仓（跨账户）

        Args:
            db: 数据库会话
            user_id: 用户ID
            symbol: 股票代码（可选）

        Returns:
            持仓列表
        """
        conditions = [Holding.user_id == user_id, Holding.is_deleted is False]

        if symbol:
            conditions.append(Holding.symbol == symbol)

        query = select(Holding).where(and_(*conditions)).order_by(Holding.account_id, Holding.created_at.desc())

        result = await db.execute(query)
        return list(result.scalars().all())

    async def create(self, db: AsyncSession, data: dict) -> Holding:
        """
        创建持仓记录

        Args:
            db: 数据库会话
            data: 持仓数据字典

        Returns:
            创建的Holding对象
        """
        holding = Holding(**data)
        db.add(holding)
        await db.commit()
        await db.refresh(holding)
        return holding

    async def upsert(self, db: AsyncSession, data: dict) -> Holding:
        """
        插入或更新持仓记录（如果已存在则更新）

        Args:
            db: 数据库会话
            data: 持仓数据字典（必须包含account_id和symbol）

        Returns:
            Holding对象
        """
        account_id = data.get("account_id")
        symbol = data.get("symbol")

        if not account_id or not symbol:
            raise ValueError("account_id and symbol are required for upsert")

        # 查找是否已存在
        existing = await self.get_by_account_symbol(db, account_id, symbol)

        if existing:
            # 更新
            for key, value in data.items():
                if hasattr(existing, key):
                    setattr(existing, key, value)
            await db.commit()
            await db.refresh(existing)
            return existing
        else:
            # 创建
            return await self.create(db, data)

    async def update(self, db: AsyncSession, holding_id: int, data: dict) -> Optional[Holding]:
        """
        更新持仓记录

        Args:
            db: 数据库会话
            holding_id: 持仓ID
            data: 更新数据字典

        Returns:
            更新后的Holding对象，不存在返回None
        """
        holding = await self.get_by_id(db, holding_id)
        if not holding:
            return None

        for key, value in data.items():
            if hasattr(holding, key):
                setattr(holding, key, value)

        await db.commit()
        await db.refresh(holding)
        return holding

    async def soft_delete(self, db: AsyncSession, holding_id: int) -> bool:
        """
        软删除持仓记录

        Args:
            db: 数据库会话
            holding_id: 持仓ID

        Returns:
            是否删除成功
        """
        from datetime import datetime

        holding = await self.get_by_id(db, holding_id)
        if not holding:
            return False

        holding.is_deleted = True
        holding.deleted_at = datetime.utcnow()

        await db.commit()
        return True
