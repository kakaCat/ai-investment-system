/**
 * AI功能相关API
 *
 * 包括：
 * - 单股AI分析
 * - AI对话
 * - 批量AI分析
 * - 每日市场复盘
 * - 投资策略生成
 */

import { post } from './request'

// ==================== 类型定义 ====================

/**
 * 单股AI分析请求
 */
export interface SingleAnalysisRequest {
  symbol: string
  stock_name?: string
  dimensions?: string[]  // fundamental, technical, valuation
  include_fundamentals?: boolean
  include_technicals?: boolean
}

/**
 * AI评分
 */
export interface AIScore {
  overall_score: number           // 综合评分 0-100
  fundamental_score?: number      // 基本面评分
  technical_score?: number        // 技术面评分
  valuation_score?: number        // 估值评分
  scores_by_dimension?: Record<string, number>
}

/**
 * 单股AI分析响应
 */
export interface SingleAnalysisResponse {
  symbol: string
  stock_name: string
  ai_score: AIScore
  ai_suggestion: string           // AI建议
  ai_reasoning?: string           // AI推理过程
  confidence_level: number        // 置信度 0-100
  dimensions_analyzed: string[]   // 分析的维度
  data_source?: string            // 数据来源 (tushare/akshare/mock)
  created_at: string
}

/**
 * AI对话请求
 */
export interface ChatRequest {
  message: string
  context?: Array<{
    role: 'user' | 'assistant'
    content: string
  }>
  symbol?: string       // 可选：当前讨论的股票代码
  stock_name?: string   // 可选：股票名称
}

/**
 * AI对话响应
 */
export interface ChatResponse {
  reply: string                   // AI回复
  conversation_id?: string        // 会话ID（用于多轮对话）
  created_at: string
}

/**
 * 批量AI分析请求
 */
export interface BatchAnalysisRequest {
  symbols: string[]               // 股票代码列表
  dimensions?: string[]
}

/**
 * 批量分析单项结果
 */
export interface BatchAnalysisItem {
  symbol: string
  stock_name: string
  ai_score: AIScore
  ai_suggestion: string
  confidence_level: number
  status: 'completed' | 'analyzing' | 'failed'
  error?: string
}

/**
 * 批量AI分析响应
 */
export interface BatchAnalysisResponse {
  results: BatchAnalysisItem[]
  progress: {
    completed: number
    total: number
    percentage: number
  }
  created_at: string
}

/**
 * 每日市场复盘请求
 */
export interface DailyReviewRequest {
  date?: string  // 可选：指定日期 YYYY-MM-DD，默认今天
}

/**
 * 每日市场复盘响应
 */
export interface DailyReviewResponse {
  market_summary: string          // 市场总结
  key_events: string[]            // 关键事件列表
  sector_performance: Record<string, {
    change_percent: number
    description: string
  }>
  top_gainers: Array<{
    symbol: string
    name: string
    change_percent: number
  }>
  top_losers: Array<{
    symbol: string
    name: string
    change_percent: number
  }>
  tomorrow_focus: string          // 明日关注点
  ai_viewpoint: string            // AI观点
  created_at: string
  review_date: string
}

/**
 * 投资策略生成请求
 */
export interface StrategyRequest {
  investment_style: string        // 投资风格：conservative/balanced/aggressive
  time_horizon: string            // 时间范围：short/medium/long
  risk_tolerance: string          // 风险承受：low/medium/high
  capital_amount?: number         // 可选：投资金额
  preferred_sectors?: string[]    // 可选：偏好行业
  exclude_sectors?: string[]      // 可选：排除行业
  custom_requirements?: string    // 可选：自定义需求
}

/**
 * 投资策略响应
 */
export interface StrategyResponse {
  strategy_summary: string        // 策略总结
  asset_allocation: Record<string, number>  // 资产配置建议
  stock_recommendations: Array<{
    symbol: string
    name: string
    allocation_percent: number
    reason: string
  }>
  risk_warning: string            // 风险提示
  rebalance_frequency: string     // 建议调仓频率
  ai_reasoning: string            // AI推理过程
  created_at: string
}

// ==================== API函数 ====================

/**
 * 单股AI分析
 *
 * POST /ai/single-analysis
 */
export function singleAnalysis(data: SingleAnalysisRequest) {
  return post<SingleAnalysisResponse>('/ai/single-analysis', data, {
    timeout: 60000  // AI分析可能需要较长时间，设置60秒超时
  })
}

/**
 * AI对话
 *
 * POST /ai/chat
 */
export function chat(data: ChatRequest) {
  return post<ChatResponse>('/ai/chat', data, {
    timeout: 60000  // AI对话可能需要较长时间
  })
}

/**
 * 批量AI分析
 *
 * POST /ai/batch-analysis
 */
export function batchAnalysis(data: BatchAnalysisRequest) {
  return post<BatchAnalysisResponse>('/ai/batch-analysis', data, {
    timeout: 120000  // 批量分析可能需要更长时间，120秒
  })
}

/**
 * 每日市场复盘
 *
 * POST /ai/daily-review
 */
export function dailyReview(data: DailyReviewRequest = {}) {
  return post<DailyReviewResponse>('/ai/daily-review', data, {
    timeout: 90000  // 复盘分析可能需要较长时间
  })
}

/**
 * 投资策略生成
 *
 * POST /ai/strategy
 */
export function generateStrategy(data: StrategyRequest) {
  return post<StrategyResponse>('/ai/strategy', data, {
    timeout: 90000
  })
}

// ==================== 辅助函数 ====================

/**
 * 格式化AI评分为百分比
 */
export function formatScore(score: number): string {
  return `${Math.round(score)}/100`
}

/**
 * 获取评分等级
 */
export function getScoreLevel(score: number): {
  level: 'excellent' | 'good' | 'fair' | 'poor'
  label: string
  color: string
} {
  if (score >= 80) {
    return { level: 'excellent', label: '优秀', color: '#67C23A' }
  } else if (score >= 60) {
    return { level: 'good', label: '良好', color: '#409EFF' }
  } else if (score >= 40) {
    return { level: 'fair', label: '一般', color: '#E6A23C' }
  } else {
    return { level: 'poor', label: '较差', color: '#F56C6C' }
  }
}

/**
 * 获取置信度等级
 */
export function getConfidenceLevel(confidence: number): {
  level: 'high' | 'medium' | 'low'
  label: string
  color: string
} {
  if (confidence >= 70) {
    return { level: 'high', label: '高', color: '#67C23A' }
  } else if (confidence >= 50) {
    return { level: 'medium', label: '中', color: '#E6A23C' }
  } else {
    return { level: 'low', label: '低', color: '#F56C6C' }
  }
}
