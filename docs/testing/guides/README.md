# 测试指南

> 详细的测试执行指南、最佳实践和编写规范

---

## 📋 文档索引

| 指南 | 说明 | 状态 |
|------|------|------|
| [ui-testing-guide.md](ui-testing-guide.md) | UI自动化测试（Playwright E2E） | ✅ 完成 |
| [integration-testing-guide.md](integration-testing-guide.md) | API和服务集成测试 | ✅ 完成 |
| [unit-testing-guide.md](unit-testing-guide.md) | Service/Converter/Repository单元测试 | ✅ 完成 |

---

## 🎯 指南概述

### UI自动化测试指南

**适用场景**: 端到端用户流程测试

**技术栈**: Playwright + Python

**核心内容**:
- 环境配置和安装
- 测试脚本编写规范
- 页面对象模式(POM)
- 断言和验证最佳实践
- 截图和调试技巧

[查看完整指南 →](ui-testing-guide.md)

---

### 集成测试指南

**适用场景**: API端点、数据库操作、第三方服务集成

**技术栈**: pytest + FastAPI TestClient

**核心内容**:
- 测试环境配置
- API测试编写规范
- 数据库测试和事务管理
- Mock外部服务
- 测试数据管理

[查看完整指南 →](integration-testing-guide.md)

---

### 单元测试指南

**适用场景**: Service、Converter、Builder、Repository单元测试

**技术栈**: pytest + unittest.mock

**核心内容**:
- Service层测试
- Converter静态方法测试
- Builder数据构建测试
- Repository数据访问测试
- Mock和Fixture使用

[查看完整指南 →](unit-testing-guide.md)

---

## ✅ 通用测试规范

### 文件命名规范

```
tests/
├── unit/
│   └── test_{module}_{class}.py      # 单元测试
├── integration/
│   └── test_{module}_api.py          # 集成测试
└── ui/
    └── {feature}_test.py              # UI测试
```

### 测试函数命名

```python
# 单元测试
def test_{function_name}_{scenario}():
    """测试 {功能} - {场景}"""
    pass

# 集成测试
async def test_{api_endpoint}_{scenario}():
    """测试 API {端点} - {场景}"""
    pass

# UI测试
async def test_{user_flow}_{scenario}():
    """测试用户流程 {流程} - {场景}"""
    pass
```

### AAA模式

所有测试遵循 **Arrange-Act-Assert** 模式：

```python
def test_example():
    # Arrange - 准备测试数据和环境
    user_id = 1
    account_data = {"name": "Test Account", "type": "a_share"}

    # Act - 执行被测试的操作
    result = create_account(user_id, account_data)

    # Assert - 验证结果
    assert result.id is not None
    assert result.name == "Test Account"
    assert result.user_id == user_id
```

---

## 🔧 开发工具

### 推荐IDE配置

**VS Code**:
```json
{
  "python.testing.pytestEnabled": true,
  "python.testing.unittestEnabled": false,
  "python.testing.pytestArgs": [
    "tests"
  ]
}
```

### 有用的命令

```bash
# 运行所有测试
pytest

# 运行特定目录
pytest tests/unit/
pytest tests/integration/

# 运行特定文件
pytest tests/unit/test_account_service.py

# 运行特定测试
pytest tests/unit/test_account_service.py::test_create_account

# 显示详细输出
pytest -v

# 显示print输出
pytest -s

# 生成覆盖率报告
pytest --cov=app --cov-report=html

# 并行执行（需要pytest-xdist）
pytest -n auto
```

---

## 📊 测试质量检查

运行测试前检查清单：

- [ ] 测试名称清晰描述测试场景
- [ ] 遵循AAA模式
- [ ] 断言具体且有意义
- [ ] 测试独立，不依赖执行顺序
- [ ] 清理测试数据
- [ ] 没有硬编码值（使用常量或Fixture）
- [ ] 有必要的文档注释

---

## 🔗 相关资源

### 内部文档
- [测试策略](../strategy/test-strategy.md)
- [后端架构约束](../../design/architecture/backend-architecture.md)
- [测试报告](../reports/)

### 外部资源
- [pytest文档](https://docs.pytest.org/)
- [Playwright Python文档](https://playwright.dev/python/)
- [FastAPI Testing文档](https://fastapi.tiangolo.com/tutorial/testing/)
- [unittest.mock文档](https://docs.python.org/3/library/unittest.mock.html)

---

**最后更新**: 2025-11-19
**维护者**: QA Team
