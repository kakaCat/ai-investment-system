# 事件分析增强设计

**版本**: v1.0
**日期**: 2025-01-14
**目标**: 在现有架构基础上增强事件(政策事件、公司事件、市场事件、行业事件)的追踪、分类与影响分析能力,让AI能够参考这些事件来分析整个股市和个股

---

## 1. 设计目标

### 1.1 核心需求
- **事件收集**: 自动从MCP数据源收集政策、公司、市场、行业相关事件
- **事件分类**: 智能分类事件类型、重要性、影响范围
- **影响分析**: 分析事件对整体市场和个股的影响
- **AI集成**: 在AI分析(持仓分析、选股、策略生成)时自动引用相关事件

### 1.2 事件类型定义

#### 政策事件 (Policy Events)
- **货币政策**: 利率调整、存款准备金率、货币供应量
- **财政政策**: 减税、补贴、政府支出
- **监管政策**: 行业监管规则、上市规则、交易规则
- **国际政策**: 贸易政策、关税、国际协议

#### 公司事件 (Company Events)
- **财报相关**: 财报发布、业绩预告、业绩修正
- **公司治理**: 高管变动、董事会决议、股东大会
- **资本运作**: 并购、重组、增发、回购、分红
- **业务变化**: 新产品发布、重大合同、产能扩张

#### 市场事件 (Market Events)
- **指数调整**: 指数成分股调整、权重变化
- **资金流动**: 北向资金、外资流入流出、大宗交易
- **市场情绪**: VIX指数、恐慌指数、投资者情绪指标
- **技术突破**: 关键点位突破、趋势变化

#### 行业事件 (Industry Events)
- **技术突破**: 新技术发布、专利突破
- **竞争格局**: 市场份额变化、新进入者
- **供需关系**: 原材料价格、产能变化、需求变化
- **政策影响**: 行业专项政策、补贴、限制

---

## 2. 数据库设计

### 2.1 事件表 (events)

