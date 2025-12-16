"""
Trade Query Service

交易查询业务服务 - Service + Converter + Builder
"""

from typing import Optional
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.trade_repo import TradeRepository
from app.schemas.common import PaginationResponse


class TradeQueryService:
    """
    交易查询业务类

    职责：权限校验、编排流程、事务管理
    """

    def __init__(self):
        self.trade_repo = TradeRepository()

    async def execute(
        self,
        db: AsyncSession,
        user_id: int,
        account_id: Optional[int] = None,
        symbol: Optional[str] = None,
        trade_type: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        """
        执行交易查询业务逻辑

        Args:
            db: 数据库会话
            user_id: 用户ID
            account_id: 账户ID筛选（可选）
            symbol: 股票代码筛选（可选）
            trade_type: 交易类型筛选（可选）
            start_date: 开始日期（可选）
            end_date: 结束日期（可选）
            page: 页码
            page_size: 每页数量

        Returns:
            分页的交易列表数据
        """
        # 1. 查询交易列表（Repository已包含user_id权限控制）
        trades, total = await self.trade_repo.query_by_user(
            db=db,
            user_id=user_id,
            account_id=account_id,
            symbol=symbol,
            trade_type=trade_type,
            start_date=start_date,
            end_date=end_date,
            page=page,
            page_size=page_size,
        )

        # 2. 调用 Converter 转换数据
        items = TradeQueryConverter.convert(trades)

        # 3. 调用 Builder 构建响应
        return TradeQueryBuilder.build_response(items, total, page, page_size)


class TradeQueryConverter:
    """
    交易查询转换器（静态类）

    职责：业务逻辑计算
    """

    @staticmethod
    def convert(trades: list) -> list:
        """
        将交易列表转换为业务数据

        Args:
            trades: 交易对象列表

        Returns:
            转换后的交易数据列表
        """
        result = []
        for trade in trades:
            # 计算交易金额
            total_amount = TradeQueryConverter._calculate_total_amount(trade)

            # 计算盈亏（如果是卖出）
            profit_loss = TradeQueryConverter._calculate_profit_loss(trade)

            trade_data = {
                "trade_id": trade.trade_id,
                "account_id": trade.account_id,
                "symbol": trade.symbol,
                "stock_name": trade.stock_name,
                "trade_type": trade.trade_type,
                "quantity": float(trade.quantity) if trade.quantity else 0.0,
                "price": float(trade.price) if trade.price else 0.0,
                "total_amount": total_amount,
                "commission": float(trade.commission) if trade.commission else 0.0,
                "tax": float(trade.tax) if trade.tax else 0.0,
                "profit_loss": profit_loss,
                "trade_date": trade.trade_date.isoformat() if trade.trade_date else None,
                "notes": trade.notes,
                "created_at": trade.created_at.isoformat() if trade.created_at else None,
            }
            result.append(trade_data)

        return result

    @staticmethod
    def _calculate_total_amount(trade) -> float:
        """
        计算交易总金额

        Args:
            trade: 交易对象

        Returns:
            交易总金额
        """
        if not trade.quantity or not trade.price:
            return 0.0

        # 总金额 = 数量 × 价格
        return float(trade.quantity * trade.price)

    @staticmethod
    def _calculate_profit_loss(trade) -> Optional[float]:
        """
        计算盈亏（仅卖出交易）

        Args:
            trade: 交易对象

        Returns:
            盈亏金额（卖出时）或 None（买入时）
        """
        if trade.trade_type != "sell" or not trade.profit_loss:
            return None

        return float(trade.profit_loss)


class TradeQueryBuilder:
    """
    交易查询数据构建器（静态类）

    职责：构建响应对象
    """

    @staticmethod
    def build_response(items: list, total: int, page: int, page_size: int) -> dict:
        """
        构建分页响应

        Args:
            items: 交易数据列表
            total: 总记录数
            page: 当前页码
            page_size: 每页数量

        Returns:
            分页响应字典
        """
        pagination = PaginationResponse.create(items=items, total=total, page=page, page_size=page_size)
        return pagination.dict()
