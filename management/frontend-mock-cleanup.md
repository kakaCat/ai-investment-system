 # 前端 Mock 数据清理报告

> 生成时间: 2025-11-20
> 负责人: 前端开发团队
> 状态: 进行中

---

## 📊 总览

| 类别 | 已清理 | 待清理 | 无需清理 |
|------|--------|--------|----------|
| 页面 | 2 | 6 | 4 |
| 组件 | 1 | 0 | 27 |
| **总计** | **3** | **6** | **31** |

---

## ✅ 已清理 Mock 数据（调用真实 API）

### 1. TradesList.vue ✅
- **清理内容**:
  - ❌ 移除 5 条 mock 交易记录
  - ❌ 移除 4 个 mock 账户
  - ✅ 调用 `/api/v1/trade/query` 获取交易列表
  - ✅ 调用 `/api/v1/trade/create` 创建交易
  - ✅ 调用 `/api/v1/account/query` 获取账户列表
- **状态**: 完成 ✅
- **验证**: 功能正常，列表为空（数据库已清空）

### 2. StockSearchDialog.vue ✅
- **清理内容**:
  - ❌ 移除 12 条 mock 股票数据
  - ✅ 调用 `/api/v1/stock/search` 搜索股票
- **状态**: 完成 ✅
- **验证**: 搜索功能正常

### 3. HoldingsList.vue ⚠️ 部分完成
- **已清理**:
  - ❌ 移除 mock 持仓数据
  - ✅ 调用 `/api/v1/holding/query` 获取持仓
  - ✅ 调用 `/api/v1/account/query` 获取账户列表
- **保留 Mock（后端接口未实现）**:
  - 🔴 AI 组合建议（aiSuggestion）
  - 🔴 事件影响矩阵（eventMatrix）
- **状态**: 部分完成 ⚠️

---

## 🔴 待清理 Mock 数据

### 1. AccountList.vue 🔴 高优先级

**Mock 数据**:
- 3 个账户（华泰、富途、盈透）
- 包含市值、现金、盈亏等数据

**后端接口**: ✅ 已存在
- `POST /api/v1/account/query` - 查询账户列表
- `POST /api/v1/account/create` - 创建账户
- `POST /api/v1/account/update` - 更新账户
- `POST /api/v1/account/delete` - 删除账户

**需要修改**:
```typescript
// 当前 (第48行):
const fetchAccounts = async () => {
  // Mock 数据
  accounts.value = [...]
}

// 修改为:
import { queryAccounts, createAccount } from '@/api/account'

const fetchAccounts = async () => {
  const response = await queryAccounts({})
  accounts.value = response.data.items || []
}
```

**优先级**: P0 - 核心功能
**估算**: 30分钟

---

### 2. StockDetail.vue 🔴 高优先级

**Mock 数据**:
- 股票基本信息（symbol, name, price等）
- 持仓信息（quantity, avg_cost等）
- 事件列表（6条事件）
- 操作策略（5条策略）

**后端接口**: ✅ 部分存在，⚠️ 部分缺失

| 功能 | 接口 | 状态 |
|------|------|------|
| 股票信息 | `POST /api/v1/stock/query` | ✅ 存在 |
| 持仓信息 | `POST /api/v1/holding/query` | ✅ 存在 |
| 事件列表 | `POST /api/v1/event/query` | ✅ 存在 |
| 操作策略 | ❌ 缺失 | 🔴 需要实现 |

**需要实现的后端接口**:
```python
# backend/app/api/v1/strategy_api.py (新建)
@router.post("/query")
async def query_strategies(
    request: StrategyQueryRequest,
    current_user: User = Depends(get_current_user)
):
    """
    查询用户的操作策略列表
    - 按股票筛选
    - 按状态筛选（pending/completed/cancelled）
    - 按类型筛选（buy/sell/hold）
    """
```

**优先级**: P0 - 核心功能
**估算**: 前端30分钟，后端2小时

---

### 3. AccountDetail.vue 🟡 中优先级

**Mock 数据**:
- 资金流水记录（cashFlows）
- 交易记录（tradeRecords）

**后端接口**: ✅ 已存在
- `POST /api/v1/account/detail` - 账户详情（包含资金流水）
- `POST /api/v1/trade/query` - 交易记录

