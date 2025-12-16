"""
Strategy Query Service

策略查询业务服务 - Service + Converter + Builder
"""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.strategy_repo import StrategyRepository
from app.schemas.common import PaginationResponse


class StrategyQueryService:
    """
    策略查询业务类

    职责:权限校验、编排流程、事务管理
    """

    def __init__(self):
        self.strategy_repo = StrategyRepository()

    async def execute(
        self,
        db: AsyncSession,
        user_id: int,
        symbol: Optional[str] = None,
        strategy_type: Optional[str] = None,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        """
        执行策略查询业务逻辑

        Args:
            db: 数据库会话
            user_id: 用户ID
            symbol: 股票代码（可选）
            strategy_type: 策略类型（可选）
            status: 策略状态（可选）
            page: 页码
            page_size: 每页数量

        Returns:
            分页查询结果
        """
        # 1. 查询策略列表
        strategies, total = await self.strategy_repo.query_by_user(
            db=db,
            user_id=user_id,
            symbol=symbol,
            strategy_type=strategy_type,
            status=status,
            page=page,
            page_size=page_size,
        )

        # 2. 调用 Converter 转换数据
        items = StrategyQueryConverter.convert(strategies)

        # 3. 调用 Builder 构建响应
        return StrategyQueryBuilder.build_response(items, total, page, page_size)


class StrategyQueryConverter:
    """
    策略查询转换器（静态类）

    职责：业务逻辑计算
    """

    @staticmethod
    def convert(strategies) -> list:
        """
        将策略列表转换为业务数据

        Args:
            strategies: 策略对象列表

        Returns:
            转换后的数据列表
        """
        result = []
        for strategy in strategies:
            result.append(
                {
                    "strategy_id": strategy.strategy_id,
                    "symbol": strategy.symbol,
                    "stock_name": strategy.stock_name,
                    "strategy_type": strategy.strategy_type,
                    "trigger_price": float(strategy.trigger_price) if strategy.trigger_price else None,
                    "target_quantity": float(strategy.target_quantity) if strategy.target_quantity else None,
                    "reason": strategy.reason,
                    "notes": strategy.notes,
                    "status": strategy.status,
                    "priority": strategy.priority,
                    "is_stop_loss": strategy.is_stop_loss,
                    "is_take_profit": strategy.is_take_profit,
                    "executed_at": strategy.executed_at.isoformat() if strategy.executed_at else None,
                    "executed_price": float(strategy.executed_price) if strategy.executed_price else None,
                    "executed_quantity": float(strategy.executed_quantity) if strategy.executed_quantity else None,
                    "created_at": strategy.created_at.isoformat() if strategy.created_at else None,
                    "updated_at": strategy.updated_at.isoformat() if strategy.updated_at else None,
                }
            )

        return result


class StrategyQueryBuilder:
    """
    策略查询数据构建器（静态类）

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
        pagination = PaginationResponse.create(items=items, total=total, page=page, page_size=page_size)

        return pagination.dict()
