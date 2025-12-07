"""
Holding Sync Service

持仓同步业务服务 - Service + Converter + Builder

根据交易记录同步更新持仓数据
"""

from decimal import Decimal
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.holding_repo import HoldingRepository
from app.repositories.trade_repo import TradeRepository
from app.repositories.account_repo import AccountRepository
from app.exceptions import ResourceNotFound, PermissionDenied


class HoldingSyncService:
    """
    持仓同步业务类

    职责：权限校验、编排流程、事务管理
    """

    def __init__(self):
        self.holding_repo = HoldingRepository()
        self.trade_repo = TradeRepository()
        self.account_repo = AccountRepository()

    async def execute(
        self,
        db: AsyncSession,
        user_id: int,
        account_id: int
    ) -> dict:
        """
        执行持仓同步业务逻辑

        根据账户的所有交易记录重新计算持仓

        Args:
            db: 数据库会话
            user_id: 用户ID
            account_id: 账户ID

        Returns:
            同步结果

        Raises:
            ResourceNotFound: 账户不存在
            PermissionDenied: 无权访问
        """
        # 1. 权限校验 - 查询账户
        account = await self.account_repo.get_by_id(db, account_id)
        if not account:
            raise ResourceNotFound(f"账户ID {account_id} 不存在")

        if account.user_id != user_id:
            raise PermissionDenied(f"无权访问账户ID {account_id}")

        # 2. 查询该账户的所有交易
        trades, _ = await self.trade_repo.query_by_account(
            db=db,
            account_id=account_id,
            page=1,
            page_size=10000  # 获取所有交易
        )

        # 3. 调用 Converter 计算持仓
        holdings_data = HoldingSyncConverter.calculate_holdings(
            user_id=user_id,
            account_id=account_id,
            trades=trades
        )

        # 4. 更新数据库中的持仓
        updated_count = 0
        for symbol, holding_data in holdings_data.items():
            await self.holding_repo.upsert(db, holding_data)
            updated_count += 1

        # 5. 调用 Builder 构建响应
        return HoldingSyncBuilder.build_response(updated_count, len(holdings_data))


class HoldingSyncConverter:
    """
    持仓同步转换器（静态类）

    职责：业务逻辑计算
    """

    @staticmethod
    def calculate_holdings(
        user_id: int,
        account_id: int,
        trades: list
    ) -> dict:
        """
        根据交易列表计算持仓

        Args:
            user_id: 用户ID
            account_id: 账户ID
            trades: 交易列表

        Returns:
            持仓数据字典 {symbol: holding_data}
        """
        # 按股票代码分组计算持仓
        holdings = {}

        for trade in trades:
            symbol = trade.symbol

            # 初始化持仓
            if symbol not in holdings:
                holdings[symbol] = {
                    "user_id": user_id,
                    "account_id": account_id,
                    "symbol": symbol,
                    "stock_name": trade.stock_name,
                    "quantity": Decimal("0"),
                    "average_cost": Decimal("0"),
                    "total_cost": Decimal("0"),
                }

            holding = holdings[symbol]

            # 根据交易类型更新持仓
            if trade.trade_type == "buy":
                # 买入：增加数量，更新平均成本
                HoldingSyncConverter._process_buy(holding, trade)
            elif trade.trade_type == "sell":
                # 卖出：减少数量
                HoldingSyncConverter._process_sell(holding, trade)

        # 过滤掉数量为0的持仓
        holdings = {
            symbol: data
            for symbol, data in holdings.items()
            if data["quantity"] > 0
        }

        return holdings

    @staticmethod
    def _process_buy(holding: dict, trade) -> None:
        """
        处理买入交易

        Args:
            holding: 持仓数据
            trade: 交易对象
        """
        old_quantity = holding["quantity"]
        old_total_cost = holding["total_cost"]

        # 买入数量和成本
        buy_quantity = trade.quantity
        buy_cost = trade.price * buy_quantity

        # 新的总数量和总成本
        new_quantity = old_quantity + buy_quantity
        new_total_cost = old_total_cost + buy_cost

        # 新的平均成本
        new_average_cost = new_total_cost / new_quantity if new_quantity > 0 else Decimal("0")

        # 更新持仓
        holding["quantity"] = new_quantity
        holding["total_cost"] = new_total_cost
        holding["average_cost"] = new_average_cost
        holding["stock_name"] = trade.stock_name  # 更新股票名称

    @staticmethod
    def _process_sell(holding: dict, trade) -> None:
        """
        处理卖出交易

        Args:
            holding: 持仓数据
            trade: 交易对象
        """
        old_quantity = holding["quantity"]
        old_total_cost = holding["total_cost"]
        avg_cost = holding["average_cost"]

        # 卖出数量
        sell_quantity = trade.quantity

        # 新的数量
        new_quantity = old_quantity - sell_quantity

        # 新的总成本（按比例减少）
        new_total_cost = avg_cost * new_quantity if new_quantity > 0 else Decimal("0")

        # 更新持仓
        holding["quantity"] = new_quantity
        holding["total_cost"] = new_total_cost
        # 平均成本保持不变


class HoldingSyncBuilder:
    """
    持仓同步数据构建器（静态类）

    职责：构建响应对象
    """

    @staticmethod
    def build_response(updated_count: int, total_holdings: int) -> dict:
        """
        构建持仓同步响应

        Args:
            updated_count: 更新的持仓数量
            total_holdings: 总持仓数量

        Returns:
            同步结果字典
        """
        return {
            "success": True,
            "updated_count": updated_count,
            "total_holdings": total_holdings,
            "message": f"成功同步 {updated_count} 个持仓"
        }
