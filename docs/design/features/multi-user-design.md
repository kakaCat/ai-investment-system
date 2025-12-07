# 多用户、多账户（多租户）设计与解决方案

> 状态说明：本页为详细设计参考，核心信息已汇总至《docs/prd-v1.md》。若存在不一致，以 PRD v1 为准；本页保留数据模型与账户上下文细节用于协作与回溯。

目标：支持“一个用户拥有多个账户”，每个账户的关注与持仓互相隔离，同时保证股票为中心的聚合视图与批量操作在账户维度上正确执行。

## 核心原则
- 严格分层：Controller（薄）→ Service（编排与防腐）→ DataService（聚合访问）→ Repository（存储）→ Adapter（外部）。
- 账户隔离：所有读写必须显式携带 `userId + accountId`（或在上下文中传递），避免跨账户泄露与污染。
- 静态工具：`Converter/Rule/Wrapper` 全部静态方法；`Wrapper` 统一权限与敏感信息过滤。
- 类型安全：TypeScript `strict: true`，复杂对象用 `interface`，禁止 `any`，必要使用 `unknown` 并在边界收敛。

## 数据模型扩展
- `users`（用户基础信息）
- `accounts`：`id`、`user_id`、`name`、`type`（`cash|margin|broker_x`）、`status`（`active|inactive`）、`created_at`、`updated_at`
- `watchlist`：增加 `account_id` 字段；唯一约束 `user_id + account_id + symbol`
- `holdings`：增加 `account_id` 字段；唯一约束 `user_id + account_id + symbol`
- `strategy_analysis`：增加 `user_id + account_id`，方便按账户查询与汇总
- `investment_plans`：增加 `user_id + account_id` 或 `scope='portfolio'` 的账户集合
- `agent_tasks`：携带 `user_id + account_id + scope` 以便调度与审计

### TypeScript 接口示例
```ts
export interface AccountScope { userId: string; accountId: string }
export interface WatchlistItem { userId: string; accountId: string; symbol: string; tier: WatchTier; note?: string }
export interface HoldingItem { userId: string; accountId: string; symbol: string; quantity: number; avgCost: number; source?: 'manual'|'ocr' }
export interface PortfolioOverviewQuery { scope: AccountScope; filters?: { status?: PositionStatus; tier?: WatchTier } }
```

## 账户上下文传递
- Controller：所有入口方法都接收 `userId` 与 `accountId`（路径、查询或 Header 中），方法不超过 5 行；不做业务判断。
- Service：方法签名显式要求 `AccountScope`，并在编排时传递到 DataService 与 Rule/Wrapper。
- DataService：所有查询与写入都要求 `AccountScope`；禁止跨账户合并除非显式请求（例如组合级概览）。
- Wrapper：`PermissionWrapper.ensureUserAccountAccess(user, accountId)` 静态校验，快速失败。

## 规则与权限
- `InputRule.validateAccountScope(scope: unknown)`：类型与非空校验。
- `DuplicateRule.ensureUniqueWatch/Hold(scope, symbol)`：避免重复记录。
- `RiskRule`：对账户类型执行差异化规则（例如 `margin` 的仓位上限不同）。
- 统一业务异常：`throw new BusinessException('账户权限不足')`、`BusinessException('重复关注/持仓')`。

## API 设计（账户维度）
- `GET /users/:userId/accounts/:accountId/portfolio/overview`
- `POST /users/:userId/accounts/:accountId/watchlist`
- `POST /users/:userId/accounts/:accountId/holdings`
- `POST /users/:userId/accounts/:accountId/holdings/ocr-import`
- `POST /users/:userId/accounts/:accountId/strategy/analyze`
- `POST /users/:userId/accounts/:accountId/investment/plan`
- `GET /users/:userId/accounts/:accountId/stocks/:symbol/overview`

> 备注：如不希望路径过长，可将 `userId/accountId` 放在 Header（例如 `X-User-Id`、`X-Account-Id`），但 Controller 层仍需统一收敛为 `AccountScope`。

## 聚合视图
- 账户级概览：显示该账户的关注与持仓的卡片网格（策略/总结/建议 mini）。
- 组合级概览（可选）：跨账户聚合，但需明确 `scope` 为账户集合；Converter 在响应中标注 `accountId`，前端可按账户分组显示。

## 调度与队列
- 调度任务按 `userId + accountId` 分片执行，避免跨账户互相影响。
- 并发与幂等：批量任务的幂等键包含 `accountId`；队列优先级可按账户类型与活跃度配置。

## 缓存与索引
- Redis Key 设计：`price:{symbol}`（公共）与 `portfolio:{userId}:{accountId}`（账户级）。
- DB 索引：`(user_id, account_id, symbol)` 在 `watchlist/holdings/strategy_analysis`；时间序列索引优化策略查询。

## OCR 场景（账户维度）
- `OcrAdapter.parseHoldings` 解析的结果必须归属当前 `accountId`；
- `PortfolioDataService.upsertHoldings(scope, parsed)` 写入时携带 `userId + accountId`；
- 盈亏计算仍动态，使用公共行情；但策略生成与记录归属账户维度。

## 前端适配
- 顶部账号切换器（Account Switcher）：选择后触发 `GET /users/:userId/accounts/:accountId/portfolio/overview`。
- 所有操作（关注/购买/分析/建议）均在当前账户上下文中执行；UI 明确标注账户。
- 支持“跨账户视图”：仅作为只读聚合（如总览页），操作仍需明确当前 `accountId`。

## 示例编排（Mermaid）
```mermaid
flowchart TD
  U[选择账号(accountId)] --> C[PortfolioController.overview]
  C --> S[PortfolioService.collectPortfolioOverview(scope)]
  S --> R[InputRule.validateAccountScope]
  S --> Dlist[PortfolioDataService.getHoldingsAndWatchlist(scope)]
  Dlist --> Dprc[MarketDataService.getPrices]
  Dlist --> Dstr[StrategyDataService.getLatestBatch(scope)]
  Dlist --> Dsum[SummaryDataService.getByPeriodBatch(scope)]
  S --> Dinv[InvestmentService.collectPlanData(scope)]
  S --> Conv[PortfolioConverter.toOverviewResponse]
  Conv --> Resp[WebResponse.success]
  Resp --> U
```

## 迁移与落地建议
- 第一步：为现有表增加 `account_id` 并构建联合唯一约束与索引；迁移历史数据归属默认账户。
- 第二步：统一 Controller 收敛 `AccountScope`；Service 与 DataService 方法签名添加 `scope` 参数。
- 第三步：改造前端加入账号切换器；所有请求携带 `userId + accountId`。
- 第四步：调度与批量任务的幂等键加入 `accountId`；观察与优化。