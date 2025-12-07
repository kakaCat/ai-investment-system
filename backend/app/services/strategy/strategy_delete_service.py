"""
Strategy Delete Service

策略删除业务服务 - Service + Converter + Builder
"""

from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.strategy_repo import StrategyRepository
from app.exceptions import PermissionDenied, ResourceNotFound


class StrategyDeleteService:
    """
    策略删除业务类

    职责：权限校验、编排流程、事务管理
    """

    def __init__(self):
        self.strategy_repo = StrategyRepository()

    async def execute(
        self,
        db: AsyncSession,
        user_id: int,
        strategy_id: int
    ) -> dict:
        """
        执行策略删除业务逻辑

        Args:
            db: 数据库会话
            user_id: 用户ID
            strategy_id: 策略ID

        Returns:
            删除结果

        Raises:
            PermissionDenied: 无权访问策略
            ResourceNotFound: 策略不存在
        """
        # 1. 权限校验 - 检查策略归属
        strategy = await self.strategy_repo.get_by_id(db, strategy_id)
        if not strategy:
            raise ResourceNotFound(f"策略ID {strategy_id} 不存在")

        if strategy.user_id != user_id:
            raise PermissionDenied(f"无权访问策略ID {strategy_id}")

        # 2. 软删除策略
        success = await self.strategy_repo.soft_delete(db, strategy_id)

        # 3. 调用 Builder 构建响应
        return StrategyDeleteBuilder.build_response(success, strategy_id)


class StrategyDeleteConverter:
    """
    策略删除转换器（静态类）

    职责：业务逻辑处理（本场景不需要）
    """
    pass


class StrategyDeleteBuilder:
    """
    策略删除数据构建器（静态类）

    职责：构建响应对象
    """

    @staticmethod
    def build_response(success: bool, strategy_id: int) -> dict:
        """
        构建策略删除响应

        Args:
            success: 是否删除成功
            strategy_id: 策略ID

        Returns:
            删除结果字典
        """
        return {
            "success": success,
            "strategy_id": strategy_id,
            "message": "策略已删除" if success else "删除失败"
        }
