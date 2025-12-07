# 项目设计与解决方案 PRD v1（股票分析与单页股票中心，含多账户）

> 目的：汇总并规范本项目的目标、范围、架构、页面与流程、数据与接口设计，统一“股票为中心”的前后端协作模式，同时支持多用户多账户（多租户）隔离与聚合视图。本文面向产品、前后端工程与架构协作。

## 1. 概述
- 背景：在既有“股票分析多 Agent 框架”基础上，前端希望降低割裂，将关注/持仓/选股/购买/策略/建议/总结在同一页通过 Modal 编排完成；同时需要支持一个用户下多个账户的关注与持仓隔离。
- 总体目标：
  - 单页股票中心展示并操作“选股→关注（分级：AI分级 + 用户分级）→购买→策略分析→投资建议→阶段总结”。
  - 股票为中心的聚合视图与聚合接口，减少前端多次拉取与拼装。
  - 明确的多账户隔离模型与账户上下文传递，确保数据与操作的正确归属。
  - 严格分层（Controller/Service/DataService/Repository/Adapter + Converter/Rule/Wrapper），类型安全（TypeScript strict）。
- 不在本期：真实券商下单、复杂风控引擎、跨市场资产（期货/债券）。

## 2. 范围与目标
- Must-have（本期交付）：
  - 单页股票中心（关注+持仓合页）与 Modal 编排动作；“购买即关注”规则。
  - 股票为中心的聚合接口：`GET /portfolio/overview`、`GET /stocks/:symbol/overview`、`POST /strategy/analyze/batch`、`POST /investment/plan`。
  - 多账户支持：所有读写携带 `userId + accountId` 上下文（路径或 Header），账户级概览与操作。
  - OCR 导入持仓（账户维度），含动态盈亏计算与策略生成跳过判断。
- Should-have：
  - 组合级概览（跨账户只读聚合），批量分析与批量建议。
  - 图表懒加载、虚拟列表、缓存优化与节流。
- Won’t-have：
  - 实盘交易与券商集成（仅模拟/占位）。

## 3. 用户与场景
- 用户：个人投资者，可能拥有多个证券账户（现金/保证金/不同券商）。
- 核心场景：
  - 在单页股票中心浏览与操作关注与持仓，触发选股、关注等级调整、买入/卖出、重新分析与查看详细。
  - 通过账号切换器选择账户，所有操作在当前账户上下文中执行；跨账户只读汇总视图。
  - 上传持仓截图（OCR）并导入为当前账户的持仓记录，计算动态盈亏并按需生成策略分析。

## 4. 信息架构与页面（单页股票中心）
- 布局（摘要）：
  - 顶部：搜索（symbol/公司）、预算输入（可选）、过滤（关注等级/持仓状态）。
  - 左侧侧栏（组合视角）：关注分级计数与筛选、持仓总览（总市值/盈亏/仓位占比）、快捷操作（选股、批量分析、批量建议）。
  - 主区域卡片网格（每只股票一张卡）：公司/价格/评级/来源、策略摘要、周期总结 mini、建议 mini；操作按钮：关注/编辑等级、购买/卖出、重新分析、查看详情。
- Modal 编排与动作：
  - 选股：提交筛选条件 → 候选列表 → 勾选“加入关注（选等级）”和可选“立即购买”；串联 `POST /strategy/select` → `POST /watchlist`（批量）→ 可选 `POST /holdings`（批量）。
  - 关注/编辑等级：`POST /watchlist`（upsert，携带 `tierUser`）；`tierAi` 由策略/模型计算并更新，仅展示不可直接修改。
  - 购买/卖出：`POST /holdings`（upsert）；“购买即关注”：未关注自动创建 watchlist。
  - 重新分析：`POST /strategy/analyze` 或 `/batch`；按 Rule 跳过已有周期。
  - 查看详情：`GET /stocks/:symbol/overview` 懒加载策略历史、总结与投资计划详情。
