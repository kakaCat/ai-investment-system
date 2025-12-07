/**
 * 账户信息
 */
export interface Account {
  account_id: number
  account_name: string
  account_type: string
  status: 'active' | 'inactive'
  created_at: string
}

/**
 * 持仓信息
 */
export interface Holding {
  symbol: string
  name: string
  quantity: number
  avg_cost: number
  current_price: number
  market_value: number
  profit_loss: number
  profit_loss_rate: number
}

/**
 * 关注股票
 */
export interface WatchlistItem {
  symbol: string
  name: string
  current_price?: number
  target_price?: number
  notes?: string
  created_at: string
}

/**
 * 账户详情
 */
export interface AccountDetail {
  account_info: Account
  holdings: {
    total: number
    list: Holding[]
  }
  watchlist: {
    total: number
    list: WatchlistItem[]
  }
  statistics: {
    total_market_value: number
    total_profit_loss: number
    profit_loss_rate: number
  }
}

/**
 * 查询参数
 */
export interface AccountQueryParams {
  page: number
  page_size: number
  account_type?: string
  status?: 'active' | 'inactive'
}

/**
 * 查询响应
 */
export interface AccountQueryResponse {
  total: number
  page: number
  page_size: number
  list: Account[]
}

/**
 * 详情响应
 */
export interface AccountDetailResponse {
  account_info: Account
  holdings: {
    total: number
    list: Holding[]
  }
  watchlist: {
    total: number
    list: WatchlistItem[]
  }
  statistics: {
    total_market_value: number
    total_profit_loss: number
    profit_loss_rate: number
  }
}
