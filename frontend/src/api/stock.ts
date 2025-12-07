import { post } from './request'

/**
 * 查询股票列表
 */
export const queryStocks = (params: {
  market?: string
  page?: number
  page_size?: number
}) => {
  return post('/stock/query', params)
}

/**
 * 获取股票详情
 */
export const getStockDetail = (params: { symbol: string }) => {
  return post('/stock/detail', params)
}

/**
 * 搜索股票
 */
export const searchStocks = (params: {
  keyword: string
  market?: string
  limit?: number
}) => {
  return post('/stock/search', params)
}