- 单页编排数据源：`GET /portfolio/overview` 作为主数据源；本地卡片操作采用乐观更新与失败回滚。

## 5. 业务流程（Mermaid 摘要）
- 单页中心与批量动作：
```mermaid
flowchart TD
  Usp[用户在「股票中心」页面] --> ActSel[打开选股Modal]
  ActSel --> Ssel[提交条件 -> /strategy/select]
  Ssel --> Cand[候选列表]
  Cand --> ActWatch[选择股票 -> 加入关注(选等级)]
  ActWatch --> Wapi[/POST /watchlist (batch)/]
  Cand -->|可选| ActBuy[立即购买]
  ActBuy --> Hapi[/POST /holdings (batch)/]
  Hapi --> RuleBuy[规则校验 + 购买即关注]
  RuleBuy --> Wapi

  Usp --> ActCard[卡片操作：关注/购买/重新分析]
  ActCard --> Ana[/POST /strategy/analyze/]
  ActCard --> Inv[/POST /investment/plan/]
  Ana --> UpdateGrid[刷新策略mini]
  Inv --> UpdateGrid

  subgraph OverviewData
    Usp --> GetOV[/GET /portfolio/overview/]
    GetOV --> Grid[卡片网格: 公司/价格/策略/总结/建议]
  end
```
- 多账户账户级概览：
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
- OCR 导入持仓：见 README 中“OCR 持仓识别设计”流程。

## 6. 架构与分层（强约束）
- 统一模式：`Controller/Facade/MQListener → Service → DataService/Repository`；外部接入 `Adapter（MCP）`；工具层 `Converter/Rule/Wrapper` 全部静态方法。
- 约束：
  - Controller 方法 ≤ 5 行，仅接参 → 调 `Service.collect{Domain}Data` → `Converter.toResponse` → `WebResponse.success()`；禁止 if/else、循环与业务逻辑。
  - Service：业务逻辑防腐层，协调流程、规则校验、权限包装；禁止直接触达基础设施（Repository/Adapter）。
  - DataService：聚合访问多数据源（Repository/Redis/ES），不含业务逻辑；外部服务通过 Adapter。
  - Repository：数据库访问与事务管理；禁止业务逻辑。
  - 禁止跨层调用与魔法值；异常统一 `BusinessException('清晰信息')`。

## 7. 数据模型与枚举
- 表与实体：
  - users、accounts（类型：`cash|margin|broker_x`）
  - watchlist（`user_id + account_id + symbol` 唯一）
  - holdings（`user_id + account_id + symbol` 唯一，`source: ocr|manual`）
  - company_info、price_snapshots
  - strategy_analysis、investment_plans、agent_tasks
- 索引与缓存：
  - DB 索引：`(user_id, account_id, symbol)` 在 watchlist/holdings/strategy_analysis，时间序列索引优化策略查询。
  - Redis Key：`price:{symbol}`（公共）；`portfolio:{userId}:{accountId}`（账户级）。
- TypeScript（strict 模式；复杂对象用 interface）：
```ts
export interface AccountScope { userId: string; accountId: string }
export interface WatchlistItem {
  userId: string;
  accountId: string;
  symbol: string;
  tierAi?: WatchTier;   // AI 分级（只读展示）
  tierUser?: WatchTier; // 用户自定义分级（可编辑）
  note?: string;
}
export interface HoldingItem { userId: string; accountId: string; symbol: string; quantity: number; avgCost: number; source?: 'manual'|'ocr' }
export interface PortfolioOverviewQuery { scope: AccountScope; filters?: { status?: PositionStatus; tier?: WatchTier } }
export type StrategySignal = 'buy' | 'sell' | 'hold';
```

