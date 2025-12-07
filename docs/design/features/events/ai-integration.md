# AI分析事件集成设计

**版本**: v1.0
**日期**: 2025-01-14
**目标**: 设计AI分析各场景下如何引用和使用事件数据

---

## 1. 设计原则

### 1.1 核心原则
- **上下文相关性**: 只提供与分析对象相关的事件
- **时间窗口合理**: 根据分析类型选择合适的事件回溯期
- **重要性排序**: 优先展示重要事件,避免信息过载
- **影响量化**: 提供事件的影响方向和强度评估
- **可追溯性**: 记录AI分析时引用了哪些事件

### 1.2 事件选择策略

| 分析场景 | 时间窗口 | 重要性过滤 | 相关性判断 |
|---------|---------|-----------|-----------|
| 单股深度分析 | 30-90天 | medium及以上 | 直接提到该股票 OR 行业事件 |
| 持仓分析 | 7-30天 | high及以上 | 持仓股票相关 OR 市场级事件 |
| 选股推荐 | 7-14天 | high及以上 | 行业事件 + 市场事件 |
| 策略生成 | 30-60天 | medium及以上 | 股票+行业+市场 |
| 阶段总结 | 周期内全部 | medium及以上 | 持仓相关 |

---

## 2. 分场景集成设计

### 2.1 单股深度分析

#### 2.1.1 事件获取逻辑

```typescript
// src/services/stock.service.ts (增强)

export class StockService {
  /**
   * 收集单股分析数据(包含事件)
   */
  static async collectStockAnalysisData(params: {
    symbol: string;
    accountId?: number;
    eventLookbackDays?: number;
  }): Promise<StockAnalysisData> {
    const { symbol, eventLookbackDays = 30 } = params;

    // 1. 基础数据
    const company = await MarketDataService.getCompany(symbol);
    const price = await MarketDataService.getPrice(symbol);

    // 2. 获取相关事件
    const events = await this.getRelevantEventsForStock(
      symbol,
      company.sector,
      eventLookbackDays
    );

    // 3. AI分析(包含事件上下文)
    const analysis = await this.analyzeStockWithEvents(
      company,
      price,
      events
    );

    return {
      company,
      price,
      events,
      analysis,
      eventsSummary: this.summarizeEvents(events)
    };
  }

  /**
   * 获取股票相关事件
   */
  private static async getRelevantEventsForStock(
    symbol: string,
    sector: string,
    lookbackDays: number
  ): Promise<Event[]> {
    const startDate = new Date();
    startDate.setDate(startDate.getDate() - lookbackDays);

    // 获取事件
    const allEvents = await EventDataService.getRelevantEvents({
      symbols: [symbol],
      sectors: [sector],
      startDate,
      importance: [
        EventImportance.CRITICAL,
        EventImportance.HIGH,
        EventImportance.MEDIUM
      ]
    });

    // 按相关性和重要性排序
    return this.sortEventsByRelevance(allEvents, symbol);
  }

  /**
   * 按相关性排序事件
   */
  private static sortEventsByRelevance(
    events: Event[],
    symbol: string
  ): Event[] {
    return events.sort((a, b) => {
      // 1. 直接提到该股票的事件优先
      const aDirectMention = a.symbols?.includes(symbol) ? 1 : 0;
      const bDirectMention = b.symbols?.includes(symbol) ? 1 : 0;
      if (aDirectMention !== bDirectMention) {
        return bDirectMention - aDirectMention;
      }

      // 2. 重要性高的优先
      const importanceOrder = {
        [EventImportance.CRITICAL]: 4,
        [EventImportance.HIGH]: 3,
        [EventImportance.MEDIUM]: 2,
        [EventImportance.LOW]: 1
      };
      const importanceDiff =
        importanceOrder[b.importance] - importanceOrder[a.importance];
      if (importanceDiff !== 0) {
        return importanceDiff;
      }

      // 3. 时间近的优先
      return b.eventTime.getTime() - a.eventTime.getTime();
    });
  }

  /**
   * AI分析(包含事件)
   */
  private static async analyzeStockWithEvents(
    company: CompanyData,
    price: PriceData,
    events: Event[]
  ): Promise<StockAnalysis> {
    const prompt = this.buildStockAnalysisPrompt(company, price, events);

    const response = await ClaudeAdapter.analyze({
      prompt,
      responseSchema: StockAnalysisSchema
    });

    return response;
  }

  /**
   * 构建分析Prompt
   */
  private static buildStockAnalysisPrompt(
    company: CompanyData,
    price: PriceData,
    events: Event[]
  ): string {
    return `
