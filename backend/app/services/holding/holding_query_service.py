"""
Holding Query Service

持仓查询业务服务 - Service + Converter + Builder
"""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.holding_repo import HoldingRepository
from app.repositories.account_repo import AccountRepository
from app.exceptions import ResourceNotFound, PermissionDenied


class HoldingQueryService:
    """
    持仓查询业务类

    职责：权限校验、编排流程、事务管理
    """

    def __init__(self):
        self.holding_repo = HoldingRepository()
        self.account_repo = AccountRepository()

    async def execute(
        self,
        db: AsyncSession,
        user_id: int,
        account_id: Optional[int] = None
    ) -> dict:
        """
        执行持仓查询业务逻辑

        Args:
            db: 数据库会话
            user_id: 用户ID
            account_id: 账户ID（为空则查询所有账户持仓）

        Returns:
            持仓列表数据（含统计信息）

        Raises:
            ResourceNotFound: 账户不存在
            PermissionDenied: 无权访问
        """
        # 1. 如果指定了account_id，进行权限校验
        if account_id is not None:
            account = await self.account_repo.get_by_id(db, account_id)
            if not account:
                raise ResourceNotFound(f"账户ID {account_id} 不存在")

            if account.user_id != user_id:
                raise PermissionDenied(f"无权访问账户ID {account_id}")

            # 2. 查询指定账户的持仓列表
            holdings = await self.holding_repo.query_by_account(db, account_id)
        else:
            # 2. 查询用户所有账户的持仓列表
            holdings = await self.holding_repo.query_by_user(db, user_id)

        # 3. 调用 Converter 转换数据和计算统计
        items, summary = HoldingQueryConverter.convert(holdings)

        # 4. 调用 Builder 构建响应
        return HoldingQueryBuilder.build_response(items, summary)


class HoldingQueryConverter:
    """
    持仓查询转换器（静态类）

    职责：业务逻辑计算
    """

    @staticmethod
    def convert(holdings: list) -> tuple[list, dict]:
        """
        将持仓列表转换为业务数据并计算汇总统计

        Args:
            holdings: 持仓对象列表

        Returns:
            (持仓数据列表, 汇总统计)
        """
        items = []
        total_cost = 0.0
        total_value = 0.0
        total_profit_loss = 0.0

        for holding in holdings:
            # 计算单个持仓数据
            item = HoldingQueryConverter._convert_single(holding)
            items.append(item)

            # 累计汇总数据
            total_cost += item["cost_basis"]
            total_value += item["market_value"]
            total_profit_loss += item["profit_loss"]

        # 计算汇总统计
        summary = {
            "total_holdings": len(items),
            "total_cost": round(total_cost, 2),
            "total_value": round(total_value, 2),
            "total_profit_loss": round(total_profit_loss, 2),
            "total_profit_loss_percent": round((total_profit_loss / total_cost * 100), 2) if total_cost > 0 else 0.0,
        }

        return items, summary

    @staticmethod
    def _convert_single(holding) -> dict:
        """
        转换单个持仓对象

        Args:
            holding: 持仓对象

        Returns:
            持仓数据字典
        """
        quantity = float(holding.quantity) if holding.quantity else 0.0
        avg_cost = float(holding.average_cost) if holding.average_cost else 0.0
        current_price = float(holding.current_price) if holding.current_price else 0.0

        # 计算成本
        cost_basis = quantity * avg_cost

        # 计算市值
        market_value = quantity * current_price

        # 计算盈亏
        profit_loss = market_value - cost_basis

        # 计算盈亏百分比
        profit_loss_percent = (profit_loss / cost_basis * 100) if cost_basis > 0 else 0.0

        return {
            "holding_id": holding.holding_id,
            "account_id": holding.account_id,
            "symbol": holding.symbol,
            "stock_name": holding.stock_name,
            "quantity": quantity,
            "average_cost": avg_cost,
            "current_price": current_price,
            "cost_basis": round(cost_basis, 2),
            "market_value": round(market_value, 2),
            "profit_loss": round(profit_loss, 2),
            "profit_loss_percent": round(profit_loss_percent, 2),
            "updated_at": holding.updated_at.isoformat() if holding.updated_at else None,
        }


class HoldingQueryBuilder:
    """
    持仓查询数据构建器（静态类）

    职责：构建响应对象
    """

    @staticmethod
    def build_response(items: list, summary: dict) -> dict:
        """
        构建持仓查询响应

        Args:
            items: 持仓数据列表
            summary: 汇总统计

        Returns:
            持仓响应字典
        """
        return {
            "holdings": items,
            "summary": summary,
        }
