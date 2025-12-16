"""
Stock Detail Service

股票详情业务服务 - Service + Converter + Builder
"""

from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.stock_repo import StockRepository
from app.exceptions import ResourceNotFound


class StockDetailService:
    """
    股票详情业务类

    职责：编排流程、事务管理
    """

    def __init__(self):
        self.stock_repo = StockRepository()

    async def execute(self, db: AsyncSession, symbol: str) -> dict:
        """
        执行股票详情查询业务逻辑

        Args:
            db: 数据库会话
            symbol: 股票代码

        Returns:
            股票详情数据

        Raises:
            ResourceNotFound: 股票不存在
        """
        # 1. 查询股票
        stock = await self.stock_repo.get_by_symbol(db, symbol)
        if not stock:
            raise ResourceNotFound(f"股票代码 {symbol} 不存在")

        # 2. 调用 Converter 转换数据
        return StockDetailConverter.convert(stock)


class StockDetailConverter:
    """
    股票详情转换器（静态类）

    职责：业务逻辑计算
    """

    @staticmethod
    def convert(stock) -> dict:
        """
        将股票对象转换为详情数据

        Args:
            stock: 股票对象

        Returns:
            股票详情字典
        """
        return {
            "stock_id": stock.stock_id,
            "symbol": stock.symbol,
            "name": stock.name,
            "market": stock.market,
            "industry": stock.industry,
            "sector": stock.sector,
            "company_name": stock.company_name,
            "description": stock.description,
            # 价格信息
            "current_price": float(stock.current_price) if stock.current_price else None,
            "change_percent": float(stock.change_percent) if stock.change_percent else None,
            "day_high": float(stock.day_high) if stock.day_high else None,
            "day_low": float(stock.day_low) if stock.day_low else None,
            "open_price": float(stock.open_price) if stock.open_price else None,
            "close_price": float(stock.close_price) if stock.close_price else None,
            # 交易量信息
            "volume": float(stock.volume) if stock.volume else None,
            "turnover": float(stock.turnover) if stock.turnover else None,
            # 基本面信息
            "market_cap": float(stock.market_cap) if stock.market_cap else None,
            "pe_ratio": float(stock.pe_ratio) if stock.pe_ratio else None,
            "pb_ratio": float(stock.pb_ratio) if stock.pb_ratio else None,
            "dividend_yield": float(stock.dividend_yield) if stock.dividend_yield else None,
            # 时间戳
            "created_at": stock.created_at.isoformat() if stock.created_at else None,
            "updated_at": stock.updated_at.isoformat() if stock.updated_at else None,
        }
