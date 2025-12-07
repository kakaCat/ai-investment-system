import { post } from './request'

/**
 * 查询策略列表
 */
export const queryStrategies = (params: {
  symbol?: string
  strategy_type?: string
  status?: string
  page?: number
  page_size?: number
}) => {
  return post('/strategy/query', params)
}

/**
 * 创建策略
 */
export const createStrategy = (params: {
  symbol: string
  stock_name: string
  strategy_type: string
  trigger_price?: number
  target_quantity?: number
  reason?: string
  notes?: string
  priority?: string
  is_stop_loss?: boolean
  is_take_profit?: boolean
}) => {
  return post('/strategy/create', params)
}

/**
 * 更新策略
 */
export const updateStrategy = (params: {
  strategy_id: number
  trigger_price?: number
  target_quantity?: number
  reason?: string
  notes?: string
  priority?: string
}) => {
  return post('/strategy/update', params)
}

/**
 * 删除策略
 */
export const deleteStrategy = (params: { strategy_id: number }) => {
  return post('/strategy/delete', params)
}

/**
 * 执行策略
 */
export const executeStrategy = (params: {
  strategy_id: number
  executed_price: number
  executed_quantity: number
}) => {
  return post('/strategy/execute', params)
}
