## 设计原则
 - 严格账户隔离：核心表均携带 `user_id + account_id`（除公共行情/公司信息）。
 - 写少读多：时序数据建立复合索引（如 `symbol + ts`），优化时间窗查询；概览查询避免 N+1。
 - 避免冗余：盈亏等动态指标不落库，通过最新价格计算；必要时使用物化视图或缓存。
 - 数值型主键：统一使用 `BIGSERIAL/BIGINT` 作为主键与外键类型（替代 UUID），便于聚簇索引与顺序存储；PostgreSQL 可选执行 `CLUSTER`。
 - 虚拟外键：不使用数据库外键；通过 `NOT NULL`、`UNIQUE`、`CHECK` 与索引维护引用字段；删除采用软删除或审计留存，不在 DB 层做级联。
 - 列命名规范：避免保留词；采用明确语义名（如 `user_name`、`account_name`、`company_name`）；统一时间字段 `created_at/updated_at`；离散值使用 `ENUM` 类型。
 - 幂等键约定：对事件/导入类表设置 `idempotency_key` 唯一约束，防止重复入账。
 - 审计与可追溯：账本类表保留原始事件，不存储计算型字段；派生视图或报表负责计算汇总。
 - 约束优先：关键字段 `NOT NULL`；合理 `CHECK`（如数量>0、金额>=0）；必要组合 `UNIQUE`（如 `user_id + account_id + symbol`）。
 - 索引策略：通用索引 `user_id + account_id`；时序表索引 `symbol + ts DESC`；多维查询使用部分索引或覆盖索引。
 - 时间与货币：统一保存为 UTC；金额使用 `NUMERIC(20,8)` 或以 `BIGINT` 存储最小单位；避免 `FLOAT`。
 - 软删除与归档：业务删除采用 `is_deleted`/`deleted_at`；历史归档使用分区或分表策略。

# 数据库表结构设计 v1（PostgreSQL）

> 目标：在多用户多账户（多租户）与“股票为中心”的聚合视图下，提供规范的表结构、约束、索引与示例查询。支持双分级（AI 分级 + 用户分级）、OCR 导入、策略分析与投资建议。优先 PostgreSQL，MySQL 可按约束与索引语法适配。

 

## 枚举（PostgreSQL ENUM 或 CHECK 替代）
```sql
-- 可选：使用 ENUM；或用 TEXT + CHECK 约束
-- 账户类型：现金账户/保证金账户/券商自定义
CREATE TYPE account_type AS ENUM ('cash','margin','broker_x');
-- 账户状态：活跃/停用
CREATE TYPE account_status AS ENUM ('active','inactive');
-- 行情来源：数据库聚合/外部市场数据提供商（MCP）
CREATE TYPE market_source AS ENUM ('db','mcp');
-- 关注分级：A（高优先）/B（中）/C（低）
CREATE TYPE watch_tier AS ENUM ('A','B','C');
-- 策略周期：日/周/月
CREATE TYPE strategy_period AS ENUM ('daily','weekly','monthly');
-- 策略信号：买入/卖出/观望
CREATE TYPE strategy_signal AS ENUM ('buy','sell','hold');
-- 持仓来源：手动录入/OCR 导入
CREATE TYPE holding_source AS ENUM ('manual','ocr');
-- 任务状态：待处理/运行中/已完成/失败
CREATE TYPE task_status AS ENUM ('pending','running','done','failed');
-- 交易事件类型：买/卖/分红/拆并/费用/税/调整
CREATE TYPE trade_event_type AS ENUM ('buy','sell','dividend','split','fee','tax','adjustment');
-- 事件来源：手动/OCR/券商回执
CREATE TYPE trade_source AS ENUM ('manual','ocr','broker');
-- 成本计算方法：FIFO/LIFO/平均
CREATE TYPE cost_method AS ENUM ('fifo','lifo','avg');
 -- Agent参考粒度：1分钟/5分钟/1小时/日线
 CREATE TYPE ref_granularity AS ENUM ('minute_1','minute_5','hour_1','daily');
 -- Agent参考范围：关注列表/持仓/自定义集合
 CREATE TYPE reference_scope AS ENUM ('watchlist','holdings','custom');
 -- Agent参考数据来源：API/导入/派生
 CREATE TYPE reference_source AS ENUM ('api','import','derived');
```
```sql
COMMENT ON TYPE account_type IS '账户类型：现金账户/保证金账户/券商自定义';
COMMENT ON TYPE account_status IS '账户状态：活跃/停用';
COMMENT ON TYPE market_source IS '行情来源：数据库聚合/外部市场数据提供商';
COMMENT ON TYPE watch_tier IS '关注分级：A高优先/B中/C低';
COMMENT ON TYPE strategy_period IS '策略周期：日/周/月';
COMMENT ON TYPE strategy_signal IS '策略信号：买入/卖出/观望';
COMMENT ON TYPE holding_source IS '持仓来源：手动录入/OCR 导入';
COMMENT ON TYPE task_status IS '任务状态：待处理/运行中/已完成/失败';
COMMENT ON TYPE trade_event_type IS '交易事件类型：买/卖/分红/拆并/费用/税/调整';
COMMENT ON TYPE trade_source IS '事件来源：手动/OCR/券商回执';
COMMENT ON TYPE cost_method IS '成本计算方法：FIFO/LIFO/平均';
 COMMENT ON TYPE ref_granularity IS 'Agent参考粒度：1分钟/5分钟/1小时/日线';
 COMMENT ON TYPE reference_scope IS 'Agent参考范围：关注列表/持仓/自定义集合';
 COMMENT ON TYPE reference_source IS 'Agent参考数据来源：API/导入/派生';
```

