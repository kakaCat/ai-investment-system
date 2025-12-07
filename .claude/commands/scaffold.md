# 模块脚手架生成

根据项目架构规范，自动生成完整的模块代码结构。

---

请为 "$ARGUMENTS" 生成模块脚手架：

## 输入说明
- 功能名称: `账户详情` → 生成 AccountDetail 相关代码
- 模块+动作: `event/analysis` → 生成事件分析模块
- 英文名称: `PortfolioSummary` → 直接使用

## 生成内容

### 1. 后端代码结构

根据 backend/ARCHITECTURE.md 规范生成：

```
backend/app/
├── api/v1/
│   └── {module}_api.py          # 新增 API 端点
├── services/{module}/
│   └── {action}_service.py      # Service + Converter + Builder
├── repositories/
│   └── {table}_repo.py          # Repository（如需要）
└── models/
    └── {table}.py               # Model（如需要）
```

### 2. 测试代码结构

```
tests/
├── unit/backend/services/
│   └── test_{action}_service.py
└── integration/api/
    └── test_{module}_api.py
```

### 3. 文档结构（如需要）

```
docs/design/features/{feature}/
├── README.md
├── requirements.md
└── implementation.md
```

## 输出格式

```
## 脚手架生成报告

### 📋 模块信息
- **功能名称**: {名称}
- **模块**: {module}
- **动作**: {action}
- **类名前缀**: {Action}

---

## 生成的文件

### 1. API 端点

**文件**: `backend/app/api/v1/{module}_api.py`

```python
from fastapi import APIRouter, Depends
from app.core.auth import get_current_user
from app.models.user import User
from app.services.{module}.{action}_service import {Action}Service

router = APIRouter(prefix="/{module}", tags=["{Module}"])


@router.post("/{action}")
async def {action}(request: dict, user: User = Depends(get_current_user)):
    """
    {功能描述}

    ========================================
    接口信息
    ========================================
    接口路径: POST /api/v1/{module}/{action}
    对应页面: pages/{module}/{action}.vue
    接口功能: {功能描述}

    ========================================
    请求参数
    ========================================
    {
        // TODO: 定义请求参数
    }

    ========================================
    响应数据
    ========================================
    {
        "code": 0,
        "message": "success",
        "data": {
            // TODO: 定义响应结构
        }
    }

    ========================================
    执行流程（时序）
    ========================================
    1. 验证用户登录
    2. 参数校验
    3. 权限检查
    4. 调用 Service 处理业务
    5. 返回结果

    ========================================
    业务规则
    ========================================
    1. TODO: 添加业务规则

    ========================================
    错误码
    ========================================
    400: 参数错误
    401: 未登录
    403: 无权限

    ========================================
    前端调用示例
    ========================================
    const response = await api.post('/api/v1/{module}/{action}', {
        // params
    })

    ========================================
    修改记录
    ========================================
    {date}: 初始版本
    """
    service = {Action}Service()
    return await service.execute(request, user.id)
```

---

### 2. Service 层

**文件**: `backend/app/services/{module}/{action}_service.py`

```python
"""
{Action} 业务场景服务

相关架构文档:
- backend/ARCHITECTURE.md
- docs/design/architecture/backend-architecture.md
"""

from app.repositories.{table}_repo import {Table}Repository


class {Action}Service:
    """
    {Action} 业务场景服务

    业务描述: {功能描述}
    """

    def __init__(self):
        self.{table}_repo = {Table}Repository()

    async def execute(self, request: dict, user_id: int) -> dict:
        """
        执行 {Action} 业务逻辑

        Args:
            request: 请求参数
            user_id: 当前用户ID

        Returns:
            处理结果
        """
        # 1. 权限检查
        # TODO: 实现权限验证

        # 2. 获取数据
        # data = await self.{table}_repo.get_by_id(request["id"])

        # 3. 业务处理
        # result = {Action}Converter.convert(data)

        # 4. 返回结果
        return {Action}Builder.build_response()


class {Action}Converter:
    """
    {Action} 业务逻辑转换器

    ⚠️ 所有方法必须是 @staticmethod
    ⚠️ 所有业务计算逻辑在这里实现
    """

    @staticmethod
    def convert(data) -> dict:
        """
        核心业务逻辑转换

        Args:
            data: 原始数据

        Returns:
            转换后的业务数据
        """
        # TODO: 实现业务逻辑
        return {Action}Builder.build_response()

    @staticmethod
    def _calculate(data):
        """私有计算方法"""
        # TODO: 实现计算逻辑
        pass


