"""
Account Update Service

账户更新业务服务 - Service + Converter + Builder
"""

from typing import Optional
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.account_repo import AccountRepository
from app.exceptions import AccountNotFound, AccountAccessDenied, ValidationError


class AccountUpdateService:
    """
    账户更新业务类

    职责：权限校验、编排流程、事务管理
    """

    def __init__(self):
        self.account_repo = AccountRepository()

    async def execute(
        self,
        db: AsyncSession,
        account_id: int,
        user_id: int,
        account_name: Optional[str] = None,
        broker: Optional[str] = None,
        account_number: Optional[str] = None,
        status: Optional[str] = None,
        current_capital: Optional[Decimal] = None
    ) -> dict:
        """
        执行账户更新业务逻辑

        Args:
            db: 数据库会话
            account_id: 账户ID
            user_id: 用户ID
            account_name: 账户名称（可选）
            broker: 券商名称（可选）
            account_number: 账户号（可选）
            status: 账户状态（可选）
            current_capital: 当前资金（可选）

        Returns:
            更新后的账户数据

        Raises:
            AccountNotFound: 账户不存在
            AccountAccessDenied: 无权访问
            ValidationError: 数据验证失败
        """
        # 1. 权限校验 - 查询账户
        account = await self.account_repo.get_by_id(db, account_id)
        if not account:
            raise AccountNotFound(f"账户ID {account_id} 不存在")

        if account.user_id != user_id:
            raise AccountAccessDenied(f"无权访问账户ID {account_id}")

        # 2. 调用 Converter 验证和准备数据
        update_data = AccountUpdateConverter.prepare_update_data(
            account_name=account_name,
            broker=broker,
            account_number=account_number,
            status=status,
            current_capital=current_capital
        )

        # 3. 更新账户
        updated_account = await self.account_repo.update(db, account_id, update_data)

        # 4. 调用 Builder 构建响应
        return AccountUpdateBuilder.build_response(updated_account)


class AccountUpdateConverter:
    """
    账户更新转换器（静态类）

    职责：数据验证、业务逻辑处理
    """

    @staticmethod
    def prepare_update_data(
        account_name: Optional[str],
        broker: Optional[str],
        account_number: Optional[str],
        status: Optional[str],
        current_capital: Optional[Decimal]
    ) -> dict:
        """
        准备更新数据（只更新提供的字段）

        Args:
            account_name: 账户名称
            broker: 券商名称
            account_number: 账户号
            status: 账户状态
            current_capital: 当前资金

        Returns:
            准备好的更新数据字典

        Raises:
            ValidationError: 验证失败
        """
        update_data = {}

        # 验证并添加账户名称
        if account_name is not None:
            if not account_name or len(account_name.strip()) == 0:
                raise ValidationError("账户名称不能为空")
            if len(account_name) > 100:
                raise ValidationError("账户名称长度不能超过100个字符")
            update_data["account_name"] = account_name.strip()

        # 添加券商名称
        if broker is not None:
            update_data["broker"] = broker

        # 添加账户号
        if account_number is not None:
            update_data["account_number"] = account_number

        # 验证并添加状态
        if status is not None:
            valid_statuses = ["active", "inactive", "closed"]
            if status not in valid_statuses:
                raise ValidationError(f"账户状态必须是以下之一: {', '.join(valid_statuses)}")
            update_data["status"] = status

        # 验证并添加当前资金
        if current_capital is not None:
            if current_capital < 0:
                raise ValidationError("当前资金不能为负数")
            update_data["current_capital"] = current_capital

        return update_data


class AccountUpdateBuilder:
    """
    账户更新数据构建器（静态类）

    职责：构建响应对象
    """

    @staticmethod
    def build_response(account) -> dict:
        """
        构建账户更新响应

        Args:
            account: 更新后的账户对象

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
            "initial_capital": float(account.initial_capital) if account.initial_capital else 0.0,
            "current_capital": float(account.current_capital) if account.current_capital else 0.0,
            "created_at": account.created_at.isoformat() if account.created_at else None,
            "updated_at": account.updated_at.isoformat() if account.updated_at else None,
        }
