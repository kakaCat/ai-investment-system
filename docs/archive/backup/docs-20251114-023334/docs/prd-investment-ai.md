# PRD — AI驱动的个人投资管理平台

**版本**: v1.0
**状态**: 草案待讨论
**日期**: 2025-01-13
**范围**: 多用户投资管理、AI投资建议、持仓分析、策略生成与追踪

---

## 1. 背景与目标

### 1.1 背景
个人投资者在管理多个账户、追踪多只股票时面临以下痛点：
- 信息分散：多个券商账户、自选股列表难以统一管理
- 决策困难：缺乏专业分析工具，难以判断买卖时机
- 策略混乱：投资理由不清晰，容易冲动交易
- 跟踪困难：持仓盈亏、操作历史难以系统化追踪

### 1.2 目标
构建一个AI驱动的个人投资管理平台，实现：
1. **统一管理**：多账户持仓、关注股票的集中管理
2. **AI赋能**：智能发现投资机会、分析持仓、生成操作建议
3. **策略驱动**：每笔投资都有明确策略，可追溯、可复盘
4. **可视化**：直观的业绩看板、持仓分析图表
5. **便捷高效**：快速导入持仓、一键AI分析、移动端友好

### 1.3 目标用户
- **主要用户**：有一定投资经验的个人投资者（1-5个账户，10-50只股票）
- **次要用户**：投资小白（需要AI指导和学习）
- **潜在用户**：家庭理财管理者（管理家庭成员的多个账户）

---

## 2. 核心功能需求

### 2.1 用户与账户管理

#### 2.1.1 用户注册与登录
- **注册方式**：邮箱注册、手机号注册（可选）
- **登录方式**：用户名/邮箱 + 密码、第三方登录（可选）
- **安全要求**：密码加密存储（bcrypt）、JWT Token认证、会话管理

#### 2.1.2 账户管理
- **账户类型**：
  - 券商账户（华泰、中信、东方财富等）
  - 虚拟账户（雪球组合、自建组合）
- **账户信息**：账户名称、券商、账号后四位、初始资金、创建时间
- **账户操作**：新增、编辑、删除、归档

#### 2.1.3 多用户支持
- 每个用户独立数据空间
- 支持账户间的数据隔离
- 可选：支持家庭账户共享（Phase 2）

---

### 2.2 股票信息库管理

#### 2.2.1 股票基础信息（全局共享）
- **基本信息**：代码、名称、市场、行业、市值
- **公司信息**：
  - 主营业务
  - 核心竞争力
  - 主要风险
  - 财务指标（市盈率、ROE、负债率等）
- **元数据**：添加人、添加时间、最后更新时间

#### 2.2.2 股票库操作
- **添加股票**：
  - 手动录入（表单填写）
  - AI辅助填充（输入股票代码，AI自动获取公司信息）
- **编辑股票**：更新公司信息、财务数据
- **查看股票**：详情页展示完整信息
- **搜索股票**：按代码、名称、行业搜索

#### 2.2.3 数据来源
- **MCP服务**（主要数据源）：通过 Model Context Protocol 统一抓取股票数据
  - 股票基础信息（代码、名称、行业、市值）
  - 公司信息（主营业务、财务指标）
  - 实时/历史行情数据
  - 财经新闻、公告（可选）
- **用户手动维护**：补充或修正MCP抓取的数据
- **优势**：
  - 统一的数据访问协议，无需硬编码API
  - 可插拔的数据源（切换不同MCP服务器）
  - AI可直接通过MCP获取最新数据进行分析
  - 支持多市场数据源（A股/美股/港股）

---

### 2.3 持仓与关注管理

#### 2.3.1 持仓管理
- **持仓信息**：
  - 股票代码、名称
  - 持仓数量
  - 平均成本
  - 当前价格（自动更新或手动输入）
  - 未实现盈亏（自动计算）
  - 持仓占比
- **持仓操作**：
  - 手动添加
  - 批量导入（CSV文件）
  - OCR导入（上传持仓截图，AI识别）
  - 编辑、删除
- **持仓状态**：持有中、已清仓（历史记录）

#### 2.3.2 关注列表
- **分类**：
  - 关注中（watching）：已研究，等待买入时机
  - 感兴趣（interested）：初步了解，需进一步研究
