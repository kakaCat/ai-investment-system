"""
Stock Repository

纯数据访问层 - 只负责股票表的CRUD操作，不包含任何业务逻辑
"""

from typing import List, Optional
from sqlalchemy import select, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.stock import Stock


class StockRepository:
    """股票数据访问层（纯CRUD，无业务逻辑）"""

    async def get_by_symbol(self, db: AsyncSession, symbol: str) -> Optional[Stock]:
        """
        根据股票代码查询

        Args:
            db: 数据库会话
            symbol: 股票代码

        Returns:
            Stock对象，不存在返回None
        """
        result = await db.execute(select(Stock).where(and_(Stock.symbol == symbol, Stock.is_deleted is False)))
        return result.scalar_one_or_none()

    async def search(
        self, db: AsyncSession, keyword: str, market: Optional[str] = None, limit: int = 20
    ) -> List[Stock]:
        """
        搜索股票（支持代码和名称模糊查询）

        Args:
            db: 数据库会话
            keyword: 搜索关键词
            market: 市场类型（可选）
            limit: 返回数量限制

        Returns:
            股票列表
        """
        conditions = [Stock.is_deleted is False]

        # 模糊搜索（代码或名称）
        conditions.append(or_(Stock.symbol.ilike(f"%{keyword}%"), Stock.name.ilike(f"%{keyword}%")))

        if market:
            conditions.append(Stock.market == market)

        query = select(Stock).where(and_(*conditions)).order_by(Stock.symbol).limit(limit)

        result = await db.execute(query)
        return list(result.scalars().all())

    async def query_by_market(
        self, db: AsyncSession, market: str, page: int = 1, page_size: int = 50
    ) -> tuple[List[Stock], int]:
        """
        查询某个市场的所有股票（分页）

        Args:
            db: 数据库会话
            market: 市场类型
            page: 页码
            page_size: 每页数量

        Returns:
            (股票列表, 总数)
        """
        conditions = [Stock.market == market, Stock.is_deleted is False]

        # 查询总数
        count_query = select(Stock).where(and_(*conditions))
        count_result = await db.execute(count_query)
        total = len(count_result.scalars().all())

        # 查询列表
        query = (
            select(Stock)
            .where(and_(*conditions))
            .order_by(Stock.symbol)
            .offset((page - 1) * page_size)
            .limit(page_size)
        )

        result = await db.execute(query)
        stocks = result.scalars().all()

        return list(stocks), total

    async def create(self, db: AsyncSession, data: dict) -> Stock:
        """
        创建股票记录

        Args:
            db: 数据库会话
            data: 股票数据字典

        Returns:
            创建的Stock对象
        """
        stock = Stock(**data)
        db.add(stock)
        await db.commit()
        await db.refresh(stock)
        return stock

    async def create_or_update(self, db: AsyncSession, data: dict) -> Stock:
        """
        创建或更新股票记录（如果symbol已存在则更新）

        Args:
            db: 数据库会话
            data: 股票数据字典（必须包含symbol）

        Returns:
            Stock对象
        """
        symbol = data.get("symbol")
        if not symbol:
            raise ValueError("symbol is required")

        # 查找是否已存在
        existing = await self.get_by_symbol(db, symbol)

        if existing:
            # 更新
            for key, value in data.items():
                if hasattr(existing, key) and key != "symbol":  # symbol不能修改
                    setattr(existing, key, value)
            await db.commit()
            await db.refresh(existing)
            return existing
        else:
            # 创建
            return await self.create(db, data)

    async def update(self, db: AsyncSession, symbol: str, data: dict) -> Optional[Stock]:
        """
        更新股票信息

        Args:
            db: 数据库会话
            symbol: 股票代码
            data: 更新数据字典

        Returns:
            更新后的Stock对象，不存在返回None
        """
        stock = await self.get_by_symbol(db, symbol)
        if not stock:
            return None

        for key, value in data.items():
            if hasattr(stock, key) and key != "symbol":  # symbol不能修改
                setattr(stock, key, value)

        await db.commit()
        await db.refresh(stock)
        return stock

    async def soft_delete(self, db: AsyncSession, symbol: str) -> bool:
        """
        软删除股票记录

        Args:
            db: 数据库会话
            symbol: 股票代码

        Returns:
            是否删除成功
        """
        from datetime import datetime

        stock = await self.get_by_symbol(db, symbol)
        if not stock:
            return False

        stock.is_deleted = True
        stock.deleted_at = datetime.utcnow()

        await db.commit()
        return True

    async def batch_create_or_update(self, db: AsyncSession, stocks_data: List[dict]) -> int:
        """
        批量创建或更新股票（用于数据同步）

        Args:
            db: 数据库会话
            stocks_data: 股票数据列表

        Returns:
            处理的股票数量
        """
        count = 0
        for data in stocks_data:
            await self.create_or_update(db, data)
            count += 1

        return count
