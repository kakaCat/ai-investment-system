"""
Strategy Execute Service

策略执行业务服务 - Service + Converter + Builder
"""

from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.strategy_repo import StrategyRepository
from app.exceptions import ValidationError, PermissionDenied, ResourceNotFound


class StrategyExecuteService:
    """
    策略执行业务类

    职责：权限校验、编排流程、事务管理
    """

    def __init__(self):
        self.strategy_repo = StrategyRepository()

    async def execute(
        self,
        db: AsyncSession,
        user_id: int,
        strategy_id: int,
        executed_price: Decimal,
        executed_quantity: Decimal
    ) -> dict:
        """
        执行策略标记业务逻辑

        Args:
            db: 数据库会话
            user_id: 用户ID
            strategy_id: 策略ID
            executed_price: 实际执行价格
            executed_quantity: 实际执行数量

        Returns:
            执行后的策略数据

        Raises:
            ValidationError: 数据验证失败
            PermissionDenied: 无权访问策略
            ResourceNotFound: 策略不存在
        """
        # 1. 权限校验 - 检查策略归属
        strategy = await self.strategy_repo.get_by_id(db, strategy_id)
        if not strategy:
            raise ResourceNotFound(f"策略ID {strategy_id} 不存在")

        if strategy.user_id != user_id:
            raise PermissionDenied(f"无权访问策略ID {strategy_id}")

        # 2. 数据验证
        StrategyExecuteConverter.validate(
            executed_price=executed_price,
            executed_quantity=executed_quantity
        )

        # 3. 执行策略
        executed_strategy = await self.strategy_repo.execute_strategy(
            db=db,
            strategy_id=strategy_id,
            executed_price=float(executed_price),
            executed_quantity=float(executed_quantity)
        )

        # 4. 调用 Builder 构建响应
        return StrategyExecuteBuilder.build_response(executed_strategy)


class StrategyExecuteConverter:
    """
    策略执行转换器（静态类）

    职责：数据验证、业务逻辑处理
    """

    @staticmethod
    def validate(
        executed_price: Decimal,
        executed_quantity: Decimal
    ) -> None:
        """
        验证策略执行数据

        Args:
            executed_price: 实际执行价格
            executed_quantity: 实际执行数量

        Raises:
            ValidationError: 验证失败
        """
        # 验证执行价格
        if executed_price <= 0:
            raise ValidationError("执行价格必须大于0")

        # 验证执行数量
        if executed_quantity <= 0:
            raise ValidationError("执行数量必须大于0")


class StrategyExecuteBuilder:
    """
    策略执行数据构建器（静态类）

    职责：构建响应对象
    """

    @staticmethod
    def build_response(strategy) -> dict:
        """
        构建策略执行响应

        Args:
            strategy: 执行后的策略对象

        Returns:
            策略数据字典
        """
        return {
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