## 8. API 设计（账户维度优先）
- 路径风格（推荐）：
  - `GET /users/:userId/accounts/:accountId/portfolio/overview`
  - `POST /users/:userId/accounts/:accountId/watchlist`
  - `POST /users/:userId/accounts/:accountId/holdings`
  - `POST /users/:userId/accounts/:accountId/holdings/ocr-import`
  - `POST /users/:userId/accounts/:accountId/strategy/analyze`
  - `POST /users/:userId/accounts/:accountId/strategy/analyze/batch`
  - `POST /users/:userId/accounts/:accountId/investment/plan`
  - `GET /users/:userId/accounts/:accountId/stocks/:symbol/overview`
- Header 方案（可选）：将 `X-User-Id`、`X-Account-Id` 放 Header 并在 Controller 收敛为 `AccountScope`。
- 聚合接口响应要点：一次返回卡片所需的公司/价格/策略摘要/周期总结/建议 mini；标注 `accountId` 便于前端分组。
  - 分级同时返回 `tierAi` 与 `tierUser`；默认展示 AI 分级，编辑仅作用用户分级。
  - 增加策略价格区间与最小买入：`strategy.entryRange/exitRange`、`market.minBuyQty`，便于前端直观显示与下单参考（仅建议）。
- 错误与异常：统一 `BusinessException('具体消息')`；前端按 `{ kind: 'loading'|'success'|'error', data?: T }` 判别联合处理。

## 9. 规则与事务
- 规则（静态 Rule）：
  - `InputRule.validateAccountScope(scope: unknown)`：类型与非空校验。
  - `InputRule.validateSymbol`、`RiskRule`、`LiquidityRule`、`PositionRule`：入参与风控约束。
  - `DuplicateRule.ensureUniqueWatch/Hold(scope, symbol)`：避免重复关注/持仓。
  - `StrategyRule.shouldGenerate(symbol, period)`：周期内存在则跳过策略生成。
  
  - 最小买入数量估算（账户/市场规则协同）：
    - 输入：账户预算（可选）、当前价 `P`、交易所规则（`boardLot`、`tickSize`、`fractionalAllowed`、`minOrderValue`）。
    - 估算：
      - 若支持碎股（`fractionalAllowed = true`）：`minQty = max(fractionalStep, floor((budget - fee) / P, step))`，默认碎股步长取券商配置（如 0.1 股）。
      - 若需整手：`minQty = max(boardLot, ceil((minOrderValue) / P / boardLot) * boardLot)`；无预算时取 `boardLot`。
      - 常见市场：美股（多支持 odd lot）`minQty = 1`；A股：`minQty = 100`；港股按 `boardLot`。
  - 策略价格范围（买入/卖出）：
    - 计算 `entryRange = [entryMin, entryMax]` 与 `exitRange = [exitMin, exitMax]`，结合 `ATR/MA/RSI` 与 `stop_loss/take_profit`：
      - 买入区间：`entryMin = max(stop_loss * (1 + ε), P - k * ATR)`；`entryMax = min(take_profit * (1 - ε), P + k * ATR)`。
      - 卖出区间：若信号 `sell`，`exitMin = P - k * ATR`（或追踪止损）；`exitMax = max(take_profit, P + k * ATR)`。
      - 推荐参数：`ε = 0.002`（0.2%），`k = 1 ~ 2`；由 `StrategyRule` 随波动率调优。
- “购买即关注”：`POST /holdings` 在 Service 编排中若发现未关注则自动 upsert `watchlist`（等级默认或由前端指定）。
- 事务边界：
  - 关注 + 购买同事务（批量 upsert 时使用幂等键与队列）。
  - OCR 导入的插入/更新 + 条件策略生成同事务块，保证原子性。

## 10. 前端实现要点
- 技术栈：`Vite + React + TypeScript (strict: true)`；复杂对象使用 `interface`；避免 `any`，必要时 `unknown` 并在 Rule/Converter 收敛。
- 状态管理：
  - 以 `portfolio/overview` 为主数据源；组件内操作乐观更新与失败回滚；短 TTL 缓存。
  - 判别联合管理异步状态；全局 Modal 管理统一为受控组件（选股、关注、购买、分析、详情）。
