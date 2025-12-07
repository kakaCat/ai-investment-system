"""
Account Detail Service

账户详情业务服务 - Service + Converter + Builder
"""

from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.account_repo import AccountRepository
from app.repositories.holding_repo import HoldingRepository
from app.exceptions import AccountNotFound, AccountAccessDenied


class AccountDetailService:
    """
    账户详情业务类

    职责：权限校验、编排流程、事务管理
    """

    def __init__(self):
        self.account_repo = AccountRepository()
        self.holding_repo = HoldingRepository()

    async def execute(self, db: AsyncSession, account_id: int, user_id: int) -> dict:
        """
        执行账户详情查询业务逻辑

        Args:
            db: 数据库会话
            account_id: 账户ID
            user_id: 用户ID

        Returns:
            账户详情数据

        Raises:
            AccountNotFound: 账户不存在
            AccountAccessDenied: 无权访问该账户
        """
        # 1. 权限校验 - 查询账户
        account = await self.account_repo.get_by_id(db, account_id)
        if not account:
            raise AccountNotFound(f"账户ID {account_id} 不存在")

        if account.user_id != user_id:
            raise AccountAccessDenied(f"无权访问账户ID {account_id}")

        # 2. 查询持仓列表
        holdings = await self.holding_repo.query_by_account(db, account_id)

        # 3. 调用 Converter 转换数据
        return AccountDetailConverter.convert(account, holdings)


class AccountDetailConverter:
    """
    账户详情转换器（静态类）

    职责：业务逻辑计算
    """

    @staticmethod
    def convert(account, holdings) -> dict:
        """
        将账户和持仓数据转换为详情业务数据

        Args:
            account: 账户对象
            holdings: 持仓列表

        Returns:
            账户详情字典
        """
        # 计算统计数据
        total_value = AccountDetailConverter._calculate_total_value(holdings)
        total_cost = AccountDetailConverter._calculate_total_cost(holdings)
        total_pnl = total_value - total_cost
        total_pnl_rate = (total_pnl / total_cost * 100) if total_cost > 0 else 0.0

        # 调用 Builder 构建响应
        return AccountDetailBuilder.build_response(
            account=account,
            holdings=holdings,
            total_value=total_value,
            total_cost=total_cost,
            total_pnl=total_pnl,
            total_pnl_rate=total_pnl_rate
        )

    @staticmethod
    def _calculate_total_value(holdings) -> float:
        """计算持仓总市值"""
        return sum(
            float(h.quantity) * float(h.current_price)
            for h in holdings
            if h.quantity and h.current_price
        )

    @staticmethod
    def _calculate_total_cost(holdings) -> float:
        """计算持仓总成本"""
        return sum(
            float(h.quantity) * float(h.cost_price)
            for h in holdings
            if h.quantity and h.cost_price
        )


class AccountDetailBuilder:
    """
    账户详情数据构建器（静态类）

    职责：构建响应对象
    """

    @staticmethod
    def build_response(
        account,
        holdings,
        total_value: float,
        total_cost: float,
        total_pnl: float,
        total_pnl_rate: float
    ) -> dict:
        """
        构建账户详情响应

        Args:
            account: 账户对象
            holdings: 持仓列表
            total_value: 总市值
            total_cost: 总成本
            total_pnl: 总盈亏
            total_pnl_rate: 总盈亏率

        Returns:
            账户详情字典
        """
        return {
            "account_info": {
                "account_id": account.account_id,
                "account_name": account.account_name,
                "market": account.market,
                "status": account.status,
                "broker": account.broker,
                "account_number": account.account_number,
                "initial_capital": float(account.initial_capital) if account.initial_capital else 0.0,
                "current_capital": float(account.current_capital) if account.current_capital else 0.0,
                "created_at": account.created_at.isoformat() if account.created_at else None,
                "updated_at": account.updated_at.isoformat() if account.updated_at else None,
            },
            "holdings": [
                AccountDetailBuilder._build_holding(h)
                for h in holdings
            ],
            "statistics": {
                "total_value": round(total_value, 2),
                "total_cost": round(total_cost, 2),
                "total_pnl": round(total_pnl, 2),
                "total_pnl_rate": round(total_pnl_rate, 2),
                "holding_count": len(holdings),
                "available_capital": float(account.current_capital) if account.current_capital else 0.0,
                "total_assets": round(total_value + (float(account.current_capital) if account.current_capital else 0.0), 2),
            }
        }

    @staticmethod
    def _build_holding(holding) -> dict:
        """
        构建单个持仓数据

        Args:
            holding: 持仓对象

        Returns:
            持仓字典
        """
        quantity = float(holding.quantity) if holding.quantity else 0.0
        cost_price = float(holding.cost_price) if holding.cost_price else 0.0
        current_price = float(holding.current_price) if holding.current_price else 0.0

        pnl = (current_price - cost_price) * quantity
        pnl_rate = ((current_price - cost_price) / cost_price * 100) if cost_price > 0 else 0.0

        return {
            "holding_id": holding.holding_id,
            "symbol": holding.symbol,
            "stock_name": holding.stock_name,
            "quantity": quantity,
            "available_quantity": float(holding.available_quantity) if holding.available_quantity else 0.0,
            "cost_price": cost_price,
            "current_price": current_price,
            "market_value": round(quantity * current_price, 2),
            "total_cost": round(quantity * cost_price, 2),
            "pnl": round(pnl, 2),
            "pnl_rate": round(pnl_rate, 2),
            "updated_at": holding.updated_at.isoformat() if holding.updated_at else None,
        }
