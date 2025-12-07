/**
 * Dashboard API
 * 首页仪表盘相关接口
 */
import { post } from './request'

/**
 * 获取账户列表
 */
export function getAccounts(params: {
  page?: number
  page_size?: number
  market?: string
  status?: string
}) {
  return post('/account/query', params)
}

/**
 * 获取持仓列表
 */
export function getHoldings(params: {
  account_id?: number
  page?: number
  page_size?: number
}) {
  return post('/holding/query', params)
}

/**
 * 获取 AI 建议
 */
export function getAISuggestions(params: {
  priority?: string
  action?: string
  page?: number
  page_size?: number
}) {
  return post('/ai/suggestions', params)
}

/**
 * 获取事件列表
 */
export function getEvents(params: {
  category?: string
  level?: string
  page?: number
  page_size?: number
}) {
  return post('/event/query', params)
}
