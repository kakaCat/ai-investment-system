# EventAdapter 实现设计

**版本**: v1.0
**日期**: 2025-01-14
**目标**: 详细设计EventAdapter和事件分析逻辑的实现

---

## 1. 类型定义 (TypeScript)

### 1.1 枚举类型

```typescript
// src/types/event.types.ts

/**
 * 事件主分类
 */
export enum EventCategory {
  POLICY = 'policy',         // 政策事件
  COMPANY = 'company',       // 公司事件
  MARKET = 'market',         // 市场事件
  INDUSTRY = 'industry'      // 行业事件
}

/**
 * 事件子分类
 */
export enum EventSubcategory {
  // 政策事件
  POLICY_MONETARY = 'policy_monetary',           // 货币政策
  POLICY_FISCAL = 'policy_fiscal',               // 财政政策
  POLICY_REGULATORY = 'policy_regulatory',       // 监管政策
  POLICY_INTERNATIONAL = 'policy_international', // 国际政策

  // 公司事件
  COMPANY_EARNINGS = 'company_earnings',         // 财报相关
  COMPANY_GOVERNANCE = 'company_governance',     // 公司治理
  COMPANY_CAPITAL = 'company_capital',           // 资本运作
  COMPANY_BUSINESS = 'company_business',         // 业务变化

  // 市场事件
  MARKET_INDEX = 'market_index',                 // 指数调整
  MARKET_FLOW = 'market_flow',                   // 资金流动
  MARKET_SENTIMENT = 'market_sentiment',         // 市场情绪
  MARKET_TECHNICAL = 'market_technical',         // 技术突破

  // 行业事件
  INDUSTRY_TECH = 'industry_tech',               // 技术突破
  INDUSTRY_COMPETITION = 'industry_competition', // 竞争格局
  INDUSTRY_SUPPLY = 'industry_supply',           // 供需关系
  INDUSTRY_POLICY = 'industry_policy'            // 行业政策
}

/**
 * 事件重要性
 */
export enum EventImportance {
  CRITICAL = 'critical',  // 极其重要
  HIGH = 'high',          // 高度重要
  MEDIUM = 'medium',      // 中度重要
  LOW = 'low'             // 低度重要
}

/**
 * 事件影响方向
 */
export enum EventImpactDirection {
  POSITIVE = 'positive',  // 利好
  NEGATIVE = 'negative',  // 利空
  NEUTRAL = 'neutral',    // 中性
  MIXED = 'mixed'         // 复杂影响
}
```

### 1.2 接口定义

```typescript
/**
 * 事件数据(原始)
 */
export interface EventData {
  // 基本信息
  title: string;
  summary: string;
  content?: string;
  sourceUrl?: string;

  // 分类信息
  category: EventCategory;
  subcategory: EventSubcategory;
  importance: EventImportance;

  // 影响范围
  symbols?: string[];
  sectors?: string[];
  markets?: string[];

  // 时间信息
  eventTime: Date;
  publishedAt?: Date;

  // 数据源
  source: string;
  externalId?: string;
}

/**
 * 事件实体(数据库)
 */
export interface Event extends EventData {
  id: number;

  // AI分析结果
  impactDirection: EventImpactDirection;
  impactMagnitude: number;
  impactSummary?: string;

  // 影响时间范围
  impactStartDate?: Date;
  impactEndDate?: Date;

  // 处理状态
  processed: boolean;
  idempotencyKey: string;

  // 审计
  createdAt: Date;
  updatedAt: Date;
}

/**
 * 事件对个股的影响
 */
export interface EventStockImpact {
  id?: number;
  eventId: number;
  symbol: string;

  impactDirection: EventImpactDirection;
  impactMagnitude: number;
  impactReason: string;

  expectedPriceChangePercent?: number;
  actualPriceChangePercent?: number;

  analyzedAt: Date;
}

/**
 * AI事件分析结果
 */
export interface EventAnalysisResult {
  direction: EventImpactDirection;
  magnitude: number;
  summary: string;
  confidence: number;
  reasoning: string;
}

/**
 * AI个股影响分析结果
 */
export interface EventImpactAnalysisResult {
  direction: EventImpactDirection;
  magnitude: number;
  reason: string;
  expectedChange: number;
  confidence: number;
}
```

---

## 2. EventAdapter 实现

