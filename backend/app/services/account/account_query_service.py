"""
Account Query Service

账户查询业务服务 - Service + Converter + Builder
"""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.account_repo import AccountRepository
from app.repositories.holding_repo import HoldingRepository
from app.schemas.common import PaginationResponse


class AccountQueryService:
    """
    账户查询业务类

    职责：权限校验、编排流程、事务管理
    """

    def __init__(self):
        self.account_repo = AccountRepository()
        self.holding_repo = HoldingRepository()

    async def execute(
        self,
        db: AsyncSession,
        user_id: int,
        market: Optional[str] = None,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> dict:
        """
        执行账户查询业务逻辑

        Args:
            db: 数据库会话
            user_id: 用户ID
            market: 市场筛选（可选）
            status: 状态筛选（可选）
            page: 页码
            page_size: 每页数量

        Returns:
            分页查询结果
        """
        # 1. 查询账户列表
        accounts, total = await self.account_repo.query_by_user(
            db=db,
            user_id=user_id,
            market=market,
            status=status,
            page=page,
            page_size=page_size
        )

        # 2. 查询每个账户的持仓统计（用于显示账户总市值等）
        account_ids = [acc.account_id for acc in accounts]
        holdings_map = {}
        for account_id in account_ids:
            holdings = await self.holding_repo.query_by_account(db, account_id)
            holdings_map[account_id] = holdings

        # 3. 调用 Converter 转换数据
        items = AccountQueryConverter.convert(accounts, holdings_map)

        # 4. 调用 Builder 构建响应
        return AccountQueryBuilder.build_response(items, total, page, page_size)


class AccountQueryConverter:
    """
    账户查询转换器（静态类）

    职责：业务逻辑计算
    """

    @staticmethod
    def convert(accounts, holdings_map) -> list:
        """
        将账户列表转换为业务数据

        Args:
            accounts: 账户对象列表
            holdings_map: 账户ID到持仓列表的映射

        Returns:
            转换后的数据列表
        """
        result = []
        for account in accounts:
            holdings = holdings_map.get(account.account_id, [])

            # 计算账户统计数据
            total_value = AccountQueryConverter._calculate_total_value(holdings)
            total_cost = AccountQueryConverter._calculate_total_cost(holdings)
            total_pnl = total_value - total_cost
            total_pnl_rate = (total_pnl / total_cost * 100) if total_cost > 0 else 0.0

            # 构建单个账户数据
            result.append({
                "account_id": account.account_id,
                "account_name": account.account_name,
                "market": account.market,
                "status": account.status,
                "broker": account.broker,
                "initial_capital": float(account.initial_capital) if account.initial_capital else 0.0,
                "current_capital": float(account.current_capital) if account.current_capital else 0.0,
                "total_value": total_value,
                "total_cost": total_cost,
                "total_pnl": total_pnl,
                "total_pnl_rate": round(total_pnl_rate, 2),
                "holding_count": len(holdings),
                "created_at": account.created_at.isoformat() if account.created_at else None,
            })

        return result

    @staticmethod
    def _calculate_total_value(holdings) -> float:
        """
        计算持仓总市值

        Args:
            holdings: 持仓列表

        Returns:
            总市值
        """
        return sum(
            float(h.quantity) * float(h.current_price)
            for h in holdings
            if h.quantity and h.current_price
        )

    @staticmethod
    def _calculate_total_cost(holdings) -> float:
        """
        计算持仓总成本

        Args:
            holdings: 持仓列表

        Returns:
            总成本
        """
        return sum(
            float(h.quantity) * float(h.cost_price)
            for h in holdings
            if h.quantity and h.cost_price
        )


class AccountQueryBuilder:
    """
    账户查询数据构建器（静态类）

    职责：构建响应对象
    """

    @staticmethod
    def build_response(items: list, total: int, page: int, page_size: int) -> dict:
        """
        构建分页响应

        Args:
            items: 数据列表
            total: 总数
            page: 当前页码
            page_size: 每页数量

        Returns:
            分页响应字典
        """
        pagination = PaginationResponse.create(
            items=items,
            total=total,
            page=page,
            page_size=page_size
        )

        return pagination.dict()