## 用户与账户
```sql
CREATE TABLE users (
  id BIGSERIAL PRIMARY KEY,            -- 用户唯一ID（数值型主键）
  email TEXT UNIQUE NOT NULL,          -- 用户邮箱（唯一）
  user_name TEXT,                      -- 用户名称
  status TEXT DEFAULT 'active',        -- 用户状态（active/inactive）
  created_at TIMESTAMPTZ DEFAULT NOW() -- 创建时间
);

CREATE TABLE accounts (
  id BIGSERIAL PRIMARY KEY,                                 -- 账户唯一ID（数值型主键）
  user_id BIGINT NOT NULL,                                  -- 所属用户ID（引用 users.id，虚拟外键）
  account_name TEXT NOT NULL,                               -- 账户名称
  type account_type NOT NULL,                               -- 账户类型（枚举：cash/margin/broker_x）
  status account_status DEFAULT 'active',                   -- 账户状态（枚举：active/inactive）
  created_at TIMESTAMPTZ DEFAULT NOW(),                     -- 创建时间
  updated_at TIMESTAMPTZ DEFAULT NOW()                      -- 更新时间
);
CREATE INDEX idx_accounts_user ON accounts(user_id); -- 加速按用户查询账户
```

## 公司与行情（公共）
```sql
CREATE TABLE company_info (
  id BIGSERIAL PRIMARY KEY,            -- 公司唯一ID（数值型主键）
  symbol TEXT UNIQUE NOT NULL,         -- 股票代码（自然键，唯一）
  company_name TEXT NOT NULL,          -- 公司名称
  exchange TEXT,                       -- 交易所
  sector TEXT,                         -- 行业门类
  industry TEXT,                       -- 子行业
  currency TEXT,                       -- 交易货币
  fundamentals JSONB,                  -- 基本面数据（JSON）
  updated_at TIMESTAMPTZ DEFAULT NOW() -- 更新时间
);

CREATE TABLE price_snapshots (
  id BIGSERIAL PRIMARY KEY,                   -- 行情快照ID
  symbol TEXT NOT NULL,                       -- 股票代码（引用 company_info.symbol，虚拟外键）
  price NUMERIC(18,6) NOT NULL,               -- 价格
  volume BIGINT,                              -- 成交量
  change_percent NUMERIC(9,4),                -- 涨跌幅（百分比）
  as_of TIMESTAMPTZ NOT NULL,                 -- 快照时间
  source market_source DEFAULT 'mcp',         -- 数据来源
  UNIQUE(symbol, as_of, source)               -- 同一股票/时间/来源唯一
);
CREATE INDEX idx_price_symbol_time ON price_snapshots(symbol, as_of DESC); -- 价格时间序列查询优化
```

## 市场交易规则（每只股票）
```sql
CREATE TABLE market_rules (
  id BIGSERIAL PRIMARY KEY,                                                -- 规则记录ID
  symbol TEXT NOT NULL,                                                    -- 股票代码（引用 company_info.symbol，虚拟外键）
  board_lot BIGINT NOT NULL,                                               -- 整手股数（如A股100、港股依股票，美股多为1）
  tick_size NUMERIC(18,6) NOT NULL,                                        -- 最小价位变动
  fractional_allowed BOOLEAN NOT NULL DEFAULT TRUE,                        -- 是否允许碎股
  fractional_step NUMERIC(18,6) DEFAULT 0.1,                               -- 碎股步长（券商配置）
  min_order_value NUMERIC(20,2),                                           -- 最小订单金额（可空）
  updated_at TIMESTAMPTZ DEFAULT NOW(),                                    -- 更新时间
  UNIQUE(symbol)                                                           -- 每只股票一条规则
);
CREATE INDEX idx_market_rules_symbol ON market_rules(symbol);
```

## 关注与持仓（账户维度，含双分级）
```sql
CREATE TABLE watchlist (
  id BIGSERIAL PRIMARY KEY,                                                -- 关注记录ID
  user_id BIGINT NOT NULL,                                                 -- 用户ID
  account_id BIGINT NOT NULL,                                              -- 账户ID（引用 accounts.id，虚拟外键）
  symbol TEXT NOT NULL,                                                    -- 股票代码（引用 company_info.symbol，虚拟外键）
  tier_ai watch_tier,                                                      -- AI 分级（只读展示，服务端更新）
  tier_user watch_tier,                                                    -- 用户分级（可编辑）
  note TEXT,                                                               -- 备注
  created_at TIMESTAMPTZ DEFAULT NOW(),                                    -- 创建时间
  updated_at TIMESTAMPTZ DEFAULT NOW(),                                    -- 更新时间
  UNIQUE(user_id, account_id, symbol)                                      -- 账户维度去重
);
CREATE INDEX idx_watchlist_account_symbol ON watchlist(account_id, symbol); -- 加速账户+股票查询
CREATE INDEX idx_watchlist_tier_user ON watchlist(account_id, tier_user);   -- 加速账户内按用户分级筛选

  CREATE TABLE holdings (
  id BIGSERIAL PRIMARY KEY,                                                -- 持仓记录ID
  user_id BIGINT NOT NULL,                                                 -- 用户ID
  account_id BIGINT NOT NULL,                                              -- 账户ID（引用 accounts.id，虚拟外键）
  symbol TEXT NOT NULL,                                                    -- 股票代码（引用 company_info.symbol，虚拟外键）
  quantity NUMERIC(20,6) NOT NULL,                                         -- 持仓数量
  avg_cost NUMERIC(18,6) NOT NULL,                                         -- 平均持仓成本
  source holding_source DEFAULT 'manual',                                   -- 来源（manual/ocr）
  last_import_at TIMESTAMPTZ,                                              -- 最近导入时间（OCR）
  updated_at TIMESTAMPTZ DEFAULT NOW(),                                    -- 更新时间
  UNIQUE(user_id, account_id, symbol)                                      -- 账户维度去重
);
  CREATE INDEX idx_holdings_account_symbol ON holdings(account_id, symbol); -- 加速账户+股票查询
```

