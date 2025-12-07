"""
Trade Detail Service

交易详情业务服务 - Service + Converter + Builder
"""

from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.trade_repo import TradeRepository
from app.exceptions import ResourceNotFound, PermissionDenied


class TradeDetailService:
    """
    交易详情业务类

    职责：权限校验、编排流程、事务管理
    """

    def __init__(self):
        self.trade_repo = TradeRepository()

    async def execute(self, db: AsyncSession, trade_id: int, user_id: int) -> dict:
        """
        执行交易详情查询业务逻辑

        Args:
            db: 数据库会话
            trade_id: 交易ID
            user_id: 用户ID

        Returns:
            交易详情数据

        Raises:
            ResourceNotFound: 交易不存在
            PermissionDenied: 无权访问
        """
        # 1. 权限校验 - 查询交易
        trade = await self.trade_repo.get_by_id(db, trade_id)
        if not trade:
            raise ResourceNotFound(f"交易ID {trade_id} 不存在")

        if trade.user_id != user_id:
            raise PermissionDenied(f"无权访问交易ID {trade_id}")

        # 2. 调用 Converter 转换数据
        return TradeDetailConverter.convert(trade)


class TradeDetailConverter:
    """
    交易详情转换器（静态类）

    职责：业务逻辑计算
    """

    @staticmethod
    def convert(trade) -> dict:
        """
        将交易对象转换为详情数据

        Args:
            trade: 交易对象

        Returns:
            交易详情字典
        """
        # 计算交易金额
        total_amount = TradeDetailConverter._calculate_total_amount(trade)

        # 计算实际金额（含手续费和税费）
        actual_amount = TradeDetailConverter._calculate_actual_amount(trade, total_amount)

        return {
            "trade_id": trade.trade_id,
            "account_id": trade.account_id,
            "user_id": trade.user_id,
            "symbol": trade.symbol,
            "stock_name": trade.stock_name,
            "trade_type": trade.trade_type,
            "quantity": float(trade.quantity) if trade.quantity else 0.0,
            "price": float(trade.price) if trade.price else 0.0,
            "total_amount": total_amount,
            "commission": float(trade.commission) if trade.commission else 0.0,
            "tax": float(trade.tax) if trade.tax else 0.0,
            "actual_amount": actual_amount,
            "profit_loss": float(trade.profit_loss) if trade.profit_loss else None,
            "trade_date": trade.trade_date.isoformat() if trade.trade_date else None,
            "notes": trade.notes,
            "created_at": trade.created_at.isoformat() if trade.created_at else None,
            "updated_at": trade.updated_at.isoformat() if trade.updated_at else None,
        }

    @staticmethod
    def _calculate_total_amount(trade) -> float:
        """计算交易总金额"""
        if not trade.quantity or not trade.price:
            return 0.0
        return float(trade.quantity * trade.price)

    @staticmethod
    def _calculate_actual_amount(trade, total_amount: float) -> float:
        """
        计算实际金额

        买入: 总金额 + 手续费 + 税费
        卖出: 总金额 - 手续费 - 税费
        """
        commission = float(trade.commission) if trade.commission else 0.0
        tax = float(trade.tax) if trade.tax else 0.0

        if trade.trade_type == "buy":
            return total_amount + commission + tax
        else:  # sell
            return total_amount - commission - tax