- **关注信息**：
  - 股票代码、名称
  - 目标价位
  - 关注理由
  - 添加时间
- **关注操作**：添加、移除、转为持仓

#### 2.3.3 智能标签系统
- **用户标签**（手动）：
  - 核心持仓、长期持有、短线交易、试验仓位等
- **AI标签**（自动生成）：
  - 长期持有（core_long_term）
  - 注意操作（watch_carefully）
  - 建议减仓（reduce_risk）
  - 成长潜力（growth_potential）
  - 价值机会（value_opportunity）
- **标签应用**：
  - 筛选和分组
  - AI分析时作为上下文
  - 看板展示

---

### 2.4 AI投资机会发现

#### 2.4.1 功能描述
用户提出投资需求（如"推荐科技股"），AI分析市场后推荐投资机会。

#### 2.4.2 交互流程
```
用户输入需求
  ↓
选择筛选条件（可选）
  - 行业：科技、医疗、消费等
  - 风险偏好：保守、稳健、激进
  - 市值范围：大盘、中盘、小盘
  - 投资期限：短期、中期、长期
  ↓
AI分析
  - 基于当前市场环境
  - 结合用户已有持仓（避免重复）
  - 考虑风险分散
  ↓
推荐列表（3-5只股票）
  - 股票代码、名称
  - AI评分（0-100）
  - 推荐理由（1-2句）
  - 风险等级
  - 建议仓位比例
  ↓
用户选择感兴趣的股票
  ↓
AI生成详细投资策略
  - 投资逻辑
  - 买入价位区间
  - 止损位
  - 目标价
  - 风险提示
  ↓
保存到策略库 + 添加到关注列表
```

#### 2.4.3 AI分析要素
- 基本面：财务指标、行业地位、成长性
- 技术面：趋势、支撑阻力位、量价关系
- 估值：市盈率、PEG、市净率
- 市场情绪：近期新闻、机构观点
- 风险因素：行业风险、公司风险、市场风险

---

### 2.5 AI持仓分析与操作建议

#### 2.5.1 整体持仓分析
**触发方式**：
- 用户主动点击"分析我的持仓"
- 定时分析（每日/每周）
- 重大市场事件触发

**分析内容**：
```
【账户概览】
- 总市值
- 总成本
- 未实现盈亏（金额 + 百分比）
- 已实现盈亏（可选）

【持仓明细分析】
对每只股票：
  - 当前价格 vs 成本价
  - 盈亏情况
  - AI操作建议：
    - 持有（hold）
    - 加仓（increase）+ 建议加仓比例
    - 减仓（reduce）+ 建议减仓比例
    - 清仓（sell）
  - 建议理由（基于基本面、技术面、市场环境）
  - 目标价、止损位

【组合层面建议】
  - 行业配置分析（是否过于集中）
  - 风险评估（波动率、回撤风险）
  - 再平衡建议（调整仓位配置）
  - 新机会提示（建议增加哪些板块）
```

#### 2.5.2 单只股票深度分析
**触发方式**：
- 点击持仓列表中的某只股票
- 输入"分析AAPL"

**分析内容**：
```
【我的持仓情况】
- 持有数量、成本、当前价、盈亏

【公司基本面】（从股票库读取）
- 主营业务、竞争优势
- 财务状况
- 近期动态

【AI深度分析】
- 基本面评分（0-100）
- 技术面分析（趋势、关键价位）
- 估值分析（便宜/合理/贵）
- 催化剂与风险

【投资建议】
- 当前阶段：持有/加仓/减仓/观望
- 具体操作计划：
  - 如果跌到X元 → 加仓Y%
  - 如果涨到Z元 → 止盈M%
  - 止损位：W元
- 长期观点：看好/中性/看空

【风险提示】
- 近期需要关注的事件
- 潜在风险因素
```

---

### 2.6 投资策略生成与管理

#### 2.6.1 策略生成
**触发场景**：
1. 发现投资机会时自动生成
2. 用户主动请求"为AAPL生成投资策略"
3. 买入持仓时补充生成