## 交易事件账本（持仓变更事件）
```sql
CREATE TABLE trade_events (
  id BIGSERIAL PRIMARY KEY,                                                -- 事件ID
  user_id BIGINT NOT NULL,                                                 -- 用户ID
  account_id BIGINT NOT NULL,                                              -- 账户ID（引用 accounts.id，虚拟外键）
  symbol TEXT NOT NULL,                                                    -- 股票代码（引用 company_info.symbol，虚拟外键）
  event_type trade_event_type NOT NULL,                                    -- 事件类型（买/卖/分红/拆并/费用/税/调整）
  qty_delta NUMERIC(20,6),                                                 -- 数量变化（买为正、卖为负；拆并按比例净变化）
  price NUMERIC(18,6),                                                     -- 单价（买/卖/调整场景）
  amount NUMERIC(20,6),                                                    -- 金额变化（买为负、卖为正；含费用税）
  fee NUMERIC(20,6),                                                       -- 手续费
  tax NUMERIC(20,6),                                                       -- 税费
  as_of TIMESTAMPTZ NOT NULL,                                              -- 发生时间
  source trade_source DEFAULT 'manual',                                     -- 来源（manual/ocr/broker）
  external_ref TEXT,                                                       -- 外部回执/订单号
  idempotency_key TEXT UNIQUE,                                             -- 幂等键（避免重复入账）
  created_at TIMESTAMPTZ DEFAULT NOW()                                     -- 创建时间
);
CREATE INDEX idx_trades_account_symbol_time ON trade_events(account_id, symbol, as_of DESC); -- 按账户+股票+时间查询
CREATE INDEX idx_trades_user_time ON trade_events(user_id, account_id, as_of DESC);           -- 按用户账户时间维度查询
CREATE INDEX idx_trades_external_ref ON trade_events(external_ref);                           -- 外部回执对账
```

## Agent参考数据（选中股票历史切片）
```sql
-- 配置表：定义 agent 参考数据的范围、粒度与时间窗
CREATE TABLE agent_reference_config (
  id BIGSERIAL PRIMARY KEY,                                                -- 配置ID
  user_id BIGINT NOT NULL,                                                 -- 用户ID
  account_id BIGINT NOT NULL,                                              -- 账户ID（引用 accounts.id，虚拟外键）
  agent_id BIGINT NOT NULL,                                                -- Agent ID（虚拟外键）
  scope reference_scope NOT NULL,                                          -- 参考范围（watchlist/holdings/custom）
  watchlist_id BIGINT,                                                     -- 自定义集合或关注列表ID（可选，虚拟外键）
  granularity ref_granularity NOT NULL,                                    -- 粒度（minute_1/minute_5/hour_1/daily）
  start_ts TIMESTAMPTZ NOT NULL,                                           -- 起始时间（UTC）
  end_ts TIMESTAMPTZ,                                                      -- 结束时间（可选）
  refresh_policy TEXT,                                                     -- 刷新策略（cron/触发/增量）
  idempotency_key TEXT UNIQUE,                                             -- 幂等键（避免重复配置）
  created_at TIMESTAMPTZ DEFAULT NOW(),                                    -- 创建时间
  updated_at TIMESTAMPTZ DEFAULT NOW()                                     -- 更新时间
);
CREATE INDEX idx_agent_ref_cfg_account_agent ON agent_reference_config(account_id, agent_id);
CREATE INDEX idx_agent_ref_cfg_window ON agent_reference_config(agent_id, start_ts, end_ts);
```

```sql
-- 可选缓存表：为 agent 高频读取场景缓存选中子集的时序数据
CREATE TABLE agent_reference_series (
  id BIGSERIAL PRIMARY KEY,                                                -- 缓存记录ID
  user_id BIGINT NOT NULL,                                                 -- 用户ID
  account_id BIGINT NOT NULL,                                              -- 账户ID（引用 accounts.id，虚拟外键）
  agent_id BIGINT NOT NULL,                                                -- Agent ID（虚拟外键）
  config_id BIGINT NOT NULL,                                               -- 配置ID（引用 agent_reference_config.id，虚拟外键）
  symbol TEXT NOT NULL,                                                    -- 股票代码（引用 company_info.symbol，虚拟外键）
  ts TIMESTAMPTZ NOT NULL,                                                 -- 时间戳（UTC）
  open NUMERIC(18,6),                                                      -- 开盘价
  high NUMERIC(18,6),                                                      -- 最高价
  low NUMERIC(18,6),                                                       -- 最低价
  close NUMERIC(18,6),                                                     -- 收盘价
  volume NUMERIC(20,6) CHECK (volume >= 0),                                -- 成交量（非负）
  source reference_source DEFAULT 'derived',                                -- 数据来源（api/import/derived）
  snapshot_id BIGINT,                                                      -- 原始行情记录ID（引用 price_snapshots.id，虚拟外键）
  idempotency_key TEXT UNIQUE,                                             -- 幂等键（避免重复入账）
  created_at TIMESTAMPTZ DEFAULT NOW()                                     -- 创建时间
);
CREATE UNIQUE INDEX uniq_agent_ref_series ON agent_reference_series(config_id, symbol, ts);
CREATE INDEX idx_agent_ref_series_hot ON agent_reference_series(account_id, agent_id, symbol, ts DESC);
```

```sql
-- 物化视图：从关注/持仓的 symbol 集合过滤公共行情，供 agent 快速查询
CREATE MATERIALIZED VIEW agent_selected_price_mv AS
SELECT w.user_id,
       w.account_id,
       w.symbol,
       p.as_of AS ts,
       p.open,
       p.high,
       p.low,
       p.close,
       p.volume
FROM watchlist w
JOIN price_snapshots p ON p.symbol = w.symbol
UNION ALL
SELECT h.user_id,
       h.account_id,
       h.symbol,
       p.as_of AS ts,
       p.open,
       p.high,
       p.low,
       p.close,
       p.volume
FROM holdings h
JOIN price_snapshots p ON p.symbol = h.symbol;

CREATE INDEX idx_agent_selected_mv ON agent_selected_price_mv(account_id, symbol, ts DESC);
-- 刷新建议：
-- REFRESH MATERIALIZED VIEW CONCURRENTLY agent_selected_price_mv;
```

