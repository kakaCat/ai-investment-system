# 422错误修复指南

## 快速修复步骤

### 1. 执行数据库迁移

```bash
cd backend
alembic upgrade head
```

这将执行迁移 `d064a2ea4323`，将 `broker` 和 `account_number` 字段改为可空。

### 2. 验证修复

```bash
python scripts/test_account_create.py
```

预期结果：测试7-10应该全部返回200状态码。

### 3. 检查数据库

```bash
psql -d ai_investment
\d accounts
```

应该看到：
```
Column         | Type          | Nullable
---------------+---------------+----------
broker         | varchar(100)  | YES
account_number | varchar(50)   | YES
```

## 问题原因

**数据库模型不一致**: 数据库要求 `broker` 和 `account_number` 必填，但API定义为可选。

## 修改内容

### 文件变更列表

1. **backend/app/models/account.py** (第17-19行)
   - `account_number`: `nullable=False` → `nullable=True`
   - `broker`: `nullable=False` → `nullable=True`

2. **backend/app/services/account/account_create_service.py** (第144-145行)
   - 显式处理NULL值

3. **backend/alembic/versions/d064a2ea4323_*.py** (新增)
   - 数据库迁移脚本

4. **docs/troubleshooting/422-error-account-create.md** (新增)
   - 完整问题分析和解决方案文档

5. **scripts/test_account_create.py** (新增)
   - 综合测试脚本

## 测试场景

### ✅ 应该通过
```bash
# 最小参数
curl -X POST http://localhost:8000/api/v1/account/create \
  -H "Authorization: Bearer dev-token" \
  -H "Content-Type: application/json" \
  -d '{"account_name": "测试", "market": "A-share"}'
```

### ❌ 应该拒绝
```bash
# 缺少market
curl -X POST http://localhost:8000/api/v1/account/create \
  -H "Authorization: Bearer dev-token" \
  -H "Content-Type: application/json" \
  -d '{"account_name": "测试"}'
# 预期: 422错误
```

## 回滚方案

如果需要回滚：

```bash
cd backend
alembic downgrade -1
```

注意：回滚会将所有NULL值填充为默认值（"未知"和"-"）。

## 相关文档

- [完整诊断文档](../docs/troubleshooting/422-error-account-create.md)
- [API文档](http://localhost:8000/docs)
- [数据库设计](../docs/design/database/schema-v1.md)