### 2.1 基础适配器

```typescript
// src/adapters/event.adapter.ts

import { EventData, EventCategory, EventImportance } from '../types/event.types';
import { MCPClient } from './mcp-client';
import { BusinessException } from '../exceptions/business.exception';

/**
 * EventAdapter: 事件数据适配器
 *
 * 职责:
 * 1. 从MCP服务获取各类事件数据
 * 2. 统一事件数据格式
 * 3. 事件去重与幂等性保证
 */
export class EventAdapter {
  private static mcpClient: MCPClient;

  /**
   * 初始化MCP客户端
   */
  static initialize(mcpServerUrl: string): void {
    this.mcpClient = new MCPClient(mcpServerUrl);
  }

  /**
   * 获取最新事件
   *
   * @param params 查询参数
   * @returns 事件列表
   */
  static async fetchRecentEvents(params: {
    startTime: Date;
    endTime?: Date;
    categories?: EventCategory[];
    symbols?: string[];
    markets?: string[];
  }): Promise<EventData[]> {
    try {
      // 1. 调用MCP服务获取原始事件数据
      const rawEvents = await this.mcpClient.call('events.getRecent', {
        start_time: params.startTime.toISOString(),
        end_time: params.endTime?.toISOString() || new Date().toISOString(),
        categories: params.categories,
        symbols: params.symbols,
        markets: params.markets
      });

      // 2. 转换为标准格式
      const events = this.transformEvents(rawEvents);

      // 3. 返回结果
      return events;
    } catch (error) {
      throw new BusinessException(`事件数据获取失败: ${error.message}`);
    }
  }

  /**
   * 获取单个股票相关事件
   *
   * @param symbol 股票代码
   * @param lookbackDays 回溯天数
   * @returns 事件列表
   */
  static async fetchSymbolEvents(
    symbol: string,
    lookbackDays: number = 30
  ): Promise<EventData[]> {
    const endTime = new Date();
    const startTime = new Date();
    startTime.setDate(startTime.getDate() - lookbackDays);

    try {
      // 1. 调用MCP服务
      const rawEvents = await this.mcpClient.call('events.getBySymbol', {
        symbol,
        start_time: startTime.toISOString(),
        end_time: endTime.toISOString()
      });

      // 2. 转换格式
      const events = this.transformEvents(rawEvents);

      // 3. 过滤相关性低的事件
      return this.filterRelevantEvents(events, symbol);
    } catch (error) {
      throw new BusinessException(`股票事件获取失败: ${error.message}`);
    }
  }

  /**
   * 获取行业相关事件
   *
   * @param sector 行业
   * @param lookbackDays 回溯天数
   * @returns 事件列表
   */
  static async fetchSectorEvents(
    sector: string,
    lookbackDays: number = 30
  ): Promise<EventData[]> {
    const endTime = new Date();
    const startTime = new Date();
    startTime.setDate(startTime.getDate() - lookbackDays);

    try {
      const rawEvents = await this.mcpClient.call('events.getBySector', {
        sector,
        start_time: startTime.toISOString(),
        end_time: endTime.toISOString()
      });

      return this.transformEvents(rawEvents);
    } catch (error) {
      throw new BusinessException(`行业事件获取失败: ${error.message}`);
    }
  }

  /**
   * 获取市场级事件
   *
   * @param market 市场代码
   * @param lookbackDays 回溯天数
   * @returns 事件列表
   */
  static async fetchMarketEvents(
    market: string,
    lookbackDays: number = 30
  ): Promise<EventData[]> {
    const endTime = new Date();
    const startTime = new Date();
    startTime.setDate(startTime.getDate() - lookbackDays);

    try {
      const rawEvents = await this.mcpClient.call('events.getByMarket', {
        market,
        start_time: startTime.toISOString(),
        end_time: endTime.toISOString()
      });

      return this.transformEvents(rawEvents);
    } catch (error) {
      throw new BusinessException(`市场事件获取失败: ${error.message}`);
    }
  }

  /**
   * 转换MCP原始事件数据为标准格式
   *
   * @param rawEvents MCP原始事件
   * @returns 标准事件列表
   */
  private static transformEvents(rawEvents: any[]): EventData[] {
    return rawEvents.map(raw => this.transformSingleEvent(raw));
  }

  /**
   * 转换单个事件
   */
  private static transformSingleEvent(raw: any): EventData {
    return {
      title: raw.title || raw.headline,
      summary: raw.summary || raw.description || '',
      content: raw.content || raw.body,
      sourceUrl: raw.url || raw.link,

      category: this.mapCategory(raw.category || raw.type),
      subcategory: this.mapSubcategory(raw.subcategory || raw.subtype),
      importance: this.mapImportance(raw.importance || raw.priority),

      symbols: raw.symbols || raw.tickers || [],
      sectors: raw.sectors || raw.industries || [],
      markets: raw.markets || raw.exchanges || [],

      eventTime: new Date(raw.event_time || raw.timestamp || raw.published_at),
      publishedAt: raw.published_at ? new Date(raw.published_at) : undefined,

      source: raw.source || 'mcp',
      externalId: raw.id || raw.external_id
    };
  }

  /**
   * 映射事件主分类
   */
  private static mapCategory(category: string): EventCategory {
    const mapping: Record<string, EventCategory> = {
      'policy': EventCategory.POLICY,
      'government': EventCategory.POLICY,
      'company': EventCategory.COMPANY,
      'corporate': EventCategory.COMPANY,
      'market': EventCategory.MARKET,
      'industry': EventCategory.INDUSTRY,
      'sector': EventCategory.INDUSTRY
    };

    const normalized = category?.toLowerCase() || '';
    return mapping[normalized] || EventCategory.MARKET;
  }

  /**
   * 映射事件子分类
   */
  private static mapSubcategory(subcategory: string): EventSubcategory {
    const normalized = subcategory?.toLowerCase() || '';

    // 简单映射逻辑,实际可以更复杂
    if (normalized.includes('monetary') || normalized.includes('interest')) {
      return EventSubcategory.POLICY_MONETARY;
    }
    if (normalized.includes('earnings') || normalized.includes('financial')) {
      return EventSubcategory.COMPANY_EARNINGS;
    }
    if (normalized.includes('merger') || normalized.includes('acquisition')) {
      return EventSubcategory.COMPANY_CAPITAL;
    }

    // 默认返回第一个子类型
    return EventSubcategory.MARKET_SENTIMENT;
  }

  /**
   * 映射事件重要性
   */
  private static mapImportance(importance: string | number): EventImportance {
    if (typeof importance === 'number') {
      if (importance >= 90) return EventImportance.CRITICAL;
      if (importance >= 70) return EventImportance.HIGH;
      if (importance >= 40) return EventImportance.MEDIUM;
      return EventImportance.LOW;
    }

    const normalized = importance?.toLowerCase() || '';
    const mapping: Record<string, EventImportance> = {
      'critical': EventImportance.CRITICAL,
      'urgent': EventImportance.CRITICAL,
      'high': EventImportance.HIGH,
      'important': EventImportance.HIGH,
      'medium': EventImportance.MEDIUM,
      'moderate': EventImportance.MEDIUM,
      'low': EventImportance.LOW,
      'minor': EventImportance.LOW
    };

    return mapping[normalized] || EventImportance.MEDIUM;
  }

  /**
   * 过滤相关性低的事件
   *
   * @param events 事件列表
   * @param symbol 股票代码
   * @returns 过滤后的事件列表
   */
  private static filterRelevantEvents(
    events: EventData[],
    symbol: string
  ): EventData[] {
    return events.filter(event => {
      // 直接提到该股票 -> 保留
      if (event.symbols?.includes(symbol)) {
        return true;
      }

      // 重要性高的事件 -> 保留
      if (event.importance === EventImportance.CRITICAL) {
        return true;
      }

      // 其他低相关性事件 -> 过滤
      return false;
    });
  }

  /**
   * 生成幂等键
   *
   * @param event 事件数据
   * @returns 幂等键
   */
  static generateIdempotencyKey(event: EventData): string {
    const crypto = require('crypto');

    const input = [
      event.externalId || '',
      event.title,
      event.eventTime.toISOString(),
      event.source
    ].join('|');

    return crypto
      .createHash('sha256')
      .update(input)
      .digest('hex')
      .substring(0, 64);
  }
}
```