**策略内容**（Markdown格式）：
```markdown
# AAPL 投资策略

**生成时间**: 2025-01-13
**策略类型**: 长期价值投资
**风险等级**: 中

## 投资逻辑
- 核心观点：iPhone业务稳健，服务业务高速增长，生态系统护城河深厚
- 催化剂：新产品发布、AI功能整合、服务业务增长超预期

## 操作计划
- **建仓价位**: $175 - $180
- **加仓条件**: 回调至$170以下，基本面无恶化
- **止损位**: $165（-10%）
- **目标价**:
  - 第一目标：$200（+15%）
  - 第二目标：$220（+25%）
- **建议仓位**: 总资金的10-15%

## 风险与应对
- **风险1**: iPhone销量不及预期 → 关注季度财报，销量下滑超10%则减仓
- **风险2**: 监管压力 → 关注反垄断进展
- **风险3**: 宏观经济衰退 → 美联储政策转向时评估

## 执行追踪
- [ ] 已建仓 @ $178（2025-01-13）
- [ ] 第一目标价达成
- [ ] 止损触发检查
```

#### 2.6.2 策略管理
- **策略列表**：显示所有已保存的策略
- **策略状态**：
  - 执行中（active）
  - 已完成（completed）：达到目标或止损
  - 已归档（archived）
- **策略更新**：
  - 手动编辑
  - AI定期复盘更新（如季度财报后）
- **策略执行追踪**：
  - 记录实际买入/卖出操作
  - 对比策略与实际执行的差异
  - 复盘总结

---

### 2.7 数据导入与同步

#### 2.7.1 持仓导入方式
1. **CSV文件导入**
   - 下载券商持仓CSV
   - 上传到平台
   - 映射字段（股票代码、数量、成本）
   - 幂等导入（避免重复）

2. **OCR图片识别**（推荐）
   - 截图券商持仓页面
   - 上传图片
   - AI识别股票代码、数量、成本
   - 确认后导入

3. **手动录入**
   - 表单逐条添加

#### 2.7.2 价格更新
- **手动更新**：用户点击"刷新价格"
- **自动更新**：
  - 定时任务（每小时/每日）
  - 调用行情API获取最新价格
  - 更新持仓表的current_price字段
- **数据源**：
  - 优先：免费API（Yahoo Finance / Alpha Vantage）
  - 备选：付费API（如需实时行情）

#### 2.7.3 幂等性保证
- 所有导入操作使用幂等键（idempotency_key）
- 规则：`hash(account_id + symbol + quantity + avg_cost + import_date)`
- 重复导入时自动去重或更新

---

### 2.8 业绩与数据可视化

#### 2.8.1 仪表板（Dashboard）
**总览卡片**：
- 总资产
- 总盈亏（金额 + 百分比）
- 持仓股票数
- 今日盈亏

**AI今日提醒**：
- 高优先级操作建议
- 风险警告
- 新机会提示

**账户列表**：
- 每个账户的市值、盈亏
- 快速跳转到账户详情

#### 2.8.2 持仓页面
**表格视图**：
| 股票 | 现价 | 成本 | 数量 | 市值 | 盈亏 | 盈亏% | AI建议 | 操作 |
|------|------|------|------|------|------|-------|--------|------|
| AAPL | 180  | 150  | 100  | 18K  | +3K  | +20%  | ✓持有  | ... |

**图表视图**：
- 饼图：行业分布、个股占比
- 柱状图：盈亏排行
- 折线图：持仓市值变化（需历史数据）

#### 2.8.3 业绩分析（Phase 2）
- 净值曲线
- 收益率（日/周/月/年）
- 最大回撤
- 夏普比率
- 换手率

---

## 3. 非功能性需求

### 3.1 性能要求
- 页面加载时间：<2秒
- AI分析响应时间：<10秒
- 支持并发用户：100+（初期）
- 数据库查询优化：索引覆盖常用查询

### 3.2 安全要求
- 密码加密：bcrypt + salt
- 通信加密：HTTPS
- 身份认证：JWT Token（1小时过期 + 刷新令牌）
- 权限控制：用户只能访问自己的数据
- 敏感信息脱敏：账号只显示后4位

### 3.3 数据一致性
- 幂等性：导入、更新操作可重复执行
- 审计追踪：所有修改操作记录时间戳和操作人
- 备份策略：每日数据库备份

