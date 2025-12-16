"""
AI Chat Service

AI对话业务服务 - Service + Converter + Builder
注意：会话数据存储在一条记录中，messages是JSON数组
"""

import uuid
from typing import Optional, List, Dict
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.ai_conversation_repo import AIConversationRepository
from app.repositories.stock_repo import StockRepository
from app.utils.ai_client import ai_client, AIPromptBuilder


class AIChatService:
    """
    AI对话业务类

    职责：权限校验、编排流程、事务管理
    """

    def __init__(self):
        self.conversation_repo = AIConversationRepository()
        self.stock_repo = StockRepository()

    async def create_session(
        self, db: AsyncSession, user_id: int, context_symbol: Optional[str] = None, context_type: Optional[str] = None
    ) -> dict:
        """
        创建对话会话

        Args:
            db: 数据库会话
            user_id: 用户ID
            context_symbol: 上下文股票代码（可选）
            context_type: 上下文类型（可选）

        Returns:
            会话信息
        """
        # 生成会话ID
        session_id = str(uuid.uuid4())

        # 创建会话记录
        await self.conversation_repo.create_or_get(
            db=db, user_id=user_id, session_id=session_id, context_symbol=context_symbol, context_type=context_type
        )
        await db.commit()

        # 使用Builder构建响应
        return AIChatBuilder.build_session_response(
            session_id=session_id, user_id=user_id, context_symbol=context_symbol, context_type=context_type
        )

    async def send_message(self, db: AsyncSession, user_id: int, session_id: str, message: str) -> dict:
        """
        发送消息并获取AI回复

        Args:
            db: 数据库会话
            user_id: 用户ID
            session_id: 会话ID
            message: 用户消息

        Returns:
            AI回复
        """
        # 1. 创建或获取会话（如果不存在则创建）
        conv = await self.conversation_repo.create_or_get(db=db, user_id=user_id, session_id=session_id)

        # 2. 添加用户消息
        await self.conversation_repo.append_message(db=db, session_id=session_id, role="user", content=message)

        # 3. 获取上下文数据
        context_data = await AIChatConverter.get_context_data(
            db=db, stock_repo=self.stock_repo, context_symbol=conv.context_symbol
        )

        # 4. 调用AI获取回复
        ai_reply = await AIChatConverter.generate_ai_reply(
            user_message=message,
            history=conv.messages if conv.messages else [],
            context_symbol=conv.context_symbol,
            context_data=context_data,
        )

        # 5. 添加AI回复
        conv = await self.conversation_repo.append_message(
            db=db, session_id=session_id, role="assistant", content=ai_reply
        )
        await db.commit()

        # 6. 使用Builder构建响应（返回最后一条消息）
        last_message = conv.messages[-1] if conv.messages else {}
        return AIChatBuilder.build_message_response(last_message)

    async def get_history(self, db: AsyncSession, user_id: int, session_id: str, limit: int = 50) -> dict:
        """
        获取会话历史消息

        Args:
            db: 数据库会话
            user_id: 用户ID
            session_id: 会话ID
            limit: 消息数量限制

        Returns:
            历史消息列表
        """
        # 1. 查询会话
        conv = await self.conversation_repo.get_by_session(db, session_id)
        if not conv:
            return AIChatBuilder.build_history_response(session_id, [])

        # 2. 获取消息列表（限制数量）
        messages = conv.messages[-limit:] if conv.messages else []

        # 3. 使用Builder构建响应
        return AIChatBuilder.build_history_response(session_id, messages)

    async def delete_session(self, db: AsyncSession, user_id: int, session_id: str) -> dict:
        """
        删除会话

        Args:
            db: 数据库会话
            user_id: 用户ID
            session_id: 会话ID

        Returns:
            删除结果
        """
        # 软删除会话
        success = await self.conversation_repo.delete_session(db, session_id)
        await db.commit()

        return AIChatBuilder.build_delete_response(1 if success else 0)


class AIChatConverter:
    """
    AI对话转换器（静态类）

    职责：业务逻辑计算
    """

    @staticmethod
    async def get_context_data(
        db: AsyncSession, stock_repo: StockRepository, context_symbol: Optional[str]
    ) -> Optional[Dict]:
        """
        获取上下文数据

        Args:
            db: 数据库会话
            stock_repo: 股票Repository
            context_symbol: 股票代码

        Returns:
            上下文数据
        """
        if not context_symbol:
            return None

        # 查询股票信息
        stock = await stock_repo.get_by_symbol(db, context_symbol)
        if not stock:
            return None

        return {
            "stock_name": stock.name,
            "symbol": context_symbol,
            "market": stock.market,
            # TODO: 后续添加更多上下文数据（实时价格、持仓等）
        }

    @staticmethod
    async def generate_ai_reply(
        user_message: str,
        history: List[Dict],
        context_symbol: Optional[str] = None,
        context_data: Optional[Dict] = None,
    ) -> str:
        """
        生成AI回复

        Args:
            user_message: 用户消息
            history: 对话历史
            context_symbol: 上下文股票代码
            context_data: 上下文数据

        Returns:
            AI回复内容
        """
        # 1. 构建Prompt
        messages = AIPromptBuilder.build_chat_prompt(
            user_message=user_message, history=history, context_symbol=context_symbol, context_data=context_data
        )

        # 2. 调用AI
        ai_reply = await ai_client.chat_completion(messages=messages, temperature=0.7, max_tokens=1000)

        return ai_reply


class AIChatBuilder:
    """
    AI对话构建器（静态类）

    职责：构建响应数据结构
    """

    @staticmethod
    def build_session_response(
        session_id: str, user_id: int, context_symbol: Optional[str], context_type: Optional[str]
    ) -> dict:
        """构建会话创建响应"""
        return {
            "session_id": session_id,
            "user_id": user_id,
            "context_symbol": context_symbol,
            "context_type": context_type,
            "created_at": datetime.now().isoformat(),
        }

    @staticmethod
    def build_message_response(message: dict) -> dict:
        """构建消息响应"""
        return {
            "message_id": message.get("timestamp", ""),  # 使用timestamp作为消息ID
            "role": message.get("role", "assistant"),
            "content": message.get("content", ""),
            "timestamp": message.get("timestamp", datetime.now().isoformat()),
        }

    @staticmethod
    def build_history_response(session_id: str, messages: list) -> dict:
        """构建历史消息响应"""
        return {"session_id": session_id, "total": len(messages), "messages": messages}

    @staticmethod
    def build_delete_response(deleted_count: int) -> dict:
        """构建删除响应"""
        return {"message": "会话已删除", "deleted_count": deleted_count}