## 量化策略支撑（特征/信号/订单/模型/运行/风险/交易日/汇率/业绩）
```sql
-- 特征定义：声明特征的名称、版本、窗口与参数
CREATE TABLE feature_definitions (
  id BIGSERIAL PRIMARY KEY,
  name TEXT NOT NULL,                                                     -- 特征名称，如 ma, rsi, atr
  version TEXT NOT NULL,                                                  -- 版本（参数集）
  dtype TEXT NOT NULL,                                                    -- 数据类型（numeric/json）
  window_spec TEXT,                                                       -- 窗口定义（如 14d, 20m）
  params JSONB,                                                           -- 参数（JSON）
  created_at TIMESTAMPTZ DEFAULT NOW(),                                   -- 创建时间
  UNIQUE(name, version)
);
CREATE INDEX idx_feature_defs_name ON feature_definitions(name);

-- 特征值：面向 symbol+ts 的特征产出，供回测与在线复用
CREATE TABLE feature_values (
  id BIGSERIAL PRIMARY KEY,
  feature_id BIGINT NOT NULL,                                             -- 引用 feature_definitions.id（虚拟外键）
  symbol TEXT NOT NULL,                                                   -- 股票代码
  ts TIMESTAMPTZ NOT NULL,                                                -- 时间戳（UTC）
  value JSONB,                                                            -- 值（可存标量或结构）
  source TEXT DEFAULT 'derived',                                          -- 来源（derived/api/import）
  idempotency_key TEXT UNIQUE,                                            -- 幂等键
  created_at TIMESTAMPTZ DEFAULT NOW(),                                   -- 创建时间
  UNIQUE(feature_id, symbol, ts)
);
CREATE INDEX idx_feature_values_symbol_time ON feature_values(symbol, ts DESC);
CREATE INDEX idx_feature_values_feature_time ON feature_values(feature_id, ts DESC);

-- 模型版本登记
CREATE TABLE model_versions (
  id BIGSERIAL PRIMARY KEY,
  name TEXT NOT NULL,                                                     -- 模型名称
  version TEXT NOT NULL,                                                  -- 版本号
  params JSONB,                                                           -- 训练/推理参数
  metrics JSONB,                                                          -- 评估指标
  artifact_ref TEXT,                                                      -- 产物存储引用（如路径/哈希）
  created_at TIMESTAMPTZ DEFAULT NOW(),                                   -- 创建时间
  UNIQUE(name, version)
);
CREATE INDEX idx_model_versions_name ON model_versions(name);

-- 运行记录：一次策略运行的过程与指标
CREATE TABLE agent_runs (
  id BIGSERIAL PRIMARY KEY,
  agent_id BIGINT NOT NULL,                                               -- Agent ID（虚拟外键）
  model_version_id BIGINT NOT NULL,                                       -- 模型版本（虚拟外键）
  config_id BIGINT,                                                       -- 可选：参考数据配置ID（虚拟外键）
  status task_status DEFAULT 'pending',                                   -- 状态（复用 task_status）
  metrics JSONB,                                                          -- 运行指标
  started_at TIMESTAMPTZ DEFAULT NOW(),                                   -- 开始时间
  finished_at TIMESTAMPTZ                                                 -- 结束时间
);
CREATE INDEX idx_agent_runs_started ON agent_runs(agent_id, started_at DESC);

-- 信号：原子信号与其特征快照
CREATE TABLE agent_signals (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT NOT NULL,
  account_id BIGINT NOT NULL,
  symbol TEXT NOT NULL,
  ts TIMESTAMPTZ NOT NULL,
  signal strategy_signal NOT NULL,                                        -- buy/sell/hold
  confidence NUMERIC(5,2),                                               -- 置信度（百分比）
  features JSONB,                                                         -- 特征快照
  run_id BIGINT,                                                          -- 引用 agent_runs.id（虚拟外键）
  created_at TIMESTAMPTZ DEFAULT NOW(),                                   -- 创建时间
  UNIQUE(run_id, symbol, ts)
);
CREATE INDEX idx_signals_account_symbol_time ON agent_signals(account_id, symbol, ts DESC);

-- 订单意图：由信号经风控产出，最终由服务层执行并入账到 trade_events
CREATE TABLE order_intents (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT NOT NULL,
  account_id BIGINT NOT NULL,
  symbol TEXT NOT NULL,
  side TEXT NOT NULL CHECK (side IN ('buy','sell')),                      -- 方向
  price NUMERIC(18,6),                                                    -- 限价（可选）
  qty NUMERIC(20,6) NOT NULL CHECK (qty > 0),                             -- 数量
  time_in_force TEXT,                                                     -- TIF（如 IOC/FOK/GTC）
  signal_id BIGINT,                                                       -- 引用 agent_signals.id（虚拟外键）
  status TEXT DEFAULT 'new' CHECK (status IN ('new','placed','partial','canceled','filled')),
  external_ref TEXT,                                                      -- 券商回执/订单号
  idempotency_key TEXT UNIQUE,                                            -- 幂等键
  created_at TIMESTAMPTZ DEFAULT NOW()                                    -- 创建时间
);
CREATE INDEX idx_order_intents_account_symbol_time ON order_intents(account_id, symbol, created_at DESC);
CREATE INDEX idx_order_intents_status ON order_intents(account_id, status);

-- 风险限额与违规
CREATE TABLE risk_limits (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT NOT NULL,
  account_id BIGINT NOT NULL,
  max_position_value NUMERIC(20,8),                                       -- 账户持仓市值上限
  max_symbol_weight NUMERIC(6,4),                                         -- 单股权重上限（0-1）
  max_daily_turnover NUMERIC(20,8),                                       -- 当日换手上限
  max_leverage NUMERIC(6,2),                                              -- 最大杠杆
  updated_at TIMESTAMPTZ DEFAULT NOW(),                                   -- 更新时间
  UNIQUE(user_id, account_id)
);
CREATE INDEX idx_risk_limits_account ON risk_limits(account_id);

CREATE TABLE risk_violations (
  id BIGSERIAL PRIMARY KEY,
  account_id BIGINT NOT NULL,
  symbol TEXT,
  ts TIMESTAMPTZ NOT NULL,
  vtype TEXT NOT NULL,                                                    -- 违规类型
  details JSONB,                                                          -- 详情
  run_id BIGINT,                                                          -- 关联运行（虚拟外键）
  created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_risk_violations_account_time ON risk_violations(account_id, ts DESC);

-- 交易日历：交易所开闭市与时段
CREATE TABLE trading_calendar (
  id BIGSERIAL PRIMARY KEY,
  market TEXT NOT NULL,                                                   -- 市场代码（如 CN, HK, US）
  date DATE NOT NULL,
  is_open BOOLEAN NOT NULL DEFAULT TRUE,
  session_open_ts TIMESTAMPTZ,                                            -- 当日开盘时间（UTC）
  session_close_ts TIMESTAMPTZ,                                           -- 当日收盘时间（UTC）
  UNIQUE(market, date)
);
CREATE INDEX idx_calendar_market_date ON trading_calendar(market, date);

-- 汇率：统一换算的汇率时序
CREATE TABLE fx_rates (
  id BIGSERIAL PRIMARY KEY,
  from_currency TEXT NOT NULL,
  to_currency TEXT NOT NULL,
  ts TIMESTAMPTZ NOT NULL,
  rate NUMERIC(20,8) NOT NULL,
  UNIQUE(from_currency, to_currency, ts)
);
CREATE INDEX idx_fx_to_time ON fx_rates(to_currency, ts DESC);

-- 业绩汇总（按日）：看板与审计
CREATE TABLE portfolio_metrics_daily (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT NOT NULL,
  account_id BIGINT NOT NULL,
  date DATE NOT NULL,
  nav NUMERIC(20,8),                                                      -- 净值
  ret NUMERIC(12,6),                                                      -- 当日收益率
  volatility NUMERIC(12,6),                                               -- 波动率（滚动窗口）
  max_drawdown NUMERIC(12,6),                                             -- 回撤（滚动窗口）
  turnover NUMERIC(20,8),                                                 -- 换手率
  UNIQUE(account_id, date)
);
CREATE INDEX idx_metrics_account_date ON portfolio_metrics_daily(account_id, date DESC);

-- 数据质量：导入与刷新异常记录
CREATE TABLE data_quality_issues (
  id BIGSERIAL PRIMARY KEY,
  table_name TEXT NOT NULL,
  field_name TEXT,
  ts TIMESTAMPTZ,
  issue TEXT NOT NULL,
  count BIGINT,
  window TEXT,                                                            -- 影响窗口描述
  created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_dq_table_time ON data_quality_issues(table_name, created_at DESC);

-- 物化视图增量刷新辅助表：记录每账户/Agent最新刷新到的时间戳
CREATE TABLE agent_selected_mv_refresh (
  id BIGSERIAL PRIMARY KEY,
  account_id BIGINT NOT NULL,
  agent_id BIGINT NOT NULL,
  last_ts TIMESTAMPTZ NOT NULL,
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(account_id, agent_id)
);
CREATE INDEX idx_agent_mv_refresh_account ON agent_selected_mv_refresh(account_id, updated_at DESC);
```

