#!/usr/bin/env python3
"""
清空测试数据脚本
"""
import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# 数据库配置
DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/investment_db"


async def clear_test_data():
    """清空测试数据"""
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        try:
            print("🗑️  开始清空测试数据...")

            # 1. 清空AI决策表
            result = await session.execute(text("DELETE FROM ai_decisions"))
            decision_count = result.rowcount
            print(f"   ✅ 删除 {decision_count} 条AI决策记录")

            # 2. 清空测试用户
            result = await session.execute(text("DELETE FROM users WHERE username LIKE 'testuser_%'"))
            user_count = result.rowcount
            print(f"   ✅ 删除 {user_count} 个测试用户")

            # 3. 清空聊天会话和消息（如果表存在）
            try:
                result = await session.execute(text("DELETE FROM ai_chat_messages"))
                message_count = result.rowcount
                print(f"   ✅ 删除 {message_count} 条聊天消息")

                result = await session.execute(text("DELETE FROM ai_chat_sessions"))
                session_count = result.rowcount
                print(f"   ✅ 删除 {session_count} 个聊天会话")
            except:
                print("   ⚠️  聊天表不存在，跳过")

            await session.commit()

            # 4. 统计剩余数据
            result = await session.execute(text("SELECT COUNT(*) FROM users"))
            remaining_users = result.scalar()

            result = await session.execute(text("SELECT COUNT(*) FROM ai_decisions"))
            remaining_decisions = result.scalar()

            print(f"\n✅ 数据清空完成！")
            print(f"   剩余用户: {remaining_users}")
            print(f"   剩余AI决策: {remaining_decisions}")

        except Exception as e:
            await session.rollback()
            print(f"❌ 清空失败: {e}")
            raise
        finally:
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(clear_test_data())
