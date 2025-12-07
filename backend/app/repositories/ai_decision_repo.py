"""
AI Decision Repository

纯数据访问层 - 只负责ai_decisions表的CRUD操作，不包含任何业务逻辑
"""

from typing import List, Optional
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.ai_decision import AIDecision


class AIDecisionRepository:
    """AI决策数据访问层（纯CRUD，无业务逻辑）"""

    async def get_by_id(self, db: AsyncSession, decision_id: int) -> Optional[AIDecision]:
        """
        根据ID查询AI决策

        Args:
            db: 数据库会话
            decision_id: 决策ID

        Returns:
            AIDecision对象，不存在返回None
        """
        result = await db.execute(
            select(AIDecision).where(
                and_(
                    AIDecision.decision_id == decision_id,
                    AIDecision.is_deleted == False
                )
            )
        )
        return result.scalar_one_or_none()

    async def query_by_user(
        self,
        db: AsyncSession,
        user_id: int,
        analysis_type: Optional[str] = None,
        symbol: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> tuple[List[AIDecision], int]:
        """
        查询用户的AI决策列表（支持分页、筛选）

        Args:
            db: 数据库会话
            user_id: 用户ID
            analysis_type: 分析类型（可选）: daily/single/portfolio
            symbol: 股票代码（可选）
            page: 页码
            page_size: 每页数量

        Returns:
            (决策列表, 总数)
        """
        # 构建查询条件
        conditions = [
            AIDecision.user_id == user_id,
            AIDecision.is_deleted == False
        ]

        if analysis_type:
            conditions.append(AIDecision.analysis_type == analysis_type)
        if symbol:
            conditions.append(AIDecision.symbol == symbol)

        # 查询总数
        count_query = select(AIDecision).where(and_(*conditions))
        count_result = await db.execute(count_query)
        total = len(count_result.scalars().all())

        # 查询列表
        query = (
            select(AIDecision)
            .where(and_(*conditions))
            .order_by(AIDecision.created_at.desc())
            .limit(page_size)
            .offset((page - 1) * page_size)
        )

        result = await db.execute(query)
        decisions = result.scalars().all()

        return list(decisions), total

    async def query_by_symbol(
        self,
        db: AsyncSession,
        symbol: str,
        analysis_type: Optional[str] = None,
        limit: int = 10
    ) -> List[AIDecision]:
        """
        查询指定股票的AI决策历史

        Args:
            db: 数据库会话
            symbol: 股票代码
            analysis_type: 分析类型（可选）
            limit: 返回数量限制

        Returns:
            决策列表
        """
        conditions = [
            AIDecision.symbol == symbol,
            AIDecision.is_deleted == False
        ]

        if analysis_type:
            conditions.append(AIDecision.analysis_type == analysis_type)

        query = (
            select(AIDecision)
            .where(and_(*conditions))
            .order_by(AIDecision.created_at.desc())
            .limit(limit)
        )

        result = await db.execute(query)
        return list(result.scalars().all())

    async def create(self, db: AsyncSession, decision_data: dict) -> AIDecision:
        """
        创建AI决策记录

        Args:
            db: 数据库会话
            decision_data: 决策数据字典

        Returns:
            创建的AIDecision对象
        """
        decision = AIDecision(**decision_data)
        db.add(decision)
        await db.flush()
        await db.refresh(decision)
        return decision

    async def update(
        self,
        db: AsyncSession,
        decision_id: int,
        update_data: dict
    ) -> Optional[AIDecision]:
        """
        更新AI决策记录

        Args:
            db: 数据库会话
            decision_id: 决策ID
            update_data: 更新数据字典

        Returns:
            更新后的AIDecision对象，不存在返回None
        """
        decision = await self.get_by_id(db, decision_id)
        if not decision:
            return None

        for key, value in update_data.items():
            if hasattr(decision, key):
                setattr(decision, key, value)

        await db.flush()
        await db.refresh(decision)
        return decision

    async def soft_delete(self, db: AsyncSession, decision_id: int) -> bool:
        """
        软删除AI决策记录

        Args:
            db: 数据库会话
            decision_id: 决策ID

        Returns:
            是否删除成功
        """
        decision = await self.get_by_id(db, decision_id)
        if not decision:
            return False

        decision.is_deleted = True
        await db.flush()
        return True
