# 单页股票中心（Modal 编排，一页完成关注/持仓/选股/购买）

> 状态说明：本页为详细设计参考，核心信息已汇总至《docs/prd-v1.md》。若存在不一致，以 PRD v1 为准；本页保留交互编排与实现要点用于协作与回溯。

目标：将关注与持仓合并到同一个页面，通过弹框（Modal）捏合“选股→关注→购买→策略/总结”，降低割裂感，实现“一页完成核心操作”。

## 页面线框（单页布局）
```
┌─────────────────────────────────────────────────────────────────────────┐
│ 顶部：搜索（symbol/公司） | 预算输入（可选） | 过滤（关注等级/持仓状态）     │
├─────────────────────────────────────────────────────────────────────────┤
│ 左侧侧栏（组合视角）：                                             │
│  - 关注（分级：A/B/C） 计数与筛选                                 │
│  - 持仓 总览：总市值/盈亏/仓位占比                                 │
│  - 快捷操作：选股、批量分析、批量建议                              │
├─────────────────────────────────────────────────────────────────────────┤
│ 主区域（卡片网格，每个股票一个卡）：                                 │
│  [公司/价格/评级/来源] [策略摘要] [周期总结mini] [建议mini]          │
│  操作按钮：关注/编辑等级 | 购买/卖出 | 重新分析 | 查看详情            │
└─────────────────────────────────────────────────────────────────────────┘
```

## Modal 编排与动作映射
- 选股 Modal（入口在侧栏或顶部）：
  - 表单：行业/因子/风险约束/其他筛选 → 返回候选列表
  - 列表操作：单选/多选 “加入关注（选择等级）”；可勾选“加入后立即购买”
  - 提交：`POST /strategy/select` → `POST /watchlist`（批量）→ 若勾选购买则串行 `POST /holdings`（批量）
- 关注/编辑等级 Modal（卡片按钮）：
  - 表单：等级（A/B/C）+ 备注
  - 提交：`POST /watchlist`（插入/更新）
- 购买/卖出 Modal（卡片按钮）：
  - 表单：数量、成本价（买入）；卖出数量/价格（可选）
  - 规则：`RiskRule`/`LiquidityRule` 前端基本校验，后端严格校验
  - 提交：`POST /holdings` 插入/更新；约定“购买即关注”：若未关注，自动 `POST /watchlist` 并设置等级（默认可选）
- 重新分析 Modal（卡片按钮或批量）：
  - 动作：`POST /strategy/analyze` 或 `POST /strategy/analyze/batch`
  - Rule：`StrategyRule.shouldGenerate(period)` 控制跳过/生成
- 查看详情 Modal：
  - 内容：策略历史、总结详情、投资计划详情（懒加载）
  - 数据：`GET /stocks/:symbol/overview` 或明细接口

## 单页编排流程图（Mermaid）
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

## 聚合与事务（后端配合）
- 插入/更新的事务边界：
  - “加入关注 + 购买”可在 Service 层事务中串联：`watchlist upsert` 与 `holdings upsert` 同事务，保证一致性。
  - 批量操作使用队列与幂等键，避免重复写入。
- “购买即关注”规则：
  - 若未关注则自动创建 `watchlist` 记录，等级由前端选择或后端默认。
  - Rule 保证无重复关注记录（`DuplicateRule.ensureUniqueHolding` 与 Watchlist 唯一约束）。

## API 建议（与聚合接口协同）
- `GET /portfolio/overview`：卡片网格一次性获取关注+持仓及每只标的的策略/总结/建议 mini。
- `POST /watchlist`：支持批量插入/更新（携带 `tier`）。
- `POST /holdings`：支持批量插入/更新，返回最新价与动态盈亏；购买时触发“购买即关注”。
- `POST /strategy/analyze/batch`：批量分析（关注/持仓选择集）。
- `POST /investment/plan`：支持 scope 为当前页面选中集合或全部持仓。
- `GET /stocks/:symbol/overview`：单标详细视图（Modal 详情或跳转）。

## 前端实现要点
- 全局 Modal 管理：将“选股/关注/购买/分析/详情”统一为受控组件，使用类型安全 props（`interface`）。
- 状态管理：
  - `portfolio/overview` 作为主数据源；本地对卡片的操作采用乐观更新（失败回滚）。
  - 判别联合处理请求状态：`{ kind: 'loading'|'success'|'error', data?: T }`。
- 过滤与分组：侧栏筛选（关注等级、持仓状态）；卡片网格支持分页与虚拟滚动。
- 性能：聚合接口短 TTL 缓存；图表按需加载；大列表批量操作节流。

## 架构契合
- Controller 保持 5 行以内：接参→Service.collect→Converter.toResponse→WebResponse.success。
- Service 统一编排事务与规则；Converter 投影卡片数据；Rule 控制“购买即关注”“策略跳过”。
- DataService 优库后 MCP；Adapter 仅做外部服务接入；Wrapper 过滤敏感信息。