### 3.4 可用性
- 服务可用性：99%+
- 错误处理：友好的错误提示
- 数据恢复：支持从备份恢复

### 3.5 兼容性
- 浏览器：Chrome、Firefox、Safari、Edge 最新版
- 移动端：响应式设计，适配手机/平板（Phase 2可考虑原生App）

---

## 4. 数据库设计概要

### 4.1 核心表

#### users（用户表）
```sql
- id: SERIAL PRIMARY KEY
- username: VARCHAR(50) UNIQUE NOT NULL
- email: VARCHAR(100) UNIQUE NOT NULL
- password_hash: VARCHAR(255) NOT NULL
- full_name: VARCHAR(100)
- avatar_url: VARCHAR(255)
- is_active: BOOLEAN DEFAULT TRUE
- created_at: TIMESTAMPTZ DEFAULT NOW()
- last_login: TIMESTAMPTZ
```

#### accounts（账户表）
```sql
- id: SERIAL PRIMARY KEY
- user_id: INTEGER REFERENCES users(id)
- name: VARCHAR(100) NOT NULL
- type: VARCHAR(50)  -- '券商账户', '虚拟账户'
- broker: VARCHAR(100)
- account_number_last4: VARCHAR(4)
- initial_capital: NUMERIC(15,2)
- created_at: TIMESTAMPTZ DEFAULT NOW()
- updated_at: TIMESTAMPTZ DEFAULT NOW()

INDEX idx_accounts_user_id (user_id)
```

#### stocks（股票信息表）- 全局共享
```sql
- id: SERIAL PRIMARY KEY
- symbol: VARCHAR(20) UNIQUE NOT NULL  -- 股票代码
- name: VARCHAR(100) NOT NULL
- name_cn: VARCHAR(100)
- market: VARCHAR(50)  -- 'NASDAQ', 'NYSE', 'A股-上交所', 'A股-深交所'
- sector: VARCHAR(50)  -- 行业
- industry: VARCHAR(100)  -- 细分行业

-- 公司信息（JSONB）
- company_info: JSONB
  -- {
  --   "business": "主营业务",
  --   "advantage": "核心竞争力",
  --   "risk": "主要风险",
  --   "founded": "成立时间",
  --   "headquarters": "总部"
  -- }

-- 财务数据（JSONB）
- financial_data: JSONB
  -- {
  --   "market_cap": "市值",
  --   "pe_ratio": "市盈率",
  --   "roe": "ROE",
  --   "debt_ratio": "负债率",
  --   "revenue_growth": "营收增长"
  -- }

- added_by: INTEGER REFERENCES users(id)
- created_at: TIMESTAMPTZ DEFAULT NOW()
- updated_at: TIMESTAMPTZ DEFAULT NOW()

INDEX idx_stocks_symbol (symbol)
INDEX idx_stocks_sector (sector)
```

#### holdings（持仓表）
```sql
- id: SERIAL PRIMARY KEY
- account_id: INTEGER REFERENCES accounts(id)
- symbol: VARCHAR(20) REFERENCES stocks(symbol)

- quantity: NUMERIC(15,4) NOT NULL
- avg_cost_basis: NUMERIC(15,4) NOT NULL  -- 平均成本
- current_price: NUMERIC(15,4)  -- 当前价格（可为空）

- status: VARCHAR(20) DEFAULT 'active'  -- 'active', 'closed'

-- 双分级标签
- tier_user: VARCHAR(50)  -- 用户分级：'核心持仓', '长期持有', '短线交易'
- tier_ai: VARCHAR(50)  -- AI分级：'core_long_term', 'watch_carefully', 'reduce_risk'
- ai_reason: TEXT  -- AI分级理由

- notes: TEXT  -- 用户备注
- idempotency_key: VARCHAR(64) UNIQUE  -- 幂等键

- created_at: TIMESTAMPTZ DEFAULT NOW()
- updated_at: TIMESTAMPTZ DEFAULT NOW()

UNIQUE (account_id, symbol)  -- 同一账户同一股票只有一条记录
INDEX idx_holdings_account_id (account_id)
INDEX idx_holdings_symbol (symbol)
INDEX idx_holdings_status (status)
```