```sql
-- 事件类型枚举
CREATE TYPE event_category AS ENUM (
  'policy',        -- 政策事件
  'company',       -- 公司事件
  'market',        -- 市场事件
  'industry'       -- 行业事件
);

-- 事件子类型
CREATE TYPE event_subcategory AS ENUM (
  -- 政策事件子类型
  'policy_monetary',    -- 货币政策
  'policy_fiscal',      -- 财政政策
  'policy_regulatory',  -- 监管政策
  'policy_international', -- 国际政策

  -- 公司事件子类型
  'company_earnings',   -- 财报相关
  'company_governance', -- 公司治理
  'company_capital',    -- 资本运作
  'company_business',   -- 业务变化

  -- 市场事件子类型
  'market_index',       -- 指数调整
  'market_flow',        -- 资金流动
  'market_sentiment',   -- 市场情绪
  'market_technical',   -- 技术突破

  -- 行业事件子类型
  'industry_tech',      -- 技术突破
  'industry_competition', -- 竞争格局
  'industry_supply',    -- 供需关系
  'industry_policy'     -- 行业政策
);

-- 事件重要性级别
CREATE TYPE event_importance AS ENUM (
  'critical',    -- 极其重要(影响整个市场)
  'high',        -- 高度重要(影响行业或大盘股)
  'medium',      -- 中度重要(影响个股或板块)
  'low'          -- 低度重要(参考性事件)
);

-- 事件影响方向
CREATE TYPE event_impact_direction AS ENUM (
  'positive',    -- 利好
  'negative',    -- 利空
  'neutral',     -- 中性
  'mixed'        -- 复杂影响
);

-- 事件表
CREATE TABLE events (
  id BIGSERIAL PRIMARY KEY,                                    -- 事件ID

  -- 基本信息
  title TEXT NOT NULL,                                         -- 事件标题
  summary TEXT NOT NULL,                                       -- 事件摘要(200-500字)
  content TEXT,                                                -- 事件详细内容
  source_url TEXT,                                             -- 来源链接

  -- 分类信息
  category event_category NOT NULL,                            -- 主分类
  subcategory event_subcategory NOT NULL,                      -- 子分类
  importance event_importance NOT NULL DEFAULT 'medium',       -- 重要性级别

  -- 影响范围
  symbols TEXT[],                                              -- 受影响的股票代码列表(可为空表示市场级事件)
  sectors TEXT[],                                              -- 受影响的行业列表
  markets TEXT[],                                              -- 受影响的市场(如['CN','US','HK'])

  -- 影响分析
  impact_direction event_impact_direction DEFAULT 'neutral',   -- 影响方向
  impact_magnitude NUMERIC(5,2),                               -- 影响强度(0-100,由AI评估)
  impact_summary TEXT,                                         -- 影响摘要(AI生成)

  -- 时间信息
  event_time TIMESTAMPTZ NOT NULL,                             -- 事件发生时间
  published_at TIMESTAMPTZ,                                    -- 事件发布时间
  impact_start_date DATE,                                      -- 影响开始日期
  impact_end_date DATE,                                        -- 影响结束日期(可为空表示持续影响)

  -- 数据源
  source TEXT NOT NULL DEFAULT 'mcp',                          -- 数据源(mcp/manual/user)
  external_id TEXT,                                            -- 外部事件ID(用于去重)

  -- 审计
  processed BOOLEAN DEFAULT FALSE,                             -- 是否已处理(AI分析)
  idempotency_key TEXT UNIQUE,                                 -- 幂等键(避免重复)
  created_at TIMESTAMPTZ DEFAULT NOW(),                        -- 创建时间
  updated_at TIMESTAMPTZ DEFAULT NOW()                         -- 更新时间
);

-- 索引
CREATE INDEX idx_events_category ON events(category, event_time DESC);
CREATE INDEX idx_events_importance ON events(importance, event_time DESC);
CREATE INDEX idx_events_symbols ON events USING GIN(symbols);               -- GIN索引支持数组查询
CREATE INDEX idx_events_sectors ON events USING GIN(sectors);
CREATE INDEX idx_events_time ON events(event_time DESC);
CREATE INDEX idx_events_processed ON events(processed, event_time DESC);
CREATE INDEX idx_events_external_id ON events(external_id);

COMMENT ON TABLE events IS '事件表:追踪政策、公司、市场、行业事件';
COMMENT ON COLUMN events.impact_magnitude IS '影响强度(0-100),由AI评估,数值越大影响越大';
COMMENT ON COLUMN events.symbols IS '受影响的股票代码列表,空数组表示市场级事件';
```

### 2.2 事件与股票关联分析表 (event_stock_impacts)

```sql
-- 事件对个股的影响详细分析
CREATE TABLE event_stock_impacts (
  id BIGSERIAL PRIMARY KEY,                                    -- 记录ID
  event_id BIGINT NOT NULL,                                    -- 事件ID(引用 events.id,虚拟外键)
  symbol TEXT NOT NULL,                                        -- 股票代码

  -- 影响分析
  impact_direction event_impact_direction NOT NULL,            -- 对该股票的影响方向
  impact_magnitude NUMERIC(5,2),                               -- 对该股票的影响强度(0-100)
  impact_reason TEXT,                                          -- 影响原因(AI生成)

  -- 价格影响预测
  expected_price_change_percent NUMERIC(9,4),                  -- 预期价格变化百分比
  actual_price_change_percent NUMERIC(9,4),                    -- 实际价格变化百分比(事后填充)

  -- 时间信息
  analyzed_at TIMESTAMPTZ DEFAULT NOW(),                       -- 分析时间

  UNIQUE(event_id, symbol)                                     -- 每个事件对每只股票只有一条分析记录
);

CREATE INDEX idx_event_impacts_symbol ON event_stock_impacts(symbol, analyzed_at DESC);
CREATE INDEX idx_event_impacts_event ON event_stock_impacts(event_id);
CREATE INDEX idx_event_impacts_direction ON event_stock_impacts(impact_direction, impact_magnitude DESC);

COMMENT ON TABLE event_stock_impacts IS '事件对个股的影响详细分析';
```

### 2.3 扩展现有表结构

#### 在 `strategy_analysis` 表中添加事件引用

