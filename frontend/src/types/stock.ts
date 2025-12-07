/**
 * 股票基本信息
 */
export interface Stock {
  symbol: string // 股票代码
  name: string // 股票名称
  market: 'A股' | '港股' | '美股' // 所属市场
  current_price: number // 当前价格
  change_amount: number // 涨跌额
  change_rate: number // 涨跌幅 (%)
  volume?: number // 成交量
  turnover?: number // 成交额
  high?: number // 最高价
  low?: number // 最低价
  open?: number // 开盘价
  prev_close?: number // 昨收价
  market_cap?: number // 总市值
}

/**
 * 股票详细信息
 */
export interface StockDetail extends Stock {
  pe_ratio?: number // 市盈率
  pb_ratio?: number // 市净率
  dividend_yield?: number // 股息率
  total_shares?: number // 总股本
  float_shares?: number // 流通股本
  industry?: string // 所属行业
  description?: string // 公司简介
}

/**
 * 股票查询参数
 */
export interface StockQueryParams {
  keyword?: string // 搜索关键词（代码/名称/拼音）
  market?: 'A股' | '港股' | '美股' // 市场筛选
  page?: number
  page_size?: number
}

/**
 * 股票查询响应
 */
export interface StockQueryResponse {
  total: number
  page: number
  page_size: number
  list: Stock[]
}

/**
 * K线数据点
 */
export interface KLineDataPoint {
  timestamp: string // 时间戳
  open: number // 开盘价
  high: number // 最高价
  low: number // 最低价
  close: number // 收盘价
  volume: number // 成交量
}

/**
 * K线数据
 */
export interface KLineData {
  symbol: string
  name: string
  period: 'day' | 'week' | 'month' // 周期
  data: KLineDataPoint[]
}