**需要修改**:
```typescript
// 调用账户详情API获取完整信息
import { getAccountDetail } from '@/api/account'
import { queryTrades } from '@/api/trade'

const fetchAccountDetail = async () => {
  const response = await getAccountDetail({ account_id: accountId })
  // 更新页面数据
}
```

**优先级**: P1 - 重要功能
**估算**: 45分钟

---

### 4. EventDetail.vue 🟡 中优先级

**Mock 数据**:
- 事件详情（title, description, content等）
- 事件时间线（timeline）
- AI影响分析（ai_impact）
- 关联股票（related_stocks）
- 关联事件（related_events）

**后端接口**: ⚠️ 部分存在

| 功能 | 接口 | 状态 |
|------|------|------|
| 事件详情 | `POST /api/v1/event/detail` | ✅ 存在 |
| AI影响分析 | 包含在 event/detail | ✅ 存在 |
| 关联股票 | ❌ 缺失 | 🟡 可选 |
| 关联事件 | ❌ 缺失 | 🟡 可选 |

**需要修改**:
```typescript
import { getEventDetail } from '@/api/event' // 需要创建

const fetchEventDetail = async () => {
  const response = await getEventDetail({ event_id: eventId })
  eventDetail.value = response.data
}
```

**优先级**: P1 - 重要功能
**估算**: 1小时（前端45分钟 + 创建API service 15分钟）

---

### 5. DailyReview.vue 🟢 低优先级

**Mock 数据**:
- 重要事件列表（importantEvents）
- 个人观点（myViews）

**后端接口**: ✅ 已存在
- `POST /api/v1/ai/review/stocks` - 获取可分析股票
- `POST /api/v1/ai/review/generate` - 生成每日复盘
- `POST /api/v1/ai/review/get` - 获取复盘结果
- `POST /api/v1/event/query` - 查询事件

**需要修改**:
```typescript
import { generateDailyReview, getDailyReview } from '@/api/ai'
import { queryEvents } from '@/api/event' // 需要创建

// 加载重要事件
const loadImportantEvents = async () => {
  const response = await queryEvents({
    importance: 'high',
    start_date: getLastWeek()
  })
  importantEvents.value = response.data.items
}
```

**优先级**: P2 - 次要功能
**估算**: 1小时

---

### 6. SettingsPage.vue 🟢 低优先级

**Mock 数据**:
- 账户列表（用于下拉选择）

**后端接口**: ✅ 已存在
- `POST /api/v1/account/query` - 查询账户列表

**需要修改**:
```typescript
import { queryAccounts } from '@/api/account'

const loadAccounts = async () => {
  const response = await queryAccounts({})
  accounts.value = response.data.items || []
}
```

**优先级**: P2 - 次要功能
**估算**: 15分钟

---

## 🟢 无需清理（UI 配置或静态数据）

以下页面/组件不需要清理，原因：

1. **Login.vue** - 登录页，无业务数据
2. **Dashboard.vue** - 调用多个 API 聚合数据（需要验证）
3. **EventsList.vue** - 需要验证是否调用真实 API
4. **AnalysisHub.vue** - AI 分析入口，无 mock 数据
5. **所有 Dialog 组件** (28个) - 表单组件，无 mock 数据

---

## 🔴 缺失的后端接口（需要实现）

### 1. 操作策略管理 API

**文件**: `backend/app/api/v1/strategy_api.py` (新建)

**接口列表**:
```python
POST /api/v1/strategy/query        # 查询策略列表
POST /api/v1/strategy/create       # 创建策略
POST /api/v1/strategy/update       # 更新策略
POST /api/v1/strategy/delete       # 删除策略
POST /api/v1/strategy/execute      # 标记策略为已执行
```

**数据库表**: `strategies` (需要新建)
```sql
CREATE TABLE strategies (
    strategy_id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    stock_name VARCHAR(100),
    strategy_type VARCHAR(20) NOT NULL,  -- buy/sell/hold
    trigger_price NUMERIC(20,8),
    quantity NUMERIC(20,8),
    reason TEXT,
    status VARCHAR(20) DEFAULT 'pending', -- pending/completed/cancelled
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    executed_at TIMESTAMPTZ
);
```

**优先级**: P1
**估算**: 4小时（数据库设计1h + Service层2h + API层1h）

---

### 2. AI 组合分析 API

**文件**: `backend/app/services/ai/portfolio_analysis_service.py` (新建)