## 策略分析（账户维度，周期唯一）
```sql
CREATE TABLE strategy_analysis (
  id BIGSERIAL PRIMARY KEY,                                                -- 策略分析ID
  user_id BIGINT NOT NULL,                                                 -- 用户ID
  account_id BIGINT NOT NULL,                                              -- 账户ID（引用 accounts.id，虚拟外键）
  symbol TEXT NOT NULL,                                                    -- 股票代码（引用 company_info.symbol，虚拟外键）
  period strategy_period NOT NULL,                                         -- 周期（daily/weekly/monthly）
  window_start DATE NOT NULL,                                              -- 窗口开始日期
  signal strategy_signal NOT NULL,                                         -- 策略信号（buy/sell/hold）
  confidence NUMERIC(5,2),                                                 -- 信心度（百分比）
  factors JSONB,                                                           -- 因子说明（JSON）
  stop_loss NUMERIC(18,6),                                                 -- 止损价
  take_profit NUMERIC(18,6),                                               -- 止盈价
  entry_min_price NUMERIC(18,6),                                           -- 建议买入区间下沿
  entry_max_price NUMERIC(18,6),                                           -- 建议买入区间上沿
  exit_min_price NUMERIC(18,6),                                            -- 建议卖出区间下沿
  exit_max_price NUMERIC(18,6),                                            -- 建议卖出区间上沿
  min_buy_qty NUMERIC(20,6),                                               -- 建议最小买入股数（结合市场规则/预算）
  rationale TEXT,                                                          -- 依据/理由
  created_at TIMESTAMPTZ DEFAULT NOW(),                                    -- 创建时间
  UNIQUE(user_id, account_id, symbol, period, window_start)                -- 周期唯一
);
CREATE INDEX idx_strategy_latest ON strategy_analysis(user_id, account_id, symbol, period, window_start DESC); -- 最近策略查询优化
```

## 已实现盈亏（可选）
```sql
CREATE TABLE realized_pnl (
  id BIGSERIAL PRIMARY KEY,                                                -- 已实现盈亏记录ID
  user_id BIGINT NOT NULL,                                                 -- 用户ID
  account_id BIGINT NOT NULL,                                              -- 账户ID（引用 accounts.id，虚拟外键）
  symbol TEXT NOT NULL,                                                    -- 股票代码（引用 company_info.symbol，虚拟外键）
  sell_event_id BIGINT NOT NULL,                                           -- 卖出事件ID（引用 trade_events.id，虚拟外键）
  qty NUMERIC(20,6) NOT NULL,                                              -- 结算数量
  cost_in NUMERIC(20,6) NOT NULL,                                          -- 成本金额
  proceeds NUMERIC(20,6) NOT NULL,                                         -- 卖出收入
  pnl NUMERIC(20,6) NOT NULL,                                              -- 盈亏金额
  cost_method cost_method NOT NULL,                                        -- 成本计算方法（fifo/lifo/avg）
  as_of TIMESTAMPTZ NOT NULL,                                              -- 结算时间
  created_at TIMESTAMPTZ DEFAULT NOW()                                     -- 创建时间
);
CREATE INDEX idx_pnl_account_time ON realized_pnl(account_id, as_of DESC); -- 按账户时间维度查询
```