```sql
-- 添加字段到现有的 strategy_analysis 表
ALTER TABLE strategy_analysis
  ADD COLUMN related_events JSONB;  -- 相关事件列表 [{"event_id": 123, "relevance": 0.85}]

CREATE INDEX idx_strategy_related_events ON strategy_analysis USING GIN(related_events);

COMMENT ON COLUMN strategy_analysis.related_events IS '策略分析时参考的相关事件列表';
```

#### 在 `ai_analysis_history` 表中添加事件引用

```sql
-- 添加字段到现有的 ai_analysis_history 表
ALTER TABLE ai_analysis_history
  ADD COLUMN related_events JSONB;  -- 分析时参考的事件列表

CREATE INDEX idx_ai_history_events ON ai_analysis_history USING GIN(related_events);

COMMENT ON COLUMN ai_analysis_history.related_events IS 'AI分析时参考的事件列表';
```

---

## 3. 架构设计

### 3.1 Adapter层扩展

#### EventAdapter (新增)

```typescript
/**
 * EventAdapter: 事件数据适配器
 * 职责:
 * 1. 从MCP服务获取各类事件数据
 * 2. 统一事件数据格式
 * 3. 事件去重与幂等性保证
 */
export class EventAdapter {
  /**
   * 获取最新事件(指定时间窗口)
   */
  static async fetchRecentEvents(params: {
    startTime: Date;
    endTime?: Date;
    categories?: EventCategory[];
    symbols?: string[];
    markets?: string[];
  }): Promise<EventData[]>;

  /**
   * 获取单个股票相关事件
   */
  static async fetchSymbolEvents(
    symbol: string,
    lookbackDays: number
  ): Promise<EventData[]>;

  /**
   * 获取行业相关事件
   */
  static async fetchSectorEvents(
    sector: string,
    lookbackDays: number
  ): Promise<EventData[]>;

  /**
   * 获取市场级事件
   */
  static async fetchMarketEvents(
    market: string,
    lookbackDays: number
  ): Promise<EventData[]>;
}
```

#### NewsAdapter增强 (现有)

```typescript
/**
 * NewsAdapter: 新闻与舆情适配器(增强)
 * 职责:
 * 1. 从新闻中识别和提取事件
 * 2. 与EventAdapter配合,将新闻转化为结构化事件
 */
export class NewsAdapter {
  /**
   * 现有功能 + 新增: 从新闻中提取事件
   */
  static async extractEventsFromNews(
    newsItems: NewsItem[]
  ): Promise<EventData[]>;
}
```

### 3.2 DataService层扩展

#### EventDataService (新增)

```typescript
/**
 * EventDataService: 事件数据服务
 * 职责: 聚合事件数据访问,统一管理缓存策略
 */
export class EventDataService {
  /**
   * 获取相关事件(优先读缓存,miss时通过Adapter拉取并落库)
   */
  static async getRelevantEvents(params: {
    symbols?: string[];
    sectors?: string[];
    startDate: Date;
    endDate?: Date;
    importance?: EventImportance[];
    categories?: EventCategory[];
  }): Promise<Event[]>;

  /**
   * 保存事件
   */
  static async saveEvents(events: EventData[]): Promise<void>;

  /**
   * 获取事件影响分析
   */
  static async getEventImpacts(
    eventId: number,
    symbols?: string[]
  ): Promise<EventStockImpact[]>;

  /**
   * 保存事件影响分析
   */
  static async saveEventImpacts(
    impacts: EventStockImpact[]
  ): Promise<void>;
}
```

### 3.3 Service层增强

#### StrategyService增强

