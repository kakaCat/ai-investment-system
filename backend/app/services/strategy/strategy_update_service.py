"""
Strategy Update Service

策略更新业务服务 - Service + Converter + Builder
"""

from typing import Optional
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.strategy_repo import StrategyRepository
from app.exceptions import ValidationError, PermissionDenied, ResourceNotFound


class StrategyUpdateService:
    """
    策略更新业务类

    职责：权限校验、编排流程、事务管理
    """

    def __init__(self):
        self.strategy_repo = StrategyRepository()

    async def execute(
        self,
        db: AsyncSession,
        user_id: int,
        strategy_id: int,
        trigger_price: Optional[Decimal] = None,
        target_quantity: Optional[Decimal] = None,
        reason: Optional[str] = None,
        notes: Optional[str] = None,
        priority: Optional[str] = None
    ) -> dict:
        """
        执行策略更新业务逻辑

        Args:
            db: 数据库会话
            user_id: 用户ID
            strategy_id: 策略ID
            trigger_price: 触发价格（可选）
            target_quantity: 目标数量（可选）
            reason: 策略原因（可选）
            notes: 备注（可选）
            priority: 优先级（可选）

        Returns:
            更新后的策略数据

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
        StrategyUpdateConverter.validate(
            trigger_price=trigger_price,
            target_quantity=target_quantity,
            priority=priority
        )

        # 3. 调用 Converter 准备数据
        data = StrategyUpdateConverter.prepare_data(
            trigger_price=trigger_price,
            target_quantity=target_quantity,
            reason=reason,
            notes=notes,
            priority=priority
        )

        # 4. 更新策略
        updated_strategy = await self.strategy_repo.update(db, strategy_id, data)

        # 5. 调用 Builder 构建响应
        return StrategyUpdateBuilder.build_response(updated_strategy)


class StrategyUpdateConverter:
    """
    策略更新转换器（静态类）

    职责：数据验证、业务逻辑处理
    """

    @staticmethod
    def validate(
        trigger_price: Optional[Decimal],
        target_quantity: Optional[Decimal],
        priority: Optional[str]
    ) -> None:
        """
        验证策略更新数据

        Args:
            trigger_price: 触发价格
            target_quantity: 目标数量
            priority: 优先级

        Raises:
            ValidationError: 验证失败
        """
        # 验证触发价格
        if trigger_price is not None and trigger_price <= 0:
            raise ValidationError("触发价格必须大于0")

        # 验证目标数量
        if target_quantity is not None and target_quantity <= 0:
            raise ValidationError("目标数量必须大于0")

        # 验证优先级
        if priority is not None:
            valid_priorities = ["urgent", "high", "normal", "low"]
            if priority not in valid_priorities:
                raise ValidationError(f"优先级必须是以下之一: {', '.join(valid_priorities)}")

    @staticmethod
    def prepare_data(
        trigger_price: Optional[Decimal],
        target_quantity: Optional[Decimal],
        reason: Optional[str],
        notes: Optional[str],
        priority: Optional[str]
    ) -> dict:
        """
        准备更新策略的数据（仅包含提供的字段）

        Args:
            trigger_price: 触发价格
            target_quantity: 目标数量
            reason: 策略原因
            notes: 备注
            priority: 优先级

        Returns:
            准备好的数据字典
        """
        data = {}

        if trigger_price is not None:
            data["trigger_price"] = trigger_price
        if target_quantity is not None:
            data["target_quantity"] = target_quantity
        if reason is not None:
            data["reason"] = reason.strip()
        if notes is not None:
            data["notes"] = notes.strip()
        if priority is not None:
            data["priority"] = priority

        return data


class StrategyUpdateBuilder:
    """
    策略更新数据构建器（静态类）

    职责：构建响应对象
    """

    @staticmethod
    def build_response(strategy) -> dict:
        """
        构建策略更新响应

        Args:
            strategy: 更新后的策略对象

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
            "created_at": strategy.created_at.isoformat() if strategy.created_at else None,
            "updated_at": strategy.updated_at.isoformat() if strategy.updated_at else None,
        }
