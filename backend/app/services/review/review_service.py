"""
Review Service

股票评价业务服务 - Service + Converter + Builder
"""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.review_repo import ReviewRepository


class ReviewService:
    """
    股票评价业务类

    职责：权限校验、编排流程、事务管理
    """

    def __init__(self):
        self.review_repo = ReviewRepository()

    async def get_review(
        self,
        db: AsyncSession,
        user_id: int,
        symbol: str
    ) -> dict:
        """
        获取用户对股票的评价

        Args:
            db: 数据库会话
            user_id: 用户ID
            symbol: 股票代码

        Returns:
            评价数据（不存在则返回空模板）
        """
        # 1. 查询评价
        review = await self.review_repo.get_by_user_symbol(db, user_id, symbol)

        # 2. 使用Converter转换数据
        if not review:
            # 返回空模板
            return ReviewConverter.convert_empty(user_id, symbol)

        return ReviewConverter.convert(review)

    async def create_or_update(
        self,
        db: AsyncSession,
        user_id: int,
        symbol: str,
        review_data: dict
    ) -> dict:
        """
        创建或更新评价

        Args:
            db: 数据库会话
            user_id: 用户ID
            symbol: 股票代码
            review_data: 评价数据

        Returns:
            评价数据
        """
        # 1. 查询现有评价
        existing_review = await self.review_repo.get_by_user_symbol(db, user_id, symbol)

        # 2. 使用Builder构建数据
        if existing_review:
            # 更新
            update_data = ReviewBuilder.build_update_data(review_data)
            review = await self.review_repo.update(db, existing_review, update_data)
        else:
            # 创建
            create_data = ReviewBuilder.build_create_data(user_id, symbol, review_data)
            review = await self.review_repo.create(db, create_data)

        await db.commit()

        # 3. 使用Converter转换响应
        return ReviewConverter.convert(review)


class ReviewConverter:
    """
    股票评价转换器（静态类）

    职责：业务逻辑计算
    """

    @staticmethod
    def convert(review) -> dict:
        """转换评价对象为字典"""
        return {
            "review_id": review.review_id,
            "user_id": review.user_id,
            "symbol": review.symbol,
            "stock_name": review.stock_name or "",
            "rating": review.rating or 0,
            "bullish_reasons": review.bullish_reasons or [],
            "bearish_reasons": review.bearish_reasons or [],
            "holding_logic": review.holding_logic,
            "target_price": float(review.target_price) if review.target_price else None,
            "stop_loss_price": float(review.stop_loss_price) if review.stop_loss_price else None,
            "created_at": review.created_at.isoformat() if review.created_at else None,
            "updated_at": review.updated_at.isoformat() if review.updated_at else None
        }

    @staticmethod
    def convert_empty(user_id: int, symbol: str) -> dict:
        """生成空评价模板"""
        return {
            "review_id": 0,
            "user_id": user_id,
            "symbol": symbol,
            "stock_name": "",
            "rating": 0,
            "bullish_reasons": [],
            "bearish_reasons": [],
            "holding_logic": None,
            "target_price": None,
            "stop_loss_price": None,
            "created_at": None,
            "updated_at": None
        }


class ReviewBuilder:
    """
    股票评价构建器（静态类）

    职责：构建数据对象
    """

    @staticmethod
    def build_create_data(user_id: int, symbol: str, review_data: dict) -> dict:
        """构建创建数据"""
        return {
            "user_id": user_id,
            "symbol": symbol,
            "stock_name": review_data.get("stock_name", ""),
            "rating": review_data.get("rating", 0),
            "bullish_reasons": review_data.get("bullish_reasons", []),
            "bearish_reasons": review_data.get("bearish_reasons", []),
            "holding_logic": review_data.get("holding_logic"),
            "target_price": review_data.get("target_price"),
            "stop_loss_price": review_data.get("stop_loss_price")
        }

    @staticmethod
    def build_update_data(review_data: dict) -> dict:
        """构建更新数据"""
        update_fields = {}

        if "stock_name" in review_data:
            update_fields["stock_name"] = review_data["stock_name"]
        if "rating" in review_data:
            update_fields["rating"] = review_data["rating"]
        if "bullish_reasons" in review_data:
            update_fields["bullish_reasons"] = review_data["bullish_reasons"]
        if "bearish_reasons" in review_data:
            update_fields["bearish_reasons"] = review_data["bearish_reasons"]
        if "holding_logic" in review_data:
            update_fields["holding_logic"] = review_data["holding_logic"]
        if "target_price" in review_data:
            update_fields["target_price"] = review_data["target_price"]
        if "stop_loss_price" in review_data:
            update_fields["stop_loss_price"] = review_data["stop_loss_price"]

        return update_fields