```typescript
/**
 * StrategyService: 策略服务(增强)
 */
export class StrategyService {
  /**
   * 生成策略分析(增强版本,包含事件分析)
   */
  static async collectStrategyData(params: {
    userId: number;
    accountId: number;
    symbol: string;
    lookbackDays?: number; // 回溯天数,用于获取历史事件
  }): Promise<StrategyAnalysisData> {
    // 1. 获取股票基础信息
    const company = await MarketDataService.getCompany(symbol);
    const price = await MarketDataService.getPrice(symbol);

    // 2. 获取相关事件(过去N天)
    const events = await EventDataService.getRelevantEvents({
      symbols: [symbol],
      sectors: [company.sector],
      startDate: subDays(new Date(), lookbackDays || 30),
      importance: ['critical', 'high', 'medium']
    });

    // 3. AI分析(包含事件上下文)
    const analysis = await this.analyzeWithEvents(
      company,
      price,
      events
    );

    // 4. 保存策略分析(含事件引用)
    const strategy = await StrategyAnalysisRepository.save({
      ...analysis,
      related_events: events.map(e => ({
        event_id: e.id,
        relevance: this.calculateRelevance(e, symbol)
      }))
    });

    return strategy;
  }

  /**
   * AI分析(包含事件上下文)
   */
  private static async analyzeWithEvents(
    company: CompanyData,
    price: PriceData,
    events: Event[]
  ): Promise<StrategyAnalysisData> {
    // 构建包含事件的Prompt
    const prompt = this.buildPromptWithEvents(company, price, events);

    // 调用Claude API
    const response = await ClaudeAdapter.analyze(prompt);

    return response;
  }

  /**
   * 构建包含事件的Prompt
   */
  private static buildPromptWithEvents(
    company: CompanyData,
    price: PriceData,
    events: Event[]
  ): string {
    return `
你是专业的投资分析师。请分析以下股票:

## 股票信息
- 代码: ${company.symbol}
- 名称: ${company.name}
- 行业: ${company.sector}
- 当前价格: ${price.price}
- 涨跌幅: ${price.changePercent}%

## 近期相关事件
${this.formatEventsForPrompt(events)}

## 请提供分析:
1. 基于上述事件,分析对该股票的影响
2. 给出操作建议(买入/卖出/持有)
3. 设定止损位和目标价
4. 评估风险等级

请以JSON格式返回分析结果。
    `;
  }

  /**
   * 格式化事件用于Prompt
   */
  private static formatEventsForPrompt(events: Event[]): string {
    if (events.length === 0) return '暂无重大事件';

    return events.map((e, idx) => `
### 事件${idx + 1}: ${e.title}
- 类型: ${e.category} / ${e.subcategory}
- 重要性: ${e.importance}
- 影响方向: ${e.impactDirection}
- 影响强度: ${e.impactMagnitude}/100
- 时间: ${e.eventTime}
- 摘要: ${e.summary}
${e.impactSummary ? `- AI分析: ${e.impactSummary}` : ''}
    `).join('\n');
  }

  /**
   * 计算事件相关性(0-1)
   */
  private static calculateRelevance(event: Event, symbol: string): number {
    let relevance = 0.5; // 基础相关性

    // 直接提到该股票 +0.4
    if (event.symbols?.includes(symbol)) {
      relevance += 0.4;
    }

    // 重要性加权
    const importanceWeight = {
      'critical': 0.3,
      'high': 0.2,
      'medium': 0.1,
      'low': 0.0
    };
    relevance += importanceWeight[event.importance] || 0;

    return Math.min(relevance, 1.0);
  }
}
```

---

## 4. 定时任务设计

### 4.1 事件收集任务

```typescript
/**
 * 事件收集定时任务
 * 频率: 每小时执行一次
 */
export class EventCollectionTask {
  /**
   * 执行事件收集
   */
  async execute(): Promise<void> {
    // 1. 获取最新事件(从上次收集时间到现在)
    const lastCollectionTime = await this.getLastCollectionTime();
    const newEvents = await EventAdapter.fetchRecentEvents({
      startTime: lastCollectionTime,
      endTime: new Date()
    });

    // 2. 去重(通过external_id或idempotency_key)
    const uniqueEvents = this.deduplicateEvents(newEvents);

    // 3. AI增强(分析影响方向、强度、摘要)
    const enrichedEvents = await this.enrichEventsWithAI(uniqueEvents);

    // 4. 保存到数据库
    await EventDataService.saveEvents(enrichedEvents);

    // 5. 触发个股影响分析(异步)
    await this.triggerImpactAnalysis(enrichedEvents);

    // 6. 更新收集时间戳
    await this.updateLastCollectionTime(new Date());
  }

  /**
   * AI增强事件分析
   */
  private async enrichEventsWithAI(
    events: EventData[]
  ): Promise<EventData[]> {
    // 批量调用Claude API分析事件影响
    const enriched = await Promise.all(
      events.map(async (event) => {
        const analysis = await ClaudeAdapter.analyzeEvent(event);
        return {
          ...event,
          impactDirection: analysis.direction,
          impactMagnitude: analysis.magnitude,
          impactSummary: analysis.summary
        };
      })
    );

    return enriched;
  }

  /**
   * 触发个股影响分析
   */
  private async triggerImpactAnalysis(
    events: Event[]
  ): Promise<void> {
    for (const event of events) {
      // 只对重要事件进行详细影响分析
      if (event.importance === 'critical' || event.importance === 'high') {
        await AgentTasksService.createTask({
          taskType: 'event_impact_analysis',
          payload: { eventId: event.id }
        });
      }
    }
  }
}
```

