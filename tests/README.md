# 测试

> 自动化测试、质量保障和测试报告

---

## 📂 目录结构

```
tests/
├── README.md              # 本文件 - 测试总览
├── e2e/                   # E2E端到端测试
│   └── specs/             # 测试规格
├── integration/           # 集成测试
│   └── api/               # API集成测试
├── unit/                  # 单元测试
│   ├── backend/           # 后端单元测试
│   │   ├── services/      # Service层测试
│   │   ├── repositories/  # Repository层测试
│   │   └── models/        # Model层测试
│   └── frontend/          # 前端单元测试
│       ├── components/    # 组件测试
│       └── stores/        # 状态管理测试
├── performance/           # 性能测试
└── conftest.py            # Pytest配置
```

---

## 🧪 测试类型

### 1. 单元测试 (Unit Tests)
- **位置**: `tests/unit/`
- **工具**: pytest (后端), vitest (前端)
- **覆盖率目标**: > 80%
- **运行频率**: 每次提交

### 2. 集成测试 (Integration Tests)
- **位置**: `tests/integration/`
- **工具**: pytest + httpx
- **重点**: API端点、数据库交互
- **运行频率**: 每次PR

### 3. E2E测试 (End-to-End Tests)
- **位置**: `tests/e2e/`
- **工具**: Playwright
- **重点**: 用户核心流程
- **运行频率**: 每次发布前

### 4. 性能测试 (Performance Tests)
- **位置**: `tests/performance/`
- **工具**: locust
- **重点**: API响应时间、并发处理
- **运行频率**: 定期（周/月）

---

## 🚀 快速开始

### 运行单元测试

```bash
# 后端单元测试
pytest tests/unit/backend/ -v

# 前端单元测试
cd frontend && npm run test:unit
```

### 运行集成测试

```bash
# API集成测试
pytest tests/integration/ -v
```

### 运行E2E测试

```bash
# 启动应用
./scripts/dev.sh

# 运行E2E测试
cd frontend && npm run test:e2e
```

### 查看覆盖率

```bash
# 后端覆盖率
pytest tests/unit/backend/ --cov=backend/app --cov-report=html

# 前端覆盖率
cd frontend && npm run test:coverage
```

---

## 📋 测试规范

### 命名规范

| 类型 | 文件命名 | 函数命名 |
|------|----------|----------|
| 单元测试 | `test_{module}.py` | `test_{function}_should_{expected}` |
| 集成测试 | `test_{api}_api.py` | `test_api_{endpoint}_{scenario}` |
| E2E测试 | `{feature}.spec.ts` | `test('{user story}')` |

### 测试结构 (AAA模式)

```python
def test_account_detail_should_return_correct_data():
    # Arrange (准备)
    account_id = 1
    user_id = 1

    # Act (执行)
    result = AccountDetailService().execute({"account_id": account_id}, user_id)

    # Assert (断言)
    assert result["code"] == 0
    assert result["data"]["account"]["id"] == account_id
```

---

## 📊 测试覆盖率

| 模块 | 单元测试 | 集成测试 | E2E测试 | 状态 |
|------|----------|----------|---------|------|
| 账户管理 | - | - | - | ⏳ 待实现 |
| 持仓管理 | - | - | - | ⏳ 待实现 |
| 事件分析 | - | - | - | ⏳ 待实现 |

---

## 🔗 相关文档

- [测试策略](../docs/testing/strategy/)
- [测试报告](../docs/testing/reports/)
- [后端架构约束](../backend/ARCHITECTURE.md)
- [前端架构约束](../frontend/ARCHITECTURE.md)

---

**最后更新**: 2025-11-19
**负责人**: QA Team