#### watchlist（关注列表）
```sql
- id: SERIAL PRIMARY KEY
- user_id: INTEGER REFERENCES users(id)
- account_id: INTEGER REFERENCES accounts(id)  -- 关联账户
- symbol: VARCHAR(20) REFERENCES stocks(symbol)

- status: VARCHAR(20) DEFAULT 'watching'  -- 'watching', 'interested'
- tier_user: VARCHAR(50)  -- '待建仓', '研究中'
- tier_ai: VARCHAR(50)  -- 'growth_potential', 'value_opportunity'
- ai_reason: TEXT

- target_price: NUMERIC(15,4)  -- 目标买入价
- notes: TEXT

- created_at: TIMESTAMPTZ DEFAULT NOW()
- updated_at: TIMESTAMPTZ DEFAULT NOW()

UNIQUE (user_id, account_id, symbol)
INDEX idx_watchlist_user_id (user_id)
INDEX idx_watchlist_symbol (symbol)
```

#### strategies（投资策略表）
```sql
- id: SERIAL PRIMARY KEY
- user_id: INTEGER REFERENCES users(id)
- account_id: INTEGER REFERENCES accounts(id)
- symbol: VARCHAR(20) REFERENCES stocks(symbol)

- title: VARCHAR(200)  -- 策略标题
- content: TEXT  -- Markdown格式的策略内容

-- 策略要点
- strategy_type: VARCHAR(50)  -- '长期价值', '短线交易', '成长投资'
- risk_level: VARCHAR(20)  -- '低', '中', '高'
- investment_logic: TEXT  -- 投资逻辑
- entry_price_min: NUMERIC(15,4)  -- 建仓价位区间
- entry_price_max: NUMERIC(15,4)
- stop_loss: NUMERIC(15,4)  -- 止损位
- target_price_1: NUMERIC(15,4)  -- 第一目标价
- target_price_2: NUMERIC(15,4)  -- 第二目标价
- suggested_position_ratio: NUMERIC(5,4)  -- 建议仓位比例（0.1 = 10%）

- status: VARCHAR(20) DEFAULT 'active'  -- 'active', 'completed', 'archived'

- created_at: TIMESTAMPTZ DEFAULT NOW()
- updated_at: TIMESTAMPTZ DEFAULT NOW()

INDEX idx_strategies_user_id (user_id)
INDEX idx_strategies_symbol (symbol)
INDEX idx_strategies_status (status)
```

#### ai_analysis_history（AI分析历史）
```sql
- id: SERIAL PRIMARY KEY
- user_id: INTEGER REFERENCES users(id)
- account_id: INTEGER REFERENCES accounts(id)
- symbol: VARCHAR(20)  -- 可为空（整体分析时）

- analysis_type: VARCHAR(50)  -- 'portfolio', 'single_stock', 'discovery'
- request: TEXT  -- 用户请求
- response: JSONB  -- AI响应（结构化数据）
- response_text: TEXT  -- AI响应（文本）

- created_at: TIMESTAMPTZ DEFAULT NOW()

INDEX idx_ai_history_user_id (user_id)
INDEX idx_ai_history_created_at (created_at)
```

#### price_history（价格历史）- 可选
```sql
- id: SERIAL PRIMARY KEY
- symbol: VARCHAR(20) REFERENCES stocks(symbol)
- date: DATE NOT NULL
- open: NUMERIC(15,4)
- high: NUMERIC(15,4)
- low: NUMERIC(15,4)
- close: NUMERIC(15,4)
- volume: BIGINT

UNIQUE (symbol, date)
INDEX idx_price_symbol_date (symbol, date)
```

### 4.2 关键约束与索引
- **唯一约束**：防止重复数据（account + symbol）
- **幂等键**：支持导入重试（idempotency_key）
- **复合索引**：加速常用查询（user_id + account_id + symbol）
- **时间索引**：支持历史查询（created_at, updated_at）

---

## 5. API设计概要

### 5.1 认证相关
- `POST /api/auth/register` - 注册
- `POST /api/auth/login` - 登录
- `POST /api/auth/logout` - 登出
- `GET /api/auth/me` - 获取当前用户信息
- `PUT /api/auth/me` - 更新个人信息
- `PUT /api/auth/password` - 修改密码

