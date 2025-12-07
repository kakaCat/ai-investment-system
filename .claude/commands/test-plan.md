# 测试计划生成

为功能模块生成完整的测试计划和测试用例框架。

---

请为 $ARGUMENTS 生成测试计划：

## 分析内容

### 1. 功能分析
- 理解功能需求和业务逻辑
- 识别输入输出
- 确定边界条件

### 2. 测试范围确定
- 单元测试范围（Service/Converter/Builder）
- 集成测试范围（API 端点）
- E2E 测试范围（用户流程）

### 3. 测试用例设计
- 正常流程测试
- 边界条件测试
- 异常情况测试
- 权限测试

### 4. 测试数据准备
- 需要的测试数据
- Mock 数据设计
- Fixture 准备

## 输出格式

```
## 测试计划

### 📋 测试概述
- **功能模块**: {模块名称}
- **测试范围**: {描述}
- **预计用例数**: X 个
- **预计工时**: X 小时

### 🎯 测试目标
1. 验证 {目标1}
2. 验证 {目标2}
3. 确保 {目标3}

---

## 单元测试

### 文件: `tests/unit/backend/services/test_{action}_service.py`

#### Converter 测试

```python
import pytest
from app.services.{module}.{action}_service import {Action}Converter

class Test{Action}Converter:
    """测试 {Action}Converter 业务逻辑"""

    # 正常流程测试
    def test_convert_success(self):
        """测试正常转换流程"""
        # Given
        input_data = {...}

        # When
        result = {Action}Converter.convert(input_data)

        # Then
        assert result["field"] == expected_value

    def test_convert_with_empty_list(self):
        """测试空列表输入"""
        pass

    # 边界条件测试
    def test_convert_with_max_value(self):
        """测试最大值边界"""
        pass

    def test_convert_with_min_value(self):
        """测试最小值边界"""
        pass

    # 计算逻辑测试
    def test_calculate_total(self):
        """测试金额计算逻辑"""
        pass

    def test_calculate_with_zero(self):
        """测试零值计算"""
        pass

    # 异常测试
    def test_convert_with_invalid_input(self):
        """测试无效输入"""
        with pytest.raises(ValueError):
            {Action}Converter.convert(invalid_data)
```

#### Builder 测试

```python
class Test{Action}Builder:
    """测试 {Action}Builder 数据构建"""

    def test_build_response_structure(self):
        """测试响应结构完整性"""
        pass

    def test_build_with_optional_fields(self):
        """测试可选字段处理"""
        pass
```

#### Service 测试

```python
class Test{Action}Service:
    """测试 {Action}Service 编排逻辑"""

    @pytest.fixture
    def service(self):
        return {Action}Service()

    @pytest.fixture
    def mock_repo(self, mocker):
        return mocker.patch.object({Table}Repository, 'get_by_id')

    def test_execute_success(self, service, mock_repo):
        """测试正常执行流程"""
        pass

    def test_execute_permission_denied(self, service, mock_repo):
        """测试权限拒绝"""
        pass

    def test_execute_not_found(self, service, mock_repo):
        """测试资源不存在"""
        pass
```

---

## 集成测试

### 文件: `tests/integration/api/test_{module}_api.py`

```python
import pytest
from httpx import AsyncClient
from app.main import app

class Test{Action}API:
    """测试 {action} API 端点"""

    @pytest.fixture
    async def client(self):
        async with AsyncClient(app=app, base_url="http://test") as ac:
            yield ac

    @pytest.fixture
    def auth_headers(self):
        return {"Authorization": "Bearer test_token"}

    # 成功场景
    async def test_api_success(self, client, auth_headers):
        """测试 API 正常响应"""
        response = await client.post(
            "/api/v1/{module}/{action}",
            json={...},
            headers=auth_headers
        )
        assert response.status_code == 200
        assert response.json()["code"] == 0

    # 参数验证
    async def test_api_missing_required_param(self, client, auth_headers):
        """测试缺少必填参数"""
        response = await client.post(
            "/api/v1/{module}/{action}",
            json={},
            headers=auth_headers
        )
        assert response.status_code == 400

    # 认证测试
    async def test_api_unauthorized(self, client):
        """测试未认证访问"""
        response = await client.post(
            "/api/v1/{module}/{action}",
            json={...}
        )
        assert response.status_code == 401

    # 权限测试
    async def test_api_forbidden(self, client, auth_headers):
        """测试无权限访问"""
        response = await client.post(
            "/api/v1/{module}/{action}",
            json={"id": other_user_resource_id},
            headers=auth_headers
        )
        assert response.status_code == 403
```

---

## 测试数据

### Fixtures

```python
# tests/conftest.py

@pytest.fixture
def sample_{entity}():
    """示例{实体}数据"""
    return {
        "id": 1,
        "name": "test",
        ...
    }

@pytest.fixture
def sample_{entity}_list():
    """示例{实体}列表"""
    return [...]
```

### Mock 数据

```python
# tests/mocks/{module}_mocks.py

MOCK_{ENTITY}_DATA = {
    "valid": {...},
    "invalid": {...},
    "edge_case": {...}
}
```

---

## 测试矩阵

| 测试场景 | 单元 | 集成 | E2E | 优先级 |
|----------|------|------|-----|--------|
| 正常流程 | ✅ | ✅ | ✅ | P0 |
| 空数据 | ✅ | ✅ | - | P1 |
| 边界值 | ✅ | - | - | P1 |
| 权限控制 | ✅ | ✅ | ✅ | P0 |
| 并发访问 | - | ✅ | - | P2 |
| 大数据量 | - | ✅ | - | P2 |

---

## 执行命令

```bash
# 运行单元测试
pytest tests/unit/backend/services/test_{action}_service.py -v

# 运行集成测试
pytest tests/integration/api/test_{module}_api.py -v

# 运行覆盖率
pytest tests/unit/backend/services/test_{action}_service.py --cov=app/services/{module} --cov-report=html

# 运行所有相关测试
pytest tests/ -k "{action}" -v
```
```

## 使用示例
- `/test-plan AccountDetailService` - 为 Service 生成测试计划
- `/test-plan 事件分析功能` - 为功能模块生成测试计划
- `/test-plan backend/app/services/event/` - 为目录下所有 Service 生成