---

## 3. ClaudeAdapter 事件分析扩展

### 3.1 事件影响分析

```typescript
// src/adapters/claude.adapter.ts (扩展)

import Anthropic from '@anthropic-ai/sdk';
import {
  Event,
  EventAnalysisResult,
  EventImpactAnalysisResult,
  EventImpactDirection
} from '../types/event.types';
import { CompanyData, PriceData } from '../types/market.types';

export class ClaudeAdapter {
  private static client: Anthropic;

  static initialize(apiKey: string): void {
    this.client = new Anthropic({ apiKey });
  }

  /**
   * 分析事件影响(通用)
   *
   * @param event 事件数据
   * @returns 分析结果
   */
  static async analyzeEvent(event: EventData): Promise<EventAnalysisResult> {
    const prompt = `
你是专业的金融分析师。请分析以下事件的影响:

## 事件信息
- 标题: ${event.title}
- 摘要: ${event.summary}
${event.content ? `- 详情: ${event.content.substring(0, 500)}...` : ''}
- 类型: ${event.category} / ${event.subcategory}
- 时间: ${event.eventTime.toISOString()}
${event.symbols ? `- 涉及股票: ${event.symbols.join(', ')}` : ''}
${event.sectors ? `- 涉及行业: ${event.sectors.join(', ')}` : ''}

