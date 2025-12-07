# 数据库迁移分析

分析数据库 Schema 变更的影响，生成迁移计划。

---

请分析数据库变更 "$ARGUMENTS"：

## 输入说明
- 描述变更: `events 表添加 impact_score 字段`
- 指定表: `accounts 表`
- 迁移文件: `migrations/001_add_events.sql`

## 分析内容

### 1. 变更影响分析
- 受影响的表
- 相关索引变更
- 约束变更
- 数据迁移需求

### 2. 代码影响分析
根据项目架构分析：
- Model 层变更
- Repository 层变更
- Service 层变更
- API 层变更

### 3. 兼容性分析
- 是否向后兼容
- 是否需要停机
- 回滚方案

### 4. 数据迁移
- 现有数据处理
- 默认值设置
- 数据转换逻辑

## 输出格式

```
## 数据库迁移分析报告

### 📋 变更概述
- **变更类型**: [新增表/新增字段/修改字段/删除字段/新增索引/...]
- **影响表**: {表名}
- **风险等级**: [高/中/低]
- **预计停机**: [是/否]

---

### 📊 Schema 变更

#### 变更前
```sql
-- 当前表结构
CREATE TABLE {table_name} (
    ...
);
```

#### 变更后
```sql
-- 新表结构
CREATE TABLE {table_name} (
    ...
    new_column TYPE DEFAULT value,  -- 新增
    ...
);
```

#### 迁移 SQL
```sql
-- 升级脚本 (UP)
ALTER TABLE {table_name}
ADD COLUMN new_column TYPE NOT NULL DEFAULT value;

CREATE INDEX idx_{table}_{column} ON {table_name}(new_column);

-- 数据迁移（如需要）
UPDATE {table_name}
SET new_column = calculated_value
WHERE condition;

-- 回滚脚本 (DOWN)
ALTER TABLE {table_name}
DROP COLUMN new_column;
```

---

### 🔗 代码影响

#### Model 层
```python
# backend/app/models/{table}.py

class {Table}(Base):
    # 新增字段
    new_column = Column(Type, nullable=False, default=value)
```

#### Repository 层
```python
# backend/app/repositories/{table}_repo.py

# 如果需要新增查询方法
async def query_by_new_column(self, value: Type) -> List[{Table}]:
    pass
```

#### Service 层
| 文件 | 修改内容 |
|------|----------|
| `{action}_service.py` | Converter 添加新字段处理 |
| `{action}_service.py` | Builder 更新响应结构 |

#### API 层
| 端点 | 修改内容 |
|------|----------|
| `POST /api/v1/{module}/{action}` | 响应新增 new_field |

---

### 📝 需要修改的文件清单

#### 必须修改
| 文件 | 修改类型 | 说明 |
|------|----------|------|
| `backend/app/models/{table}.py` | 新增字段 | 添加 new_column |
| `backend/app/services/{module}/{action}_service.py` | 更新逻辑 | Converter 处理新字段 |
| `tests/unit/.../test_{action}_service.py` | 更新测试 | 覆盖新字段 |

#### 可能需要修改
| 文件 | 修改类型 | 说明 |
|------|----------|------|
| `docs/design/database/schema-v1.md` | 更新文档 | 记录 schema 变更 |

---

### 🔄 迁移步骤

#### 开发环境
```bash
# 1. 更新 Model
# 2. 生成迁移文件
alembic revision --autogenerate -m "add new_column to {table}"

# 3. 检查生成的迁移
cat alembic/versions/xxx_add_new_column.py

# 4. 执行迁移
alembic upgrade head

# 5. 验证
psql -c "\\d {table_name}"
```

#### 生产环境
```bash
# 1. 备份数据库
pg_dump -h host -U user -d dbname > backup_$(date +%Y%m%d).sql

# 2. 执行迁移（在维护窗口）
alembic upgrade head

# 3. 验证数据
psql -c "SELECT COUNT(*) FROM {table_name} WHERE new_column IS NOT NULL"

# 4. 如需回滚
alembic downgrade -1
```

---

### ⚠️ 风险与注意事项

#### 风险点
| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| 大表加字段 | 锁表 | 使用 `CONCURRENTLY` 或分批更新 |
| 数据迁移失败 | 数据不一致 | 先备份，分批执行 |
| NOT NULL 约束 | 现有数据报错 | 先设默认值或允许 NULL |

#### 注意事项
1. {注意事项1}
2. {注意事项2}
3. 确保所有环境（dev/staging/prod）同步执行

---

### ✅ 迁移检查清单

#### 迁移前
- [ ] 备份数据库
- [ ] 测试环境验证通过
- [ ] 回滚脚本准备好
- [ ] 通知相关人员

#### 迁移中
- [ ] 执行迁移脚本
- [ ] 监控数据库性能
- [ ] 检查错误日志

#### 迁移后
- [ ] 验证表结构
- [ ] 验证数据完整性
- [ ] 更新文档
- [ ] 部署新代码
- [ ] 监控应用日志

---

### 📅 时间估算
| 阶段 | 工时 |
|------|------|
| Schema 设计 | X h |
| Model 修改 | X h |
| Service 修改 | X h |
| 测试编写 | X h |
| 文档更新 | X h |
| 迁移执行 | X h |
| **总计** | **X h** |
```

## 使用示例
- `/db-migration events表添加impact_score字段` - 分析字段添加
- `/db-migration 新建event_alerts表` - 分析新表创建
- `/db-migration accounts表重构` - 分析表重构影响
