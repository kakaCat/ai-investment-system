"""
Daily Review Service

每日复盘业务服务 - Service + Converter + Builder
"""

import json
from datetime import datetime
from typing import Optional, List, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.holding_repo import HoldingRepository
from app.repositories.stock_repo import StockRepository
from app.repositories.event_repo import EventRepository
from app.repositories.review_repo import ReviewRepository
from app.utils.ai_client import ai_client, AIPromptBuilder


class DailyReviewService:
    """
    每日复盘业务类

    职责：权限校验、编排流程、事务管理
    """

    def __init__(self):
        self.holding_repo = HoldingRepository()
        self.stock_repo = StockRepository()
        self.event_repo = EventRepository()
        self.review_repo = ReviewRepository()

    async def get_analyzable_stocks(self, db: AsyncSession, user_id: int) -> dict:
        """
        获取可分析股票列表（持仓+自选）

        Args:
            db: 数据库会话
            user_id: 用户ID

        Returns:
            可分析股票列表
        """
        # 查询持仓股票
        holdings = await self.holding_repo.get_by_user(db, user_id)

        # 转换为列表格式
        holdings_list = [
            {
                "symbol": h.symbol,
                "name": h.stock_name,
                "type": "holding",
                "quantity": float(h.quantity) if h.quantity else 0,
                "cost_price": float(h.cost_price) if h.cost_price else 0,
            }
            for h in holdings
        ]

        # TODO: 查询自选股（需要添加watchlist表）
        watchlist = []

        return DailyReviewBuilder.build_stocks_response(holdings_list, watchlist)

    async def generate_review(self, db: AsyncSession, user_id: int, review_date: Optional[str] = None) -> dict:
        """
        生成每日复盘报告

        Args:
            db: 数据库会话
            user_id: 用户ID
            review_date: 复盘日期（可选）

        Returns:
            生成任务信息
        """
        target_date = review_date or datetime.now().strftime("%Y-%m-%d")

        # 1. 获取持仓数据
        holdings = await self.holding_repo.get_by_user(db, user_id)
        holdings_data = [
            {
                "symbol": h.symbol,
                "stock_name": h.stock_name,
                "quantity": float(h.quantity) if h.quantity else 0,
                "cost_price": float(h.cost_price) if h.cost_price else 0,
            }
            for h in holdings
        ]

        # 2. 获取重要事件
        events = await self.event_repo.query_by_user(
            db=db,
            user_id=user_id,
            start_date=datetime.strptime(target_date, "%Y-%m-%d").date(),
            end_date=datetime.strptime(target_date, "%Y-%m-%d").date(),
        )

        events_data = [
            {
                "title": e.title,
                "content": e.content[:200] if e.content else "",  # 限制长度
                "category": e.category,
                "impact_level": e.impact_level,
            }
            for e in events[:5]  # 最多5个事件
        ]

        # 3. 调用AI生成复盘
        review_content = await DailyReviewConverter.generate_review_with_ai(
            date=target_date, holdings=holdings_data, events=events_data
        )

        # 4. 保存复盘报告
        review_data = {"user_id": user_id, "review_date": target_date, "content": review_content, "type": "daily"}

        review = await self.review_repo.create(db, review_data)
        await db.commit()

        return DailyReviewBuilder.build_task_response(review_id=review.review_id, status="completed")

    async def get_review(self, db: AsyncSession, user_id: int, review_date: Optional[str] = None) -> dict:
        """
        获取每日复盘报告

        Args:
            db: 数据库会话
            user_id: 用户ID
            review_date: 复盘日期（可选，默认最新）

        Returns:
            复盘报告
        """
        if review_date:
            # 查询指定日期的复盘
            review = await self.review_repo.get_by_date(db, user_id, review_date)
        else:
            # 查询最新复盘
            review = await self.review_repo.get_latest(db, user_id)

        if not review:
            return DailyReviewBuilder.build_review_response(None)

        # 解析复盘内容
        review_data = DailyReviewConverter.parse_review_content(
            review_id=review.review_id,
            user_id=user_id,
            date=review.review_date,
            content=review.content,
            created_at=review.created_at,
        )

        return DailyReviewBuilder.build_review_response(review_data)


