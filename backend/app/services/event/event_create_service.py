"""
Event Create Service

事件创建业务服务 - Service + Converter + Builder
"""

from typing import Optional
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.event_repo import EventRepository
from app.exceptions import ValidationError


class EventCreateService:
    """
    事件创建业务类

    职责：权限校验、编排流程、事务管理
    """

    def __init__(self):
        self.event_repo = EventRepository()

    async def execute(
        self,
        db: AsyncSession,
        user_id: int,
        symbol: str,
        stock_name: str,
        category: str,
        subcategory: str,
        title: str,
        content: str,
        event_date: date,
        source: Optional[str] = None,
        source_url: Optional[str] = None,
        impact_level: Optional[int] = None,
        impact_analysis: Optional[str] = None,
        tags: Optional[list] = None,
    ) -> dict:
        """
        执行事件创建业务逻辑

        Args:
            db: 数据库会话
            user_id: 用户ID
            symbol: 股票代码
            stock_name: 股票名称
            category: 事件类别
            subcategory: 事件子类别
            title: 标题
            content: 内容
            event_date: 事件日期
            source: 来源（可选）
            source_url: 来源URL（可选）
            impact_level: 影响等级1-5（可选）
            impact_analysis: 影响分析（可选）
            tags: 标签列表（可选）

        Returns:
            创建的事件数据

        Raises:
            ValidationError: 数据验证失败
        """
        # 1. 数据验证
        EventCreateConverter.validate(
            symbol=symbol,
            stock_name=stock_name,
            category=category,
            subcategory=subcategory,
            title=title,
            content=content,
            impact_level=impact_level,
        )

        # 2. 调用 Converter 准备数据
        data = EventCreateConverter.prepare_data(
            user_id=user_id,
            symbol=symbol,
            stock_name=stock_name,
            category=category,
            subcategory=subcategory,
            title=title,
            content=content,
            event_date=event_date,
            source=source,
            source_url=source_url,
            impact_level=impact_level,
            impact_analysis=impact_analysis,
            tags=tags,
        )

        # 3. 创建事件
        event = await self.event_repo.create(db, data)

        # 4. 调用 Builder 构建响应
        return EventCreateBuilder.build_response(event)


class EventCreateConverter:
    """
    事件创建转换器（静态类）

    职责：数据验证、业务逻辑处理
    """

    @staticmethod
    def validate(
        symbol: str,
        stock_name: str,
        category: str,
        subcategory: str,
        title: str,
        content: str,
        impact_level: Optional[int],
    ) -> None:
        """
        验证事件创建数据

        Args:
            symbol: 股票代码
            stock_name: 股票名称
            category: 事件类别
            subcategory: 事件子类别
            title: 标题
            content: 内容
            impact_level: 影响等级

        Raises:
            ValidationError: 验证失败
        """
        # 验证股票代码
        if not symbol or len(symbol.strip()) == 0:
            raise ValidationError("股票代码不能为空")

        # 验证股票名称
        if not stock_name or len(stock_name.strip()) == 0:
            raise ValidationError("股票名称不能为空")

        # 验证类别
        valid_categories = ["policy", "company", "market", "industry"]
        if category not in valid_categories:
            raise ValidationError(f"事件类别必须是以下之一: {', '.join(valid_categories)}")

        # 验证子类别（根据类别）
        valid_subcategories = {
            "policy": ["monetary", "fiscal", "regulatory", "international"],
            "company": ["earnings", "dividend", "merger", "governance"],
            "market": ["volatility", "rotation", "sentiment", "liquidity"],
            "industry": ["technology", "regulation", "competition", "cycle"],
        }
        if subcategory not in valid_subcategories.get(category, []):
            raise ValidationError(f"事件子类别必须是以下之一: {', '.join(valid_subcategories.get(category, []))}")

        # 验证标题
        if not title or len(title.strip()) == 0:
            raise ValidationError("标题不能为空")
        if len(title) > 200:
            raise ValidationError("标题长度不能超过200个字符")

        # 验证内容
        if not content or len(content.strip()) == 0:
            raise ValidationError("内容不能为空")

        # 验证影响等级
        if impact_level is not None:
            if impact_level < 1 or impact_level > 5:
                raise ValidationError("影响等级必须在1-5之间")

    @staticmethod
    def prepare_data(
        user_id: int,
        symbol: str,
        stock_name: str,
        category: str,
        subcategory: str,
        title: str,
        content: str,
        event_date: date,
        source: Optional[str],
        source_url: Optional[str],
        impact_level: Optional[int],
        impact_analysis: Optional[str],
        tags: Optional[list],
    ) -> dict:
        """
        准备创建事件的数据

        Args:
            user_id: 用户ID
            symbol: 股票代码
            stock_name: 股票名称
            category: 事件类别
            subcategory: 事件子类别
            title: 标题
            content: 内容
            event_date: 事件日期
            source: 来源
            source_url: 来源URL
            impact_level: 影响等级
            impact_analysis: 影响分析
            tags: 标签列表

        Returns:
            准备好的数据字典
        """
        return {
            "user_id": user_id,
            "symbol": symbol.strip().upper(),
            "stock_name": stock_name.strip(),
            "category": category,
            "subcategory": subcategory,
            "title": title.strip(),
            "content": content.strip(),
            "event_date": event_date,
            "source": source.strip() if source else None,
            "source_url": source_url.strip() if source_url else None,
            "impact_level": impact_level,
            "impact_analysis": impact_analysis.strip() if impact_analysis else None,
            "tags": tags if tags else [],
            "is_read": False,  # 新事件默认未读
        }


class EventCreateBuilder:
    """
    事件创建数据构建器（静态类）

    职责：构建响应对象
    """

    @staticmethod
    def build_response(event) -> dict:
        """
        构建事件创建响应

        Args:
            event: 创建的事件对象

        Returns:
            事件数据字典
        """
        return {
            "event_id": event.event_id,
            "symbol": event.symbol,
            "stock_name": event.stock_name,
            "category": event.category,
            "subcategory": event.subcategory,
            "title": event.title,
            "content": event.content,
            "event_date": event.event_date.isoformat() if event.event_date else None,
            "impact_level": event.impact_level,
            "is_read": event.is_read,
            "created_at": event.created_at.isoformat() if event.created_at else None,
        }
