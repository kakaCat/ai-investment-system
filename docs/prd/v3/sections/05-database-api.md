# PRD v3 — AI驱动的个人投资管理与复盘系统

**版本**: v3.1
**状态**: 待评审
**日期**: 2025-01-14
**范围**: 多账户投资管理、AI策略生成、策略复盘、资金流动性管理、事件分析与追踪

**v3.1 更新**:
- ✨ 新增完整的事件分析与追踪体系（2.9章节）
  - 四大类事件（政策/公司/市场/行业）、16种子类型
  - AI事件影响分析与预测
  - 事件时间线与可视化
  - 事件与持仓/策略的深度集成
  - 定时任务与智能提醒

---
## 4. 数据库设计

### 3.1 核心表结构

#### users（用户表）
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),

    -- AI Token管理
    ai_tokens_total BIGINT DEFAULT 0,          -- 总购买tokens
    ai_tokens_used BIGINT DEFAULT 0,           -- 已使用tokens
    ai_tokens_remaining BIGINT DEFAULT 0,      -- 剩余tokens

    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_login TIMESTAMPTZ,

    INDEX idx_username (username),
    INDEX idx_email (email)
);
```

#### ai_token_transactions（Token交易记录）
```sql
CREATE TABLE ai_token_transactions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),

    transaction_type VARCHAR(20) NOT NULL,     -- 'purchase', 'consume', 'refund'
    amount BIGINT NOT NULL,                    -- 正数=充值，负数=消耗
    balance_after BIGINT NOT NULL,             -- 交易后余额

    -- 消耗详情（当transaction_type='consume'时）
    related_analysis_id INTEGER,               -- 关联的AI分析记录

    description TEXT,                          -- 描述
    created_at TIMESTAMPTZ DEFAULT NOW(),

    INDEX idx_user_id (user_id),
    INDEX idx_created_at (created_at)
);
```

#### accounts（账户表）
```sql
CREATE TABLE accounts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,

    name VARCHAR(100) NOT NULL,                -- 账户名称
    broker VARCHAR(100),                       -- 券商
    account_number_last4 VARCHAR(4),           -- 账号后四位

    -- 资金管理
    total_capital NUMERIC(15,2) NOT NULL,      -- 总资金
    invested_amount NUMERIC(15,2) DEFAULT 0,   -- 已投资金额（持仓市值）
    liquid_funds NUMERIC(15,2) DEFAULT 0,      -- 流动资金
    frozen_funds NUMERIC(15,2) DEFAULT 0,      -- 冻结资金

    -- 交易费用配置（JSONB存储，便于扩展）
    fee_config JSONB,                          -- 交易费用配置
    /*
    {
      "commission_rate": 0.0003,       // 佣金率（万3）
      "min_commission": 5.0,           // 最低佣金
      "stamp_duty_rate": 0.001,        // 印花税率（卖出）
      "transfer_fee_rate": 0.00001,    // 过户费率
      "other_fees": {
        "regulatory_fee": 0.00002,     // 证管费
        "handling_fee": 0.0000487      // 经手费
      }
    }
    */

    status VARCHAR(20) DEFAULT 'active',       -- 'active', 'archived'
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    INDEX idx_user_id (user_id),
    INDEX idx_status (status)
);
```

#### stocks（股票信息表）- 全局共享
```sql
CREATE TABLE stocks (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) UNIQUE NOT NULL,        -- 股票代码
    name VARCHAR(100) NOT NULL,
    name_cn VARCHAR(100),

    -- 市场信息
    market VARCHAR(20) NOT NULL,               -- 'A', 'HK', 'US', 'JP'等
    exchange VARCHAR(50),                      -- 交易所：'SSE', 'SZSE', 'HKEX', 'NASDAQ'
    sector VARCHAR(50),                        -- 行业
    industry VARCHAR(100),                     -- 细分行业

    -- 交易规则
    lot_size INTEGER DEFAULT 1,                -- 最小交易单位（A股=100，港股不同，美股=1）
    price_limit_up NUMERIC(5,2),               -- 涨幅限制（A股=10.00，港股/美股=NULL）
    price_limit_down NUMERIC(5,2),             -- 跌幅限制
    currency VARCHAR(3) NOT NULL,              -- 'CNY', 'HKD', 'USD'

    -- 交易时间
    trading_hours JSONB,                       -- {open: "09:30", close: "15:00"}

    -- 公司信息
    company_info JSONB,                        -- {business, advantage, risk, ...}
    financial_data JSONB,                      -- {market_cap, pe_ratio, roe, ...}

    added_by INTEGER REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    INDEX idx_symbol (symbol),
    INDEX idx_market (market),
    INDEX idx_sector (sector)
);
```

#### holdings（持仓表）
```sql
CREATE TABLE holdings (
    id SERIAL PRIMARY KEY,
    account_id INTEGER REFERENCES accounts(id) ON DELETE CASCADE,
    symbol VARCHAR(20) REFERENCES stocks(symbol),

    -- 持仓数量
    quantity NUMERIC(15,4) NOT NULL,           -- 持仓数量
    available_quantity NUMERIC(15,4) NOT NULL, -- 可用数量

    -- 成本与价格
    avg_cost NUMERIC(15,4) NOT NULL,           -- 平均成本
    current_price NUMERIC(15,4),               -- 当前价格

    -- 盈亏
    market_value NUMERIC(15,2),                -- 市值 = quantity × current_price
    unrealized_pnl NUMERIC(15,2),              -- 未实现盈亏
    unrealized_pnl_pct NUMERIC(8,4),           -- 盈亏比例
    position_ratio NUMERIC(8,4),               -- 持仓占比（占账户总资金）

    -- 标签
    user_tags JSONB,                           -- ['核心持仓', '长期持有']
    ai_tags JSONB,                             -- ['core_long_term', 'watch_carefully']
    ai_reason TEXT,                            -- AI标签理由

    status VARCHAR(20) DEFAULT 'holding',      -- 'holding', 'closed'
    notes TEXT,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE (account_id, symbol, status),       -- 同一账户同一股票只有一条持仓记录
    INDEX idx_account_id (account_id),
    INDEX idx_symbol (symbol),
    INDEX idx_status (status)
);
```

#### watchlist（关注列表）
```sql
CREATE TABLE watchlist (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    account_id INTEGER REFERENCES accounts(id) ON DELETE CASCADE,
    symbol VARCHAR(20) REFERENCES stocks(symbol),

    target_price NUMERIC(15,4),                -- 目标买入价
    notes TEXT,                                -- 关注理由

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE (user_id, account_id, symbol),
    INDEX idx_user_id (user_id),
    INDEX idx_symbol (symbol)
);
```

#### trade_records（交易记录）
```sql
CREATE TABLE trade_records (
    id SERIAL PRIMARY KEY,
    account_id INTEGER REFERENCES accounts(id) ON DELETE CASCADE,
    symbol VARCHAR(20) REFERENCES stocks(symbol),

    trade_type VARCHAR(20) NOT NULL,           -- 'buy', 'sell', 'dividend', 'split'
    trade_date DATE NOT NULL,
    trade_time TIME,

    quantity NUMERIC(15,4) NOT NULL,           -- 数量
    price NUMERIC(15,4) NOT NULL,              -- 价格
    amount NUMERIC(15,2) NOT NULL,             -- 总金额

    -- 费用
    commission NUMERIC(15,2) DEFAULT 0,        -- 佣金
    stamp_duty NUMERIC(15,2) DEFAULT 0,        -- 印花税
    transfer_fee NUMERIC(15,2) DEFAULT 0,      -- 过户费
    total_fee NUMERIC(15,2) DEFAULT 0,         -- 总费用

    -- 已实现盈亏（卖出时）
    realized_pnl NUMERIC(15,2),
    realized_pnl_pct NUMERIC(8,4),

    notes TEXT,
    idempotency_key VARCHAR(64) UNIQUE,        -- 幂等键

    created_at TIMESTAMPTZ DEFAULT NOW(),

    INDEX idx_account_id (account_id),
    INDEX idx_symbol (symbol),
    INDEX idx_trade_date (trade_date),
    INDEX idx_trade_type (trade_type)
);
```

#### ai_strategies（AI策略记录）
```sql
CREATE TABLE ai_strategies (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    account_id INTEGER REFERENCES accounts(id),
    symbol VARCHAR(20) REFERENCES stocks(symbol),  -- NULL表示整体分析

    strategy_type VARCHAR(50) NOT NULL,        -- 'portfolio', 'single_stock', 'discovery'

    -- 策略内容
    recommendation JSONB NOT NULL,             -- AI建议（结构化）
    /*
    {
      "action": "buy|sell|hold|add|reduce",
      "target_price_min": 62.0,
      "target_price_max": 64.0,
      "stop_loss": 58.0,
      "target_profit": 85.0,
      "suggested_quantity": 500,
      "suggested_amount": 31500,
      "reason": "消费底部，估值修复空间大",
      "risk_level": "medium"
    }
    */

    -- 当时的快照
    holding_snapshot JSONB,                    -- 持仓快照
    price_snapshot JSONB,                      -- 价格快照
    account_snapshot JSONB,                    -- 资金快照

    -- Token消耗
    tokens_used INTEGER NOT NULL,              -- 本次消耗tokens

    -- 执行情况
    is_executed BOOLEAN DEFAULT FALSE,         -- 是否已执行
    executed_at TIMESTAMPTZ,                   -- 执行时间
    execution_notes TEXT,                      -- 执行备注（如：未执行原因）

    created_at TIMESTAMPTZ DEFAULT NOW(),

    INDEX idx_user_id (user_id),
    INDEX idx_symbol (symbol),
    INDEX idx_strategy_type (strategy_type),
    INDEX idx_created_at (created_at),
    INDEX idx_is_executed (is_executed)
);
```

#### strategy_evaluations（策略评估）
```sql
CREATE TABLE strategy_evaluations (
    id SERIAL PRIMARY KEY,
    strategy_id INTEGER REFERENCES ai_strategies(id) ON DELETE CASCADE,

    -- 评估时间
    evaluation_date DATE NOT NULL,

    -- 策略结果
    actual_action VARCHAR(20),                 -- 实际执行的操作
    actual_price NUMERIC(15,4),                -- 实际执行价格
    actual_quantity NUMERIC(15,4),             -- 实际数量

    -- 收益评估
    profit_loss NUMERIC(15,2),                 -- 盈亏金额
    profit_loss_pct NUMERIC(8,4),              -- 盈亏比例

    -- 如果没执行，假设执行的收益
    hypothetical_pnl NUMERIC(15,2),            -- 假设执行的收益

    evaluation_notes TEXT,                     -- 评估备注

    created_at TIMESTAMPTZ DEFAULT NOW(),

    INDEX idx_strategy_id (strategy_id),
    INDEX idx_evaluation_date (evaluation_date)
);
```

#### price_snapshots（价格快照）
```sql
CREATE TABLE price_snapshots (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) REFERENCES stocks(symbol),

    snapshot_time TIMESTAMPTZ NOT NULL,
    snapshot_type VARCHAR(20) DEFAULT 'manual',  -- 'manual', 'scheduled'

    open NUMERIC(15,4),
    high NUMERIC(15,4),
    low NUMERIC(15,4),
    close NUMERIC(15,4),
    volume BIGINT,

    created_at TIMESTAMPTZ DEFAULT NOW(),

    INDEX idx_symbol (symbol),
    INDEX idx_snapshot_time (snapshot_time)
);
```

#### company_events（公司重大事件表）
```sql
CREATE TABLE company_events (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    symbol VARCHAR(20) REFERENCES stocks(symbol),

    -- 事件基本信息
    event_type VARCHAR(50) NOT NULL,           -- 事件类型
    /* event_type枚举值：
       财务类: 'earnings', 'dividend', 'profit_forecast'
       治理类: 'management_change', 'shareholder_change', 'board_resolution'
       业务类: 'major_contract', 'product_launch', 'capacity_expansion'
       市场类: 'merger', 'partnership', 'financing', 'ipo'
       风险类: 'penalty', 'lawsuit', 'fraud', 'warning'
       政策类: 'policy_change', 'subsidy', 'regulation'
    */

    event_date DATE NOT NULL,                  -- 事件发生日期
    event_title VARCHAR(200) NOT NULL,         -- 事件标题
    event_description TEXT,                    -- 事件详情

    -- 影响评估
    price_impact VARCHAR(20),                  -- 'positive', 'negative', 'neutral'
    short_term_impact TEXT,                    -- 短期影响描述
    mid_term_impact TEXT,                      -- 中期影响描述
    long_term_impact TEXT,                     -- 长期影响描述
    ai_score INTEGER,                          -- AI评分 0-100

    -- 股价数据
    price_before NUMERIC(15,4),                -- 事件前股价
    price_after NUMERIC(15,4),                 -- 事件后股价（T+1）
    price_change_pct NUMERIC(8,4),             -- 涨跌幅%

    -- 关联操作
    related_trade_id INTEGER,                  -- 关联的交易记录
    triggered_ai_analysis BOOLEAN DEFAULT FALSE, -- 是否触发了AI分析

    -- 用户备注
    user_notes TEXT,                           -- 用户备注

    -- 提醒设置
    reminder_date DATE,                        -- 提醒日期
    is_reminded BOOLEAN DEFAULT FALSE,         -- 是否已提醒

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    INDEX idx_user_id (user_id),
    INDEX idx_symbol (symbol),
    INDEX idx_event_type (event_type),
    INDEX idx_event_date (event_date),
    INDEX idx_reminder_date (reminder_date)
);
```

#### event_analysis（事件AI分析记录）
```sql
CREATE TABLE event_analysis (
    id SERIAL PRIMARY KEY,
    event_id INTEGER REFERENCES company_events(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id),

    -- AI分析结果
    analysis_content JSONB NOT NULL,           -- AI分析内容（结构化）
    /*
    {
      "short_term": {
        "prediction": "下跌5-8%",
        "reason": "业绩低于预期",
        "action": "观望"
      },
      "mid_term": {
        "prediction": "Q4改善",
        "reason": "消费旺季",
        "action": "回调后加仓"
      },
      "long_term": {
        "trend": "高端化转型",
        "risk": "成本压力",
        "action": "长期持有"
      },
      "scores": {
        "financial_health": 75,
        "growth": 60,
        "valuation": 70,
        "overall": 65
      }
    }
    */

    tokens_used INTEGER NOT NULL,              -- 消耗的tokens

    created_at TIMESTAMPTZ DEFAULT NOW(),

    INDEX idx_event_id (event_id),
    INDEX idx_created_at (created_at)
);
```

#### macro_events（宏观政策事件表）
```sql
CREATE TABLE macro_events (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,

    -- 事件基本信息
    event_category VARCHAR(50) NOT NULL,       -- 事件大类
    /* event_category枚举值：
       'monetary_policy' - 货币政策
       'economic_data' - 经济数据
       'fiscal_policy' - 财政政策
       'trade_policy' - 贸易政策
       'regulatory_policy' - 监管政策
    */

    event_type VARCHAR(50) NOT NULL,           -- 具体事件类型
    /* event_type示例：
       货币政策: 'fed_rate_hike', 'fed_rate_cut', 'pboc_rrr_cut', 'lpr_adjustment'
       经济数据: 'us_cpi', 'us_ppi', 'us_nonfarm', 'cn_cpi', 'cn_pmi', 'cn_gdp'
       财政政策: 'stimulus_plan', 'tax_policy'
       贸易政策: 'trade_negotiation', 'tariff'
       监管政策: 'industry_regulation', 'antitrust'
    */

    country VARCHAR(20) NOT NULL,              -- 国家/地区：'US', 'CN', 'EU', 'JP'等
    event_date DATE NOT NULL,                  -- 事件发生日期
    event_title VARCHAR(200) NOT NULL,         -- 事件标题
    event_description TEXT,                    -- 事件详情

    -- 数据具体值（针对经济数据）
    data_value NUMERIC(15,4),                  -- 数据值（如CPI 3.7%）
    data_previous NUMERIC(15,4),               -- 前值
    data_expected NUMERIC(15,4),               -- 预期值
    data_unit VARCHAR(20),                     -- 单位：'%', 'bp', '万人'等

    -- 市场影响
    impact_scope VARCHAR(50),                  -- 影响范围：'global', 'regional', 'domestic'
    affected_markets JSONB,                    -- 受影响市场及涨跌幅
    /*
    {
      "US": {"sp500": -1.5, "nasdaq": -2.3},
      "HK": {"hsi": -1.8, "hscei": -2.5},
      "CN": {"sse": -0.8, "szse": -1.2}
    }
    */

    affected_sectors JSONB,                    -- 受影响行业
    /*
    {
      "technology": {"impact": "negative", "change_pct": -2.5},
      "financials": {"impact": "positive", "change_pct": 1.5},
      "consumer": {"impact": "neutral", "change_pct": -0.5},
      "realestate": {"impact": "negative", "change_pct": -3.0}
    }
    */

    -- 对持仓的影响
    portfolio_impact JSONB,                    -- 对我的持仓的影响
    /*
    {
      "overall_impact": -1.2,
      "stocks": {
        "600600": {"impact": "neutral", "change_pct": -0.5, "notes": "国内为主"},
        "00700": {"impact": "negative", "change_pct": -2.5, "notes": "港股科技股"}
      }
    }
    */

    -- 我的应对
    my_response TEXT,                          -- 我的应对措施
    related_trade_ids TEXT[],                  -- 关联的交易ID数组
    triggered_ai_analysis BOOLEAN DEFAULT FALSE,

    -- 提醒设置
    reminder_date DATE,                        -- 提醒日期
    is_reminded BOOLEAN DEFAULT FALSE,
    importance_level INTEGER,                  -- 重要性：1-5星

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    INDEX idx_user_id (user_id),
    INDEX idx_event_category (event_category),
    INDEX idx_event_type (event_type),
    INDEX idx_country (country),
    INDEX idx_event_date (event_date),
    INDEX idx_reminder_date (reminder_date)
);
```

#### macro_event_analysis（宏观事件AI分析）
```sql
CREATE TABLE macro_event_analysis (
    id SERIAL PRIMARY KEY,
    macro_event_id INTEGER REFERENCES macro_events(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id),

    -- AI分析结果
    analysis_content JSONB NOT NULL,
    /*
    {
      "market_impact": {
        "US": {"forecast": "-2%~-3%", "reason": "高估值压力"},
        "HK": {"forecast": "-1.5%~-2%", "reason": "资金外流"},
        "CN": {"forecast": "-0.5%~-1%", "reason": "人民币贬值压力"}
      },
      "sector_impact": {
        "technology": {"impact": "negative", "forecast": -2.5},
        "financials": {"impact": "positive", "forecast": 1.5},
        "consumer": {"impact": "neutral", "forecast": -0.5}
      },
      "portfolio_impact": {
        "600600": {
          "impact_level": "minor_negative",
          "forecast": -0.5,
          "reason": "主要市场在中国",
          "recommendation": "继续持有"
        },
        "00700": {
          "impact_level": "major_negative",
          "forecast": -2.5,
          "reason": "港股科技股承压",
          "recommendation": "考虑减仓10-20%"
        }
      },
      "strategy_recommendations": {
        "short_term": ["减仓港股科技股", "增持防御板块"],
        "mid_term": ["等待暂停加息信号", "关注国内政策"],
        "risk_control": ["降低Beta", "提高现金仓位"]
      },
      "portfolio_forecast": {
        "before_action": "-1.5%~-2%",
        "after_action": "-0.8%~-1%"
      }
    }
    */

    tokens_used INTEGER NOT NULL,

    created_at TIMESTAMPTZ DEFAULT NOW(),

    INDEX idx_macro_event_id (macro_event_id),
    INDEX idx_created_at (created_at)
);
```

#### account_fund_records（账户资金变动记录）
```sql
CREATE TABLE account_fund_records (
    id SERIAL PRIMARY KEY,
    account_id INTEGER REFERENCES accounts(id) ON DELETE CASCADE,

    record_type VARCHAR(20) NOT NULL,          -- 'deposit', 'withdraw', 'buy', 'sell'
    amount NUMERIC(15,2) NOT NULL,             -- 变动金额（正=入金，负=出金）

    balance_before NUMERIC(15,2),              -- 变动前余额
    balance_after NUMERIC(15,2),               -- 变动后余额

    related_trade_id INTEGER,                  -- 关联的交易记录
    notes TEXT,

    created_at TIMESTAMPTZ DEFAULT NOW(),

    INDEX idx_account_id (account_id),
    INDEX idx_record_type (record_type),
    INDEX idx_created_at (created_at)
);
```

---

## 4. API设计

### 4.1 认证相关
- `POST /api/auth/register` - 注册
- `POST /api/auth/login` - 登录
- `GET /api/auth/me` - 获取当前用户信息
- `PUT /api/auth/password` - 修改密码

### 4.2 AI Token管理
- `GET /api/tokens/balance` - 获取Token余额
- `POST /api/tokens/purchase` - 购买Token
- `GET /api/tokens/transactions` - Token交易记录

### 4.3 账户管理
- `GET /api/accounts` - 获取所有账户
- `POST /api/accounts` - 创建账户
- `GET /api/accounts/:id` - 获取账户详情
- `PUT /api/accounts/:id` - 更新账户
- `DELETE /api/accounts/:id` - 删除账户
- `GET /api/accounts/:id/summary` - 账户汇总（资金、持仓）
- `PUT /api/accounts/:id/fee-config` - 更新交易费用配置
  ```json
  Request: {
    "commission_rate": 0.0003,
    "min_commission": 5.0,
    "stamp_duty_rate": 0.001,
    "transfer_fee_rate": 0.00001,
    "other_fees": {
      "regulatory_fee": 0.00002,
      "handling_fee": 0.0000487
    }
  }
  ```
- `POST /api/accounts/:id/calculate-fee` - 预估交易费用
  ```json
  Request: {
    "trade_type": "buy",
    "quantity": 1000,
    "price": 65.8
  }
  Response: {
    "amount": 65800,
    "commission": 19.74,
    "stamp_duty": 0,
    "transfer_fee": 0.66,
    "other_fees": 3.53,
    "total_fee": 23.93,
    "total_cost": 65823.93
  }
  ```

### 4.4 股票信息
- `GET /api/stocks` - 获取股票列表（分页、搜索、按市场筛选）
- `POST /api/stocks` - 添加新股票
- `GET /api/stocks/:symbol` - 获取股票详情
- `PUT /api/stocks/:symbol` - 更新股票信息

### 4.5 持仓管理
- `GET /api/accounts/:id/holdings` - 获取账户持仓
- `POST /api/accounts/:id/holdings` - 添加持仓
- `PUT /api/holdings/:id` - 更新持仓
- `DELETE /api/holdings/:id` - 删除持仓
- `POST /api/holdings/refresh-price` - 刷新价格（批量）
- `POST /api/holdings/:id/refresh-price` - 刷新单只股票价格

### 4.6 交易记录
- `GET /api/accounts/:id/trades` - 获取交易记录
- `POST /api/accounts/:id/trades` - 添加交易记录（自动计算费用）
  ```json
  Request: {
    "symbol": "600600",
    "trade_type": "buy",
    "quantity": 1000,
    "price": 65.8,
    "trade_date": "2025-01-13",
    "notes": "建仓"
  }
  Response: {
    "id": 123,
    "symbol": "600600",
    "quantity": 1000,
    "price": 65.8,
    "amount": 65800,
    "commission": 19.74,        // 自动计算
    "stamp_duty": 0,            // 买入无印花税
    "transfer_fee": 0.66,       // 自动计算
    "total_fee": 23.93,         // 自动计算
    "total_cost": 65823.93,     // 成交金额 + 总费用
    "created_at": "2025-01-13T10:30:00Z"
  }
  ```
- `POST /api/accounts/:id/trades/import` - 批量导入交易记录
- `GET /api/accounts/:id/trades/fees-summary` - 费用统计
  ```json
  Response: {
    "period": "2025-01",
    "total_commission": 1234.56,
    "total_stamp_duty": 876.54,
    "total_transfer_fee": 12.34,
    "total_fees": 2123.44,
    "trade_count": 48
  }
  ```

### 4.7 关注列表
- `GET /api/watchlist` - 获取关注列表
- `POST /api/watchlist` - 添加关注
- `DELETE /api/watchlist/:id` - 移除关注

### 4.8 AI分析
- `POST /api/ai/analyze/portfolio` - 分析整体持仓
  ```json
  Request: {
    "account_id": 1,
    "depth": "detailed"
  }
  Response: {
    "tokens_used": 2500,
    "tokens_remaining": 97500,
    "analysis": {
      "account_summary": {...},
      "holdings_analysis": [...],
      "fund_usage_advice": {...},
      "portfolio_advice": {...}
    }
  }
  ```

- `POST /api/ai/analyze/stock` - 分析单只股票
  ```json
  Request: {
    "symbol": "600600",
    "account_id": 1
  }
  Response: {
    "tokens_used": 5000,
    "tokens_remaining": 92500,
    "analysis": {
      "my_position": {...},
      "fundamental": {...},
      "technical": {...},
      "recommendation": {...}
    }
  }
  ```

- `POST /api/ai/discover` - 发现投资机会
  ```json
  Request: {
    "account_id": 1,
    "sector": "科技",
    "risk_preference": "稳健",
    "max_investment": 50000
  }
  Response: {
    "tokens_used": 3000,
    "tokens_remaining": 89500,
    "recommendations": [...]
  }
  ```

### 4.9 策略管理
- `GET /api/strategies` - 获取策略列表（支持筛选、分页）
- `GET /api/strategies/:id` - 获取策略详情
- `PUT /api/strategies/:id/execution` - 更新策略执行情况
  ```json
  {
    "is_executed": true,
    "executed_at": "2025-11-05T10:30:00Z",
    "execution_notes": "按建议在63元买入500股"
  }
  ```

### 4.10 策略复盘
- `GET /api/review/strategies` - 策略回顾看板（列表）
- `GET /api/review/summary` - 复盘汇总
  ```json
  {
    "period": "weekly",
    "date_range": ["2025-11-01", "2025-11-07"],
    "execution_rate": {...},
    "accuracy_rate": {...},
    "fund_utilization": {...},
    "improvements": [...]
  }
  ```
- `POST /api/review/evaluate/:strategyId` - 评估策略效果

### 4.11 公司事件管理
- `GET /api/stocks/:symbol/events` - 获取股票的事件列表
- `POST /api/stocks/:symbol/events` - 添加重大事件
  ```json
  Request: {
    "event_type": "earnings",
    "event_date": "2025-10-29",
    "event_title": "Q3财报：营收+5%，净利润-3%",
    "event_description": "营收120亿元(+5%),净利润8.5亿元(-3%),毛利率42%(-1.2pct)",
    "price_impact": "negative",
    "price_before": 68.5,
    "price_after": 65.8,
    "user_notes": "业绩略低于预期，等待Q4表现",
    "trigger_ai_analysis": true
  }
  Response: {
    "id": 456,
    "event_type": "earnings",
    "event_title": "Q3财报：营收+5%，净利润-3%",
    "price_change_pct": -3.94,
    "ai_analysis": {
      "short_term": {...},
      "mid_term": {...},
      "long_term": {...},
      "scores": {...}
    },
    "tokens_used": 3500,
    "created_at": "2025-10-29T15:00:00Z"
  }
  ```
- `PUT /api/events/:id` - 更新事件信息
- `DELETE /api/events/:id` - 删除事件
- `GET /api/events/:id` - 获取事件详情（含AI分析）
- `POST /api/events/:id/analyze` - 对已有事件进行AI分析
  ```json
  Response: {
    "analysis": {
      "short_term": {
        "prediction": "下跌5-8%",
        "reason": "业绩低于预期，市场情绪偏负面",
        "action": "观望，等待回调至62-64元"
      },
      "mid_term": {
        "prediction": "Q4业绩有望改善",
        "reason": "进入消费旺季，高端产品放量",
        "action": "回调后可考虑加仓"
      },
      "long_term": {
        "trend": "高端化转型继续推进",
        "risk": "原材料成本压力持续",
        "action": "长期持有，关注成本控制进展"
      },
      "scores": {
        "financial_health": 75,
        "growth": 60,
        "valuation": 70,
        "overall": 65
      }
    },
    "tokens_used": 3500
  }
  ```
- `GET /api/events/timeline` - 事件时间线（多只股票）
  ```json
  Request: {
    "symbols": ["600600", "00700"],
    "start_date": "2025-01-01",
    "end_date": "2025-12-31",
    "event_types": ["earnings", "dividend"]
  }
  Response: {
    "events": [
      {
        "date": "2025-10-29",
        "symbol": "600600",
        "name": "青岛啤酒",
        "event_type": "earnings",
        "event_title": "Q3财报",
        "price_impact": "negative",
        "price_change_pct": -3.94,
        "related_trade_id": null
      },
      ...
    ]
  }
  ```
- `GET /api/events/statistics` - 事件统计分析
  ```json
  Request: {
    "symbol": "600600",
    "period": "1year"
  }
  Response: {
    "symbol": "600600",
    "total_events": 9,
    "by_type": {
      "earnings": {"count": 4, "avg_impact": -1.2},
      "dividend": {"count": 2, "avg_impact": -2.0},
      "management_change": {"count": 1, "avg_impact": 3.5},
      "product_launch": {"count": 1, "avg_impact": 2.0},
      "shareholder_change": {"count": 1, "avg_impact": 3.0}
    },
    "user_response_rate": 22,
    "trades_after_events": 2
  }
  ```
- `GET /api/events/reminders` - 获取待提醒事件
- `PUT /api/events/:id/remind` - 设置事件提醒

### 4.12 宏观事件管理
- `GET /api/macro-events` - 获取宏观事件列表
  ```json
  Request: {
    "category": "monetary_policy",
    "country": "US",
    "start_date": "2025-01-01",
    "end_date": "2025-12-31"
  }
  ```
- `POST /api/macro-events` - 添加宏观事件
  ```json
  Request: {
    "event_category": "monetary_policy",
    "event_type": "fed_rate_hike",
    "country": "US",
    "event_date": "2025-11-07",
    "event_title": "美联储加息25个基点至5.25%-5.50%",
    "event_description": "加息25bp，投票11-1，鲍威尔表态通胀需进一步降温",
    "data_value": 5.375,
    "data_previous": 5.125,
    "data_unit": "%",
    "impact_scope": "global",
    "affected_markets": {
      "US": {"sp500": -1.5, "nasdaq": -2.3},
      "HK": {"hsi": -1.8},
      "CN": {"sse": -0.8}
    },
    "affected_sectors": {
      "technology": {"impact": "negative", "change_pct": -2.5},
      "financials": {"impact": "positive", "change_pct": 1.5}
    },
    "my_response": "减仓腾讯控股",
    "related_trade_ids": ["123"],
    "trigger_ai_analysis": true,
    "importance_level": 5
  }
  Response: {
    "id": 789,
    "event_title": "美联储加息25个基点至5.25%-5.50%",
    "ai_analysis": {
      "market_impact": {...},
      "sector_impact": {...},
      "portfolio_impact": {...}
    },
    "tokens_used": 4500,
    "created_at": "2025-11-07T15:00:00Z"
  }
  ```
- `PUT /api/macro-events/:id` - 更新宏观事件
- `DELETE /api/macro-events/:id` - 删除宏观事件
- `GET /api/macro-events/:id` - 获取事件详情（含AI分析）
- `POST /api/macro-events/:id/analyze` - AI分析宏观事件影响
  ```json
  Response: {
    "market_impact": {
      "US": {"forecast": "-2%~-3%", "reason": "高估值压力"},
      "HK": {"forecast": "-1.5%~-2%", "reason": "资金外流"},
      "CN": {"forecast": "-0.5%~-1%", "reason": "人民币贬值"}
    },
    "sector_impact": {
      "technology": {"impact": "negative", "forecast": -2.5, "reason": "融资成本上升"},
      "financials": {"impact": "positive", "forecast": 1.5, "reason": "利差扩大"}
    },
    "portfolio_impact": {
      "600600": {
        "impact_level": "minor_negative",
        "forecast": -0.5,
        "reason": "主要市场在中国，美联储影响有限",
        "recommendation": "继续持有，影响可忽略"
      },
      "00700": {
        "impact_level": "major_negative",
        "forecast": -2.5,
        "reason": "港股科技股，高估值压力大",
        "recommendation": "考虑减仓10-20%，降低风险敞口"
      }
    },
    "strategy_recommendations": {
      "short_term": ["减仓港股科技股（腾讯）10-20%", "增持防御性板块"],
      "mid_term": ["等待暂停加息信号", "关注国内反向政策"],
      "risk_control": ["降低组合Beta值", "提高现金仓位至40%"]
    },
    "portfolio_forecast": {
      "before_action": "-1.5%~-2%",
      "after_action": "-0.8%~-1%"
    },
    "tokens_used": 4500
  }
  ```
- `GET /api/macro-events/timeline` - 宏观事件时间线
  ```json
  Request: {
    "categories": ["monetary_policy", "economic_data"],
    "countries": ["US", "CN"],
    "start_date": "2025-01-01",
    "end_date": "2025-12-31"
  }
  Response: {
    "events": [
      {
        "date": "2025-11-07",
        "country": "US",
        "category": "monetary_policy",
        "event_type": "fed_rate_hike",
        "event_title": "美联储加息25bp",
        "importance_level": 5,
        "market_impact": {"US": -1.5, "HK": -1.8, "CN": -0.8},
        "my_response": "减仓腾讯控股",
        "related_trades_count": 1
      },
      ...
    ]
  }
  ```
- `GET /api/macro-events/statistics` - 宏观事件统计分析
  ```json
  Request: {
    "period": "1year"
  }
  Response: {
    "total_events": 23,
    "by_category": {
      "monetary_policy": {"count": 5, "avg_portfolio_impact": -1.2},
      "economic_data": {"count": 12, "avg_portfolio_impact": -0.3},
      "fiscal_policy": {"count": 3, "avg_portfolio_impact": 0.8},
      "trade_policy": {"count": 2, "avg_portfolio_impact": -0.8},
      "regulatory_policy": {"count": 1, "avg_portfolio_impact": -1.5}
    },
    "portfolio_sensitivity": {
      "us_monetary_policy": -1.2,
      "cn_monetary_policy": 1.8,
      "us_cpi": -0.5,
      "cn_gdp": 0.6
    },
    "my_response_rate": 35,
    "trades_after_events": 8
  }
  ```
- `GET /api/macro-events/calendar` - 重要数据发布日历
  ```json
  Request: {
    "month": "2025-11",
    "importance_level": 4
  }
  Response: {
    "upcoming_events": [
      {
        "date": "2025-11-14",
        "time": "21:30",
        "country": "US",
        "event_type": "us_cpi",
        "event_title": "美国10月CPI数据",
        "importance_level": 5,
        "expected_value": 3.3,
        "previous_value": 3.7,
        "unit": "%",
        "market_consensus": "通胀回落",
        "reminder_set": true
      },
      {
        "date": "2025-11-22",
        "time": "03:00",
        "country": "US",
        "event_type": "fed_minutes",
        "event_title": "美联储11月会议纪要",
        "importance_level": 4,
        "reminder_set": false
      },
      ...
    ]
  }
  ```
- `GET /api/macro-events/impact-backtest` - 历史影响回测
  ```json
  Request: {
    "event_type": "fed_rate_hike",
    "lookback_period": "2years"
  }
  Response: {
    "event_type": "fed_rate_hike",
    "occurrence_count": 8,
    "avg_market_impact": {
      "US": -1.8,
      "HK": -1.5,
      "CN": -0.6
    },
    "my_portfolio_impact": {
      "avg": -1.2,
      "max": -2.5,
      "min": -0.3,
      "beta": 1.2
    },
    "best_performing_stocks": [
      {"symbol": "600036", "name": "招商银行", "avg_change": 1.2}
    ],
    "worst_performing_stocks": [
      {"symbol": "00700", "name": "腾讯控股", "avg_change": -2.8}
    ],
    "recommendations": [
      "降低组合对美联储政策的敏感度（Beta 1.2 → 1.0）",
      "加息周期降低仓位或增持防御股",
      "提前减仓高估值科技股"
    ]
  }
  ```
- `PUT /api/macro-events/:id/remind` - 设置事件提醒

---

