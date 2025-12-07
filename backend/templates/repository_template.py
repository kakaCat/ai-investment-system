"""
Repository Template - {Module}数据访问层

========================================
使用说明
========================================
1. 复制此文件到 backend/app/repositories/{module}_repo.py
2. 全局替换以下占位符:
   - {Module} → 模块名称（如 Account）
   - {module} → 模块名称小写（如 account）
   - {table} → 表名（如 accounts）
3. 根据实际需求添加查询方法
4. 确保不在 Repository 中编写业务逻辑

========================================
架构约束
========================================
✅ Repository只负责数据访问，不允许编写业务逻辑
✅ 所有方法必须是纯粹的CRUD操作
✅ 不允许在Repository中进行数据计算
✅ 不允许在Repository中调用其他Repository
✅ 使用软删除（is_deleted字段）
✅ 查询时默认过滤已删除记录

参考文档: backend/ARCHITECTURE.md
"""

from typing import List, Optional
from sqlalchemy import select, update, and_, or_, desc, asc
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

# TODO: 导入Model
# from backend.app.models.{module} import {Module}


class {Module}Repository:
    """
    {Module}数据访问仓库

    职责:
    - 提供纯粹的数据库CRUD操作
    - 不包含任何业务逻辑

    约束:
    - 不允许在此层进行业务计算
    - 不允许调用其他Repository
    - 不允许直接访问HTTP请求或用户信息
    """

    def __init__(self, db: AsyncSession):
        """
        初始化Repository

        Args:
            db: 数据库会话
        """
        self.db = db

    # ========================================
    # 基础CRUD操作
    # ========================================

    async def get_by_id(self, id: int) -> Optional[{Module}]:
        """
        根据ID查询单条记录

        Args:
            id: 记录ID

        Returns:
            {Module}对象，如果不存在或已删除返回None
        """
        # TODO: 实现查询逻辑
        # stmt = select({Module}).where(
        #     and_(
        #         {Module}.id == id,
        #         {Module}.is_deleted == False
        #     )
        # )
        # result = await self.db.execute(stmt)
        # return result.scalar_one_or_none()

        raise NotImplementedError("请实现查询逻辑")

    async def query_by_user(self, user_id: int) -> List[{Module}]:
        """
        查询用户的所有记录

        Args:
            user_id: 用户ID

        Returns:
            {Module}对象列表
        """
        # TODO: 实现查询逻辑
        # stmt = select({Module}).where(
        #     and_(
        #         {Module}.user_id == user_id,
        #         {Module}.is_deleted == False
        #     )
        # ).order_by(desc({Module}.created_at))
        # result = await self.db.execute(stmt)
        # return result.scalars().all()

        raise NotImplementedError("请实现查询逻辑")

    async def query_with_filters(
        self,
        user_id: int,
        filters: Optional[dict] = None,
        page: int = 1,
        page_size: int = 20
    ) -> tuple[List[{Module}], int]:
        """
        条件查询（支持分页）

        Args:
            user_id: 用户ID
            filters: 筛选条件字典
            page: 页码（从1开始）
            page_size: 每页数量

        Returns:
            (记录列表, 总数) 元组
        """
        filters = filters or {}

        # TODO: 构建查询条件
        # conditions = [
        #     {Module}.user_id == user_id,
        #     {Module}.is_deleted == False
        # ]
        #
        # # 添加筛选条件
        # if "status" in filters:
        #     conditions.append({Module}.status == filters["status"])
        #
        # if "keyword" in filters and filters["keyword"]:
        #     conditions.append(
        #         or_(
        #             {Module}.name.ilike(f"%{filters['keyword']}%"),
        #             {Module}.description.ilike(f"%{filters['keyword']}%")
        #         )
        #     )
        #
        # # 查询总数
        # count_stmt = select(func.count()).select_from({Module}).where(and_(*conditions))
        # total_result = await self.db.execute(count_stmt)
        # total = total_result.scalar()
        #
        # # 查询数据
        # stmt = (
        #     select({Module})
        #     .where(and_(*conditions))
        #     .order_by(desc({Module}.created_at))
        #     .offset((page - 1) * page_size)
        #     .limit(page_size)
        # )
        # result = await self.db.execute(stmt)
        # items = result.scalars().all()
        #
        # return items, total

        raise NotImplementedError("请实现查询逻辑")

    async def create(self, data: dict) -> {Module}:
        """
        创建新记录

        Args:
            data: 记录数据字典

        Returns:
            创建的{Module}对象
        """
        # TODO: 实现创建逻辑
        # instance = {Module}(**data)
        # self.db.add(instance)
        # await self.db.flush()
        # await self.db.refresh(instance)
        # return instance

        raise NotImplementedError("请实现创建逻辑")

    async def update(self, id: int, data: dict) -> Optional[{Module}]:
        """
        更新记录

        Args:
            id: 记录ID
            data: 更新数据字典

        Returns:
            更新后的{Module}对象，如果不存在返回None
        """
        # TODO: 实现更新逻辑
        # # 添加更新时间
        # data["updated_at"] = datetime.utcnow()
        #
        # stmt = (
        #     update({Module})
        #     .where(
        #         and_(
        #             {Module}.id == id,
        #             {Module}.is_deleted == False
        #         )
        #     )
        #     .values(**data)
        #     .returning({Module})
        # )
        # result = await self.db.execute(stmt)
        # await self.db.flush()
        # return result.scalar_one_or_none()

        raise NotImplementedError("请实现更新逻辑")

    async def soft_delete(self, id: int) -> bool:
        """
        软删除记录

        Args:
            id: 记录ID

        Returns:
            是否删除成功
        """
        # TODO: 实现软删除逻辑
        # stmt = (
        #     update({Module})
        #     .where(
        #         and_(
        #             {Module}.id == id,
        #             {Module}.is_deleted == False
        #         )
        #     )
        #     .values(
        #         is_deleted=True,
        #         deleted_at=datetime.utcnow()
        #     )
        # )
        # result = await self.db.execute(stmt)
        # await self.db.flush()
        # return result.rowcount > 0

        raise NotImplementedError("请实现删除逻辑")

    # ========================================
    # 特定业务查询（根据需要添加）
    # ========================================

    async def get_by_xxx(self, xxx: str) -> Optional[{Module}]:
        """
        根据特定字段查询

        Args:
            xxx: 查询字段值

        Returns:
            {Module}对象或None
        """
        # TODO: 实现特定查询逻辑
        # 示例: 根据名称查询
        # stmt = select({Module}).where(
        #     and_(
        #         {Module}.name == name,
        #         {Module}.is_deleted == False
        #     )
        # )
        # result = await self.db.execute(stmt)
        # return result.scalar_one_or_none()

        raise NotImplementedError("请实现查询逻辑")

    async def exists(self, **conditions) -> bool:
        """
        检查记录是否存在

        Args:
            **conditions: 查询条件

        Returns:
            是否存在
        """
        # TODO: 实现存在性检查
        # 示例: 检查名称是否已存在
        # stmt = select({Module}.id).where(
        #     and_(
        #         {Module}.name == conditions.get("name"),
        #         {Module}.is_deleted == False
        #     )
        # ).limit(1)
        # result = await self.db.execute(stmt)
        # return result.scalar_one_or_none() is not None

        raise NotImplementedError("请实现存在性检查")

    async def count_by_user(self, user_id: int, **filters) -> int:
        """
        统计用户记录数

        Args:
            user_id: 用户ID
            **filters: 额外筛选条件

        Returns:
            记录数量
        """
        # TODO: 实现计数逻辑
        # conditions = [
        #     {Module}.user_id == user_id,
        #     {Module}.is_deleted == False
        # ]
        #
        # if "status" in filters:
        #     conditions.append({Module}.status == filters["status"])
        #
        # stmt = select(func.count()).select_from({Module}).where(and_(*conditions))
        # result = await self.db.execute(stmt)
        # return result.scalar()

        raise NotImplementedError("请实现计数逻辑")

    async def query_by_ids(self, ids: List[int]) -> List[{Module}]:
        """
        批量查询

        Args:
            ids: ID列表

        Returns:
            {Module}对象列表
        """
        # TODO: 实现批量查询
        # if not ids:
        #     return []
        #
        # stmt = select({Module}).where(
        #     and_(
        #         {Module}.id.in_(ids),
        #         {Module}.is_deleted == False
        #     )
        # )
        # result = await self.db.execute(stmt)
        # return result.scalars().all()

        raise NotImplementedError("请实现批量查询")

    async def bulk_create(self, data_list: List[dict]) -> List[{Module}]:
        """
        批量创建

        Args:
            data_list: 数据字典列表

        Returns:
            创建的{Module}对象列表
        """
        # TODO: 实现批量创建
        # instances = [{Module}(**data) for data in data_list]
        # self.db.add_all(instances)
        # await self.db.flush()
        # for instance in instances:
        #     await self.db.refresh(instance)
        # return instances

        raise NotImplementedError("请实现批量创建")


