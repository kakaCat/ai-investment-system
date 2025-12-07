"""
Account Delete Service

账户删除业务服务 - Service + Converter + Builder
"""

from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.account_repo import AccountRepository
from app.repositories.holding_repo import HoldingRepository
from app.exceptions import AccountNotFound, AccountAccessDenied, InvalidOperation


class AccountDeleteService:
    """
    账户删除业务类

    职责：权限校验、编排流程、事务管理
    """

    def __init__(self):
        self.account_repo = AccountRepository()
        self.holding_repo = HoldingRepository()

    async def execute(self, db: AsyncSession, account_id: int, user_id: int) -> dict:
        """
        执行账户删除业务逻辑（软删除）

        Args:
            db: 数据库会话
            account_id: 账户ID
            user_id: 用户ID

        Returns:
            删除结果

        Raises:
            AccountNotFound: 账户不存在
            AccountAccessDenied: 无权访问
            InvalidOperation: 账户有持仓不能删除
        """
        # 1. 权限校验 - 查询账户
        account = await self.account_repo.get_by_id(db, account_id)
        if not account:
            raise AccountNotFound(f"账户ID {account_id} 不存在")

        if account.user_id != user_id:
            raise AccountAccessDenied(f"无权访问账户ID {account_id}")

        # 2. 业务规则校验 - 检查是否有持仓
        holdings = await self.holding_repo.query_by_account(db, account_id)
        AccountDeleteConverter.validate_can_delete(holdings)

        # 3. 软删除账户
        success = await self.account_repo.soft_delete(db, account_id)

        # 4. 调用 Builder 构建响应
        return AccountDeleteBuilder.build_response(success, account_id)


class AccountDeleteConverter:
    """
    账户删除转换器（静态类）

    职责：业务规则验证
    """

    @staticmethod
    def validate_can_delete(holdings: list) -> None:
        """
        验证账户是否可以删除

        Args:
            holdings: 持仓列表

        Raises:
            InvalidOperation: 账户有持仓不能删除
        """
        # 检查是否有持仓
        if holdings and len(holdings) > 0:
            # 检查是否有数量大于0的持仓
            active_holdings = [h for h in holdings if h.quantity and h.quantity > 0]
            if active_holdings:
                raise InvalidOperation(
                    f"账户有 {len(active_holdings)} 个持仓，请先清空持仓后再删除账户"
                )


class AccountDeleteBuilder:
    """
    账户删除数据构建器（静态类）

    职责：构建响应对象
    """

    @staticmethod
    def build_response(success: bool, account_id: int) -> dict:
        """
        构建账户删除响应

        Args:
            success: 是否删除成功
            account_id: 账户ID

        Returns:
            删除结果字典
        """
        return {
            "success": success,
            "account_id": account_id,
            "message": "账户已删除" if success else "删除失败"
        }
