# 单元测试指南

> Service/Converter/Builder/Repository单元测试完整指南

---

## 📐 概述

**目的**: 验证单个函数、类的逻辑正确性

**技术栈**: pytest + unittest.mock

**覆盖范围**:
- Service业务编排
- Converter计算和转换
- Builder数据构建
- Repository数据访问
- 工具函数

**目标覆盖率**: > 80% (关键模块 > 90%)

---

## 🔧 环境配置

```bash
pip install pytest pytest-cov pytest-mock
```

---

## ✍️ Service层测试

### Service测试模板

```python
# tests/unit/services/test_account_detail_service.py
import pytest
from unittest.mock import AsyncMock, Mock
from app.services.account.detail_service import AccountDetailService

@pytest.mark.asyncio
async def test_execute_success():
    """测试Service正常执行流程"""
    # Arrange - Mock依赖
    mock_db = AsyncMock()
    service = AccountDetailService(mock_db)

    # Mock Repository返回值
    mock_account = Mock(id=1, user_id=1, name="测试账户")
    mock_holdings = [
        Mock(quantity=100, current_price=10.5),
        Mock(quantity=200, current_price=5.2)
    ]

    service.account_repo.get_by_id = AsyncMock(return_value=mock_account)
    service.holding_repo.query_by_account = AsyncMock(return_value=mock_holdings)

    # Act
    result = await service.execute(
        request={"account_id": 1},
        user_id=1
    )

    # Assert
    assert result is not None
    assert "account" in result
    assert "stats" in result

    # 验证Repository被调用
    service.account_repo.get_by_id.assert_called_once_with(1)
    service.holding_repo.query_by_account.assert_called_once_with(1)

@pytest.mark.asyncio
async def test_execute_permission_denied():
    """测试权限验证"""
    mock_db = AsyncMock()
    service = AccountDetailService(mock_db)

    # Mock返回其他用户的账户
    mock_account = Mock(id=1, user_id=999, name="其他用户账户")
    service.account_repo.get_by_id = AsyncMock(return_value=mock_account)

    # 应该抛出权限异常
    with pytest.raises(PermissionError):
        await service.execute(
            request={"account_id": 1},
            user_id=1  # 当前用户ID=1，账户属于用户999
        )
```

---

## 🧮 Converter层测试

### Converter测试模板

```python
# tests/unit/services/test_account_detail_converter.py
import pytest
from unittest.mock import Mock
from app.services.account.detail_service import AccountDetailConverter

def test_calculate_total_value():
    """测试总市值计算"""
    # Arrange
    holdings = [
        Mock(quantity=100, current_price=10.5),
        Mock(quantity=200, current_price=5.2),
        Mock(quantity=50, current_price=20.0)
    ]

    # Act
    result = AccountDetailConverter._calculate_total_value(holdings)

    # Assert
    expected = 100*10.5 + 200*5.2 + 50*20.0
    assert result == expected

def test_calculate_profit_loss():
    """测试盈亏计算"""
    holdings = [
        Mock(quantity=100, current_price=10.5, cost_price=10.0),
        Mock(quantity=200, current_price=5.2, cost_price=5.5)
    ]

    result = AccountDetailConverter._calculate_profit_loss(holdings)

    # 盈亏 = (10.5-10.0)*100 + (5.2-5.5)*200 = 50 - 60 = -10
    assert result == -10.0

def test_convert_complete_flow():
    """测试完整转换流程"""
    # Arrange
    mock_account = Mock(id=1, name="测试账户", account_type=Mock(value="a_share"))
    mock_holdings = [
        Mock(
            stock_code="600000",
            quantity=100,
            current_price=10.5,
            cost_price=10.0
        )
    ]

    # Act
    result = AccountDetailConverter.convert(mock_account, mock_holdings)

    # Assert
    assert "account" in result
    assert "stats" in result
    assert "holdings" in result
    assert result["account"]["id"] == 1
    assert result["stats"]["total_value"] == 1050.0
```

---

## 🏗️ Builder层测试

### Builder测试模板

```python
# tests/unit/services/test_account_detail_builder.py
from unittest.mock import Mock
from app.services.account.detail_service import AccountDetailBuilder

def test_build_response():
    """测试响应构建"""
    # Arrange
    mock_account = Mock(
        id=1,
        name="测试账户",
        account_type=Mock(value="a_share")
    )
    holdings = [
        Mock(
            stock_code="600000",
            quantity=100,
            cost_price=10.0,
            current_price=10.5
        )
    ]
    total_value = 1050.0
    profit_loss = 50.0

    # Act
    result = AccountDetailBuilder.build_response(
        account=mock_account,
        holdings=holdings,
        total_value=total_value,
        profit_loss=profit_loss
    )

    # Assert
    assert result["account"]["id"] == 1
    assert result["account"]["name"] == "测试账户"
    assert result["stats"]["total_value"] == 1050.0
    assert result["stats"]["profit_loss"] == 50.0
    assert len(result["holdings"]) == 1

def test_build_list():
    """测试列表构建"""
    items = [
        Mock(id=1, name="项目1", value=100),
        Mock(id=2, name="项目2", value=200)
    ]

    result = SomeBuilder._build_list(items)

    assert len(result) == 2
    assert result[0]["id"] == 1
    assert result[1]["id"] == 2
```