### 5.2 账户管理
- `GET /api/accounts` - 获取当前用户的所有账户
- `POST /api/accounts` - 创建新账户
- `GET /api/accounts/:id` - 获取账户详情
- `PUT /api/accounts/:id` - 更新账户
- `DELETE /api/accounts/:id` - 删除账户

### 5.3 股票信息库
- `GET /api/stocks` - 获取股票列表（分页、搜索）
- `POST /api/stocks` - 添加新股票
- `GET /api/stocks/:symbol` - 获取股票详情
- `PUT /api/stocks/:symbol` - 更新股票信息
- `DELETE /api/stocks/:symbol` - 删除股票
- `GET /api/stocks/search?q=苹果` - 搜索股票

### 5.4 持仓管理
- `GET /api/accounts/:accountId/holdings` - 获取账户持仓
- `POST /api/accounts/:accountId/holdings` - 添加持仓
- `PUT /api/holdings/:id` - 更新持仓
- `DELETE /api/holdings/:id` - 删除持仓
- `POST /api/holdings/import` - 批量导入（CSV）
- `POST /api/holdings/import/ocr` - OCR导入
- `POST /api/holdings/refresh-price` - 刷新价格
- `GET /api/holdings/summary` - 持仓汇总（所有账户）

### 5.5 关注列表
- `GET /api/watchlist` - 获取关注列表
- `POST /api/watchlist` - 添加到关注
- `PUT /api/watchlist/:id` - 更新关注项
- `DELETE /api/watchlist/:id` - 移除关注

### 5.6 AI分析
- `POST /api/ai/discover` - 发现投资机会
  ```json
  Request: {
    "sector": "科技",
    "risk_preference": "稳健",
    "market_cap": "大盘",
    "count": 5
  }
  Response: {
    "recommendations": [...]
  }
  ```

- `POST /api/ai/analyze/portfolio` - 分析整体持仓
  ```json
  Request: {
    "account_id": 10,
    "depth": "detailed"
  }
  Response: {
    "summary": {...},
    "holdings_analysis": [...],
    "portfolio_advice": {...}
  }
  ```

- `POST /api/ai/analyze/stock` - 分析单只股票
  ```json
  Request: {
    "symbol": "AAPL",
    "account_id": 10,
    "depth": "deep"
  }
  Response: {
    "my_position": {...},
    "company_analysis": {...},
    "ai_recommendation": {...}
  }
  ```

- `POST /api/ai/generate-strategy` - 生成投资策略
  ```json
  Request: {
    "symbol": "AAPL",
    "account_id": 10
  }
  Response: {
    "strategy": {
      "title": "...",
      "content": "...(Markdown)",
      "entry_price_min": 175,
      ...
    }
  }
  ```

- `GET /api/ai/history` - AI分析历史

### 5.7 策略管理
- `GET /api/strategies` - 获取策略列表
- `POST /api/strategies` - 创建新策略
- `GET /api/strategies/:id` - 获取策略详情
- `PUT /api/strategies/:id` - 更新策略
- `DELETE /api/strategies/:id` - 删除策略

---

## 6. 技术架构

### 6.1 技术栈选型

**后端**：
- 语言：TypeScript
- 框架：NestJS（依赖注入、模块化、装饰器）
- 数据库：PostgreSQL 14+
- ORM：Prisma（类型安全、迁移管理）
- 认证：JWT（Passport.js）
- AI：Claude API（Anthropic SDK）
- 数据获取：MCP（Model Context Protocol）
  - MCP客户端：@modelcontextprotocol/sdk
  - 股票数据MCP服务器（自建或第三方）
  - 支持动态切换数据源
- 任务队列：BullMQ（定时刷新价格、增量数据同步）
- 缓存：Redis（MCP数据缓存、会话管理）

**前端**：
- 框架：React 18 + TypeScript
- 路由：React Router v6
- 状态管理：Zustand / Redux Toolkit
- UI库：Ant Design / shadcn/ui
- 图表：Apache ECharts / Recharts
- HTTP客户端：Axios
- 表单：React Hook Form + Zod

**部署**：
- 容器化：Docker + Docker Compose
- Web服务器：Nginx
- 数据库：PostgreSQL 容器
- 监控：可选（Prometheus + Grafana）

