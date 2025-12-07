"""
Trade Update Service

交易更新业务服务 - Service + Converter + Builder
"""

from typing import Optional
from decimal import Decimal
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.trade_repo import TradeRepository
from app.exceptions import ResourceNotFound, PermissionDenied, ValidationError


class TradeUpdateService:
    """
    交易更新业务类

    职责：权限校验、编排流程、事务管理
    """

    def __init__(self):
        self.trade_repo = TradeRepository()

    async def execute(
        self,
        db: AsyncSession,
        trade_id: int,
        user_id: int,
        symbol: Optional[str] = None,
        stock_name: Optional[str] = None,
        trade_type: Optional[str] = None,
        quantity: Optional[Decimal] = None,
        price: Optional[Decimal] = None,
        trade_date: Optional[date] = None,
        commission: Optional[Decimal] = None,
        tax: Optional[Decimal] = None,
        profit_loss: Optional[Decimal] = None,
        notes: Optional[str] = None
    ) -> dict:
        """
        执行交易更新业务逻辑

        Args:
            db: 数据库会话
            trade_id: 交易ID
            user_id: 用户ID
            symbol: 股票代码（可选）
            stock_name: 股票名称（可选）
            trade_type: 交易类型（可选）
            quantity: 数量（可选）
            price: 价格（可选）
            trade_date: 交易日期（可选）
            commission: 手续费（可选）
            tax: 税费（可选）
            profit_loss: 盈亏（可选）
            notes: 备注（可选）

        Returns:
            更新后的交易数据

        Raises:
            ResourceNotFound: 交易不存在
            PermissionDenied: 无权访问
            ValidationError: 数据验证失败
        """
        # 1. 权限校验 - 查询交易
        trade = await self.trade_repo.get_by_id(db, trade_id)
        if not trade:
            raise ResourceNotFound(f"交易ID {trade_id} 不存在")

        if trade.user_id != user_id:
            raise PermissionDenied(f"无权访问交易ID {trade_id}")

        # 2. 调用 Converter 验证和准备数据
        update_data = TradeUpdateConverter.prepare_update_data(
            symbol=symbol,
            stock_name=stock_name,
            trade_type=trade_type,
            quantity=quantity,
            price=price,
            trade_date=trade_date,
            commission=commission,
            tax=tax,
            profit_loss=profit_loss,
            notes=notes
        )

        # 3. 更新交易
        updated_trade = await self.trade_repo.update(db, trade_id, update_data)

        # 4. 调用 Builder 构建响应
        return TradeUpdateBuilder.build_response(updated_trade)


class TradeUpdateConverter:
    """
    交易更新转换器（静态类）

    职责：数据验证、业务逻辑处理
    """

    @staticmethod
    def prepare_update_data(
        symbol: Optional[str],
        stock_name: Optional[str],
        trade_type: Optional[str],
        quantity: Optional[Decimal],
        price: Optional[Decimal],
        trade_date: Optional[date],
        commission: Optional[Decimal],
        tax: Optional[Decimal],
        profit_loss: Optional[Decimal],
        notes: Optional[str]
    ) -> dict:
        """
        准备更新数据（只更新提供的字段）

        Args:
            symbol: 股票代码
            stock_name: 股票名称
            trade_type: 交易类型
            quantity: 数量
            price: 价格
            trade_date: 交易日期
            commission: 手续费
            tax: 税费
            profit_loss: 盈亏
            notes: 备注

        Returns:
            准备好的更新数据字典

        Raises:
            ValidationError: 验证失败
        """
        update_data = {}

        # 验证并添加股票代码
        if symbol is not None:
            if not symbol or len(symbol.strip()) == 0:
                raise ValidationError("股票代码不能为空")
            update_data["symbol"] = symbol.strip().upper()

        # 验证并添加股票名称
        if stock_name is not None:
            if not stock_name or len(stock_name.strip()) == 0:
                raise ValidationError("股票名称不能为空")
            update_data["stock_name"] = stock_name.strip()

        # 验证并添加交易类型
        if trade_type is not None:
            valid_types = ["buy", "sell"]
            if trade_type not in valid_types:
                raise ValidationError(f"交易类型必须是以下之一: {', '.join(valid_types)}")
            update_data["trade_type"] = trade_type

        # 验证并添加数量
        if quantity is not None:
            if quantity <= 0:
                raise ValidationError("交易数量必须大于0")
            update_data["quantity"] = quantity

        # 验证并添加价格
        if price is not None:
            if price <= 0:
                raise ValidationError("交易价格必须大于0")
            update_data["price"] = price

        # 添加交易日期
        if trade_date is not None:
            update_data["trade_date"] = trade_date

        # 验证并添加手续费
        if commission is not None:
            if commission < 0:
                raise ValidationError("手续费不能为负数")
            update_data["commission"] = commission

        # 验证并添加税费
        if tax is not None:
            if tax < 0:
                raise ValidationError("税费不能为负数")
            update_data["tax"] = tax

        # 添加盈亏
        if profit_loss is not None:
            update_data["profit_loss"] = profit_loss

        # 添加备注
        if notes is not None:
            update_data["notes"] = notes.strip() if notes else None

        return update_data


class TradeUpdateBuilder:
    """
    交易更新数据构建器（静态类）

    职责：构建响应对象
    """

    @staticmethod
    def build_response(trade) -> dict:
        """
        构建交易更新响应

        Args:
            trade: 更新后的交易对象

        Returns:
            交易数据字典
        """
        # 计算交易金额
        total_amount = float(trade.quantity * trade.price) if trade.quantity and trade.price else 0.0

        return {
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
            "profit_loss": float(trade.profit_loss) if trade.profit_loss else None,
            "trade_date": trade.trade_date.isoformat() if trade.trade_date else None,
            "notes": trade.notes,
            "created_at": trade.created_at.isoformat() if trade.created_at else None,
            "updated_at": trade.updated_at.isoformat() if trade.updated_at else None,
        }
