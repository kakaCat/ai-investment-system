# PRD v2 — 股票中心与量化 Agent 支撑

版本：v2（取代 v1）
状态：草案（可迭代到冻结版）
范围：多用户多账户、关注与持仓、交易事件账本、Agent参考数据与量化支撑、风险与业绩看板、任务调度与增量刷新

## 1. 背景与目标
- 统一管理多账户的关注与持仓，保证账本与业绩可追溯。
- 为量化 Agent 提供参考数据切片、特征/信号/订单闭环与风控支撑。
- 保证幂等与一致性，避免重复入账，便于增量刷新与审计。
- 面向查询与看板优化索引与视图，提升常用场景性能。

## 2. 用户与角色
- 普通用户：维护关注与持仓，查看建议与业绩。
- 量化 Agent：消费参考数据、计算特征与信号，生成订单意图。
- 管理员/系统：配置任务与刷新策略，监控数据质量。

## 3. 范围与不做事项（Out of Scope）
- 不实现券商下单通道；仅保留订单意图与对账字段。
- 不在数据库层使用外键触发器；采用虚拟外键与服务层编排。

## 4. 关键设计原则（数据库维度）
- 虚拟外键：通过 `symbol/account_id/...` 建立天然引用；删除由服务层编排。
- 幂等键：对导入/事件/订单意图/特征值使用 `idempotency_key` 唯一约束。
- 审计可追溯：所有入账保留时间戳与来源，支持从事件重建持仓。
- UTC 时间与高精度金额：`TIMESTAMPTZ`、`NUMERIC(18,6)/(20,8)`，避免精度损失。
- 索引策略：覆盖账户+股票+时间维度的查询，视图/物化视图按需增量刷新。

## 5. 数据对象与表映射（与 db-schema 一致）
- 关注与持仓：`watchlist`、`holdings`（双分级 `tier_ai/tier_user`）。
- 交易事件账本：`trade_events`（买/卖/分红/拆并/费用/税/调整）。
- 已实现盈亏：`realized_pnl`；账户偏好：`account_preferences`。
- Agent参考数据：`agent_reference_config`、`agent_reference_series`（可选缓存）、`agent_selected_price_mv`（物化视图）。
- 量化支撑：
  - 特征：`feature_definitions`、`feature_values`
  - 模型与运行：`model_versions`、`agent_runs`
  - 信号与订单意图：`agent_signals`、`order_intents`
  - 风险与违规：`risk_limits`、`risk_violations`
  - 时序支撑：`trading_calendar`、`fx_rates`
  - 看板：`portfolio_metrics_daily`
  - 数据质量：`data_quality_issues`
  - 刷新辅助：`agent_selected_mv_refresh`

## 6. 主要功能需求
- 关注与持仓管理：新增/更新/删除；购买即关注由服务层编排。
- 事件入账：幂等 upsert，支持外部回执 `external_ref` 对账。
- Agent参考数据：按范围（关注/持仓/自定义）、粒度（分钟/小时/日线）与时间窗配置；生成缓存或依赖物化视图。
- 特征计算与存储：按 `symbol+ts` 写入 `feature_values`，保存参数快照与来源。
- 信号生成：保存置信度与特征快照；绑定运行 `run_id`。
- 订单意图：状态流转（new/placed/partial/canceled/filled）与幂等键，最终与 `trade_events` 对账。
- 风险控制：账户限额、单股权重、当日换手、杠杆约束；违规记录。
- 时序与汇率：交易日历控制开闭市，汇率统一计价。
- 业绩看板：按日净值/收益率/波动率/回撤/换手率。
- 任务与刷新：支持增量刷新（记录到 `agent_selected_mv_refresh`）、调度回放与异常记录。

## 7. 典型用户流程
- OCR 导入持仓：
  1) 解析 -> 2) holdings 幂等 upsert -> 3) strategy_analysis（可选） -> 4) 购买即关注（服务层）
- Agent 策略运行：
  1) 读取参考视图 -> 2) 计算特征 -> 3) 产出信号 -> 4) 风控 -> 5) 生成订单意图 -> 6) 成交入账 `trade_events`
- 看板加载：
  1) 最新持仓/行情 -> 2) 汇率换算 -> 3) 指标聚合 -> 4) 展示。

## 8. API 蓝图（示例）
- Watchlist：`GET/POST/DELETE /users/{id}/accounts/{id}/watchlist`
- Holdings：`GET/PUT /users/{id}/accounts/{id}/holdings`
- Trade Events：`POST /users/{id}/accounts/{id}/events`（幂等键）
- Agent Reference Config：`POST/GET /users/{id}/accounts/{id}/agent/reference-config`
- Features：`POST/GET /features/{name}/values`
- Signals：`POST/GET /users/{id}/accounts/{id}/signals`
- Order Intents：`POST/GET /users/{id}/accounts/{id}/orders/intents`
- Risk Limits：`PUT/GET /users/{id}/accounts/{id}/risk-limits`
- Portfolio Metrics：`GET /users/{id}/accounts/{id}/metrics/daily`
- Tasks：`POST/GET /agent/tasks`

## 9. 非功能性要求
- 稳定性与一致性：严格幂等，失败可重试，避免双写和重复入账。
- 性能：热点索引（账户+股票+时间）、视图/物化视图、增量刷新。
- 安全与审计：敏感信息过滤、操作留痕、数据质量告警。
- 兼容性：PostgreSQL 优先；MySQL 适配注意 ENUM/CHECK 差异与索引策略。

## 10. 技术约束（架构与编码）
- 分层模式：Controller/Facade/MQListener → Service → DataService/Repository。
- 防腐层：Converter（数据转换）、Rule（业务规则）、Wrapper（权限/脱敏）、Adapter（外部服务）。
- 约束：Controller 无业务逻辑与分支；Service 不直接操作基础设施（统一走 DataService）；静态工具类方法。
- TypeScript 规范：严格模式、判别联合、避免 any、Promise<T> 返回、Error 使用明确消息。

## 11. 迁移与升级策略（v1 → v2）
- 数据枚举与索引：补充参考枚举与量化支撑表的唯一约束与索引（详见 db-schema）。
- 视图与增量：引入 `agent_selected_price_mv` 与 `agent_selected_mv_refresh`；任务驱动增量刷新。
- 兼容：保留 v1 表结构与数据，新增表不破坏原查询；逐步迁移业务到 v2 API。

## 12. 风险与缓解
- 数据新鲜度：增量刷新与窗口对齐；异常记录到 `data_quality_issues`。
- 一致性：统一幂等键生成策略与对账；避免跨层写入。
- 性能热点：分区与覆盖索引评估；必要时引入按账户分表或缓存。

## 13. 里程碑
- M1：PRD v2 冻结与 db-schema 对齐。
- M2：Agent参考数据与视图上线；增量刷新任务。
- M3：量化支撑表与 API 上线；风控与订单意图闭环。
- M4：业绩看板与数据质量监控上线。

## 14. 变更日志（相较 v1）
- 新增 Agent参考数据（配置/缓存/物化视图）章节与 DDL。
- 新增量化支撑表（特征/模型/运行/信号/订单/风险/交易日/汇率/业绩/数据质量/刷新辅助）。
- 补充“关键约束与规则映射”覆盖唯一约束、索引与枚举约束。
- 明确 API 蓝图与非功能性要求，强化幂等与增量刷新策略。

—— 完 ——