### 6.2 分层架构

```
Controller (接收HTTP请求，参数验证)
    ↓
Service (业务逻辑编排)
    ↓
DataService / Repository (数据访问)
    ↓
Database (PostgreSQL)
```

**约束**：
- Controller 无业务逻辑，只做参数验证和调用Service
- Service 不直接操作数据库，统一通过 DataService
- 工具类方法必须是静态方法

### 6.3 防腐层设计
- **Converter**：DTO ↔ Entity 转换
- **Wrapper**：权限检查、数据脱敏
- **Adapter**：外部服务适配
  - Claude API Adapter：AI分析调用
  - MCP Adapter：股票数据获取（统一接口，支持多数据源）
  - 通知Adapter：消息推送（可选）
- **Rule**：业务规则封装（幂等键生成、风险检查）

---

## 7. 典型用户流程

### 7.1 新用户上手流程
```
注册账号
  ↓
创建第一个账户（券商账户）
  ↓
导入持仓（OCR截图识别）
  ↓
查看持仓列表
  ↓
点击"AI分析持仓"
  ↓
查看AI建议
  ↓
点击某只股票查看详情
  ↓
查看/编辑投资策略
```

### 7.2 日常使用流程
```
登录 → 查看仪表板
  ↓
查看AI今日提醒
  ↓
点击"发现投资机会"
  ↓
AI推荐5只股票
  ↓
选择2只感兴趣的
  ↓
AI生成投资策略
  ↓
添加到关注列表
  ↓
等待合适价位买入
```

### 7.3 AI分析流程（集成MCP）
```
用户点击"分析持仓"
  ↓
后端收集数据：
  - 持仓列表（symbol, quantity, cost）从数据库读取
  - 通过 MCP Adapter 获取实时数据：
    * 最新价格（current_price）
    * 公司最新财务数据
    * 近期新闻/公告（可选）
  - 股票基础信息（从stocks表读取）
  ↓
构建AI Prompt（可直接给AI提供MCP工具）：
  方案1：后端预取数据
  """
  你是投资顾问。分析以下持仓：

  账户：华泰证券
  总市值：¥500,000

  持仓明细：
  1. AAPL - 苹果
     成本：$150, 现价：$180, 盈亏：+20%
     公司信息：{...}
     最新财务：{通过MCP获取}

  请提供：
  1. 每只股票的操作建议（持有/加仓/减仓）
  2. 整体组合建议
  3. 风险提示
  """

  方案2：AI直接调用MCP（推荐）
  - AI可主动通过MCP获取需要的最新数据
  - 更灵活，减少后端数据处理
  ↓
调用Claude API（带MCP支持）
  ↓
解析AI响应
  ↓
保存到 ai_analysis_history
  ↓
返回结构化结果给前端
  ↓
前端展示（卡片 + 表格）
```

---

## 8. 实施计划

### Phase 1：基础框架（2周）
**目标**：完成项目搭建和用户认证

- [ ] 后端项目搭建（NestJS）
- [ ] 数据库设计 + Prisma Schema
- [ ] 用户注册/登录/JWT认证
- [ ] 前端项目搭建（React + Ant Design）
- [ ] 登录/注册页面
- [ ] 路由和布局框架

### Phase 2：核心数据管理（3周）
**目标**：实现账户、持仓、股票库的CRUD + MCP集成

- [ ] 账户管理API + UI
- [ ] **MCP集成**
  - [ ] MCP客户端封装（Adapter层）
  - [ ] 股票数据MCP服务配置
  - [ ] 测试数据获取（行情、公司信息）
- [ ] 股票信息库
  - [ ] 手动添加/编辑
  - [ ] 通过MCP自动填充数据
- [ ] 持仓管理（添加/编辑/删除）
- [ ] CSV批量导入
- [ ] OCR导入（调用OCR API）
- [ ] 关注列表管理
- [ ] 仪表板页面（基础版）

### Phase 3：AI集成（2-3周）
**目标**：实现AI核心功能（结合MCP实时数据）

- [ ] Claude API集成
- [ ] **AI + MCP 集成**
  - [ ] AI可通过MCP获取实时数据
  - [ ] 配置AI可用的MCP工具