## 投资建议（账户维度，分配子表）
```sql
CREATE TABLE investment_plans (
  id BIGSERIAL PRIMARY KEY,                                 -- 投资计划ID
  user_id BIGINT NOT NULL,                                  -- 用户ID
  account_id BIGINT NOT NULL,                               -- 账户ID（引用 accounts.id，虚拟外键）
  budget NUMERIC(20,2) NOT NULL,                            -- 预算金额
  plan_scope TEXT DEFAULT 'portfolio',                      -- 计划范围（portfolio|custom）
  notes TEXT,                                               -- 备注
  created_at TIMESTAMPTZ DEFAULT NOW()                      -- 创建时间
);
CREATE INDEX idx_investment_plans_account ON investment_plans(account_id, created_at DESC); -- 按账户与创建时间查询

CREATE TABLE investment_allocations (
  id BIGSERIAL PRIMARY KEY,                                                -- 分配记录ID
  plan_id BIGINT NOT NULL,                                                 -- 计划ID（引用 investment_plans.id，虚拟外键）
  account_id BIGINT NOT NULL,                                              -- 账户ID（引用 accounts.id，虚拟外键）
  symbol TEXT NOT NULL,                                                    -- 股票代码（引用 company_info.symbol，虚拟外键）
  action strategy_signal NOT NULL,                                         -- 动作（buy/sell/hold）
  weight NUMERIC(6,4) NOT NULL CHECK (weight >= 0 AND weight <= 1),        -- 权重（0-1）
  quantity NUMERIC(20,6),                                                  -- 计划数量（可选）
  UNIQUE(plan_id, account_id, symbol)                                      -- 计划+账户+股票唯一
);
CREATE INDEX idx_allocations_plan ON investment_allocations(plan_id); -- 按计划查询分配
```

## 账户偏好（可选）
```sql
CREATE TABLE account_preferences (
  id BIGSERIAL PRIMARY KEY,                                                -- 偏好记录ID
  user_id BIGINT NOT NULL,                                                 -- 用户ID
  account_id BIGINT NOT NULL,                                              -- 账户ID（引用 accounts.id，虚拟外键）
  cost_method cost_method DEFAULT 'fifo',                                  -- 成本方法（默认 fifo）
  base_currency TEXT,                                                      -- 账户基础货币
  updated_at TIMESTAMPTZ DEFAULT NOW()                                     -- 更新时间
);
UNIQUE(user_id, account_id);                                              -- 每账户一条偏好记录
CREATE INDEX idx_account_prefs_account ON account_preferences(account_id); -- 按账户查询偏好
```

## 阶段总结（账户维度，可选 symbol）
```sql
CREATE TABLE strategy_summary (
  id BIGSERIAL PRIMARY KEY,                                                -- 阶段总结ID
  user_id BIGINT NOT NULL,                                                 -- 用户ID
  account_id BIGINT NOT NULL,                                              -- 账户ID（引用 accounts.id，虚拟外键）
  symbol TEXT,                                                             -- 股票代码（可空表示组合级；引用 company_info.symbol，虚拟外键）
  period strategy_period NOT NULL,                                         -- 周期（daily/weekly/monthly）
  period_start DATE NOT NULL,                                              -- 周期开始日期
  period_end DATE NOT NULL,                                                -- 周期结束日期
  pnl NUMERIC(20,6),                                                       -- 收益（可空）
  max_drawdown NUMERIC(9,4),                                               -- 最大回撤
  hit_rate NUMERIC(9,4),                                                   -- 胜率
  risk_exposure NUMERIC(9,4),                                              -- 风险暴露
  notes TEXT,                                                              -- 备注
  created_at TIMESTAMPTZ DEFAULT NOW(),                                    -- 创建时间
  UNIQUE(user_id, account_id, symbol, period, period_start)                -- 周期唯一
);
CREATE INDEX idx_summary_account_period ON strategy_summary(account_id, period, period_start DESC); -- 最近阶段总结查询
```

## 调度与任务
```sql
CREATE TABLE agent_tasks (
  id BIGSERIAL PRIMARY KEY,            -- 任务ID
  user_id BIGINT,                      -- 用户ID（可选）
  account_id BIGINT,                   -- 账户ID（可选）
  scope TEXT,                          -- 任务作用域（portfolio|symbol|account_set）
  task_type TEXT NOT NULL,             -- 任务类型
  status task_status DEFAULT 'pending',-- 任务状态
  payload JSONB,                       -- 任务载荷参数（JSON）
  idempotency_key TEXT UNIQUE,         -- 幂等键（避免重复执行）
  created_at TIMESTAMPTZ DEFAULT NOW(),-- 创建时间
  updated_at TIMESTAMPTZ DEFAULT NOW() -- 更新时间
);
CREATE INDEX idx_tasks_account_status ON agent_tasks(account_id, status); -- 按账户与状态查询
```