## 请分析:
1. 影响方向(positive/negative/neutral/mixed)
2. 影响强度(0-100,数值越大影响越大)
3. 影响摘要(100字以内)
4. 分析依据
5. 置信度(0-1)

请以JSON格式返回:
{
  "direction": "positive|negative|neutral|mixed",
  "magnitude": 75,
  "summary": "...",
  "reasoning": "...",
  "confidence": 0.85
}
`;

    try {
      const response = await this.client.messages.create({
        model: 'claude-sonnet-4-5-20250929',
        max_tokens: 1024,
        messages: [{
          role: 'user',
          content: prompt
        }]
      });

      const textContent = response.content.find(c => c.type === 'text');
      if (!textContent || textContent.type !== 'text') {
        throw new Error('AI返回格式错误');
      }

      const result = JSON.parse(textContent.text);

      return {
        direction: result.direction as EventImpactDirection,
        magnitude: result.magnitude,
        summary: result.summary,
        confidence: result.confidence,
        reasoning: result.reasoning
      };
    } catch (error) {
      // 降级: 返回默认值
      return {
        direction: EventImpactDirection.NEUTRAL,
        magnitude: 50,
        summary: '分析失败,请稍后重试',
        confidence: 0,
        reasoning: error.message
      };
    }
  }

  /**
   * 分析事件对单只股票的影响
   *
   * @param params 分析参数
   * @returns 影响分析结果
   */
  static async analyzeEventImpact(params: {
    event: Event;
    company: CompanyData;
    price: PriceData;
  }): Promise<EventImpactAnalysisResult> {
    const { event, company, price } = params;

    const prompt = `
你是专业的股票分析师。请分析以下事件对特定股票的影响:

## 事件信息
- 标题: ${event.title}
- 摘要: ${event.summary}
- 类型: ${event.category} / ${event.subcategory}
- 重要性: ${event.importance}
- 时间: ${event.eventTime.toISOString()}

## 股票信息
- 代码: ${company.symbol}
- 名称: ${company.name}
- 行业: ${company.sector}
- 当前价格: ${price.price}
- 涨跌幅: ${price.changePercent}%

## 公司基本面
${JSON.stringify(company.fundamentals, null, 2)}

## 请分析:
1. 该事件对这只股票的影响方向
2. 影响强度(0-100)
3. 影响原因(为什么会有这个影响)
4. 预期价格变化百分比
5. 置信度(0-1)

请以JSON格式返回:
{
  "direction": "positive|negative|neutral|mixed",
  "magnitude": 75,
  "reason": "...",
  "expectedChange": 5.2,
  "confidence": 0.80
}
`;

    try {
      const response = await this.client.messages.create({
        model: 'claude-sonnet-4-5-20250929',
        max_tokens: 1024,
        messages: [{
          role: 'user',
          content: prompt
        }]
      });

      const textContent = response.content.find(c => c.type === 'text');
      if (!textContent || textContent.type !== 'text') {
        throw new Error('AI返回格式错误');
      }

      const result = JSON.parse(textContent.text);

      return {
        direction: result.direction as EventImpactDirection,
        magnitude: result.magnitude,
        reason: result.reason,
        expectedChange: result.expectedChange,
        confidence: result.confidence
      };
    } catch (error) {
      // 降级
      return {
        direction: EventImpactDirection.NEUTRAL,
        magnitude: 0,
        reason: '分析失败',
        expectedChange: 0,
        confidence: 0
      };
    }
  }

  /**
   * 批量分析多个事件(优化版本,减少API调用)
   *
   * @param events 事件列表
   * @returns 分析结果列表
   */
  static async analyzEventsBatch(
    events: EventData[]
  ): Promise<EventAnalysisResult[]> {
    // 分批处理,每批5个事件
    const batchSize = 5;
    const results: EventAnalysisResult[] = [];

    for (let i = 0; i < events.length; i += batchSize) {
      const batch = events.slice(i, i + batchSize);

      const prompt = `