你是资深的股票分析师。请对以下股票进行深度分析。

## 股票信息
- 代码: ${company.symbol}
- 名称: ${company.name}
- 行业: ${company.sector}
- 市值: ${company.marketCap}

## 当前行情
- 价格: ${price.price}
- 涨跌幅: ${price.changePercent}%
- 成交量: ${price.volume}
- 更新时间: ${price.asOf}

## 公司基本面
${this.formatFundamentals(company.fundamentals)}

## 近期相关事件分析

${this.formatEventsForAnalysis(events)}

---

## 请基于以上信息,特别是近期事件对该股票的影响,提供以下分析:

### 1. 综合评估
- 基本面评分(0-100)
- 技术面评分(0-100)
- 事件影响评分(0-100,正面为正,负面为负)
- 综合投资评级(强力买入/买入/持有/卖出/强力卖出)

### 2. 事件影响分析
- 利好事件总结(列出主要利好事件及影响)
- 利空事件总结(列出主要利空事件及影响)
- 整体事件影响评估(利好/利空/中性/复杂)

### 3. 操作建议
- 当前阶段: 买入/持有/观望/减仓/清仓
- 建议理由(100-200字,重点说明事件因素)
- 目标价位
- 止损价位
- 持有期限建议

### 4. 风险提示
- 主要风险因素(结合近期事件)
- 需要关注的未来事件
- 风险等级(低/中/高)

请以JSON格式返回分析结果。
    `;
  }

  /**
   * 格式化事件用于AI分析
   */
  private static formatEventsForAnalysis(events: Event[]): string {
    if (events.length === 0) {
      return '📌 近期无重大相关事件';
    }

    // 按类型分组
    const grouped = this.groupEventsByCategory(events);

    let output = '';

    // 政策事件
    if (grouped.policy.length > 0) {
      output += '\n### 📜 政策事件\n';
      output += grouped.policy
        .map(e => this.formatSingleEvent(e))
        .join('\n');
    }

    // 公司事件
    if (grouped.company.length > 0) {
      output += '\n### 🏢 公司事件\n';
      output += grouped.company
        .map(e => this.formatSingleEvent(e))
        .join('\n');
    }

    // 市场事件
    if (grouped.market.length > 0) {
      output += '\n### 📊 市场事件\n';
      output += grouped.market
        .map(e => this.formatSingleEvent(e))
        .join('\n');
    }

    // 行业事件
    if (grouped.industry.length > 0) {
      output += '\n### 🏭 行业事件\n';
      output += grouped.industry
        .map(e => this.formatSingleEvent(e))
        .join('\n');
    }

    return output;
  }

  /**
   * 格式化单个事件
   */
  private static formatSingleEvent(event: Event): string {
    const importanceIcon = {
      [EventImportance.CRITICAL]: '🔴',
      [EventImportance.HIGH]: '🟠',
      [EventImportance.MEDIUM]: '🟡',
      [EventImportance.LOW]: '⚪'
    };

    const impactIcon = {
      [EventImpactDirection.POSITIVE]: '✅',
      [EventImpactDirection.NEGATIVE]: '❌',
      [EventImpactDirection.NEUTRAL]: 'ℹ️',
      [EventImpactDirection.MIXED]: '⚠️'
    };

    return `
${importanceIcon[event.importance]} ${impactIcon[event.impactDirection]} **${event.title}**
- 时间: ${event.eventTime.toISOString().substring(0, 10)}
- 类型: ${event.subcategory}
- 影响: ${event.impactDirection} (强度: ${event.impactMagnitude}/100)
- 摘要: ${event.summary}
${event.impactSummary ? `- AI评估: ${event.impactSummary}` : ''}
    `.trim();
  }

  /**
   * 按类型分组事件
   */
  private static groupEventsByCategory(events: Event[]): {
    policy: Event[];
    company: Event[];
    market: Event[];
    industry: Event[];
  } {
    return {
      policy: events.filter(e => e.category === EventCategory.POLICY),
      company: events.filter(e => e.category === EventCategory.COMPANY),
      market: events.filter(e => e.category === EventCategory.MARKET),
      industry: events.filter(e => e.category === EventCategory.INDUSTRY)
    };
  }

  /**
   * 事件摘要(用于响应)
   */
  private static summarizeEvents(events: Event[]): EventsSummary {
    const positive = events.filter(
      e => e.impactDirection === EventImpactDirection.POSITIVE
    );
    const negative = events.filter(
      e => e.impactDirection === EventImpactDirection.NEGATIVE
    );

    return {
      total: events.length,
      positive: positive.length,
      negative: negative.length,
      neutral: events.length - positive.length - negative.length,
      avgImpact: events.reduce((sum, e) => {
        const sign = e.impactDirection === EventImpactDirection.POSITIVE ? 1 :
                     e.impactDirection === EventImpactDirection.NEGATIVE ? -1 : 0;
        return sum + (sign * e.impactMagnitude);
      }, 0) / events.length,
      topEvents: events.slice(0, 5)
    };
  }
}
```

