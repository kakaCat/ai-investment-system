"""
Account Repository

纯数据访问层 - 只负责账户表的CRUD操作，不包含任何业务逻辑
"""

from typing import List, Optional
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.account import Account


class AccountRepository:
    """账户数据访问层（纯CRUD，无业务逻辑）"""

    async def get_by_id(self, db: AsyncSession, account_id: int) -> Optional[Account]:
        """
        根据ID查询账户

        Args:
            db: 数据库会话
            account_id: 账户ID

        Returns:
            Account对象，不存在返回None
        """
        result = await db.execute(
            select(Account).where(
                and_(
                    Account.account_id == account_id,
                    Account.is_deleted == False
                )
            )
        )
        return result.scalar_one_or_none()

    async def query_by_user(
        self,
        db: AsyncSession,
        user_id: int,
        market: Optional[str] = None,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> tuple[List[Account], int]:
        """
        查询用户账户列表（支持分页、筛选）

        Args:
            db: 数据库会话
            user_id: 用户ID
            market: 市场类型（可选）
            status: 账户状态（可选）
            page: 页码
            page_size: 每页数量

        Returns:
            (账户列表, 总数)
        """
        # 构建查询条件
        conditions = [
            Account.user_id == user_id,
            Account.is_deleted == False
        ]

        if market:
            conditions.append(Account.market == market)
        if status:
            conditions.append(Account.status == status)

        # 查询总数
        count_query = select(Account).where(and_(*conditions))
        count_result = await db.execute(count_query)
        total = len(count_result.scalars().all())

        # 查询列表
        query = (
            select(Account)
            .where(and_(*conditions))
            .order_by(Account.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )

        result = await db.execute(query)
        accounts = result.scalars().all()

        return list(accounts), total

    async def create(self, db: AsyncSession, data: dict) -> Account:
        """
        创建账户

        Args:
            db: 数据库会话
            data: 账户数据字典

        Returns:
            创建的Account对象
        """
        account = Account(**data)
        db.add(account)
        await db.commit()
        await db.refresh(account)
        return account

    async def update(self, db: AsyncSession, account_id: int, data: dict) -> Optional[Account]:
        """
        更新账户

        Args:
            db: 数据库会话
            account_id: 账户ID
            data: 更新数据字典

        Returns:
            更新后的Account对象，不存在返回None
        """
        account = await self.get_by_id(db, account_id)
        if not account:
            return None

        for key, value in data.items():
            if hasattr(account, key):
                setattr(account, key, value)

        await db.commit()
        await db.refresh(account)
        return account

    async def soft_delete(self, db: AsyncSession, account_id: int) -> bool:
        """
        软删除账户

        Args:
            db: 数据库会话
            account_id: 账户ID

        Returns:
            是否删除成功
        """
        from datetime import datetime

        account = await self.get_by_id(db, account_id)
        if not account:
            return False

        account.is_deleted = True
        account.deleted_at = datetime.utcnow()

        await db.commit()
        return True

    async def get_by_user_and_name(
        self,
        db: AsyncSession,
        user_id: int,
        account_name: str
    ) -> Optional[Account]:
        """
        根据用户ID和账户名称查询（用于检查重名）

        Args:
            db: 数据库会话
            user_id: 用户ID
            account_name: 账户名称

        Returns:
            Account对象，不存在返回None
        """
        result = await db.execute(
            select(Account).where(
                and_(
                    Account.user_id == user_id,
                    Account.account_name == account_name,
                    Account.is_deleted == False
                )
            )
        )
        return result.scalar_one_or_none()