### 4.2 事件影响分析任务

```typescript
/**
 * 事件影响分析任务
 * 触发方式: 事件收集后异步执行
 */
export class EventImpactAnalysisTask {
  /**
   * 分析事件对相关股票的影响
   */
  async execute(eventId: number): Promise<void> {
    // 1. 获取事件
    const event = await EventRepository.findById(eventId);

    // 2. 确定受影响的股票列表
    const affectedSymbols = await this.getAffectedSymbols(event);

    // 3. 对每只股票进行影响分析
    const impacts = await Promise.all(
      affectedSymbols.map(symbol =>
        this.analyzeImpactOnSymbol(event, symbol)
      )
    );

    // 4. 保存影响分析结果
    await EventDataService.saveEventImpacts(impacts);

    // 5. 标记事件为已处理
    await EventRepository.update(eventId, { processed: true });
  }

  /**
   * 获取受影响的股票列表
   */
  private async getAffectedSymbols(event: Event): Promise<string[]> {
    const symbols = new Set<string>();

    // 1. 事件中直接提到的股票
    if (event.symbols) {
      event.symbols.forEach(s => symbols.add(s));
    }

    // 2. 事件影响的行业中的股票(取前N只)
    if (event.sectors && event.sectors.length > 0) {
      const sectorStocks = await CompanyRepository.findBySectors(
        event.sectors,
        { limit: 50 } // 每个行业取前50只
      );
      sectorStocks.forEach(s => symbols.add(s.symbol));
    }

    return Array.from(symbols);
  }

  /**
   * 分析事件对单只股票的影响
   */
  private async analyzeImpactOnSymbol(
    event: Event,
    symbol: string
  ): Promise<EventStockImpact> {
    // 获取股票信息
    const company = await MarketDataService.getCompany(symbol);
    const price = await MarketDataService.getPrice(symbol);

    // AI分析影响
    const analysis = await ClaudeAdapter.analyzeEventImpact({
      event,
      company,
      price
    });

    return {
      eventId: event.id,
      symbol,
      impactDirection: analysis.direction,
      impactMagnitude: analysis.magnitude,
      impactReason: analysis.reason,
      expectedPriceChangePercent: analysis.expectedChange
    };
  }
}
```

---

## 5. API设计

### 5.1 事件管理API

```typescript
// 获取事件列表
GET /api/events
Query params:
  - category?: EventCategory
  - subcategory?: EventSubcategory
  - importance?: EventImportance
  - symbol?: string
  - sector?: string
  - startDate?: Date
  - endDate?: Date
  - page?: number
  - limit?: number

Response: {
  events: Event[];
  total: number;
  page: number;
  totalPages: number;
}

// 获取单个事件详情
GET /api/events/:id
Response: {
  event: Event;
  impacts: EventStockImpact[];  // 对个股的影响分析
}

// 获取股票相关事件
GET /api/stocks/:symbol/events
Query params:
  - lookbackDays?: number (default: 30)
  - importance?: EventImportance[]

Response: {
  symbol: string;
  events: Event[];
  total: number;
}

// 手动触发事件收集
POST /api/events/collect
Request: {
  startTime?: Date;
  categories?: EventCategory[];
}
Response: {
  collected: number;
  processed: number;
}

// 手动添加事件
POST /api/events
Request: {
  title: string;
  summary: string;
  content?: string;
  category: EventCategory;
  subcategory: EventSubcategory;
  importance: EventImportance;
  symbols?: string[];
  sectors?: string[];
  eventTime: Date;
}
Response: {
  event: Event;
}
```