---

### 2.2 持仓分析集成

```typescript
// src/services/portfolio.service.ts (增强)

export class PortfolioService {
  /**
   * 收集持仓分析数据(包含事件)
   */
  static async collectPortfolioAnalysisData(params: {
    accountId: number;
    userId: number;
    eventLookbackDays?: number;
  }): Promise<PortfolioAnalysisData> {
    const { accountId, userId, eventLookbackDays = 7 } = params;

    // 1. 获取持仓列表
    const holdings = await PortfolioDataService.getHoldings(
      userId,
      accountId
    );

    // 2. 获取持仓股票的最新价格
    const prices = await MarketDataService.getPricesBatch(
      holdings.map(h => h.symbol)
    );

    // 3. 获取相关事件
    const events = await this.getRelevantEventsForPortfolio(
      holdings,
      eventLookbackDays
    );

    // 4. AI分析持仓(包含事件)
    const analysis = await this.analyzePortfolioWithEvents(
      holdings,
      prices,
      events
    );

    return {
      holdings,
      prices,
      events,
      analysis,
      eventAlerts: this.generateEventAlerts(events, holdings)
    };
  }

  /**
   * 获取持仓相关事件
   */
  private static async getRelevantEventsForPortfolio(
    holdings: Holding[],
    lookbackDays: number
  ): Promise<Event[]> {
    const symbols = holdings.map(h => h.symbol);
    const sectors = [...new Set(
      holdings.map(h => h.sector).filter(Boolean)
    )];

    const startDate = new Date();
    startDate.setDate(startDate.getDate() - lookbackDays);

    // 获取事件(只获取high及以上)
    const events = await EventDataService.getRelevantEvents({
      symbols,
      sectors,
      startDate,
      importance: [EventImportance.CRITICAL, EventImportance.HIGH]
    });

    return events;
  }

  /**
   * AI持仓分析(包含事件)
   */
  private static async analyzePortfolioWithEvents(
    holdings: Holding[],
    prices: Map<string, PriceData>,
    events: Event[]
  ): Promise<PortfolioAnalysis> {
    const prompt = `
你是专业的投资顾问。请分析以下投资组合。

## 持仓概览
${this.formatHoldingsSummary(holdings, prices)}

## 近期重要事件
${this.formatEventsForPortfolio(events, holdings)}

---

## 请提供分析:

### 1. 整体评估
- 组合健康度评分(0-100)
- 风险等级(低/中/高)
- 集中度分析
- 事件影响评估

### 2. 单股建议
为每只持仓股票提供:
- 操作建议(持有/加仓/减仓/清仓)
- 建议理由(结合相关事件)
- 风险提示

### 3. 组合优化建议
- 需要减仓的股票及理由
- 建议增持的板块
- 再平衡建议

### 4. 事件预警
- 需要关注的重大事件
- 可能的风险点
- 建议行动

请以JSON格式返回。
    `;

    const response = await ClaudeAdapter.analyze({
      prompt,
      responseSchema: PortfolioAnalysisSchema
    });

    return response;
  }

  /**
   * 生成事件告警
   */
  private static generateEventAlerts(
    events: Event[],
    holdings: Holding[]
  ): EventAlert[] {
    const alerts: EventAlert[] = [];

    for (const event of events) {
      // 只为critical和high事件生成告警
      if (event.importance !== EventImportance.CRITICAL &&
          event.importance !== EventImportance.HIGH) {
        continue;
      }

      // 找出受影响的持仓
      const affectedHoldings = holdings.filter(h =>
        event.symbols?.includes(h.symbol) ||
        event.sectors?.includes(h.sector)
      );

      if (affectedHoldings.length > 0) {
        alerts.push({
          event,
          affectedSymbols: affectedHoldings.map(h => h.symbol),
          alertLevel: event.importance === EventImportance.CRITICAL
            ? 'critical'
            : 'warning',
          message: this.generateAlertMessage(event, affectedHoldings)
        });
      }
    }

    return alerts;
  }

  /**
   * 生成告警消息
   */
  private static generateAlertMessage(
    event: Event,
    holdings: Holding[]
  ): string {
    const symbolList = holdings.map(h => h.symbol).join(', ');

    if (event.impactDirection === EventImpactDirection.POSITIVE) {
      return `利好消息: ${event.title}。您持有的 ${symbolList} 可能受益。`;
    } else if (event.impactDirection === EventImpactDirection.NEGATIVE) {
      return `风险提示: ${event.title}。您持有的 ${symbolList} 可能受到负面影响,请关注。`;
    } else {
      return `重要事件: ${event.title}。涉及您持有的 ${symbolList}。`;
    }
  }
}
```