- [ ] AI发现投资机会
  - Prompt工程
  - 推荐列表展示
  - 基于MCP实时数据分析
- [ ] AI持仓分析
  - 整体分析
  - 单股深度分析
  - 结合MCP最新财务/新闻数据
- [ ] AI投资策略生成
  - Markdown渲染
  - 策略管理CRUD
- [ ] AI分析历史记录

### Phase 4：可视化与优化（2周）
**目标**：完善UI和性能优化

- [ ] 仪表板完善
  - 图表展示（行业分布、盈亏排行）
  - AI今日提醒
- [ ] 持仓页面优化
  - 表格排序/筛选
  - 导出功能
- [ ] 价格自动更新
  - 定时任务
  - 行情API集成
- [ ] 性能优化
  - 数据库索引
  - 查询优化
  - 前端懒加载

### Phase 5：测试与上线（1周）
**目标**：测试、修复、部署

- [ ] 单元测试（关键业务逻辑）
- [ ] 集成测试（API端到端）
- [ ] 前端测试（关键流程）
- [ ] Docker配置
- [ ] 部署到服务器
- [ ] 数据备份策略
- [ ] 监控和日志

---

## 9. 风险与挑战

### 9.1 技术风险
| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| Claude API限流 | AI功能不可用 | 实现重试机制、请求队列 |
| MCP服务不稳定/超时 | 数据获取失败 | 多MCP服务源备份、Redis缓存、降级为手动输入 |
| MCP数据质量问题 | 分析结果不准确 | 数据验证层、用户可手动修正 |
| OCR识别准确率低 | 导入错误 | 人工确认环节、支持手动修正 |
| 数据库性能瓶颈 | 查询慢 | 索引优化、分页、缓存 |

### 9.2 产品风险
| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| AI建议不准确 | 用户信任度下降 | 免责声明、用户教育、持续优化Prompt |
| 用户隐私泄露 | 法律风险 | 数据加密、权限控制、安全审计 |
| 用户粘性不足 | 用户流失 | 定时AI提醒、策略追踪、社区功能（Phase 2） |

### 9.3 业务风险
| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| 合规问题 | 平台下架 | 明确定位为"个人记录工具"，不提供交易通道 |
| AI成本过高 | 亏损 | 控制调用频率、付费订阅模式 |

---

## 10. 成功指标

### 10.1 MVP阶段（3个月内）
- 注册用户数：100+
- 日活用户：20+
- 导入持仓股票数：500+
- AI分析调用次数：200+/周
- 用户留存率（7日）：40%+

### 10.2 产品指标（6个月内）
- 注册用户数：500+
- 月活用户：100+
- 用户平均管理账户数：2+
- AI策略生成数：1000+
- 用户满意度：4.0/5.0+

---

## 11. 未来扩展方向（Out of Scope for MVP）

### Phase 2（3-6个月后）
- [ ] 移动端App（React Native / Flutter）
- [ ] 交易事件账本（买入/卖出记录）
- [ ] 已实现盈亏计算
- [ ] 业绩净值曲线
- [ ] 策略回测功能
- [ ] 用户社区（分享策略）

### Phase 3（6-12个月后）
- [ ] 量化策略支持（简化版）
- [ ] 家庭账户共享
- [ ] 智能提醒（价格到达、财报发布）
- [ ] 多语言支持
- [ ] 付费订阅模式

---

## 12. 附录

### 12.1 名词解释
- **持仓（Holdings）**：用户实际购买并持有的股票
- **关注（Watchlist）**：用户关注但尚未购买的股票
- **幂等性（Idempotency）**：同一操作执行多次结果相同
- **AI分级（AI Tier）**：AI根据分析结果自动给股票打标签
- **投资策略（Strategy）**：包含买入逻辑、目标价、止损位的投资计划

### 12.2 参考资料
- Anthropic Claude API文档
- NestJS官方文档
- Prisma文档
- PostgreSQL性能优化指南

---

## 13. 变更记录
| 版本 | 日期 | 变更内容 | 作者 |
|------|------|----------|------|
| v1.0 | 2025-01-13 | 初始版本 | Claude |

---

**下一步**：
1. 审阅PRD，确认功能范围
2. 评估技术栈选型
3. 细化数据库Schema
4. 启动Phase 1开发

---
