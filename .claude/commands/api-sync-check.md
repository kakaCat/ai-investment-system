# 前后端 API 一致性检查

检查前后端 API 定义是否同步，包括类型、参数、响应结构。

---

请检查 $ARGUMENTS 的前后端 API 一致性：

## 检查范围
- 如果参数为空，检查所有 API
- 如果指定模块，只检查该模块的 API
- 如果指定端点，只检查该端点

## 检查维度

### 1. 端点一致性
- 后端定义的 API 前端是否都有调用
- 前端调用的 API 后端是否都有定义
- URL 路径是否完全匹配

### 2. 请求参数一致性
- 参数名称是否一致
- 参数类型是否匹配
- 必填/选填是否一致
- 默认值是否一致

### 3. 响应结构一致性
- 字段名称是否一致
- 字段类型是否匹配
- 嵌套结构是否一致
- 前端是否处理了所有字段

### 4. 类型定义检查
- TypeScript 类型是否与后端 Pydantic 模型匹配
- 枚举值是否同步
- 可空字段是否一致

### 5. 错误处理一致性
- 错误码是否同步
- 前端是否处理了所有错误情况

## 输出格式

```
## API 一致性检查报告

### 📊 检查统计
- 检查 API 数量: X
- 一致: X
- 不一致: X
- 一致率: X%

---

### ❌ 不一致项

#### 1. 端点不存在

| 类型 | 端点 | 说明 |
|------|------|------|
| 后端有前端无 | `POST /api/v1/account/detail` | 前端未实现调用 |
| 前端有后端无 | `POST /api/v1/event/list` | 后端未实现 |

---

#### 2. 参数不一致

##### `POST /api/v1/account/detail`

**后端定义** (`backend/app/api/v1/account_api.py:42`):
```python
{
    "account_id": int,      # 必填
    "include_holdings": bool  # 可选，默认 True
}
```

**前端调用** (`frontend/src/services/account.ts:25`):
```typescript
{
    accountId: number,      // ❌ 命名不一致：应为 account_id
    includeHoldings?: boolean
}
```

**问题**:
- ❌ `accountId` → 应为 `account_id`（snake_case）

**修复建议**:
```typescript
// frontend/src/services/account.ts
interface AccountDetailRequest {
    account_id: number;
    include_holdings?: boolean;
}
```

---

#### 3. 响应不一致

##### `POST /api/v1/portfolio/summary`

**后端响应** (`backend/app/services/portfolio/summary_service.py`):
```python
{
    "total_value": float,
    "daily_change": float,
    "daily_change_percent": float,  # 后端有
    "holdings": [...]
}
```

**前端类型** (`frontend/src/types/portfolio.ts`):
```typescript
{
    total_value: number;
    daily_change: number;
    // ❌ 缺少 daily_change_percent
    holdings: Holding[];
}
```

**问题**:
- ❌ 前端缺少 `daily_change_percent` 字段

**修复建议**:
```typescript
interface PortfolioSummary {
    total_value: number;
    daily_change: number;
    daily_change_percent: number;  // 添加
    holdings: Holding[];
}
```

---

#### 4. 类型不匹配

| 端点 | 字段 | 后端类型 | 前端类型 | 建议 |
|------|------|----------|----------|------|
| `/account/list` | `balance` | `Decimal` | `number` | 前端用 string 处理精度 |
| `/event/detail` | `impact_score` | `int (1-5)` | `string` | 前端改为 number |

---

#### 5. 枚举不同步

##### EventType 枚举

**后端** (`backend/app/models/enums.py`):
```python
class EventType(str, Enum):
    POLICY = "policy"
    COMPANY = "company"
    MARKET = "market"
    INDUSTRY = "industry"
```

**前端** (`frontend/src/types/enums.ts`):
```typescript
enum EventType {
    POLICY = "policy",
    COMPANY = "company",
    MARKET = "market",
    // ❌ 缺少 INDUSTRY
}
```

---

### ✅ 一致的 API

| 端点 | 状态 |
|------|------|
| `POST /api/v1/auth/login` | ✅ 完全一致 |
| `POST /api/v1/auth/logout` | ✅ 完全一致 |
| `POST /api/v1/user/profile` | ✅ 完全一致 |

---

### 📋 修复清单

#### 高优先级（类型安全）
1. [ ] 修复参数命名：`accountId` → `account_id`
2. [ ] 添加缺失字段：`daily_change_percent`
3. [ ] 同步枚举：添加 `INDUSTRY`

#### 中优先级（功能完整）
4. [ ] 实现缺失 API 调用
5. [ ] 添加错误码处理

#### 低优先级（优化）
6. [ ] 统一 Decimal 处理方式
7. [ ] 添加 API 版本检查

---

### 🔧 自动同步建议

考虑使用以下工具自动保持同步：

1. **OpenAPI/Swagger**: 从后端生成 API 文档
2. **openapi-typescript**: 从 OpenAPI 生成 TypeScript 类型
3. **Pydantic to TypeScript**: 直接转换模型

```bash
# 示例：从 OpenAPI 生成 TypeScript
npx openapi-typescript http://localhost:8000/openapi.json -o frontend/src/types/api.ts
```
```

## 使用示例
- `/api-sync-check` - 检查所有 API
- `/api-sync-check account` - 检查账户模块
- `/api-sync-check /api/v1/event/list` - 检查特定端点