### 5.2 增强的AI分析API

```typescript
// 持仓分析(增强版,包含事件分析)
POST /api/ai/analyze/portfolio
Request: {
  accountId: number;
  includeEvents: boolean;      // 是否包含事件分析
  eventLookbackDays?: number;  // 事件回溯天数
}
Response: {
  summary: {...};
  holdings_analysis: [
    {
      symbol: string;
      ...
      relatedEvents: Event[];  // 相关事件
    }
  ];
  portfolio_advice: {...};
  marketEvents: Event[];       // 市场级事件
}

// 单股分析(增强版,包含事件分析)
POST /api/ai/analyze/stock
Request: {
  symbol: string;
  accountId?: number;
  includeEvents: boolean;
  eventLookbackDays?: number;
}
Response: {
  ...
  relatedEvents: Event[];      // 相关事件
  eventAnalysis: {             // 事件影响分析
    positiveEvents: Event[];
    negativeEvents: Event[];
    overallImpact: string;
  };
}
```

---

## 6. 前端UI设计

### 6.1 事件中心页面

```
┌─────────────────────────────────────────────────────┐
│ 事件中心                                             │
├─────────────────────────────────────────────────────┤
│ [筛选] 类型: [全部▼] 重要性: [全部▼] 时间: [30天▼]  │
├─────────────────────────────────────────────────────┤
│ 🔴 [极重要] 央行降息50个基点                         │
│    政策事件 > 货币政策 | 2025-01-14 10:30           │
│    影响: 利好 (85/100) | 市场级事件                 │
│    📊 影响25只股票 | 💡 查看详情                    │
├─────────────────────────────────────────────────────┤
│ 🟠 [高度重要] 苹果公司发布Q4财报超预期               │
│    公司事件 > 财报相关 | 2025-01-13 16:00           │
│    影响: 利好 (78/100) | AAPL                       │
│    📊 查看影响分析                                   │
├─────────────────────────────────────────────────────┤
│ 🟡 [中度重要] 半导体行业补贴政策出台                 │
│    行业事件 > 行业政策 | 2025-01-12 09:00           │
│    影响: 利好 (65/100) | 影响科技板块               │
└─────────────────────────────────────────────────────┘
```

### 6.2 股票详情页 - 事件区块(新增)

在现有股票详情页增加"相关事件"区块:

```
┌─────────────────────────────────────────────────────┐
│ AAPL - 苹果公司                                      │
│ 当前价格: $180.50 (+2.3%)                           │
├─────────────────────────────────────────────────────┤
│ [公司信息] [价格走势] [相关事件] [策略分析]         │
├─────────────────────────────────────────────────────┤
│ 📅 近30天相关事件 (5条)                              │
├─────────────────────────────────────────────────────┤
│ ✅ 2025-01-13 | Q4财报超预期                        │
│    利好 (78/100) | AI分析: 服务业务增长强劲...      │
├─────────────────────────────────────────────────────┤
│ ⚠️ 2025-01-10 | 欧盟反垄断调查升级                  │
│    利空 (45/100) | AI分析: 可能面临罚款...          │
├─────────────────────────────────────────────────────┤
│ ℹ️ 2025-01-08 | 美联储维持利率不变                  │
│    中性 (20/100) | 市场级事件                       │
└─────────────────────────────────────────────────────┘
```

### 6.3 持仓分析结果 - 事件卡片(增强)