你是专业的金融分析师。请批量分析以下${batch.length}个事件的影响:

${batch.map((e, idx) => `
## 事件${idx + 1}
- 标题: ${e.title}
- 摘要: ${e.summary}
- 类型: ${e.category} / ${e.subcategory}
- 时间: ${e.eventTime.toISOString()}
${e.symbols ? `- 涉及股票: ${e.symbols.join(', ')}` : ''}
`).join('\n')}

请为每个事件返回JSON格式的分析:
[
  {
    "eventIndex": 0,
    "direction": "positive|negative|neutral|mixed",
    "magnitude": 75,
    "summary": "...",
    "reasoning": "...",
    "confidence": 0.85
  },
  ...
]
`;

      try {
        const response = await this.client.messages.create({
          model: 'claude-sonnet-4-5-20250929',
          max_tokens: 4096,
          messages: [{
            role: 'user',
            content: prompt
          }]
        });

        const textContent = response.content.find(c => c.type === 'text');
        if (textContent && textContent.type === 'text') {
          const batchResults = JSON.parse(textContent.text);
          results.push(...batchResults.map((r: any) => ({
            direction: r.direction as EventImpactDirection,
            magnitude: r.magnitude,
            summary: r.summary,
            confidence: r.confidence,
            reasoning: r.reasoning
          })));
        }
      } catch (error) {
        // 降级: 为这批事件返回默认值
        results.push(...batch.map(() => ({
          direction: EventImpactDirection.NEUTRAL,
          magnitude: 50,
          summary: '批量分析失败',
          confidence: 0,
          reasoning: error.message
        })));
      }
    }

    return results;
  }
}
```

---

## 4. EventDataService 实现

