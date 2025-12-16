"""
Stock Query Service

股票查询业务服务 - Service + Converter + Builder
"""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.stock_repo import StockRepository
from app.schemas.common import PaginationResponse


class StockQueryService:
    """
    股票查询业务类

    职责：编排流程、事务管理
    """

    def __init__(self):
        self.stock_repo = StockRepository()

    async def execute(self, db: AsyncSession, market: Optional[str] = None, page: int = 1, page_size: int = 20) -> dict:
        """
        执行股票查询业务逻辑

        Args:
            db: 数据库会话
            market: 市场类型筛选（可选）
            page: 页码
            page_size: 每页数量

        Returns:
            分页的股票列表数据
        """
        # 1. 查询股票列表
        stocks, total = await self.stock_repo.query_all(db=db, market=market, page=page, page_size=page_size)

        # 2. 调用 Converter 转换数据
        items = StockQueryConverter.convert(stocks)

        # 3. 调用 Builder 构建响应
        return StockQueryBuilder.build_response(items, total, page, page_size)


class StockQueryConverter:
    """
    股票查询转换器（静态类）

    职责：业务逻辑计算
    """

    @staticmethod
    def convert(stocks: list) -> list:
        """
        将股票列表转换为业务数据

        Args:
            stocks: 股票对象列表

        Returns:
            转换后的股票数据列表
        """
        result = []
        for stock in stocks:
            stock_data = {
                "stock_id": stock.stock_id,
                "symbol": stock.symbol,
                "name": stock.name,
                "market": stock.market,
                "industry": stock.industry,
                "current_price": float(stock.current_price) if stock.current_price else None,
                "change_percent": float(stock.change_percent) if stock.change_percent else None,
                "volume": float(stock.volume) if stock.volume else None,
                "market_cap": float(stock.market_cap) if stock.market_cap else None,
                "pe_ratio": float(stock.pe_ratio) if stock.pe_ratio else None,
                "updated_at": stock.updated_at.isoformat() if stock.updated_at else None,
            }
            result.append(stock_data)

        return result


class StockQueryBuilder:
    """
    股票查询数据构建器（静态类）

    职责：构建响应对象
    """

    @staticmethod
    def build_response(items: list, total: int, page: int, page_size: int) -> dict:
        """
        构建分页响应

        Args:
            items: 股票数据列表
            total: 总记录数
            page: 当前页码
            page_size: 每页数量

        Returns:
            分页响应字典
        """
        pagination = PaginationResponse.create(items=items, total=total, page=page, page_size=page_size)
        return pagination.dict()