class DailyReviewConverter:
    """
    每日复盘转换器（静态类）

    职责：业务逻辑计算
    """

    @staticmethod
    async def generate_review_with_ai(date: str, holdings: List[Dict], events: List[Dict]) -> str:
        """
        使用AI生成复盘报告

        Args:
            date: 复盘日期
            holdings: 持仓列表
            events: 事件列表

        Returns:
            复盘内容JSON字符串
        """
        # 构建Prompt
        messages = AIPromptBuilder.build_daily_review_prompt(date=date, holdings=holdings, events=events)

        # 调用AI
        ai_response = await ai_client.chat_completion(messages=messages, temperature=0.7, max_tokens=2000)

        # 解析AI响应
        try:
            review_content = DailyReviewConverter._parse_ai_review(ai_response)
        except Exception as e:
            print(f"解析AI复盘失败: {e}")
            review_content = DailyReviewConverter._get_default_review(date)

        return json.dumps(review_content, ensure_ascii=False)

    @staticmethod
    def _parse_ai_review(ai_response: str) -> dict:
        """解析AI复盘响应"""
        response = ai_response.strip()

        # 移除markdown代码块
        if "```json" in response:
            start = response.find("```json") + 7
            end = response.find("```", start)
            response = response[start:end].strip()
        elif "```" in response:
            start = response.find("```") + 3
            end = response.find("```", start)
            response = response[start:end].strip()

        # 提取JSON
        if "{" in response:
            start = response.find("{")
            end = response.rfind("}") + 1
            json_str = response[start:end]
            result = json.loads(json_str)

            # 验证必需字段
            if "summary" in result:
                return result

        raise ValueError("无法解析AI复盘响应")

    @staticmethod
    def _get_default_review(date: str) -> dict:
        """获取默认复盘内容"""
        return {
            "summary": f"{date} 市场概况",
            "holdings_analysis": "持仓数据分析中...",
            "events_impact": "暂无重要事件",
            "suggestions": ["持续关注市场动态"],
            "risks": ["市场波动风险"],
            "next_actions": ["保持观察"],
        }

    @staticmethod
    def parse_review_content(review_id: int, user_id: int, date: str, content: str, created_at: datetime) -> dict:
        """解析复盘内容"""
        try:
            content_dict = json.loads(content) if content else {}
        except Exception:
            content_dict = {}

        return {
            "review_id": review_id,
            "user_id": user_id,
            "date": date,
            "summary": content_dict.get("summary", ""),
            "holdings_analysis": content_dict.get("holdings_analysis", ""),
            "events_impact": content_dict.get("events_impact", ""),
            "suggestions": content_dict.get("suggestions", []),
            "risks": content_dict.get("risks", []),
            "next_actions": content_dict.get("next_actions", []),
            "created_at": created_at.isoformat() if created_at else None,
        }


class DailyReviewBuilder:
    """
    每日复盘构建器（静态类）

    职责：构建响应数据结构
    """

    @staticmethod
    def build_stocks_response(holdings: List[Dict], watchlist: List[Dict]) -> dict:
        """构建可分析股票列表响应"""
        return {"holdings": holdings, "watchlist": watchlist, "total": len(holdings) + len(watchlist)}

    @staticmethod
    def build_task_response(review_id: int, status: str) -> dict:
        """构建复盘生成任务响应"""
        return {
            "review_id": review_id,
            "status": status,
            "message": "复盘报告已生成" if status == "completed" else "生成中",
        }

    @staticmethod
    def build_review_response(review_data: Optional[dict]) -> dict:
        """构建复盘报告响应"""
        if not review_data:
            return {"message": "暂无复盘报告", "data": None}

        return review_data
