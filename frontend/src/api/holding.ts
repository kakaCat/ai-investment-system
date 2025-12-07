import { post } from './request'

/**
 * 查询持仓列表
 */
export const queryHoldings = (params: {
  account_id?: number
  symbol?: string
  page?: number
  page_size?: number
}) => {
  return post('/holding/query', params)
}

/**
 * 同步持仓数据
 */
export const syncHoldings = (params: { account_id: number }) => {
  return post('/holding/sync', params)
}