---

### 2.3 选股推荐集成

```typescript
// src/services/strategy.service.ts (增强)

export class StrategyService {
  /**
   * 智能选股(包含事件分析)
   */
  static async collectSelectionData(params: {
    sector?: string;
    riskPreference: 'conservative' | 'balanced' | 'aggressive';
    marketCap?: 'large' | 'mid' | 'small';
    count?: number;
    eventLookbackDays?: number;
  }): Promise<StockSelectionData> {
    const { eventLookbackDays = 14, count = 20 } = params;

    // 1. 获取候选股票池
    const candidates = await this.getCandidateStocks(params);

    // 2. 获取相关市场和行业事件
    const events = await this.getRelevantEventsForSelection(
      params.sector,
      eventLookbackDays
    );

    // 3. AI选股分析(结合事件)
    const selections = await this.analyzeStocksWithEvents(
      candidates,
      events,
      params
    );

    // 4. 排序并返回Top N
    const topSelections = selections
      .sort((a, b) => b.score - a.score)
      .slice(0, count);

    return {
      selections: topSelections,
      events,
      marketContext: this.buildMarketContext(events)
    };
  }

  /**
   * 获取选股相关事件
   */
  private static async getRelevantEventsForSelection(
    sector: string | undefined,
    lookbackDays: number
  ): Promise<Event[]> {
    const startDate = new Date();
    startDate.setDate(startDate.getDate() - lookbackDays);

    // 获取市场级事件 + 行业事件
    const events = await EventDataService.getRelevantEvents({
      sectors: sector ? [sector] : undefined,
      startDate,
      importance: [EventImportance.CRITICAL, EventImportance.HIGH],
      categories: [
        EventCategory.POLICY,
        EventCategory.MARKET,
        EventCategory.INDUSTRY
      ]
    });

    return events;
  }

  /**
   * AI选股分析(结合事件)
   */
  private static async analyzeStocksWithEvents(
    candidates: StockCandidate[],
    events: Event[],
    params: any
  ): Promise<StockSelection[]> {
    const prompt = `
你是专业的选股分析师。请基于当前市场环境和事件,推荐优质股票。

## 选股要求
- 行业: ${params.sector || '不限'}
- 风险偏好: ${params.riskPreference}
- 市值范围: ${params.marketCap || '不限'}

## 近期市场环境与事件
${this.formatMarketEvents(events)}

## 候选股票池
${this.formatCandidates(candidates)}

---

## 请为每只候选股票评分(0-100),并说明理由:

评分考虑因素:
1. 基本面质量(30%)
2. 估值合理性(25%)
3. 近期事件影响(25%)
4. 技术面(20%)

请重点关注近期事件对股票的影响,优先推荐受益于政策/行业利好的股票。

