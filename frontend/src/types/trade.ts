/**
 * 交易类型
 */
export type TradeType = 'buy' | 'sell' | 'dividend' | 'split' | 'transfer_in' | 'transfer_out'

/**
 * 交易记录
 */
export interface Trade {
  trade_id: number
  account_id: number
  account_name?: string
  symbol: string
  stock_name: string
  trade_type: TradeType
  quantity: number // 数量
  price: number // 价格
  amount: number // 金额
  fee: number // 手续费
  trade_date: string // 交易日期
  notes?: string // 备注
  created_at: string
}

/**
 * 交易类型标签映射
 */
export const TRADE_TYPE_LABELS: Record<TradeType, string> = {
  buy: '买入',
  sell: '卖出',
  dividend: '分红',
  split: '拆股',
  transfer_in: '转入',
  transfer_out: '转出'
}

/**
 * 交易类型颜色映射
 */
export const TRADE_TYPE_COLORS: Record<TradeType, string> = {
  buy: 'danger',
  sell: 'success',
  dividend: 'warning',
  split: 'info',
  transfer_in: 'primary',
  transfer_out: 'default'
}

/**
 * 交易查询参数
 */
export interface TradeQueryParams {
  account_id?: number
  symbol?: string
  trade_type?: TradeType
  start_date?: string
  end_date?: string
  page?: number
  page_size?: number
}

/**
 * 交易查询响应
 */
export interface TradeQueryResponse {
  total: number
  page: number
  page_size: number
  list: Trade[]
}
