"""
Service Template - {Feature}功能

========================================
使用说明
========================================
1. 复制此文件到 backend/app/services/{module}/{action}_service.py
2. 全局替换以下占位符:
   - {Feature} → 功能名称（如 AccountDetail）
   - {Module} → 模块名称（如 account）
   - {Action} → 动作名称（如 detail）
3. 根据实际业务逻辑填充 TODO 部分
4. 确保 Converter 和 Builder 所有方法使用 @staticmethod

========================================
架构约束
========================================
✅ Service + Converter + Builder 三个类必须在同一文件
✅ Converter 负责所有业务逻辑和计算
✅ Builder 负责构建响应数据结构
✅ Converter 和 Builder 所有方法必须是 @staticmethod
✅ Service 负责权限检查、数据获取、调用 Converter
✅ 不允许在 Repository 中编写业务逻辑

参考文档: backend/ARCHITECTURE.md
"""

from typing import Dict, List, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession

# TODO: 导入需要的 Repository
# from backend.app.repositories.{module}_repo import {Module}Repository

# TODO: 导入需要的 Model
# from backend.app.models.{module} import {Module}


# ========================================
# Service 类 - 业务编排
# ========================================
class {Feature}Service:
    """
    {Feature}业务服务

    职责:
    - 权限检查
    - 数据获取（调用 Repository）
    - 业务编排（调用 Converter）
    - 事务管理
    """

    def __init__(self, db: AsyncSession):
        """
        初始化 Service

        Args:
            db: 数据库会话
        """
        self.db = db
        # TODO: 初始化需要的 Repository
        # self.{module}_repo = {Module}Repository(db)

    async def execute(
        self,
        request: Dict[str, Any],
        user_id: int
    ) -> Dict[str, Any]:
        """
        执行业务逻辑

        Args:
            request: 请求参数
            user_id: 当前用户ID

        Returns:
            响应数据

        Raises:
            PermissionError: 无权限访问
            ValueError: 参数错误
            Exception: 其他业务异常
        """
        # TODO: 第1步 - 参数验证
        # self._validate_request(request)

        # TODO: 第2步 - 权限检查
        # await self._check_permission(request, user_id)

        # TODO: 第3步 - 获取数据
        # data = await self._fetch_data(request)

        # TODO: 第4步 - 调用 Converter 处理业务逻辑
        # result = {Feature}Converter.convert(data)

        # TODO: 第5步 - 返回结果
        # return result

        raise NotImplementedError("请实现业务逻辑")

    def _validate_request(self, request: Dict[str, Any]) -> None:
        """
        验证请求参数

        Args:
            request: 请求参数

        Raises:
            ValueError: 参数错误
        """
        # TODO: 实现参数验证逻辑
        # required_fields = ["field1", "field2"]
        # for field in required_fields:
        #     if field not in request:
        #         raise ValueError(f"缺少必需参数: {field}")
        pass

    async def _check_permission(
        self,
        request: Dict[str, Any],
        user_id: int
    ) -> None:
        """
        检查用户权限

        Args:
            request: 请求参数
            user_id: 当前用户ID

        Raises:
            PermissionError: 无权限访问
        """
        # TODO: 实现权限检查逻辑
        # 示例:
        # resource = await self.{module}_repo.get_by_id(request["id"])
        # if resource.user_id != user_id:
        #     raise PermissionError("无权访问此资源")
        pass

    async def _fetch_data(
        self,
        request: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        获取业务数据

        Args:
            request: 请求参数

        Returns:
            业务数据字典
        """
        # TODO: 调用 Repository 获取数据
        # 示例:
        # main_data = await self.{module}_repo.get_by_id(request["id"])
        # related_data = await self.related_repo.query_by_xxx(xxx)
        #
        # return {
        #     "main": main_data,
        #     "related": related_data
        # }

        raise NotImplementedError("请实现数据获取逻辑")


# ========================================
# Converter 类 - 业务逻辑
# ========================================
class {Feature}Converter:
    """
    {Feature}业务逻辑转换器

    职责:
    - 所有业务逻辑和计算
    - 数据转换和聚合
    - 调用 Builder 构建响应

    约束:
    - 所有方法必须使用 @staticmethod
    - 不允许访问数据库（通过 Service 获取数据）
    - 不允许修改输入参数
    """

    @staticmethod
    def convert(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        主转换方法

        Args:
            data: Service 传入的业务数据

        Returns:
            转换后的响应数据
        """
        # TODO: 第1步 - 执行业务计算
        # calculated_value = {Feature}Converter._calculate_xxx(data)

        # TODO: 第2步 - 聚合数据
        # aggregated_data = {Feature}Converter._aggregate_xxx(data)

        # TODO: 第3步 - 调用 Builder 构建响应
        # return {Feature}Builder.build_response(
        #     main_data=data["main"],
        #     calculated_value=calculated_value,
        #     aggregated_data=aggregated_data
        # )

        raise NotImplementedError("请实现转换逻辑")

    @staticmethod
    def _calculate_xxx(data: Dict[str, Any]) -> Any:
        """
        业务计算示例

        Args:
            data: 输入数据

        Returns:
            计算结果
        """
        # TODO: 实现具体计算逻辑
        # 示例:
        # total = sum(item.amount for item in data["items"])
        # return total

        raise NotImplementedError("请实现计算逻辑")

    @staticmethod
    def _aggregate_xxx(data: Dict[str, Any]) -> Any:
        """
        数据聚合示例

        Args:
            data: 输入数据

        Returns:
            聚合结果
        """
        # TODO: 实现具体聚合逻辑
        # 示例:
        # grouped = {}
        # for item in data["items"]:
        #     key = item.category
        #     if key not in grouped:
        #         grouped[key] = []
        #     grouped[key].append(item)
        # return grouped

        raise NotImplementedError("请实现聚合逻辑")

    @staticmethod
    def _transform_xxx(item: Any) -> Dict[str, Any]:
        """
        单项转换示例

        Args:
            item: 单个数据项

        Returns:
            转换后的数据
        """
        # TODO: 实现单项转换逻辑
        # 示例:
        # return {
        #     "id": item.id,
        #     "name": item.name,
        #     "status": item.status.value,
        #     "created_at": item.created_at.isoformat()
        # }

        raise NotImplementedError("请实现转换逻辑")


# ========================================
# Builder 类 - 响应构建
# ========================================
class {Feature}Builder:
    """
    {Feature}响应数据构建器

    职责:
    - 构建标准化的响应数据结构
    - 格式化输出数据

    约束:
    - 所有方法必须使用 @staticmethod
    - 只负责数据结构组装，不做业务计算
    """

    @staticmethod
    def build_response(**kwargs) -> Dict[str, Any]:
        """
        构建主响应数据

        Args:
            **kwargs: 各部分数据

        Returns:
            完整的响应数据结构
        """
        # TODO: 构建响应数据结构
        # 示例:
        # return {
        #     "data": {
        #         "main": {Feature}Builder._build_main_data(kwargs["main_data"]),
        #         "stats": {Feature}Builder._build_stats(kwargs["calculated_value"]),
        #         "summary": {Feature}Builder._build_summary(kwargs["aggregated_data"])
        #     },
        #     "meta": {
        #         "timestamp": datetime.utcnow().isoformat(),
        #         "version": "1.0"
        #     }
        # }

        raise NotImplementedError("请实现响应构建逻辑")

    @staticmethod
    def _build_main_data(data: Any) -> Dict[str, Any]:
        """
        构建主数据部分

        Args:
            data: 主数据对象

        Returns:
            格式化的主数据
        """
        # TODO: 实现主数据构建
        # 示例:
        # return {
        #     "id": data.id,
        #     "name": data.name,
        #     "status": data.status.value,
        #     "created_at": data.created_at.isoformat()
        # }

        raise NotImplementedError("请实现数据构建逻辑")

    @staticmethod
    def _build_stats(stats: Dict[str, Any]) -> Dict[str, Any]:
        """
        构建统计数据部分

        Args:
            stats: 统计数据

        Returns:
            格式化的统计数据
        """
        # TODO: 实现统计数据构建
        # 示例:
        # return {
        #     "total": stats["total"],
        #     "average": round(stats["average"], 2),
        #     "max": stats["max"],
        #     "min": stats["min"]
        # }

        raise NotImplementedError("请实现统计构建逻辑")

    @staticmethod
    def _build_list(items: List[Any]) -> List[Dict[str, Any]]:
        """
        构建列表数据

        Args:
            items: 数据项列表

        Returns:
            格式化的列表数据
        """
        # TODO: 实现列表数据构建
        # 示例:
        # return [
        #     {
        #         "id": item.id,
        #         "name": item.name,
        #         "value": item.value
        #     }
        #     for item in items
        # ]

        raise NotImplementedError("请实现列表构建逻辑")


# ========================================
# 使用示例
# ========================================
"""
# 在 API Controller 中调用:

@router.post("/{action}")
async def {action}_endpoint(
    request: dict,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    service = {Feature}Service(db)
    result = await service.execute(request, user.id)
    return result
"""