class {Action}Builder:
    """
    {Action} 数据构建器

    ⚠️ 所有方法必须是 @staticmethod
    ⚠️ 只负责数据结构组装
    """

    @staticmethod
    def build_response(**kwargs) -> dict:
        """
        构建 API 响应数据

        Returns:
            标准响应格式
        """
        return {
            "code": 0,
            "message": "success",
            "data": {
                # TODO: 构建响应数据
            }
        }
```

---

### 3. Repository 层（如需要）

**文件**: `backend/app/repositories/{table}_repo.py`

```python
"""
{Table} 数据访问层

⚠️ 只包含纯 CRUD 操作，不包含业务逻辑
"""

from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.models.{table} import {Table}


class {Table}Repository:
    """
    {Table} 数据访问

    职责: 纯数据库操作
    """

    async def get_by_id(self, id: int) -> Optional[{Table}]:
        """根据 ID 获取记录"""
        async with get_session() as session:
            result = await session.execute(
                select({Table}).where({Table}.id == id)
            )
            return result.scalar_one_or_none()

    async def query_by_user(self, user_id: int) -> List[{Table}]:
        """查询用户的所有记录"""
        async with get_session() as session:
            result = await session.execute(
                select({Table}).where({Table}.user_id == user_id)
            )
            return result.scalars().all()

    async def create(self, data: dict) -> {Table}:
        """创建新记录"""
        async with get_session() as session:
            entity = {Table}(**data)
            session.add(entity)
            await session.commit()
            await session.refresh(entity)
            return entity

    async def update(self, id: int, data: dict) -> Optional[{Table}]:
        """更新记录"""
        async with get_session() as session:
            entity = await self.get_by_id(id)
            if entity:
                for key, value in data.items():
                    setattr(entity, key, value)
                await session.commit()
                await session.refresh(entity)
            return entity

    async def delete(self, id: int) -> bool:
        """软删除记录"""
        async with get_session() as session:
            entity = await self.get_by_id(id)
            if entity:
                entity.is_deleted = True
                await session.commit()
                return True
            return False
```

---

### 4. 单元测试

**文件**: `tests/unit/backend/services/test_{action}_service.py`

```python
import pytest
from app.services.{module}.{action}_service import (
    {Action}Service,
    {Action}Converter,
    {Action}Builder
)


class Test{Action}Converter:
    """测试 {Action}Converter"""

    def test_convert_success(self):
        """测试正常转换"""
        # Given
        input_data = {}

        # When
        result = {Action}Converter.convert(input_data)

        # Then
        assert "data" in result

    def test_convert_empty_input(self):
        """测试空输入"""
        pass


class Test{Action}Builder:
    """测试 {Action}Builder"""

    def test_build_response_structure(self):
        """测试响应结构"""
        result = {Action}Builder.build_response()
        assert "code" in result
        assert "data" in result


class Test{Action}Service:
    """测试 {Action}Service"""

    @pytest.fixture
    def service(self):
        return {Action}Service()

    async def test_execute_success(self, service):
        """测试正常执行"""
        pass

    async def test_execute_permission_denied(self, service):
        """测试权限拒绝"""
        pass
```

---

### 5. 集成测试

**文件**: `tests/integration/api/test_{module}_api.py`

```python
import pytest
from httpx import AsyncClient


class Test{Action}API:
    """测试 {action} API"""

    @pytest.fixture
    async def client(self):
        # TODO: 配置测试客户端
        pass

    async def test_api_success(self, client):
        """测试 API 成功响应"""
        response = await client.post(
            "/api/v1/{module}/{action}",
            json={},
            headers={"Authorization": "Bearer test_token"}
        )
        assert response.status_code == 200

    async def test_api_unauthorized(self, client):
        """测试未认证"""
        response = await client.post(
            "/api/v1/{module}/{action}",
            json={}
        )
        assert response.status_code == 401
```

---

## 📋 后续步骤

### 必做
1. [ ] 补充 API 文档中的请求/响应参数
2. [ ] 实现 Service.execute() 业务逻辑
3. [ ] 实现 Converter 计算逻辑
4. [ ] 完善测试用例
5. [ ] 运行 `python scripts/check_architecture.py`

### 建议
6. [ ] 添加到 `backend/app/api/v1/__init__.py` 路由注册
7. [ ] 更新 API 文档
8. [ ] 更新 `management/sprints/current.md` 任务状态
```

## 使用示例
- `/scaffold 账户详情` - 生成账户详情模块
- `/scaffold event/impact-analysis` - 生成事件影响分析模块
- `/scaffold PortfolioSummary` - 生成投资组合汇总模块
