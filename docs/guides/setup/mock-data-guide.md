# Mock 数据方案指南

**版本**: v1.0
**日期**: 2025-01-15
**用途**: 前端开发阶段使用 Mock 数据，后期切换到真实后端接口

---

## 目录

- [1. Mock 方案概述](#1-mock-方案概述)
- [2. Mock 数据结构](#2-mock-数据结构)
- [3. 完整 Mock 示例](#3-完整-mock-示例)
- [4. 切换真实接口](#4-切换真实接口)

---

## 1. Mock 方案概述

### 1.1 技术选型

使用 **vite-plugin-mock** + **mockjs**

**优点**：
- ✅ 无需修改业务代码
- ✅ 开发时自动拦截 API 请求
- ✅ 生产环境自动禁用
- ✅ 支持 TypeScript
- ✅ 热更新支持

### 1.2 工作原理

```
前端发起请求
    ↓
/api/v1/account/query
    ↓
vite-plugin-mock 拦截
    ↓
返回 mock/account.ts 中定义的数据
    ↓
前端接收数据（和真实接口一样）
```

### 1.3 目录结构

```
frontend/
├── mock/                      # Mock 数据目录
│   ├── account.ts             # 账户相关接口
│   ├── trade.ts               # 交易相关接口
│   ├── stock.ts               # 股票相关接口
│   ├── event.ts               # 事件相关接口
│   ├── user.ts                # 用户相关接口
│   └── _utils.ts              # Mock 工具函数
│
└── src/
    └── api/
        └── account.ts         # 业务代码（不需要修改）
```

---

## 2. Mock 数据结构

### 2.1 统一响应格式

所有 Mock 数据必须符合后端统一响应格式：

```typescript
{
  code: 0,              // 0=成功，非0=失败
  message: "success",
  data: {               // 具体数据
    ...
  },
  timestamp: "2025-01-15T14:30:00Z"
}
```

### 2.2 Mock 文件模板

```typescript
import { MockMethod } from 'vite-plugin-mock'

export default [
  {
    url: '/api/v1/{module}/{action}',
    method: 'post',
    response: (req) => {
      // 可以根据请求参数返回不同数据
      const { account_id } = req.body

      return {
        code: 0,
        message: 'success',
        data: {
          // 返回的数据
        },
        timestamp: new Date().toISOString()
      }
    }
  }
] as MockMethod[]
```

---

## 3. 完整 Mock 示例

### 3.1 账户模块 Mock

创建 `mock/account.ts`：

```typescript
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
              created_at: '2025-01-01'
            },
            {
              account_id: 2,
              account_name: '港股账户',
              account_type: '港股',
              status: 'active',
              created_at: '2025-01-05'
            },
            {
              account_id: 3,
              account_name: '美股账户',
              account_type: '美股',
              status: 'inactive',
              created_at: '2025-01-10'
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
    response: (req) => {
      const { account_id } = req.body

      return {
        code: 0,
        message: 'success',
        data: {
          account_info: {
            account_id: account_id || 1,
            account_name: '我的A股账户',
            account_type: 'A股',
            status: 'active',
            created_at: '2025-01-01'
          },
          holdings: {
            total: 2,
            list: [
              {
                symbol: '600519',
                name: '贵州茅台',
                quantity: 100,
                avg_cost: 1800.00,
                current_price: 1850.00,
                market_value: 185000.00,
                profit_loss: 5000.00,
                profit_loss_rate: 2.78
              },
              {
                symbol: '000001',
                name: '平安银行',
                quantity: 500,
                avg_cost: 12.50,
                current_price: 13.20,
                market_value: 6600.00,
                profit_loss: 350.00,
                profit_loss_rate: 5.60
              }
            ]
          },
          watchlist: {
            total: 1,
            list: [
              {
                symbol: '601318',
                name: '中国平安',
                target_price: 50.00,
                notes: '等待回调',
                created_at: '2025-01-10 14:30:00'
              }
            ]
          },
          statistics: {
            total_market_value: 191600.00,
            total_profit_loss: 5350.00,
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
    response: (req) => {
      const { account_name, account_type } = req.body

      return {
        code: 0,
        message: '创建成功',
        data: {
          account_id: 4,
          account_name,
          account_type,
          status: 'active',
          created_at: new Date().toISOString()
        },
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
        message: '删除成功',
        data: null,
        timestamp: new Date().toISOString()
      }
    }
  }
] as MockMethod[]
```

### 3.2 交易模块 Mock

创建 `mock/trade.ts`：

```typescript
import { MockMethod } from 'vite-plugin-mock'

export default [
  // 查询交易记录
  {
    url: '/api/v1/trade/query',
    method: 'post',
    response: () => {
      return {
        code: 0,
        message: 'success',
        data: {
          total: 5,
          list: [
            {
              trade_id: 1,
              symbol: '600519',
              name: '贵州茅台',
              trade_type: '买入',
              quantity: 100,
              price: 1800.00,
              total_amount: 180000.00,
              fees: {
                commission: 54.00,
                tax: 0.00,
                total: 54.00
              },
              trade_time: '2025-01-10 14:30:00'
            },
            {
              trade_id: 2,
              symbol: '000001',
              name: '平安银行',
              trade_type: '买入',
              quantity: 500,
              price: 12.50,
              total_amount: 6250.00,
              fees: {
                commission: 5.00,
                tax: 0.00,
                total: 5.00
              },
              trade_time: '2025-01-12 10:15:00'
            }
          ]
        },
        timestamp: new Date().toISOString()
      }
    }
  },

  // 创建交易
  {
    url: '/api/v1/trade/create',
    method: 'post',
    response: (req) => {
      const { symbol, trade_type, quantity, price } = req.body

      return {
        code: 0,
        message: '交易记录成功',
        data: {
          trade_id: 6,
          symbol,
          trade_type: trade_type === 'buy' ? '买入' : '卖出',
          quantity,
          price,
          total_amount: quantity * price,
          fees: {
            commission: Math.max(quantity * price * 0.0003, 5),
            tax: trade_type === 'sell' ? quantity * price * 0.001 : 0,
            total: Math.max(quantity * price * 0.0003, 5) + (trade_type === 'sell' ? quantity * price * 0.001 : 0)
          },
          trade_time: new Date().toISOString()
        },
        timestamp: new Date().toISOString()
      }
    }
  }
] as MockMethod[]
```

### 3.3 事件模块 Mock

创建 `mock/event.ts`：

```typescript
import { MockMethod } from 'vite-plugin-mock'

export default [
  // 查询事件列表
  {
    url: '/api/v1/event/query',
    method: 'post',
    response: () => {
      return {
        code: 0,
        message: 'success',
        data: {
          total: 3,
          list: [
            {
              event_id: 1,
              symbol: '600519',
              name: '贵州茅台',
              event_category: 'company',
              event_subcategory: 'earnings',
              title: '贵州茅台发布2024年度业绩预告',
              summary: '预计全年营收增长15%，净利润增长12%',
              importance: 'High',
              impact_direction: 'positive',
              impact_score: 85,
              event_date: '2025-01-15',
              published_at: '2025-01-15 09:00:00'
            },
            {
              event_id: 2,
              symbol: '000001',
              name: '平安银行',
              event_category: 'policy',
              event_subcategory: 'monetary',
              title: '央行降准0.5个百分点',
              summary: '释放长期资金约1万亿元，利好银行股',
              importance: 'Critical',
              impact_direction: 'positive',
              impact_score: 90,
              event_date: '2025-01-14',
              published_at: '2025-01-14 16:00:00'
            },
            {
              event_id: 3,
              symbol: '601318',
              name: '中国平安',
              event_category: 'market',
              event_subcategory: 'sector_rotation',
              title: '保险板块资金流入',
              summary: '今日保险板块资金净流入5亿元',
              importance: 'Medium',
              impact_direction: 'positive',
              impact_score: 70,
              event_date: '2025-01-15',
              published_at: '2025-01-15 15:00:00'
            }
          ]
        },
        timestamp: new Date().toISOString()
      }
    }
  },

  // 事件详情
  {
    url: '/api/v1/event/detail',
    method: 'post',
    response: (req) => {
      const { event_id } = req.body

      return {
        code: 0,
        message: 'success',
        data: {
          event_id: event_id || 1,
          symbol: '600519',
          name: '贵州茅台',
          event_category: 'company',
          event_subcategory: 'earnings',
          title: '贵州茅台发布2024年度业绩预告',
          summary: '预计全年营收增长15%，净利润增长12%',
          importance: 'High',
          impact_direction: 'positive',
          impact_score: 85,
          event_date: '2025-01-15',
          published_at: '2025-01-15 09:00:00',
          content: '贵州茅台酒股份有限公司发布2024年度业绩预告...',
          source_url: 'https://example.com/news/123',
          ai_analysis: {
            market_impact: '预计短期内刺激白酒板块上涨',
            industry_impact: '行业龙头业绩超预期，带动整体估值提升',
            holding_impact: '建议继续持有，目标价上调至2000元',
            confidence_score: 85
          }
        },
        timestamp: new Date().toISOString()
      }
    }
  }
] as MockMethod[]
```

### 3.4 用户模块 Mock

创建 `mock/user.ts`：

```typescript
import { MockMethod } from 'vite-plugin-mock'

export default [
  // 登录
  {
    url: '/api/v1/user/login',
    method: 'post',
    response: (req) => {
      const { email, password } = req.body

      // 简单模拟登录验证
      if (email === 'demo@example.com' && password === '123456') {
        return {
          code: 0,
          message: '登录成功',
          data: {
            token: 'mock-token-' + Date.now(),
            user: {
              user_id: 1,
              email: 'demo@example.com',
              user_name: '演示用户'
            }
          },
          timestamp: new Date().toISOString()
        }
      } else {
        return {
          code: 1001,
          message: '用户名或密码错误',
          data: null,
          timestamp: new Date().toISOString()
        }
      }
    }
  },

  // 获取用户信息
  {
    url: '/api/v1/user/profile',
    method: 'post',
    response: () => {
      return {
        code: 0,
        message: 'success',
        data: {
          user_id: 1,
          email: 'demo@example.com',
          user_name: '演示用户',
          ai_token_balance: 10000,
          created_at: '2025-01-01'
        },
        timestamp: new Date().toISOString()
      }
    }
  }
] as MockMethod[]
```

---

## 4. 切换真实接口

### 4.1 环境变量控制

在 `.env.development` 中：

```bash
# 开发阶段使用 Mock
VITE_USE_MOCK=true
```

在 `.env.production` 中：

```bash
# 生产环境使用真实接口
VITE_USE_MOCK=false
```

### 4.2 Vite 配置

```typescript
// vite.config.ts
import { viteMockServe } from 'vite-plugin-mock'

export default defineConfig({
  plugins: [
    viteMockServe({
      mockPath: 'mock',
      enable: process.env.VITE_USE_MOCK === 'true'  // 根据环境变量启用
    })
  ],
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',  // 真实后端地址
        changeOrigin: true
      }
    }
  }
})
```

### 4.3 无需修改业务代码

前端业务代码完全不需要修改，自动切换：

```typescript
// src/api/account.ts
import { post } from './index'

export const accountApi = {
  query(params) {
    // 开发时：Mock 数据
    // 生产时：真实接口
    return post('/account/query', params)
  }
}
```

---

## 5. Mock 数据清单

### 5.1 必需的 Mock 接口

根据 PRD v3.1，以下接口必须有 Mock 数据：

| 模块 | 接口 | 优先级 | 状态 |
|------|------|--------|------|
| **账户** | POST /account/query | P0 | ✅ 已提供 |
| **账户** | POST /account/detail | P0 | ✅ 已提供 |
| **账户** | POST /account/create | P0 | ✅ 已提供 |
| **账户** | POST /account/delete | P0 | ✅ 已提供 |
| **交易** | POST /trade/query | P0 | ✅ 已提供 |
| **交易** | POST /trade/create | P0 | ✅ 已提供 |
| **事件** | POST /event/query | P0 | ✅ 已提供 |
| **事件** | POST /event/detail | P0 | ✅ 已提供 |
| **用户** | POST /user/login | P0 | ✅ 已提供 |
| **用户** | POST /user/profile | P0 | ✅ 已提供 |
| **持仓** | POST /holding/query | P1 | 待补充 |
| **关注** | POST /watchlist/add | P1 | 待补充 |
| **股票** | POST /stock/search | P1 | 待补充 |
| **AI** | POST /ai/analyze_stock | P1 | 待补充 |

### 5.2 Mock 数据文件清单

```
mock/
├── account.ts         ✅ 账户相关接口
├── trade.ts           ✅ 交易相关接口
├── event.ts           ✅ 事件相关接口
├── user.ts            ✅ 用户相关接口
├── holding.ts         ⏳ 持仓相关接口（待创建）
├── watchlist.ts       ⏳ 关注列表接口（待创建）
├── stock.ts           ⏳ 股票相关接口（待创建）
└── ai.ts              ⏳ AI分析接口（待创建）
```

---

## 6. 测试 Mock 数据

### 6.1 在组件中调用

```vue
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { accountApi } from '@/api/account'

const accounts = ref([])

onMounted(async () => {
  const res = await accountApi.query({ status: 'active' })
  accounts.value = res.list
  console.log('账户列表（Mock数据）:', accounts.value)
})
</script>
```

### 6.2 浏览器控制台查看

Network 面板会显示：
- 请求：POST /api/v1/account/query
- 响应：Mock 返回的数据

---

## 7. 相关文档

- [前端项目初始化](./frontend-setup.md)
- [前端架构设计](../../design/architecture/frontend-architecture.md)
- [后端架构设计](../../design/architecture/backend-architecture.md)

---

**创建者**: Claude Code
**日期**: 2025-01-15
**状态**: ✅ 完成
