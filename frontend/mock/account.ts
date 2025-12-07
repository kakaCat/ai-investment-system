import { MockMethod } from 'vite-plugin-mock'

export default [
  // 查询账户列表
  {
    url: '/api/v1/account/query',
    method: 'post',
    response: () => {
      return {
        code: 0,
        message: 'success',
        data: {
          total: 3,
          page: 1,
          page_size: 20,
          list: [
            {
              account_id: 1,
              account_name: '我的A股账户',
              account_type: 'A股',
              status: 'active',
              created_at: '2025-01-01 10:00:00'
            },
            {
              account_id: 2,
              account_name: '港股账户',
              account_type: '港股',
              status: 'active',
              created_at: '2025-01-05 14:30:00'
            },
            {
              account_id: 3,
              account_name: '美股账户',
              account_type: '美股',
              status: 'active',
              created_at: '2025-01-10 09:15:00'
            }
          ]
        },
        timestamp: new Date().toISOString()
      }
    }
  },

  // 获取账户详情
  {
    url: '/api/v1/account/detail',
    method: 'post',
    response: () => {
      return {
        code: 0,
        message: 'success',
        data: {
          account_info: {
            account_id: 1,
            account_name: '我的A股账户',
            account_type: 'A股',
            status: 'active',
            created_at: '2025-01-01 10:00:00'
          },
          holdings: {
            total: 2,
            list: [
              {
                symbol: '600519',
                name: '贵州茅台',
                quantity: 100,
                avg_cost: 1800.0,
                current_price: 1850.0,
                market_value: 185000.0,
                profit_loss: 5000.0,
                profit_loss_rate: 2.78
              },
              {
                symbol: '000001',
                name: '平安银行',
                quantity: 500,
                avg_cost: 12.5,
                current_price: 13.2,
                market_value: 6600.0,
                profit_loss: 350.0,
                profit_loss_rate: 5.6
              }
            ]
          },
          watchlist: {
            total: 1,
            list: [
              {
                symbol: '601318',
                name: '中国平安',
                current_price: 48.5,
                target_price: 50.0,
                notes: '等待回调',
                created_at: '2025-01-10 14:30:00'
              }
            ]
          },
          statistics: {
            total_market_value: 191600.0,
            total_profit_loss: 5350.0,
            profit_loss_rate: 2.87
          }
        },
        timestamp: new Date().toISOString()
      }
    }
  },

  // 创建账户
  {
    url: '/api/v1/account/create',
    method: 'post',
    response: () => {
      return {
        code: 0,
        message: 'success',
        data: {
          account_id: Math.floor(Math.random() * 10000)
        },
        timestamp: new Date().toISOString()
      }
    }
  },

  // 更新账户
  {
    url: '/api/v1/account/update',
    method: 'post',
    response: () => {
      return {
        code: 0,
        message: 'success',
        data: {},
        timestamp: new Date().toISOString()
      }
    }
  },

  // 删除账户
  {
    url: '/api/v1/account/delete',
    method: 'post',
    response: () => {
      return {
        code: 0,
        message: 'success',
        data: {},
        timestamp: new Date().toISOString()
      }
    }
  },

  // 创建账户
  {
    url: '/api/v1/account/create',
    method: 'post',
    response: (req: any) => {
      const body = req.body
      return {
        code: 0,
        message: 'success',
        data: {
          account_id: Math.floor(Math.random() * 10000) + 100
        },
        timestamp: new Date().toISOString()
      }
    }
  }
] as MockMethod[]