```typescript
// src/services/event-data.service.ts

import {
  Event,
  EventData,
  EventStockImpact,
  EventCategory,
  EventImportance
} from '../types/event.types';
import { EventRepository } from '../repositories/event.repository';
import { EventImpactRepository } from '../repositories/event-impact.repository';
import { EventAdapter } from '../adapters/event.adapter';
import { RedisCache } from '../infrastructure/redis-cache';

/**
 * EventDataService: 事件数据服务
 *
 * 职责:
 * 1. 聚合事件数据访问
 * 2. 统一管理缓存策略
 * 3. 先读缓存,miss时通过Adapter拉取并落库
 */
export class EventDataService {
  private static cache: RedisCache;

  static initialize(redisClient: any): void {
    this.cache = new RedisCache(redisClient);
  }

  /**
   * 获取相关事件
   *
   * 策略: 缓存优先 -> 数据库 -> MCP拉取并落库
   *
   * @param params 查询参数
   * @returns 事件列表
   */
  static async getRelevantEvents(params: {
    symbols?: string[];
    sectors?: string[];
    startDate: Date;
    endDate?: Date;
    importance?: EventImportance[];
    categories?: EventCategory[];
  }): Promise<Event[]> {
    // 1. 生成缓存键
    const cacheKey = this.generateCacheKey(params);

    // 2. 尝试从缓存读取
    const cached = await this.cache.get<Event[]>(cacheKey);
    if (cached) {
      return cached;
    }

    // 3. 从数据库读取
    let events = await EventRepository.findByParams({
      symbols: params.symbols,
      sectors: params.sectors,
      startTime: params.startDate,
      endTime: params.endDate || new Date(),
      importance: params.importance,
      categories: params.categories
    });

    // 4. 如果数据库中没有或数据不新鲜,从MCP拉取
    const isStale = this.isDataStale(events, params);
    if (events.length === 0 || isStale) {
      // 从MCP拉取
      const newEvents = await EventAdapter.fetchRecentEvents({
        startTime: params.startDate,
        endTime: params.endTime,
        categories: params.categories,
        symbols: params.symbols,
        markets: undefined
      });

      // 保存到数据库
      if (newEvents.length > 0) {
        await this.saveEvents(newEvents);

        // 重新查询
        events = await EventRepository.findByParams({
          symbols: params.symbols,
          sectors: params.sectors,
          startTime: params.startDate,
          endTime: params.endTime || new Date(),
          importance: params.importance,
          categories: params.categories
        });
      }
    }

    // 5. 写入缓存(TTL: 1小时)
    await this.cache.set(cacheKey, events, 3600);

    return events;
  }

  /**
   * 保存事件(带去重)
   *
   * @param eventsData 事件数据列表
   */
  static async saveEvents(eventsData: EventData[]): Promise<void> {
    for (const eventData of eventsData) {
      // 生成幂等键
      const idempotencyKey = EventAdapter.generateIdempotencyKey(eventData);

      // 检查是否已存在
      const existing = await EventRepository.findByIdempotencyKey(
        idempotencyKey
      );

      if (!existing) {
        // 新事件,插入
        await EventRepository.create({
          ...eventData,
          idempotencyKey,
          processed: false,
          impactDirection: 'neutral' as any, // 初始值,待AI分析
          impactMagnitude: 0
        });
      } else {
        // 已存在,跳过或更新
        // 可选: 更新部分字段(如content)
      }
    }
  }

  /**
   * 获取事件影响分析
   *
   * @param eventId 事件ID
   * @param symbols 股票代码列表(可选)
   * @returns 影响分析列表
   */
  static async getEventImpacts(
    eventId: number,
    symbols?: string[]
  ): Promise<EventStockImpact[]> {
    return EventImpactRepository.findByEventId(eventId, symbols);
  }

  /**
   * 保存事件影响分析
   *
   * @param impacts 影响分析列表
   */
  static async saveEventImpacts(
    impacts: EventStockImpact[]
  ): Promise<void> {
    for (const impact of impacts) {
      await EventImpactRepository.upsert(impact);
    }
  }

  /**
   * 生成缓存键
   */
  private static generateCacheKey(params: any): string {
    const parts = [
      'events',
      params.symbols?.sort().join(',') || 'all',
      params.sectors?.sort().join(',') || 'all',
      params.startDate.toISOString(),
      params.endDate?.toISOString() || 'now',
      params.importance?.sort().join(',') || 'all',
      params.categories?.sort().join(',') || 'all'
    ];

    return parts.join(':');
  }

  /**
   * 判断数据是否过时
   */
  private static isDataStale(events: Event[], params: any): boolean {
    if (events.length === 0) return true;

    // 如果请求的是最近的数据(endDate未指定或是当前时间)
    const isRecentRequest = !params.endDate ||
      (new Date().getTime() - params.endDate.getTime()) < 3600000; // 1小时内

    if (!isRecentRequest) {
      // 历史数据,不算过时
      return false;
    }

    // 检查最新事件的时间
    const latestEvent = events.reduce((latest, e) =>
      e.createdAt > latest.createdAt ? e : latest
    , events[0]);

    const now = new Date();
    const ageMinutes = (now.getTime() - latestEvent.createdAt.getTime()) / 60000;

    // 如果最新事件是30分钟前创建的,认为数据过时
    return ageMinutes > 30;
  }
}
```

---

## 5. 事件去重策略

### 5.1 幂等键生成

```typescript
/**
 * 生成幂等键的详细逻辑
 */
export function generateEventIdempotencyKey(event: EventData): string {
  const crypto = require('crypto');

  // 使用外部ID(如果有)
  if (event.externalId) {
    return crypto
      .createHash('sha256')
      .update(`external:${event.externalId}:${event.source}`)
      .digest('hex')
      .substring(0, 64);
  }

  // 否则使用标题+时间+来源
  const input = [
    event.title,
    event.eventTime.toISOString().substring(0, 10), // 只取日期部分
    event.source
  ].join('|');

  return crypto
    .createHash('sha256')
    .update(input)
    .digest('hex')
    .substring(0, 64);
}
```

### 5.2 相似事件检测

