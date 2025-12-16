"""
AI Conversation Repository

纯数据访问层 - 只负责ai_conversations表的CRUD操作，不包含任何业务逻辑
注意：AIConversation表结构中messages是JSON数组，每个会话存一条记录
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.ai_decision import AIConversation  # AIConversation定义在ai_decision.py中


class AIConversationRepository:
    """AI对话数据访问层（纯CRUD，无业务逻辑）"""

    async def get_by_session(self, db: AsyncSession, session_id: str) -> Optional[AIConversation]:
        """
        根据session_id查询会话

        Args:
            db: 数据库会话
            session_id: 会话ID

        Returns:
            AIConversation对象，不存在返回None
        """
        # 使用context_symbol作为session_id（简化处理）
        result = await db.execute(
            select(AIConversation).where(
                and_(AIConversation.context_symbol == session_id, AIConversation.is_deleted is False)
            )
        )
        return result.scalar_one_or_none()

    async def create_or_get(
        self,
        db: AsyncSession,
        user_id: int,
        session_id: str,
        context_symbol: Optional[str] = None,
        context_type: Optional[str] = None,
    ) -> AIConversation:
        """
        创建或获取会话记录

        Args:
            db: 数据库会话
            user_id: 用户ID
            session_id: 会话ID
            context_symbol: 上下文股票代码
            context_type: 上下文类型

        Returns:
            AIConversation对象
        """
        # 先尝试获取
        conv = await self.get_by_session(db, session_id)
        if conv:
            return conv

        # 不存在则创建
        conv = AIConversation(
            user_id=user_id,
            context_symbol=session_id,  # 使用session_id作为context_symbol
            context_type=context_type or "chat",
            messages=[],  # 初始化空消息列表
            total_tokens=0,
        )
        db.add(conv)
        await db.flush()
        await db.refresh(conv)
        return conv

    async def append_message(self, db: AsyncSession, session_id: str, role: str, content: str) -> AIConversation:
        """
        向会话添加消息

        Args:
            db: 数据库会话
            session_id: 会话ID
            role: 角色 (user/assistant/system)
            content: 消息内容

        Returns:
            更新后的AIConversation对象
        """
        conv = await self.get_by_session(db, session_id)
        if not conv:
            raise ValueError(f"Session {session_id} not found")

        # 构建新消息
        new_message = {"role": role, "content": content, "timestamp": datetime.now().isoformat()}

        # 追加消息到messages数组
        if conv.messages is None:
            conv.messages = []

        messages = list(conv.messages) if conv.messages else []
        messages.append(new_message)
        conv.messages = messages

        await db.flush()
        await db.refresh(conv)
        return conv

    async def delete_session(self, db: AsyncSession, session_id: str) -> bool:
        """
        软删除会话

        Args:
            db: 数据库会话
            session_id: 会话ID

        Returns:
            是否删除成功
        """
        conv = await self.get_by_session(db, session_id)
        if not conv:
            return False

        conv.is_deleted = True
        await db.flush()
        return True