## 关键约束与规则映射
- 主键策略：所有表采用数值型主键 `id`（BIGSERIAL/BIGINT）；`company_info` 保留 `symbol` 的唯一约束以支持天然键查询与现有跨表引用（虚拟外键，逐步迁移到 `company_id` 可选）。
- 唯一性：`watchlist(user_id, account_id, symbol)` 与 `holdings(user_id, account_id, symbol)` 保证无重复；策略周期唯一用 `(user_id, account_id, symbol, period, window_start)`。
- 购买即关注：由 Service 在持仓 upsert 时检查 watchlist 是否存在，不存在则插入；DB 不用触发器，减少隐式副作用。
- 双分级：`tier_ai` 仅由分析任务更新；`tier_user` 来自用户操作；前端展示优先 AI 分级。
- 删除策略：不使用数据库外键；由 Service 层编排删除与清理，必要时通过任务异步清理关联数据。
 - 市场规则：`market_rules` 维护每只股票的 `board_lot/tick_size/fractional_allowed/fractional_step/min_order_value`；`strategy_analysis.min_buy_qty` 存储结合账户预算/市场规则计算的建议最小买入股数。
 - 事件账本：所有买卖/费用/分红/拆并等变化写入 `trade_events`；持仓更新由 Service 统一驱动，可按需从事件重建，保持可追溯与审计。
 - 幂等入账：使用 `trade_events.idempotency_key` 保证重复上报不二次入账；`external_ref` 支持与券商回执对账；成本方法偏好来自 `account_preferences`，已实现盈亏可写入 `realized_pnl`。

 - 特征定义：`feature_definitions` 使用 `UNIQUE(name, version)`；`idx_feature_defs_name(name)` 加速按名称检索。
 - 特征值：`feature_values` 使用 `UNIQUE(feature_id, symbol, ts)`；`idempotency_key` 唯一避免重复；`idx_feature_values_symbol_time(symbol, ts DESC)` 与 `idx_feature_values_feature_time(feature_id, ts DESC)` 优化时序查询。
 - 模型版本：`model_versions` 使用 `UNIQUE(name, version)`；`idx_model_versions_name(name)` 加速查询。
 - 策略运行：`agent_runs` 复用枚举 `task_status`；`idx_agent_runs_started(agent_id, started_at DESC)`；与 `model_versions/agent_reference_config` 采用虚拟外键引用。
 - 信号：`agent_signals` 使用 `strategy_signal` 枚举；`UNIQUE(run_id, symbol, ts)` 防重复；`idx_signals_account_symbol_time(account_id, symbol, ts DESC)` 便于账户维度时序检索。
 - 订单意图：`order_intents.side` 使用 `CHECK ('buy','sell')`；`status` 状态流转限定；`idempotency_key` 唯一；`idx_order_intents_account_symbol_time(account_id, symbol, created_at DESC)` 与 `idx_order_intents_status(account_id, status)` 便于下单与对账；最终成交入账 `trade_events`。
 - 风险限额：`risk_limits` 使用 `UNIQUE(user_id, account_id)`；`idx_risk_limits_account(account_id)`；违规表 `risk_violations` 使用 `idx_risk_violations_account_time(account_id, ts DESC)`。
 - 交易日历：`trading_calendar` 使用 `UNIQUE(market, date)`；开闭市时间统一存储为 UTC。
 - 汇率：`fx_rates` 使用 `UNIQUE(from_currency, to_currency, ts)`；`idx_fx_to_time(to_currency, ts DESC)`；用于统一计价与业绩换算。
 - 业绩汇总：`portfolio_metrics_daily` 使用 `UNIQUE(account_id, date)`；`idx_metrics_account_date(account_id, date DESC)` 用于看板查询。
 - 数据质量：`data_quality_issues` 使用 `idx_dq_table_time(table_name, created_at DESC)`；记录刷新/导入异常以支持审计与回溯。
 - 物化视图刷新：`agent_selected_mv_refresh` 使用 `UNIQUE(account_id, agent_id)`；记录最新刷新到的时间戳以支持增量刷新策略。
 - Agent参考数据：`agent_reference_config` 使用枚举 `reference_scope/ref_granularity/reference_source` 与 `idempotency_key` 唯一；`agent_reference_series` 使用 `UNIQUE(config_id, symbol, ts)` 与热点索引；`agent_selected_price_mv` 使用 `idx_agent_selected_mv(account_id, symbol, ts DESC)`。

## 概览查询示例（GET /users/:userId/accounts/:accountId/portfolio/overview）
```sql
-- 选取账户的关注与持仓，并关联公司与最新价格、最新策略摘要
WITH wl AS (
  SELECT w.user_id, w.account_id, w.symbol, w.tier_ai, w.tier_user, w.note
  FROM watchlist w
  WHERE w.user_id = $1 AND w.account_id = $2
), hd AS (
  SELECT h.user_id, h.account_id, h.symbol, h.quantity, h.avg_cost, h.source
  FROM holdings h
  WHERE h.user_id = $1 AND h.account_id = $2
), px AS (
  SELECT DISTINCT ON (p.symbol) p.symbol, p.price, p.volume, p.change_percent, p.as_of
  FROM price_snapshots p
  ORDER BY p.symbol, p.as_of DESC
), sa AS (
  SELECT DISTINCT ON (s.symbol) s.symbol, s.period, s.signal, s.confidence, s.window_start,
         s.entry_min_price, s.entry_max_price, s.exit_min_price, s.exit_max_price, s.min_buy_qty
  FROM strategy_analysis s
  WHERE s.user_id = $1 AND s.account_id = $2
  ORDER BY s.symbol, s.window_start DESC
)
SELECT c.symbol, c.company_name, wl.tier_ai, wl.tier_user, wl.note,
       hd.quantity, hd.avg_cost, hd.source,
       px.price, px.volume, px.change_percent, px.as_of,
       sa.period, sa.signal, sa.confidence, sa.window_start,
       sa.entry_min_price, sa.entry_max_price, sa.exit_min_price, sa.exit_max_price, sa.min_buy_qty
FROM company_info c
LEFT JOIN wl ON wl.symbol = c.symbol
LEFT JOIN hd ON hd.symbol = c.symbol
LEFT JOIN px ON px.symbol = c.symbol
LEFT JOIN sa ON sa.symbol = c.symbol
WHERE wl.symbol IS NOT NULL OR hd.symbol IS NOT NULL;
```

## OCR 导入与幂等建议
- 幂等键：`idempotency_key = sha256(user_id + account_id + symbol + quantity + avg_cost + as_of)`；失败重试不产生重复记录。
- OCR 导入事务：持仓 upsert + 条件策略生成同事务块；策略周期唯一避免重复生成。

## 迁移与数据质量
- 迁移 1：为既有 `watchlist/holdings/strategy_analysis` 增加 `account_id` 与联合唯一约束；历史数据归属默认账户。
- 迁移 2：补充枚举/约束与索引；移除数据库外键与 ON DELETE 策略，采用虚拟外键与服务层清理。
- 数据质量：建立 NOT NULL 与 CHECK 约束，关键列（数量、成本价、预算、权重）设置范围校验。

## MySQL 适配要点（简述）
- ENUM 语法差异：使用 `ENUM` 或 `VARCHAR + CHECK`（MySQL 8 支持 CHECK）。
- 时序查询优化：使用 `INDEX(symbol, as_of DESC)` + 覆盖索引；`DISTINCT ON` 改写为 `JOIN` 最新记录子查询。
- 主键与聚簇索引：统一使用数值型主键（`BIGINT`），更符合 InnoDB 的聚簇索引与页分配策略；避免 UUID 产生的随机写入与页分裂。

---

如需，我可以继续补充表间 ER 图与更完整的示例查询，并在后端 Repository 层提供最小 DDL 初始化脚本。

## 表间 ER 图（Mermaid）

