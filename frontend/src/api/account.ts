import { post } from './request'

/**
 * 查询账户列表
 */
export const queryAccounts = (params: any = {}) => {
  return post('/account/query', params)
}

/**
 * 获取账户详情
 */
export const getAccountDetail = (params: { account_id: number }) => {
  return post('/account/detail', params)
}

/**
 * 创建账户
 */
export const createAccount = (params: {
  broker_name: string
  account_no: string
  market: string
  initial_cash?: number
  notes?: string
}) => {
  return post('/account/create', params)
}

/**
 * 更新账户
 */
export const updateAccount = (params: {
  account_id: number
  broker_name?: string
  account_no?: string
  notes?: string
}) => {
  return post('/account/update', params)
}

/**
 * 删除账户
 */
export const deleteAccount = (params: { account_id: number }) => {
  return post('/account/delete', params)
}
