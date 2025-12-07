# 集成测试指南

> API和服务集成测试完整指南

---

## 📐 概述

**目的**: 验证API端点、数据库操作和第三方服务集成的正确性

**技术栈**: pytest + FastAPI TestClient + PostgreSQL Test Database

**覆盖范围**:
- API端点测试（Controller → Service → Repository → DB）
- 数据库事务测试
- 第三方API集成（DeepSeek、Tushare）
- 认证和权限验证

---

## 🔧 环境配置

### 安装依赖

```bash
pip install pytest pytest-asyncio httpx
```

### 测试数据库配置

```python
# backend/tests/conftest.py
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

TEST_DATABASE_URL = "postgresql+asyncpg://user:pass@localhost/test_db"

@pytest.fixture
async def db_session():
    """创建测试数据库会话"""
    engine = create_async_engine(TEST_DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        yield session
        await session.rollback()  # 回滚测试数据

@pytest.fixture
async def client():
    """创建测试客户端"""
    from app.main import app
    from httpx import AsyncClient

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
```

---

## ✍️ API端点测试

### 基础API测试

```python
# tests/integration/api/test_account_api.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_query_accounts(client: AsyncClient, auth_headers):
    """测试查询账户列表API"""
    # Arrange
    request_data = {
        "page": 1,
        "page_size": 20
    }

    # Act
    response = await client.post(
        "/api/v1/account/query",
        json=request_data,
        headers=auth_headers
    )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert "data" in data
    assert "items" in data["data"]
    assert "pagination" in data["data"]

@pytest.mark.asyncio
async def test_create_account(client: AsyncClient, auth_headers):
    """测试创建账户API"""
    # Arrange
    request_data = {
        "name": "测试账户",
        "account_type": "a_share",
        "initial_balance": 100000.0,
        "broker": "中信证券"
    }

    # Act
    response = await client.post(
        "/api/v1/account/create",
        json=request_data,
        headers=auth_headers
    )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert data["data"]["id"] is not None
    assert data["data"]["name"] == "测试账户"
```

### 认证测试

```python
@pytest.mark.asyncio
async def test_unauthorized_access(client: AsyncClient):
    """测试未授权访问"""
    response = await client.post("/api/v1/account/query", json={})
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_permission_denied(client: AsyncClient, auth_headers):
    """测试权限不足"""
    # 尝试访问其他用户的账户
    response = await client.post(
        "/api/v1/account/detail",
        json={"account_id": 999999},  # 不属于当前用户
        headers=auth_headers
    )
    assert response.status_code == 403
```

### 参数验证测试

```python
@pytest.mark.asyncio
async def test_missing_required_params(client: AsyncClient, auth_headers):
    """测试缺少必需参数"""
    response = await client.post(
        "/api/v1/account/create",
        json={},  # 缺少必需参数
        headers=auth_headers
    )
    assert response.status_code == 400

@pytest.mark.asyncio
async def test_invalid_param_type(client: AsyncClient, auth_headers):
    """测试参数类型错误"""
    response = await client.post(
        "/api/v1/account/create",
        json={
            "name": "测试",
            "account_type": "invalid_type",  # 无效的枚举值
            "initial_balance": "not_a_number"  # 错误的类型
        },
        headers=auth_headers
    )
    assert response.status_code == 400
```

---

## 🗄️ 数据库集成测试

### 基础CRUD测试

```python
# tests/integration/repositories/test_account_repository.py
import pytest
from app.repositories.account_repo import AccountRepository

@pytest.mark.asyncio
async def test_create_account(db_session):
    """测试创建账户"""
    # Arrange
    repo = AccountRepository(db_session)
    data = {
        "user_id": 1,
        "name": "测试账户",
        "account_type": "a_share",
        "broker": "中信证券",
        "account_number": "1234567890"
    }

    # Act
    account = await repo.create(data)
    await db_session.commit()

    # Assert
    assert account.id is not None
    assert account.name == "测试账户"
    assert account.user_id == 1

@pytest.mark.asyncio
async def test_query_by_user(db_session):
    """测试查询用户账户"""
    repo = AccountRepository(db_session)

    # 创建测试数据
    await repo.create({"user_id": 1, "name": "账户1", ...})
    await repo.create({"user_id": 1, "name": "账户2", ...})
    await db_session.commit()

    # 查询
    accounts = await repo.query_by_user(user_id=1)

    # 验证
    assert len(accounts) >= 2
    assert all(a.user_id == 1 for a in accounts)
```

### 事务测试

```python
@pytest.mark.asyncio
async def test_transaction_rollback(db_session):
    """测试事务回滚"""
    repo = AccountRepository(db_session)

    try:
        # 创建账户
        account = await repo.create({"user_id": 1, "name": "测试", ...})

        # 模拟错误
        raise Exception("模拟错误")

    except Exception:
        await db_session.rollback()

    # 验证数据未提交
    accounts = await repo.query_by_user(user_id=1)
    assert len([a for a in accounts if a.name == "测试"]) == 0
```

---

## 🌐 第三方服务集成测试

### Mock外部API

```python
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_deepseek_api_integration():
    """测试DeepSeek API集成"""
    with patch('app.services.ai.deepseek_client.chat') as mock_chat:
        # 配置Mock
        mock_chat.return_value = AsyncMock(
            choices=[{"message": {"content": "分析结果"}}]
        )

        # 调用服务
        from app.services.ai.analysis_service import AnalysisService
        service = AnalysisService()
        result = await service.analyze_stock("600000")

        # 验证
        assert result is not None
        mock_chat.assert_called_once()
```

---

## 📊 Fixture使用

### 常用Fixture

```python
# tests/conftest.py

@pytest.fixture
async def auth_headers(test_user):
    """认证头"""
    token = generate_jwt_token(test_user.id)
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
async def test_user(db_session):
    """创建测试用户"""
    from app.models.user import User
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=hash_password("Test123456")
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user

@pytest.fixture(autouse=True)
async def cleanup_test_data(db_session):
    """自动清理测试数据"""
    yield
    # 测试结束后清理
    await db_session.rollback()
```

---

## ✅ 最佳实践

1. **独立性**: 每个测试独立运行，不依赖其他测试
2. **幂等性**: 测试可以重复运行，结果一致
3. **清理**: 测试结束后清理数据
4. **Mock外部依赖**: 使用Mock隔离外部服务
5. **使用Fixture**: 复用测试数据和配置

---

## 🔗 相关资源

- [pytest文档](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [SQLAlchemy Testing](https://docs.sqlalchemy.org/en/14/orm/session_transaction.html)

---

**最后更新**: 2025-11-19