```typescript
/**
 * 检测相似事件(避免重复)
 */
export async function detectSimilarEvents(
  newEvent: EventData,
  lookbackHours: number = 24
): Promise<Event | null> {
  // 1. 查询时间窗口内的事件
  const startTime = new Date(newEvent.eventTime.getTime() - lookbackHours * 3600000);
  const existingEvents = await EventRepository.findByTimeRange(
    startTime,
    newEvent.eventTime
  );

  // 2. 计算标题相似度
  for (const existing of existingEvents) {
    const similarity = calculateTextSimilarity(
      newEvent.title,
      existing.title
    );

    // 相似度>80%,认为是相同事件
    if (similarity > 0.8) {
      return existing;
    }
  }

  return null;
}

/**
 * 计算文本相似度(简单版本,使用Jaccard相似度)
 */
function calculateTextSimilarity(text1: string, text2: string): number {
  const set1 = new Set(text1.toLowerCase().split(/\s+/));
  const set2 = new Set(text2.toLowerCase().split(/\s+/));

  const intersection = new Set(
    [...set1].filter(x => set2.has(x))
  );

  const union = new Set([...set1, ...set2]);

  return intersection.size / union.size;
}
```

---

## 6. 性能优化

### 6.1 批量处理

```typescript
/**
 * 批量保存事件(事务)
 */
export async function batchSaveEvents(
  events: EventData[]
): Promise<void> {
  // 使用数据库事务
  await db.transaction(async (trx) => {
    for (const event of events) {
      const idempotencyKey = generateEventIdempotencyKey(event);

      // 使用 INSERT ... ON CONFLICT DO NOTHING (PostgreSQL)
      await trx.raw(`
        INSERT INTO events (
          title, summary, content, source_url,
          category, subcategory, importance,
          symbols, sectors, markets,
          impact_direction, impact_magnitude,
          event_time, published_at,
          source, external_id,
          idempotency_key,
          processed
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT (idempotency_key) DO NOTHING
      `, [
        event.title,
        event.summary,
        event.content,
        event.sourceUrl,
        event.category,
        event.subcategory,
        event.importance,
        JSON.stringify(event.symbols || []),
        JSON.stringify(event.sectors || []),
        JSON.stringify(event.markets || []),
        'neutral',
        0,
        event.eventTime,
        event.publishedAt,
        event.source,
        event.externalId,
        idempotencyKey,
        false
      ]);
    }
  });
}
```

### 6.2 缓存策略

```typescript
/**
 * 多级缓存策略
 */
export class EventCacheStrategy {
  /**
   * L1缓存: 内存(最近1000个事件)
   */
  private static memCache = new Map<string, Event>();

  /**
   * L2缓存: Redis(7天内的critical/high事件)
   */
  static async getCriticalEvents(
    startDate: Date,
    endDate: Date
  ): Promise<Event[]> {
    const cacheKey = `critical:${startDate.toISOString()}:${endDate.toISOString()}`;

    // 1. 尝试Redis
    const cached = await RedisCache.get<Event[]>(cacheKey);
    if (cached) return cached;

    // 2. 查询数据库
    const events = await EventRepository.findByParams({
      startTime: startDate,
      endTime: endDate,
      importance: [EventImportance.CRITICAL, EventImportance.HIGH]
    });

    // 3. 写入Redis(TTL: 1小时)
    await RedisCache.set(cacheKey, events, 3600);

    return events;
  }
}
```

---

## 7. 错误处理与降级

```typescript
/**
 * 带重试和降级的事件获取
 */
export async function fetchEventsWithRetry(
  params: any,
  maxRetries: number = 3
): Promise<EventData[]> {
  let lastError: Error;

  for (let i = 0; i < maxRetries; i++) {
    try {
      return await EventAdapter.fetchRecentEvents(params);
    } catch (error) {
      lastError = error;

      // 指数退避
      const delay = Math.pow(2, i) * 1000;
      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }

  // 降级: 返回数据库中的历史数据
  console.error('事件获取失败,降级到数据库查询', lastError);

  return EventRepository.findByParams({
    startTime: params.startTime,
    endTime: params.endTime || new Date(),
    categories: params.categories
  });
}
```

---

**总结**: EventAdapter和事件分析逻辑的详细实现设计,包括类型定义、数据转换、AI分析集成、缓存策略、性能优化和错误处理。