> 说明：为保持数据库层无外键，本图展示的是“虚拟外键”与引用关系，实际约束由 Service 层编排与唯一/索引保证。

```mermaid
erDiagram
  USERS ||--o{ ACCOUNTS : owns
  COMPANY_INFO ||--o{ PRICE_SNAPSHOTS : has
  COMPANY_INFO ||--o{ MARKET_RULES : has

  ACCOUNTS ||--o{ WATCHLIST : tracks
  ACCOUNTS ||--o{ HOLDINGS : holds
  COMPANY_INFO ||--o{ WATCHLIST : references
  COMPANY_INFO ||--o{ HOLDINGS : references

  ACCOUNTS ||--o{ TRADE_EVENTS : logs
  COMPANY_INFO ||--o{ TRADE_EVENTS : references

  ACCOUNTS ||--o{ ACCOUNT_PREFERENCES : prefers
  ACCOUNTS ||--o{ REALIZED_PNL : realizes

  ACCOUNTS ||--o{ AGENT_REFERENCE_CONFIG : config
  AGENT_REFERENCE_CONFIG ||--o{ AGENT_REFERENCE_SERIES : caches
  WATCHLIST ||--o{ AGENT_SELECTED_PRICE_MV : selects
  HOLDINGS ||--o{ AGENT_SELECTED_PRICE_MV : selects

  FEATURE_DEFINITIONS ||--o{ FEATURE_VALUES : produces
  MODEL_VERSIONS ||--o{ AGENT_RUNS : uses
  ACCOUNTS ||--o{ AGENT_RUNS : executes
  AGENT_RUNS ||--o{ AGENT_SIGNALS : generates
  ACCOUNTS ||--o{ AGENT_SIGNALS : owns
  AGENT_SIGNALS ||--o{ ORDER_INTENTS : leads
  ACCOUNTS ||--o{ ORDER_INTENTS : places

  ACCOUNTS ||--o{ RISK_LIMITS : sets
  AGENT_RUNS ||--o{ RISK_VIOLATIONS : flags

  TRADING_CALENDAR ||--o{ PRICE_SNAPSHOTS : tradingDay
  FX_RATES ||--o{ PORTFOLIO_METRICS_DAILY : converts
  ACCOUNTS ||--o{ PORTFOLIO_METRICS_DAILY : measures

  ACCOUNTS ||--o{ DATA_QUALITY_ISSUES : reports
  ACCOUNTS ||--o{ AGENT_SELECTED_MV_REFRESH : tracks

  ACCOUNTS ||--o{ STRATEGY_ANALYSIS : analyzes
  ACCOUNTS ||--o{ STRATEGY_SUMMARY : summarizes

  ACCOUNTS ||--o{ INVESTMENT_PLANS : plans
  INVESTMENT_PLANS ||--o{ INVESTMENT_ALLOCATIONS : allocates

  ACCOUNTS ||--o{ AGENT_TASKS : schedules

  USERS {
    BIGINT id PK
    TEXT email
  }
  ACCOUNTS {
    BIGINT id PK
    BIGINT user_id
  }
  COMPANY_INFO {
    BIGINT id PK
    TEXT symbol UNIQUE
  }
  PRICE_SNAPSHOTS {
    BIGINT id PK
    TEXT symbol
    TIMESTAMPTZ as_of
  }
  WATCHLIST {
    BIGINT id PK
    BIGINT account_id
    TEXT symbol
  }
  HOLDINGS {
    BIGINT id PK
    BIGINT account_id
    TEXT symbol
  }
  TRADE_EVENTS {
    BIGINT id PK
    BIGINT account_id
    TEXT symbol
  }
  FEATURE_DEFINITIONS {
    BIGINT id PK
    TEXT name
    TEXT version
  }
  FEATURE_VALUES {
    BIGINT id PK
    BIGINT feature_id
    TEXT symbol
    TIMESTAMPTZ ts
  }
  MODEL_VERSIONS {
    BIGINT id PK
    TEXT name
    TEXT version
  }
  AGENT_RUNS {
    BIGINT id PK
    BIGINT account_id
    BIGINT model_version_id
  }
  AGENT_SIGNALS {
    BIGINT id PK
    BIGINT account_id
    TEXT symbol
    TIMESTAMPTZ ts
  }
  ORDER_INTENTS {
    BIGINT id PK
    BIGINT account_id
    TEXT symbol
  }
  RISK_LIMITS {
    BIGINT id PK
    BIGINT account_id
  }
  RISK_VIOLATIONS {
    BIGINT id PK
    BIGINT account_id
    TIMESTAMPTZ ts
  }
  TRADING_CALENDAR {
    BIGINT id PK
    TEXT market
    DATE date
  }
  FX_RATES {
    BIGINT id PK
    TEXT from_currency
    TEXT to_currency
    TIMESTAMPTZ ts
  }
  PORTFOLIO_METRICS_DAILY {
    BIGINT id PK
    BIGINT account_id
    DATE date
  }
  DATA_QUALITY_ISSUES {
    BIGINT id PK
    TEXT table_name
  }
  AGENT_SELECTED_MV_REFRESH {
    BIGINT id PK
    BIGINT account_id
    BIGINT agent_id
    TIMESTAMPTZ last_ts
  }
  STRATEGY_ANALYSIS {
    BIGINT id PK
    BIGINT account_id
    TEXT symbol
  }
  STRATEGY_SUMMARY {
    BIGINT id PK
    BIGINT account_id
    TEXT symbol
  }
  ACCOUNT_PREFERENCES {
    BIGINT id PK
    BIGINT account_id
  }
  REALIZED_PNL {
    BIGINT id PK
    BIGINT account_id
    TEXT symbol
  }
  INVESTMENT_PLANS {
    BIGINT id PK
    BIGINT account_id
  }
  INVESTMENT_ALLOCATIONS {
    BIGINT id PK
    BIGINT plan_id
    BIGINT account_id
    TEXT symbol
  }
  AGENT_TASKS {
    BIGINT id PK
    BIGINT account_id
  }
```

> 提示：如需更细字段级 ER（含所有列），可拆分为“账户域/行情域/策略域/Agent域”四张图，并在 README 引用渲染。