```
┌─────────────────────────────────────────────────────┐
│ 持仓分析结果                                         │
├─────────────────────────────────────────────────────┤
│ 📊 整体评估                                          │
│ 总市值: ¥500,000 | 盈亏: +¥50,000 (+11%)           │
├─────────────────────────────────────────────────────┤
│ 🔔 重要事件提醒                                      │
│ • 央行降息 → 利好您持有的银行股和地产股              │
│ • 科技补贴政策 → 利好您持有的AAPL、MSFT             │
│ • 贸易摩擦升级 → 注意风险(持仓中有XX股)              │
├─────────────────────────────────────────────────────┤
│ 📋 个股建议 (基于事件分析)                           │
│ AAPL | 持有 | 财报超预期,建议继续持有               │
│ MSFT | 加仓 | 受益于AI政策,建议适当加仓             │
│ XXX  | 减仓 | 受贸易摩擦影响,建议减仓观望            │
└─────────────────────────────────────────────────────┘
```

---

## 7. 实施计划

### Phase 1: 数据库与基础设施 (1周)
- [ ] 创建事件表结构(events, event_stock_impacts)
- [ ] 扩展现有表(strategy_analysis, ai_analysis_history)
- [ ] 编写数据库迁移脚本
- [ ] 创建Repository层(EventRepository)

### Phase 2: Adapter与DataService (1-2周)
- [ ] 实现EventAdapter(MCP集成)
- [ ] 增强NewsAdapter(事件提取)
- [ ] 实现EventDataService
- [ ] 编写单元测试

### Phase 3: Service层与AI集成 (2周)
- [ ] 增强StrategyService(包含事件分析)
- [ ] 增强StockService
- [ ] 实现事件收集定时任务
- [ ] 实现事件影响分析任务
- [ ] AI Prompt优化(包含事件上下文)

### Phase 4: API与前端 (2周)
- [ ] 实现事件管理API
- [ ] 增强AI分析API(返回事件数据)
- [ ] 前端事件中心页面
- [ ] 前端股票详情页事件区块
- [ ] 前端持仓分析结果事件卡片

### Phase 5: 测试与优化 (1周)
- [ ] 端到端测试
- [ ] 性能优化(缓存、索引)
- [ ] AI分析质量评估
- [ ] 文档完善

---

## 8. 技术要点

### 8.1 事件去重策略
- 使用`external_id`作为外部事件唯一标识
- 使用`idempotency_key`防止重复导入
- 相似事件合并(标题相似度>80%且时间差<24h)

### 8.2 AI分析优化
- 批量分析(一次API调用分析多个事件)
- 缓存事件影响分析结果(24小时TTL)
- 渐进式分析(critical事件优先,low事件延后)

### 8.3 性能优化
- 事件表按时间分区(月度分区)
- GIN索引优化数组查询(symbols, sectors)
- Redis缓存热点事件(7天内的critical/high事件)
- 物化视图缓存股票-事件关联

### 8.4 数据质量保证
- AI分析结果置信度评分
- 人工审核机制(critical事件)
- 事件来源可追溯
- 影响分析准确性回测(对比实际价格变化)

---

## 9. 监控与运维

### 9.1 监控指标
- 事件收集成功率
- 事件去重率
- AI分析延迟
- 影响分析准确率(MAE/RMSE)

### 9.2 告警规则
- critical事件收集失败 → 立即告警
- AI分析队列积压>100 → 告警
- 影响分析准确率<60% → 告警

---

## 10. 风险与挑战

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| MCP事件数据源不稳定 | 事件收集失败 | 多数据源备份、降级策略 |
| AI分析成本高 | 运营成本增加 | 分级处理、批量分析 |
| 事件影响预测不准 | 用户信任度下降 | 置信度评分、回测优化 |
| 事件数据量大 | 数据库性能下降 | 分区表、归档策略 |

---

## 11. 未来扩展

### 11.1 事件订阅与推送
- 用户订阅特定类型事件
- 重要事件实时推送(WebSocket/SSE)
- 每日事件摘要邮件

### 11.2 事件知识图谱
- 事件间关联关系
- 事件链分析(因果关系)
- 事件相似度推荐

### 11.3 自定义事件
- 用户手动添加事件
- 社区事件分享
- 事件评论与讨论

---

**总结**: 通过增强现有架构,添加事件管理模块,让AI能够在分析股票和持仓时参考政策事件、公司事件、市场事件和行业事件,从而提供更全面、更准确的投资建议。
