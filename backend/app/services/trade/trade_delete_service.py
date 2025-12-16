"""
Trade Delete Service

交易删除业务服务 - Service + Converter + Builder
"""

from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.trade_repo import TradeRepository
from app.exceptions import ResourceNotFound, PermissionDenied


class TradeDeleteService:
    """
    交易删除业务类

    职责：权限校验、编排流程、事务管理
    """

    def __init__(self):
        self.trade_repo = TradeRepository()

    async def execute(self, db: AsyncSession, trade_id: int, user_id: int) -> dict:
        """
        执行交易删除业务逻辑（软删除）

        Args:
            db: 数据库会话
            trade_id: 交易ID
            user_id: 用户ID

        Returns:
            删除结果

        Raises:
            ResourceNotFound: 交易不存在
            PermissionDenied: 无权访问
        """
        # 1. 权限校验 - 查询交易
        trade = await self.trade_repo.get_by_id(db, trade_id)
        if not trade:
            raise ResourceNotFound(f"交易ID {trade_id} 不存在")

        if trade.user_id != user_id:
            raise PermissionDenied(f"无权访问交易ID {trade_id}")

        # 2. 软删除交易
        success = await self.trade_repo.soft_delete(db, trade_id)

        # 3. 调用 Builder 构建响应
        return TradeDeleteBuilder.build_response(success, trade_id)


class TradeDeleteBuilder:
    """
    交易删除数据构建器（静态类）

    职责：构建响应对象
    """

    @staticmethod
    def build_response(success: bool, trade_id: int) -> dict:
        """
        构建交易删除响应

        Args:
            success: 是否删除成功
            trade_id: 交易ID

        Returns:
            删除结果字典
        """
        return {"success": success, "trade_id": trade_id, "message": "交易已删除" if success else "删除失败"}
