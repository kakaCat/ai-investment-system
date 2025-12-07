/**
 * 事件类别
 */
export type EventCategory = 'policy' | 'company' | 'market' | 'industry'

/**
 * 事件子类型
 */
export type EventSubtype =
  // 政策事件
  | 'monetary_policy' // 货币政策
  | 'fiscal_policy' // 财政政策
  | 'regulatory_policy' // 监管政策
  | 'international_policy' // 国际政策
  // 公司事件
  | 'earnings' // 财报发布
  | 'dividend' // 分红派息
  | 'ma' // 并购重组
  | 'governance' // 公司治理
  // 市场事件
  | 'index_volatility' // 指数波动
  | 'sector_rotation' // 板块轮动
  | 'sentiment_shift' // 情绪转向
  | 'liquidity_change' // 流动性变化
  // 行业事件
  | 'tech_change' // 技术变革
  | 'regulatory_shift' // 监管变化
  | 'competitive_dynamics' // 竞争格局
  | 'demand_supply' // 供需变化

/**
 * 事件重要性级别（对应PRD中的EventImportance）
 */
export type EventImportance = 'critical' | 'high' | 'medium' | 'low'

/**
 * 事件影响方向
 */
export type ImpactDirection = 'positive' | 'negative' | 'neutral' | 'mixed'

/**
 * 影响级别
 */
export type ImpactLevel = 1 | 2 | 3 | 4 | 5

/**
 * 市场类型
 */
export type MarketType = 'CN' | 'HK' | 'US'

/**
 * 事件影响
 */
export interface EventImpact {
  short_term: ImpactLevel // 短期影响 (1-3月)
  mid_term: ImpactLevel // 中期影响 (3-12月)
  long_term: ImpactLevel // 长期影响 (>12月)
  confidence: number // 置信度 (0-1)
  reasoning?: string // AI分析理由
}

/**
 * 持仓影响详情
 */
export interface HoldingImpact {
  symbol: string // 股票代码
  stock_name: string // 股票名称
  expected_change_percent: number // 预期变化百分比
  impact_direction: ImpactDirection // 影响方向
}

/**
 * 事件基本信息（匹配最新PRD）
 */
export interface Event {
  event_id: number
  title: string // 事件标题
  summary: string // 事件摘要
  category: EventCategory // 事件类别
  subtype: EventSubtype // 事件子类型
  importance: EventImportance // 重要性级别

  // 影响分析
  impact_direction: ImpactDirection // 影响方向
  impact_magnitude: number // 影响强度 (0-100)
  impact_summary?: string // 影响摘要（AI生成）

  // 影响范围
  symbols?: string[] // 受影响的股票代码
  sectors?: string[] // 受影响的行业
  markets?: MarketType[] // 受影响的市场

  // 时间信息
  event_time: string // 事件发生时间
  published_at?: string // 发布时间
  created_at: string // 记录创建时间

  // 数据源
  source_url?: string // 新闻链接
  source: string // 数据源（mcp/manual/user）

  // 用户状态
  is_read?: boolean // 是否已读
  read_at?: string // 已读时间

  // 持仓影响（如果影响用户持仓）
  holding_impacts?: HoldingImpact[] // 对用户持仓的影响
  ai_suggestion?: string // AI操作建议

  // 旧字段兼容（逐步废弃）
  description?: string // 事件描述（兼容旧代码）
  event_date?: string // 事件发生日期（兼容旧代码）
  ai_impact?: EventImpact // AI影响评估（兼容旧代码）
  related_stocks?: string[] // 关联股票代码（兼容旧代码）
  is_processed?: boolean // 是否已处理（兼容旧代码）
  is_followed?: boolean // 是否关注（兼容旧代码）
}

/**
 * 事件详情
 */
export interface EventDetail extends Event {
  content: string // 事件详细内容
  timeline: EventTimelineItem[] // 事件时间线
  related_events?: Event[] // 相关事件
  user_notes?: string // 用户备注
}

/**
 * 事件时间线项
 */
export interface EventTimelineItem {
  date: string
  title: string
  description: string
}

/**
 * 事件查询参数
 */
export interface EventQueryParams {
  category?: EventCategory
  subtype?: EventSubtype
  start_date?: string
  end_date?: string
  related_stock?: string
  page?: number
  page_size?: number
}

/**
 * 事件查询响应
 */
export interface EventQueryResponse {
  total: number
  page: number
  page_size: number
  list: Event[]
}

/**
 * 事件类别标签映射
 */
export const EVENT_CATEGORY_LABELS: Record<EventCategory, string> = {
  policy: '政策事件',
  company: '公司事件',
  market: '市场事件',
  industry: '行业事件'
}

/**
 * 事件子类型标签映射
 */
export const EVENT_SUBTYPE_LABELS: Record<EventSubtype, string> = {
  monetary_policy: '货币政策',
  fiscal_policy: '财政政策',
  regulatory_policy: '监管政策',
  international_policy: '国际政策',
  earnings: '财报发布',
  dividend: '分红派息',
  ma: '并购重组',
  governance: '公司治理',
  index_volatility: '指数波动',
  sector_rotation: '板块轮动',
  sentiment_shift: '情绪转向',
  liquidity_change: '流动性变化',
  tech_change: '技术变革',
  regulatory_shift: '监管变化',
  competitive_dynamics: '竞争格局',
  demand_supply: '供需变化'
}

/**
 * 影响级别标签映射
 */
export const IMPACT_LEVEL_LABELS: Record<ImpactLevel, string> = {
  1: '极低',
  2: '较低',
  3: '中等',
  4: '较高',
  5: '极高'
}

/**
 * 影响级别颜色映射
 */
export const IMPACT_LEVEL_COLORS: Record<ImpactLevel, string> = {
  1: '#67c23a',
  2: '#95d475',
  3: '#e6a23c',
  4: '#f56c6c',
  5: '#d03050'
}

/**
 * 事件重要性级别标签
 */
export const IMPORTANCE_LABELS: Record<EventImportance, string> = {
  critical: '极其重要',
  high: '高度重要',
  medium: '中度重要',
  low: '低度重要'
}

/**
 * 事件重要性级别颜色
 */
export const IMPORTANCE_COLORS: Record<EventImportance, string> = {
  critical: '#d03050', // 红色
  high: '#f56c6c', // 橙色
  medium: '#e6a23c', // 黄色
  low: '#67c23a' // 绿色
}

/**
 * 影响方向标签
 */
export const IMPACT_DIRECTION_LABELS: Record<ImpactDirection, string> = {
  positive: '利好',
  negative: '利空',
  neutral: '中性',
  mixed: '复杂影响'
}

/**
 * 影响方向图标
 */
export const IMPACT_DIRECTION_ICONS: Record<ImpactDirection, string> = {
  positive: '📈',
  negative: '📉',
  neutral: '➖',
  mixed: '🔀'
}

/**
 * 市场类型标签
 */
export const MARKET_TYPE_LABELS: Record<MarketType, string> = {
  CN: 'A股',
  HK: '港股',
  US: '美股'
}
