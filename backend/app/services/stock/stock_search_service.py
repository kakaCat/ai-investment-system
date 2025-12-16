"""
Stock Search Service

股票搜索业务服务 - Service + Converter + Builder
"""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.stock_repo import StockRepository
from app.exceptions import ValidationError


class StockSearchService:
    """
    股票搜索业务类

    职责：编排流程、事务管理
    """

    def __init__(self):
        self.stock_repo = StockRepository()

    async def execute(self, db: AsyncSession, keyword: str, market: Optional[str] = None, limit: int = 20) -> dict:
        """
        执行股票搜索业务逻辑

        Args:
            db: 数据库会话
            keyword: 搜索关键词（股票代码或名称）
            market: 市场类型筛选（可选）
            limit: 最大返回数量

        Returns:
            搜索结果列表

        Raises:
            ValidationError: 参数验证失败
        """
        # 1. 验证参数
        StockSearchConverter.validate(keyword, limit)

        # 2. 搜索股票
        stocks = await self.stock_repo.search(db=db, keyword=keyword, market=market, limit=limit)

        # 3. 调用 Converter 转换数据
        items = StockSearchConverter.convert(stocks)

        # 4. 调用 Builder 构建响应
        return StockSearchBuilder.build_response(items, keyword)


class StockSearchConverter:
    """
    股票搜索转换器（静态类）

    职责：数据验证、业务逻辑处理
    """

    @staticmethod
    def validate(keyword: str, limit: int) -> None:
        """
        验证搜索参数

        Args:
            keyword: 搜索关键词
            limit: 最大返回数量

        Raises:
            ValidationError: 验证失败
        """
        # 验证关键词
        if not keyword or len(keyword.strip()) == 0:
            raise ValidationError("搜索关键词不能为空")

        if len(keyword) > 100:
            raise ValidationError("搜索关键词长度不能超过100个字符")

        # 验证限制数量
        if limit < 1 or limit > 100:
            raise ValidationError("返回数量必须在1-100之间")

    @staticmethod
    def convert(stocks: list) -> list:
        """
        将股票列表转换为搜索结果数据

        Args:
            stocks: 股票对象列表

        Returns:
            转换后的搜索结果列表
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
            }
            result.append(stock_data)

        return result


class StockSearchBuilder:
    """
    股票搜索数据构建器（静态类）

    职责：构建响应对象
    """

    @staticmethod
    def build_response(items: list, keyword: str) -> dict:
        """
        构建搜索响应

        Args:
            items: 搜索结果列表
            keyword: 搜索关键词

        Returns:
            搜索响应字典
        """
        return {
            "items": items,
            "total": len(items),
            "keyword": keyword,
        }
