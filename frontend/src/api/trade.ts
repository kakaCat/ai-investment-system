import { post } from './request'

/**
 * 查询交易记录
 */
export const queryTrades = (params: {
  account_id?: number
  trade_type?: string
  symbol?: string
  start_date?: string
  end_date?: string
  page?: number
  page_size?: number
}) => {
  return post('/trade/query', params)
}

/**
 * 创建交易记录
 */
export const createTrade = (params: {
  account_id: number
  trade_type: string
  symbol: string
  stock_name: string
  quantity: number
  price: number
  trade_date: string
  trade_time: string
  fee?: number
  notes?: string
}) => {
  return post('/trade/create', params)
}

/**
 * 更新交易记录
 */
export const updateTrade = (params: {
  trade_id: number
  quantity?: number
  price?: number
  trade_date?: string
  trade_time?: string
  fee?: number
  notes?: string
}) => {
  return post('/trade/update', params)
}

/**
 * 删除交易记录
 */
export const deleteTrade = (params: { trade_id: number }) => {
  return post('/trade/delete', params)
}

/**
 * 交易详情
 */
export const getTradeDetail = (params: { trade_id: number }) => {
  return post('/trade/detail', params)
}