- 交互：
  - 账号切换器触发 `GET /users/:userId/accounts/:accountId/portfolio/overview`；所有操作显式账户上下文。
  - 过滤与分组（关注等级、持仓状态）；卡片网格分页/虚拟滚动；图表懒加载与节流。

## 11. 调度与缓存
- 调度：`Cron/Quartz/BullMQ`；按 `userId + accountId` 分片执行；批量任务幂等键包含 `accountId`。
- 缓存：行情公共缓存（Redis）；概览短 TTL；策略摘要与总结使用时间窗缓存与失效策略。

## 12. 权限与防腐层
- Service 作为业务逻辑防腐层：封装基础设施调用、统一异常与流程。
- Converter 层：投影视图数据、格式标准化、必要的业务计算（轻量）。
- Adapter 层：外部服务接入（行情/新闻/财报/OCR），协议转换与重试；统一错误 `BusinessException('外部服务不可用')`。
- Wrapper 层：`PermissionWrapper.ensureUserAccountAccess(user, accountId)` 统一权限；敏感信息过滤；缓存标记。

## 13. 里程碑与交付
- M1：项目骨架初始化（TypeScript strict、分层目录、基础异常与响应）
- M2：Repository 与 Adapter（至少行情）与 DataService 打通“优库后 MCP 拉取”路径
- M3：聚合接口 v1（账户级 `portfolio/overview` 与 `stocks/:symbol/overview`）
- M4：单页股票中心原型（卡片网格 + 关注/购买/分析/详情 Modal）
- M5：OCR 导入持仓与动态盈亏计算，策略生成跳过规则
- M6：批量分析与投资建议、短 TTL 缓存与性能优化
- M7：调度与 MQListener（策略周期检查与阶段总结）
- M8：端到端测试与观测、验收

## 14. 验收标准（示例）
- 接口：
  - `GET /users/:userId/accounts/:accountId/portfolio/overview` 在缓存命中时 ≤ 200ms；miss ≤ 800ms。
  - 购买/关注批量 upsert 幂等，无重复记录；失败时事务回滚一致。
  - OCR 导入 100 条记录在 ≤ 2s 完成并正确计算盈亏；已有周期策略则跳过生成。
- 前端：
  - 单页中心内完成“选股→关注→购买→分析→建议→总结”的主要操作，无页面跳转强制依赖；Modal 管理一致、乐观更新回退正确。
  - 多账户切换后数据与操作严格归属当前账户，无交叉污染。

## 15. 风险与边界
- 外部服务（行情/OCR）不可用或延迟高：通过 Adapter 重试与降级；前端提示与缓存兜底。
- OCR 解析不可信：需 `OcrRule` 标准化与必要时人工确认；异常统一为 `BusinessException('OCR服务不可用或解析失败')`。
- 数据一致性：批量与事务边界清晰，幂等键与去重，避免重复写入。

## 16. 命名与代码规范（统一约束）
- 类命名：`{Domain}Controller/{Domain}Service/{Domain}Converter/{Domain}Rule/{Domain}Wrapper`；外部服务 `{External}Adapter/{External}ServiceClient`。
- 方法命名：Controller 用 `get/create/update/delete` 前缀；Service 用 `collect{Domain}Data`。
- 数据对象：`{Domain}Request/{Domain}Response/{Domain}Data/{Domain}VO/{Domain}Entity`。
- 包结构：`controller/`、`service/{domain}/`、`infrastructure/serviceclient/`、`infrastructure/repository/`。
- 工具类静态方法；禁止 `any`，优先 `unknown` 并在边界类型收敛；`strict: true`；异步统一 `Promise<T>`。

## 17. 附录与参考
- 详细设计：
  - 单页股票中心：`docs/one-page-stock-center.md`
  - 多用户/多账户：`docs/multi-user-multi-account.md`
  - 总体架构与流程：`README.md`
- 流程图：见各文档 Mermaid 图示。

---

如需，我可在 `src/` 初始化前端骨架并先落地单页股票中心的原型，同时搭建后端聚合接口的最小骨架用于联调。