---

## 🗄️ Repository层测试

### Repository测试策略

由于Repository涉及数据库操作，建议在**集成测试**中测试。如果必须单元测试，需要Mock数据库会话：

```python
# tests/unit/repositories/test_account_repository.py
import pytest
from unittest.mock import AsyncMock, Mock
from app.repositories.account_repo import AccountRepository

@pytest.mark.asyncio
async def test_get_by_id():
    """测试根据ID查询（需要Mock数据库）"""
    # Arrange
    mock_db = AsyncMock()
    mock_result = AsyncMock()
    mock_account = Mock(id=1, name="测试")

    mock_result.scalar_one_or_none.return_value = mock_account
    mock_db.execute.return_value = mock_result

    repo = AccountRepository(mock_db)

    # Act
    result = await repo.get_by_id(1)

    # Assert
    assert result == mock_account
    mock_db.execute.assert_called_once()
```

**建议**: Repository测试放在集成测试中更有意义，单元测试Repository价值有限。

---

## 🧰 Mock使用技巧

### 基础Mock

```python
from unittest.mock import Mock

# 创建Mock对象
mock_obj = Mock()

# 设置返回值
mock_obj.method.return_value = "result"

# 设置属性
mock_obj.attribute = "value"

# 验证调用
mock_obj.method()
mock_obj.method.assert_called_once()
```

### AsyncMock（异步）

```python
from unittest.mock import AsyncMock

# 创建异步Mock
mock_async = AsyncMock()

# 设置返回值
mock_async.return_value = "result"

# 调用
result = await mock_async()
```

### Patch装饰器

```python
from unittest.mock import patch

@patch('app.services.account.detail_service.AccountRepository')
def test_with_patch(mock_repo_class):
    """使用patch替换整个类"""
    # mock_repo_class 是类的Mock
    mock_repo = mock_repo_class.return_value

    # 配置Mock实例
    mock_repo.get_by_id.return_value = Mock(id=1)

    # 测试代码...
```

---

## ✅ 最佳实践

### 1. 测试命名清晰

```python
# ❌ 不好
def test_1():
    pass

# ✅ 好
def test_calculate_total_value_with_empty_list():
    pass
```

### 2. 一个测试一个断言主题

```python
# ❌ 不好: 测试多个不相关的东西
def test_everything():
    assert calculate(1, 2) == 3
    assert validate("test") == True
    assert format_date(date) == "2025-01-01"

# ✅ 好: 每个测试专注一个功能
def test_calculate_sum():
    assert calculate(1, 2) == 3

def test_validate_input():
    assert validate("test") == True
```

### 3. 使用参数化测试

```python
import pytest

@pytest.mark.parametrize("quantity,price,expected", [
    (100, 10.5, 1050.0),
    (200, 5.2, 1040.0),
    (50, 20.0, 1000.0),
])
def test_calculate_value_parametrized(quantity, price, expected):
    holdings = [Mock(quantity=quantity, current_price=price)]
    result = Converter._calculate_total_value(holdings)
    assert result == expected
```

### 4. 边界条件测试

```python
def test_empty_list():
    """测试空列表"""
    assert Converter._calculate_total_value([]) == 0

def test_negative_values():
    """测试负值"""
    holdings = [Mock(quantity=-100, current_price=10.0)]
    # 应该抛出异常或返回0，取决于业务逻辑
```

---

## 📊 覆盖率测试

### 运行覆盖率

```bash
# 运行测试并生成覆盖率报告
pytest --cov=app --cov-report=html tests/unit/

# 查看HTML报告
open htmlcov/index.html
```

### 覆盖率配置

```ini
# .coveragerc
[run]
source = app
omit =
    */tests/*
    */migrations/*
    */venv/*

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
    if __name__ == .__main__.:
```

---

## 🔗 相关资源

- [pytest文档](https://docs.pytest.org/)
- [unittest.mock文档](https://docs.python.org/3/library/unittest.mock.html)
- [pytest-cov文档](https://pytest-cov.readthedocs.io/)

---

**最后更新**: 2025-11-19