返回JSON格式。
    `;

    const response = await ClaudeAdapter.analyze({
      prompt,
      responseSchema: StockSelectionSchema
    });

    return response.selections;
  }

  /**
   * 构建市场环境上下文
   */
  private static buildMarketContext(events: Event[]): MarketContext {
    // 分析政策环境
    const policyEvents = events.filter(
      e => e.category === EventCategory.POLICY
    );
    const policyTone = this.analyzePolicyTone(policyEvents);

    // 分析市场情绪
    const marketEvents = events.filter(
      e => e.category === EventCategory.MARKET
    );
    const marketSentiment = this.analyzeMarketSentiment(marketEvents);

    return {
      policyTone,
      marketSentiment,
      keyEvents: events.slice(0, 5),
      recommendation: this.generateMarketRecommendation(
        policyTone,
        marketSentiment
      )
    };
  }

  /**
   * 分析政策基调
   */
  private static analyzePolicyTone(events: Event[]): PolicyTone {
    if (events.length === 0) return 'neutral';

    const positiveCount = events.filter(
      e => e.impactDirection === EventImpactDirection.POSITIVE
    ).length;

    const ratio = positiveCount / events.length;

    if (ratio >= 0.7) return 'accommodative';      // 宽松
    if (ratio >= 0.4) return 'neutral';            // 中性
    return 'restrictive';                          // 紧缩
  }

  /**
   * 分析市场情绪
   */
  private static analyzeMarketSentiment(events: Event[]): MarketSentiment {
    if (events.length === 0) return 'neutral';

    const avgImpact = events.reduce((sum, e) => {
      const sign = e.impactDirection === EventImpactDirection.POSITIVE ? 1 :
                   e.impactDirection === EventImpactDirection.NEGATIVE ? -1 : 0;
      return sum + (sign * e.impactMagnitude);
    }, 0) / events.length;

    if (avgImpact >= 30) return 'bullish';         // 看多
    if (avgImpact <= -30) return 'bearish';        // 看空
    return 'neutral';                              // 中性
  }
}
```

---

## 3. 事件引用记录

### 3.1 数据库扩展

```sql
-- 在 strategy_analysis 表中记录引用的事件
ALTER TABLE strategy_analysis
  ADD COLUMN related_events JSONB;

-- 示例数据
{
  "events": [
    {
      "event_id": 123,
      "relevance": 0.85,
      "impact_on_analysis": "positive"
    },
    {
      "event_id": 124,
      "relevance": 0.60,
      "impact_on_analysis": "negative"
    }
  ]
}

-- 在 ai_analysis_history 表中记录
ALTER TABLE ai_analysis_history
  ADD COLUMN related_events JSONB;
```

### 3.2 记录事件引用

```typescript
/**
 * 记录策略分析时引用的事件
 */
async function recordEventReferences(
  strategyId: number,
  events: Event[],
  symbol: string
): Promise<void> {
  const references = events.map(event => ({
    event_id: event.id,
    relevance: calculateEventRelevance(event, symbol),
    impact_on_analysis: determineEventImpact(event)
  }));

  await StrategyAnalysisRepository.update(strategyId, {
    related_events: { events: references }
  });
}

/**
 * 计算事件相关性
 */
function calculateEventRelevance(event: Event, symbol: string): number {
  let relevance = 0.5;

  // 直接提到该股票
  if (event.symbols?.includes(symbol)) {
    relevance += 0.3;
  }

  // 重要性加权
  const importanceWeight = {
    [EventImportance.CRITICAL]: 0.2,
    [EventImportance.HIGH]: 0.15,
    [EventImportance.MEDIUM]: 0.1,
    [EventImportance.LOW]: 0
  };
  relevance += importanceWeight[event.importance];

  return Math.min(relevance, 1.0);
}

/**
 * 判断事件对分析的影响
 */
function determineEventImpact(event: Event): string {
  if (event.impactDirection === EventImpactDirection.POSITIVE) {
    return 'positive';
  }
  if (event.impactDirection === EventImpactDirection.NEGATIVE) {
    return 'negative';
  }
  return 'neutral';
}
```

---

## 4. API响应格式

### 4.1 单股分析API响应

```typescript
// GET /api/stocks/:symbol/analysis

{
  "stock": {
    "symbol": "AAPL",
    "name": "Apple Inc.",
    "price": 180.50,
    "changePercent": 2.3
  },

  "events": {
    "summary": {
      "total": 5,
      "positive": 3,
      "negative": 1,
      "neutral": 1,
      "avgImpact": 35.6
    },
    "list": [
      {
        "id": 123,
        "title": "Apple Q4 财报超预期",
        "category": "company",
        "subcategory": "company_earnings",
        "importance": "high",
        "impactDirection": "positive",
        "impactMagnitude": 78,
        "eventTime": "2025-01-13T16:00:00Z",
        "summary": "服务业务增长强劲..."
      }
      // ... 更多事件
    ]
  },

  "analysis": {
    "score": {
      "fundamentals": 85,
      "technicals": 72,
      "events": 78,
      "overall": 80
    },

    "eventImpact": {
      "positiveEvents": [
        {
          "event_id": 123,
          "impact": "财报超预期,服务业务增长强劲"
        }
      ],
      "negativeEvents": [
        {
          "event_id": 124,
          "impact": "欧盟反垄断调查升级"
        }
      ],
      "overallAssessment": "利好因素主导,建议持有或适当加仓"
    },

    "recommendation": {
      "action": "buy",
      "reasoning": "基于近期财报超预期和AI业务进展,建议买入...",
      "targetPrice": 200,
      "stopLoss": 170,
      "timeHorizon": "3-6个月"
    },

    "risks": [
      "欧盟反垄断调查可能导致罚款",
      "关注下季度iPhone销量数据"
    ]
  }
}
```

