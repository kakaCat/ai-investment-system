"""
Account Create Service

账户创建业务服务 - Service + Converter + Builder
"""

from typing import Optional
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.account_repo import AccountRepository
from app.exceptions import AccountNameDuplicate, ValidationError


class AccountCreateService:
    """
    账户创建业务类

    职责：权限校验、编排流程、事务管理
    """

    def __init__(self):
        self.account_repo = AccountRepository()

    async def execute(
        self,
        db: AsyncSession,
        user_id: int,
        account_name: str,
        market: str,
        broker: Optional[str] = None,
        account_number: Optional[str] = None,
        initial_capital: Optional[Decimal] = None,
    ) -> dict:
        """
        执行账户创建业务逻辑

        Args:
            db: 数据库会话
            user_id: 用户ID
            account_name: 账户名称
            market: 市场类型
            broker: 券商名称（可选）
            account_number: 账户号（可选）
            initial_capital: 初始资金（可选）

        Returns:
            创建的账户数据

        Raises:
            AccountNameDuplicate: 账户名称重复
            ValidationError: 数据验证失败
        """
        # 1. 数据验证
        AccountCreateConverter.validate(account_name, market, initial_capital)

        # 2. 检查账户名称是否重复
        existing = await self.account_repo.get_by_user_and_name(db, user_id, account_name)
        if existing:
            raise AccountNameDuplicate(f"账户名称 '{account_name}' 已存在")

        # 3. 调用 Converter 准备数据
        data = AccountCreateConverter.prepare_data(
            user_id=user_id,
            account_name=account_name,
            market=market,
            broker=broker,
            account_number=account_number,
            initial_capital=initial_capital,
        )

        # 4. 创建账户
        account = await self.account_repo.create(db, data)

        # 5. 调用 Builder 构建响应
        return AccountCreateBuilder.build_response(account)


class AccountCreateConverter:
    """
    账户创建转换器（静态类）

    职责：数据验证、业务逻辑处理
    """

    @staticmethod
    def validate(account_name: str, market: str, initial_capital: Optional[Decimal]) -> None:
        """
        验证账户创建数据

        Args:
            account_name: 账户名称
            market: 市场类型
            initial_capital: 初始资金

        Raises:
            ValidationError: 验证失败
        """
        # 验证账户名称
        if not account_name or len(account_name.strip()) == 0:
            raise ValidationError("账户名称不能为空")
        if len(account_name) > 100:
            raise ValidationError("账户名称长度不能超过100个字符")

        # 验证市场类型
        valid_markets = ["A-share", "HK", "US"]
        if market not in valid_markets:
            raise ValidationError(f"市场类型必须是以下之一: {', '.join(valid_markets)}")

        # 验证初始资金
        if initial_capital is not None and initial_capital < 0:
            raise ValidationError("初始资金不能为负数")

    @staticmethod
    def prepare_data(
        user_id: int,
        account_name: str,
        market: str,
        broker: Optional[str],
        account_number: Optional[str],
        initial_capital: Optional[Decimal],
    ) -> dict:
        """
        准备创建账户的数据

        Args:
            user_id: 用户ID
            account_name: 账户名称
            market: 市场类型
            broker: 券商名称
            account_number: 账户号
            initial_capital: 初始资金

        Returns:
            准备好的数据字典
        """
        # 如果没有提供初始资金，默认为0
        if initial_capital is None:
            initial_capital = Decimal("0")

        return {
            "user_id": user_id,
            "account_name": account_name.strip(),
            "market": market,
            "broker": broker if broker else None,
            "account_number": account_number if account_number else None,
            # 映射到Account模型字段
            "available_cash": initial_capital,  # 初始资金作为可用资金
            "total_value": initial_capital,  # 总资产初始等于初始资金
            "invested_value": Decimal("0"),  # 初始持仓市值为0
            "status": "active",  # 新账户默认为激活状态
        }


class AccountCreateBuilder:
    """
    账户创建数据构建器（静态类）

    职责：构建响应对象
    """

    @staticmethod
    def build_response(account) -> dict:
        """
        构建账户创建响应

        Args:
            account: 创建的账户对象

        Returns:
            账户数据字典
        """
        return {
            "account_id": account.account_id,
            "account_name": account.account_name,
            "market": account.market,
            "status": account.status,
            "broker": account.broker,
            "account_number": account.account_number,
            "initial_capital": float(account.available_cash) if account.available_cash else 0.0,
            "current_capital": float(account.available_cash) if account.available_cash else 0.0,
            "total_value": float(account.total_value) if account.total_value else 0.0,
            "created_at": account.created_at.isoformat() if account.created_at else None,
        }