**接口**:
```python
POST /api/v1/ai/portfolio-analysis  # 分析整个投资组合

# 响应数据:
{
  "score": 7.2,                    # 组合评分 (0-10)
  "risk_level": "medium",          # 风险等级
  "risk_description": "...",
  "suggestions": [                 # AI建议列表
    {
      "type": "reduce",            # reduce/wait/hold/add
      "title": "...",
      "description": "..."
    }
  ],
  "urgency": "moderate",           # urgent/moderate/low
  "urgency_description": "..."
}
```

**优先级**: P1 - HoldingsList.vue 需要
**估算**: 6小时（AI提示词设计2h + Service层3h + API层1h）

---

### 3. 事件影响矩阵 API

**文件**: `backend/app/services/event/impact_matrix_service.py` (新建)

**接口**:
```python
POST /api/v1/event/impact-matrix   # 批量分析事件对持仓的影响

# 请求参数:
{
  "account_id": 1,
  "days": 30                       # 分析最近N天的事件
}

# 响应数据:
{
  "holdings": [                    # 持仓股票列表
    { "symbol": "600519", "name": "贵州茅台" }
  ],
  "events": [                      # 事件列表
    {
      "event_id": 1,
      "title": "...",
      "impacts": [                 # 对每只股票的影响
        {
          "symbol": "600519",
          "impact_level": "bearish",  # bullish/light-bullish/neutral/light-bearish/bearish
          "change_percent": -2.5,
          "description": "..."
        }
      ]
    }
  ]
}
```

**优先级**: P1 - HoldingsList.vue 需要
**估算**: 8小时（算法设计3h + Service层4h + API层1h）

---

## 📋 任务分配建议

### Sprint 1: 核心功能（估算: 2天）

**前端任务** (FE-001 ~ FE-003):
- [ ] FE-001: 清理 AccountList.vue mock 数据 (30min)
- [ ] FE-002: 清理 StockDetail.vue mock 数据（股票、持仓、事件部分）(30min)
- [ ] FE-003: 清理 AccountDetail.vue mock 数据 (45min)

**后端任务** (BE-001):
- [ ] BE-001: 实现操作策略管理 API (4h)
  - 数据库表设计
  - Repository 层
  - Service 层（CRUD）
  - API 路由

**验证任务** (QA-001):
- [ ] QA-001: 测试账户、持仓、交易功能的真实 API 调用

---

### Sprint 2: AI 增强功能（估算: 3天）

**后端任务** (BE-002 ~ BE-003):
- [ ] BE-002: 实现 AI 组合分析 API (6h)
  - AI 提示词设计
  - 组合评分算法
  - Service 层实现
  - API 集成

- [ ] BE-003: 实现事件影响矩阵 API (8h)
  - 事件-股票关联算法
  - 影响等级计算
  - 矩阵数据结构设计
  - Service + API 实现

**前端任务** (FE-004):
- [ ] FE-004: 集成 AI 组合建议和事件矩阵到 HoldingsList.vue (1h)

**验证任务** (QA-002):
- [ ] QA-002: 测试 AI 组合分析和事件影响矩阵功能

---

### Sprint 3: 次要功能（估算: 1天）

**前端任务** (FE-005 ~ FE-007):
- [ ] FE-005: 清理 EventDetail.vue mock 数据 (1h)
- [ ] FE-006: 清理 DailyReview.vue mock 数据 (1h)
- [ ] FE-007: 清理 SettingsPage.vue mock 数据 (15min)

**验证任务** (QA-003):
- [ ] QA-003: 完整回归测试所有页面

---

## 📈 进度跟踪

| Sprint | 任务数 | 已完成 | 进行中 | 待开始 | 完成率 |
|--------|--------|--------|--------|--------|--------|
| Sprint 1 | 5 | 0 | 0 | 5 | 0% |
| Sprint 2 | 4 | 0 | 0 | 4 | 0% |
| Sprint 3 | 4 | 0 | 0 | 4 | 0% |
| **总计** | **13** | **0** | **0** | **13** | **0%** |

---

## 🔗 相关文档

- [PRD v3.1](../docs/prd/v3/main.md)
- [后端架构设计](../docs/design/architecture/backend-architecture.md)
- [数据库Schema](../docs/design/database/schema-v1.md)
- [Sprint 任务列表](./sprints/current.md)

---

**最后更新**: 2025-11-20
**下次评审**: Sprint 计划会议