### 4.2 持仓分析API响应

```typescript
// POST /api/ai/analyze/portfolio

{
  "portfolio": {
    "totalValue": 500000,
    "totalCost": 450000,
    "unrealizedPnL": 50000,
    "unrealizedPnLPercent": 11.11
  },

  "eventAlerts": [
    {
      "level": "warning",
      "event": {
        "id": 125,
        "title": "央行降息50个基点",
        "category": "policy"
      },
      "affectedSymbols": ["ICBC", "CMB"],
      "message": "利好消息: 央行降息50个基点。您持有的 ICBC, CMB 可能受益。"
    }
  ],

  "holdingsAnalysis": [
    {
      "symbol": "AAPL",
      "recommendation": "hold",
      "reasoning": "财报超预期,但估值偏高,建议持有观望",
      "relatedEvents": [
        {
          "event_id": 123,
          "relevance": 0.95,
          "impact": "positive"
        }
      ]
    }
    // ... 更多持仓分析
  ],

  "portfolioAdvice": {
    "overallAssessment": "组合整体健康,受益于近期政策利好",
    "suggestedActions": [
      "银行股受益于降息,可适当加仓",
      "科技股估值偏高,建议部分止盈"
    ]
  }
}
```

---

## 5. 性能优化

### 5.1 事件预加载

```typescript
/**
 * 预加载常用事件到缓存
 */
export async function preloadCommonEvents(): Promise<void> {
  // 加载最近7天的critical/high事件
  const events = await EventDataService.getRelevantEvents({
    startDate: subDays(new Date(), 7),
    importance: [EventImportance.CRITICAL, EventImportance.HIGH]
  });

  // 写入缓存
  await RedisCache.set('events:hot', events, 3600);
}
```

### 5.2 批量事件查询

```typescript
/**
 * 批量获取多只股票的事件
 */
export async function getEventsBatch(
  symbols: string[],
  lookbackDays: number
): Promise<Map<string, Event[]>> {
  const result = new Map<string, Event[]>();

  // 一次性获取所有相关事件
  const allEvents = await EventDataService.getRelevantEvents({
    symbols,
    startDate: subDays(new Date(), lookbackDays),
    importance: [EventImportance.CRITICAL, EventImportance.HIGH, EventImportance.MEDIUM]
  });

  // 按股票分组
  for (const symbol of symbols) {
    const symbolEvents = allEvents.filter(e =>
      e.symbols?.includes(symbol) ||
      e.symbols === null // 市场级事件
    );
    result.set(symbol, symbolEvents);
  }

  return result;
}
```

---

## 6. 监控与度量

### 6.1 事件使用统计

```typescript
/**
 * 记录事件被AI分析引用的次数
 */
export async function trackEventUsage(eventId: number): Promise<void> {
  await RedisCache.increment(`event:usage:${eventId}`);
}

/**
 * 获取热门事件(被引用最多)
 */
export async function getHotEvents(topN: number = 10): Promise<Event[]> {
  // 从Redis获取引用次数最多的事件ID
  // ... 实现逻辑

  return hotEvents;
}
```

### 6.2 事件质量评估

```typescript
/**
 * 评估事件影响预测的准确性
 */
export async function evaluateEventAccuracy(
  eventId: number
): Promise<AccuracyMetrics> {
  const event = await EventRepository.findById(eventId);
  const impacts = await EventImpactRepository.findByEventId(eventId);

  // 对比预期价格变化 vs 实际价格变化
  let totalError = 0;
  let validCount = 0;

  for (const impact of impacts) {
    if (impact.actualPriceChangePercent !== null) {
      const error = Math.abs(
        impact.expectedPriceChangePercent - impact.actualPriceChangePercent
      );
      totalError += error;
      validCount++;
    }
  }

  const mae = validCount > 0 ? totalError / validCount : null;

  return {
    eventId,
    mae,
    validPredictions: validCount,
    totalPredictions: impacts.length
  };
}
```

---

**总结**: 完整的AI分析事件集成方案,涵盖单股分析、持仓分析、选股推荐等多个场景,提供详细的事件获取、格式化、引用记录和性能优化策略。
