"""
Strategy Create Service

策略创建业务服务 - Service + Converter + Builder
"""

from typing import Optional
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.strategy_repo import StrategyRepository
from app.exceptions import ValidationError


class StrategyCreateService:
    """
    策略创建业务类

    职责：权限校验、编排流程、事务管理
    """

    def __init__(self):
        self.strategy_repo = StrategyRepository()

    async def execute(
        self,
        db: AsyncSession,
        user_id: int,
        symbol: str,
        stock_name: str,
        strategy_type: str,
        trigger_price: Optional[Decimal] = None,
        target_quantity: Optional[Decimal] = None,
        reason: Optional[str] = None,
        notes: Optional[str] = None,
        priority: str = "normal",
        is_stop_loss: bool = False,
        is_take_profit: bool = False,
    ) -> dict:
        """
        执行策略创建业务逻辑

        Args:
            db: 数据库会话
            user_id: 用户ID
            symbol: 股票代码
            stock_name: 股票名称
            strategy_type: 策略类型（buy/sell/hold）
            trigger_price: 触发价格（可选）
            target_quantity: 目标数量（可选）
            reason: 策略原因（可选）
            notes: 备注（可选）
            priority: 优先级（urgent/high/normal/low，默认normal）
            is_stop_loss: 是否止损策略（默认False）
            is_take_profit: 是否止盈策略（默认False）

        Returns:
            创建的策略数据

        Raises:
            ValidationError: 数据验证失败
        """
        # 1. 数据验证
        StrategyCreateConverter.validate(
            symbol=symbol,
            stock_name=stock_name,
            strategy_type=strategy_type,
            trigger_price=trigger_price,
            target_quantity=target_quantity,
            priority=priority,
        )

        # 2. 调用 Converter 准备数据
        data = StrategyCreateConverter.prepare_data(
            user_id=user_id,
            symbol=symbol,
            stock_name=stock_name,
            strategy_type=strategy_type,
            trigger_price=trigger_price,
            target_quantity=target_quantity,
            reason=reason,
            notes=notes,
            priority=priority,
            is_stop_loss=is_stop_loss,
            is_take_profit=is_take_profit,
        )

        # 3. 创建策略
        strategy = await self.strategy_repo.create(db, data)

        # 4. 调用 Builder 构建响应
        return StrategyCreateBuilder.build_response(strategy)


class StrategyCreateConverter:
    """
    策略创建转换器（静态类）

    职责：数据验证、业务逻辑处理
    """

    @staticmethod
    def validate(
        symbol: str,
        stock_name: str,
        strategy_type: str,
        trigger_price: Optional[Decimal],
        target_quantity: Optional[Decimal],
        priority: str,
    ) -> None:
        """
        验证策略创建数据

        Args:
            symbol: 股票代码
            stock_name: 股票名称
            strategy_type: 策略类型
            trigger_price: 触发价格
            target_quantity: 目标数量
            priority: 优先级

        Raises:
            ValidationError: 验证失败
        """
        # 验证股票代码
        if not symbol or len(symbol.strip()) == 0:
            raise ValidationError("股票代码不能为空")

        # 验证股票名称
        if not stock_name or len(stock_name.strip()) == 0:
            raise ValidationError("股票名称不能为空")

        # 验证策略类型
        valid_types = ["buy", "sell", "hold"]
        if strategy_type not in valid_types:
            raise ValidationError(f"策略类型必须是以下之一: {', '.join(valid_types)}")

        # 验证触发价格
        if trigger_price is not None and trigger_price <= 0:
            raise ValidationError("触发价格必须大于0")

        # 验证目标数量
        if target_quantity is not None and target_quantity <= 0:
            raise ValidationError("目标数量必须大于0")

        # 验证优先级
        valid_priorities = ["urgent", "high", "normal", "low"]
        if priority not in valid_priorities:
            raise ValidationError(f"优先级必须是以下之一: {', '.join(valid_priorities)}")

    @staticmethod
    def prepare_data(
        user_id: int,
        symbol: str,
        stock_name: str,
        strategy_type: str,
        trigger_price: Optional[Decimal],
        target_quantity: Optional[Decimal],
        reason: Optional[str],
        notes: Optional[str],
        priority: str,
        is_stop_loss: bool,
        is_take_profit: bool,
    ) -> dict:
        """
        准备创建策略的数据

        Args:
            user_id: 用户ID
            symbol: 股票代码
            stock_name: 股票名称
            strategy_type: 策略类型
            trigger_price: 触发价格
            target_quantity: 目标数量
            reason: 策略原因
            notes: 备注
            priority: 优先级
            is_stop_loss: 是否止损策略
            is_take_profit: 是否止盈策略

        Returns:
            准备好的数据字典
        """
        return {
            "user_id": user_id,
            "symbol": symbol.strip().upper(),
            "stock_name": stock_name.strip(),
            "strategy_type": strategy_type,
            "trigger_price": trigger_price,
            "target_quantity": target_quantity,
            "reason": reason.strip() if reason else None,
            "notes": notes.strip() if notes else None,
            "priority": priority,
            "status": "pending",  # 新创建的策略状态为pending
            "is_stop_loss": is_stop_loss,
            "is_take_profit": is_take_profit,
        }


class StrategyCreateBuilder:
    """
    策略创建数据构建器（静态类）

    职责：构建响应对象
    """

    @staticmethod
    def build_response(strategy) -> dict:
        """
        构建策略创建响应

        Args:
            strategy: 创建的策略对象

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
        }
