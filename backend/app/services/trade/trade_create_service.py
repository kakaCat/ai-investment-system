"""
Trade Create Service

交易创建业务服务 - Service + Converter + Builder
"""

from typing import Optional
from decimal import Decimal
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.trade_repo import TradeRepository
from app.repositories.account_repo import AccountRepository
from app.exceptions import ValidationError, PermissionDenied, ResourceNotFound


class TradeCreateService:
    """
    交易创建业务类

    职责：权限校验、编排流程、事务管理
    """

    def __init__(self):
        self.trade_repo = TradeRepository()
        self.account_repo = AccountRepository()

    async def execute(
        self,
        db: AsyncSession,
        user_id: int,
        account_id: int,
        symbol: str,
        stock_name: str,
        trade_type: str,
        quantity: Decimal,
        price: Decimal,
        trade_date: date,
        commission: Optional[Decimal] = None,
        tax: Optional[Decimal] = None,
        profit_loss: Optional[Decimal] = None,
        notes: Optional[str] = None,
    ) -> dict:
        """
        执行交易创建业务逻辑

        Args:
            db: 数据库会话
            user_id: 用户ID
            account_id: 账户ID
            symbol: 股票代码
            stock_name: 股票名称
            trade_type: 交易类型（buy/sell）
            quantity: 数量
            price: 价格
            trade_date: 交易日期
            commission: 手续费（可选）
            tax: 税费（可选）
            profit_loss: 盈亏（可选，卖出时）
            notes: 备注（可选）

        Returns:
            创建的交易数据

        Raises:
            ValidationError: 数据验证失败
            PermissionDenied: 无权访问账户
            ResourceNotFound: 账户不存在
        """
        # 1. 权限校验 - 检查账户归属
        account = await self.account_repo.get_by_id(db, account_id)
        if not account:
            raise ResourceNotFound(f"账户ID {account_id} 不存在")

        if account.user_id != user_id:
            raise PermissionDenied(f"无权访问账户ID {account_id}")

        # 2. 数据验证
        TradeCreateConverter.validate(
            symbol=symbol,
            stock_name=stock_name,
            trade_type=trade_type,
            quantity=quantity,
            price=price,
            commission=commission,
            tax=tax,
        )

        # 3. 调用 Converter 准备数据
        data = TradeCreateConverter.prepare_data(
            user_id=user_id,
            account_id=account_id,
            symbol=symbol,
            stock_name=stock_name,
            trade_type=trade_type,
            quantity=quantity,
            price=price,
            trade_date=trade_date,
            commission=commission,
            tax=tax,
            profit_loss=profit_loss,
            notes=notes,
        )

        # 4. 创建交易
        trade = await self.trade_repo.create(db, data)

        # 5. 调用 Builder 构建响应
        return TradeCreateBuilder.build_response(trade)


class TradeCreateConverter:
    """
    交易创建转换器（静态类）

    职责：数据验证、业务逻辑处理
    """

    @staticmethod
    def validate(
        symbol: str,
        stock_name: str,
        trade_type: str,
        quantity: Decimal,
        price: Decimal,
        commission: Optional[Decimal],
        tax: Optional[Decimal],
    ) -> None:
        """
        验证交易创建数据

        Args:
            symbol: 股票代码
            stock_name: 股票名称
            trade_type: 交易类型
            quantity: 数量
            price: 价格
            commission: 手续费
            tax: 税费

        Raises:
            ValidationError: 验证失败
        """
        # 验证股票代码
        if not symbol or len(symbol.strip()) == 0:
            raise ValidationError("股票代码不能为空")

        # 验证股票名称
        if not stock_name or len(stock_name.strip()) == 0:
            raise ValidationError("股票名称不能为空")

        # 验证交易类型
        valid_types = ["buy", "sell"]
        if trade_type not in valid_types:
            raise ValidationError(f"交易类型必须是以下之一: {', '.join(valid_types)}")

        # 验证数量
        if quantity <= 0:
            raise ValidationError("交易数量必须大于0")

        # 验证价格
        if price <= 0:
            raise ValidationError("交易价格必须大于0")

        # 验证手续费
        if commission is not None and commission < 0:
            raise ValidationError("手续费不能为负数")

        # 验证税费
        if tax is not None and tax < 0:
            raise ValidationError("税费不能为负数")

    @staticmethod
    def prepare_data(
        user_id: int,
        account_id: int,
        symbol: str,
        stock_name: str,
        trade_type: str,
        quantity: Decimal,
        price: Decimal,
        trade_date: date,
        commission: Optional[Decimal],
        tax: Optional[Decimal],
        profit_loss: Optional[Decimal],
        notes: Optional[str],
    ) -> dict:
        """
        准备创建交易的数据

        Args:
            user_id: 用户ID
            account_id: 账户ID
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
            准备好的数据字典
        """
        # 如果没有提供手续费和税费，默认为0
        if commission is None:
            commission = Decimal("0")
        if tax is None:
            tax = Decimal("0")

        return {
            "user_id": user_id,
            "account_id": account_id,
            "symbol": symbol.strip().upper(),
            "stock_name": stock_name.strip(),
            "trade_type": trade_type,
            "quantity": quantity,
            "price": price,
            "commission": commission,
            "tax": tax,
            "profit_loss": profit_loss,
            "trade_date": trade_date,
            "notes": notes.strip() if notes else None,
        }


class TradeCreateBuilder:
    """
    交易创建数据构建器（静态类）

    职责：构建响应对象
    """

    @staticmethod
    def build_response(trade) -> dict:
        """
        构建交易创建响应

        Args:
            trade: 创建的交易对象

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
        }