# ========================================
# Repository使用示例
# ========================================
"""
# 在 Service 中使用:

class SomeService:
    def __init__(self, db: AsyncSession):
        self.{module}_repo = {Module}Repository(db)

    async def execute(self, request: dict, user_id: int):
        # 查询单条记录
        item = await self.{module}_repo.get_by_id(request["id"])

        # 查询用户的所有记录
        items = await self.{module}_repo.query_by_user(user_id)

        # 条件查询
        items, total = await self.{module}_repo.query_with_filters(
            user_id=user_id,
            filters={"status": "active", "keyword": "搜索"},
            page=1,
            page_size=20
        )

        # 创建记录
        new_item = await self.{module}_repo.create({
            "user_id": user_id,
            "name": "示例",
            "status": "active"
        })

        # 更新记录
        updated_item = await self.{module}_repo.update(
            id=123,
            data={"name": "新名称"}
        )

        # 删除记录
        success = await self.{module}_repo.soft_delete(123)

        # 提交事务
        await self.db.commit()

        return result
"""


# ========================================
# 注意事项
# ========================================
"""
❌ 不允许的操作:

1. 在Repository中编写业务逻辑:
   # ❌ 错误示例
   async def calculate_total_value(self, user_id: int):
       items = await self.query_by_user(user_id)
       return sum(item.price * item.quantity for item in items)

   # ✅ 正确做法: 在Converter中计算
   # Repository只负责查询数据，计算由Converter完成

2. 在Repository中调用其他Repository:
   # ❌ 错误示例
   async def get_with_details(self, id: int):
       item = await self.get_by_id(id)
       details = await self.other_repo.query_by_xxx(item.xxx)
       return item, details

   # ✅ 正确做法: 在Service中编排
   # Service调用多个Repository获取数据，然后传给Converter

3. 在Repository中进行数据转换:
   # ❌ 错误示例
   async def get_formatted(self, id: int):
       item = await self.get_by_id(id)
       return {
           "id": item.id,
           "name": item.name,
           "created": item.created_at.isoformat()
       }

   # ✅ 正确做法: 在Builder中格式化
   # Repository返回ORM对象，Builder负责格式化

✅ 允许的操作:

1. 纯粹的数据库查询
2. 简单的条件组合
3. 排序和分页
4. 软删除标记
5. 事务操作（在Service中commit）
"""
