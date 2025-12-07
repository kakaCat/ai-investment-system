# 前端组件开发指南

**版本**: v1.0
**日期**: 2025-01-15
**技术栈**: Vue 3 + TypeScript + Element Plus + TailwindCSS

---

## 目录

- [1. 组件开发规范](#1-组件开发规范)
- [2. 核心页面组件示例](#2-核心页面组件示例)
- [3. 公共组件示例](#3-公共组件示例)
- [4. API 调用示例](#4-api-调用示例)
- [5. Store 使用示例](#5-store-使用示例)

---

## 1. 组件开发规范

### 1.1 组件结构

所有组件使用组合式 API + TypeScript：

```vue
<script setup lang="ts">
// 1. 导入
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { accountApi } from '@/api/account'
import type { Account } from '@/types/account'

// 2. Props 定义
interface Props {
  accountId?: number
  editable?: boolean
}
const props = withDefaults(defineProps<Props>(), {
  editable: false
})

// 3. Emits 定义
interface Emits {
  (e: 'update', account: Account): void
  (e: 'delete', id: number): void
}
const emit = defineEmits<Emits>()

// 4. 响应式数据
const loading = ref(false)
const accounts = ref<Account[]>([])

// 5. 计算属性
const activeAccounts = computed(() =>
  accounts.value.filter(a => a.status === 'active')
)

// 6. 方法
const fetchAccounts = async () => {
  loading.value = true
  try {
    const res = await accountApi.query({ page: 1, page_size: 20 })
    accounts.value = res.data.list
  } finally {
    loading.value = false
  }
}

// 7. 生命周期
onMounted(() => {
  fetchAccounts()
})
</script>

<template>
  <!-- 模板内容 -->
</template>

<style scoped>
/* 样式 - 优先使用 Tailwind */
</style>
```

### 1.2 命名规范

| 类型 | 规范 | 示例 |
|------|------|------|
| 组件文件 | PascalCase | `AccountList.vue` |
| 组件名 | PascalCase | `<AccountCard>` |
| Props | camelCase | `accountId`, `showActions` |
| Events | kebab-case | `@update-account`, `@delete` |
| 变量 | camelCase | `accountList`, `isLoading` |
| 常量 | UPPER_SNAKE_CASE | `MAX_PAGE_SIZE` |
| 类型 | PascalCase | `Account`, `TradeRecord` |

### 1.3 目录组织

```
src/
├── views/                    # 页面组件（路由级别）
│   ├── account/
│   │   ├── AccountList.vue   # 账户列表页
│   │   └── AccountDetail.vue # 账户详情页
│   ├── trade/
│   │   └── TradeHistory.vue
│   └── dashboard/
│       └── Dashboard.vue
├── components/               # 公共组件
│   ├── common/               # 通用组件
│   │   ├── AppHeader.vue
│   │   └── PageContainer.vue
│   ├── account/              # 账户相关组件
│   │   ├── AccountCard.vue
│   │   └── AccountForm.vue
│   ├── holding/              # 持仓相关组件
│   │   ├── HoldingTable.vue
│   │   └── WatchlistTable.vue
│   └── charts/               # 图表组件
│       ├── ProfitChart.vue
│       └── KLineChart.vue
```

---

## 2. 核心页面组件示例

### 2.1 账户列表页面

**文件**: `src/views/account/AccountList.vue`

```vue
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { accountApi } from '@/api/account'
import type { Account, AccountQueryParams } from '@/types/account'

// 路由
const router = useRouter()

// 状态
const loading = ref(false)
const accounts = ref<Account[]>([])
const total = ref(0)
const queryParams = ref<AccountQueryParams>({
  page: 1,
  page_size: 20,
  account_type: undefined,
  status: 'active'
})

// 查询账户列表
const fetchAccounts = async () => {
  loading.value = true
  try {
    const res = await accountApi.query(queryParams.value)
    accounts.value = res.data.list
    total.value = res.data.total
  } catch (error) {
    ElMessage.error('查询账户列表失败')
  } finally {
    loading.value = false
  }
}

// 查看详情
const viewDetail = (account: Account) => {
  router.push({
    name: 'AccountDetail',
    params: { id: account.account_id }
  })
}

// 新建账户
const createAccount = () => {
  router.push({ name: 'AccountCreate' })
}

// 删除账户
const deleteAccount = async (account: Account) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除账户「${account.account_name}」吗？`,
      '确认删除',
      { type: 'warning' }
    )

    await accountApi.delete({ account_id: account.account_id })
    ElMessage.success('删除成功')
    fetchAccounts()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// 分页变化
const handlePageChange = (page: number) => {
  queryParams.value.page = page
  fetchAccounts()
}

// 初始化
onMounted(() => {
  fetchAccounts()
})
</script>

<template>
  <div class="p-6">
    <!-- 页面标题和操作 -->
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-2xl font-bold text-gray-800">我的账户</h1>
      <el-button type="primary" @click="createAccount">
        新建账户
      </el-button>
    </div>

    <!-- 筛选条件 -->
    <el-card class="mb-4">
      <el-form :model="queryParams" inline>
        <el-form-item label="账户类型">
          <el-select
            v-model="queryParams.account_type"
            placeholder="全部类型"
            clearable
            @change="fetchAccounts"
          >
            <el-option label="A股" value="A股" />
            <el-option label="港股" value="港股" />
            <el-option label="美股" value="美股" />
          </el-select>
        </el-form-item>

        <el-form-item label="账户状态">
          <el-select
            v-model="queryParams.status"
            @change="fetchAccounts"
          >
            <el-option label="活跃" value="active" />
            <el-option label="已停用" value="inactive" />
          </el-select>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 账户列表 -->
    <el-card v-loading="loading">
      <el-table :data="accounts" stripe>
        <el-table-column prop="account_name" label="账户名称" min-width="150" />
        <el-table-column prop="account_type" label="账户类型" width="100" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'info'">
              {{ row.status === 'active' ? '活跃' : '已停用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button
              link
              type="primary"
              @click="viewDetail(row)"
            >
              详情
            </el-button>
            <el-button
              link
              type="danger"
              @click="deleteAccount(row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="flex justify-end mt-4">
        <el-pagination
          v-model:current-page="queryParams.page"
          :page-size="queryParams.page_size"
          :total="total"
          layout="total, prev, pager, next"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>
  </div>
</template>
```

### 2.2 账户详情页面（双列表设计）

**文件**: `src/views/account/AccountDetail.vue`

```vue
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { accountApi } from '@/api/account'
import type { AccountDetail, Holding, WatchlistItem } from '@/types/account'
import HoldingTable from '@/components/holding/HoldingTable.vue'
import WatchlistTable from '@/components/holding/WatchlistTable.vue'

const route = useRoute()
const router = useRouter()

// 状态
const loading = ref(false)
const activeTab = ref('overview')
const accountDetail = ref<AccountDetail | null>(null)

// 获取账户详情
const fetchAccountDetail = async () => {
  loading.value = true
  try {
    const res = await accountApi.detail({
      account_id: Number(route.params.id)
    })
    accountDetail.value = res.data
  } catch (error) {
    ElMessage.error('查询账户详情失败')
  } finally {
    loading.value = false
  }
}

// 返回列表
const goBack = () => {
  router.push({ name: 'AccountList' })
}

onMounted(() => {
  fetchAccountDetail()
})
</script>

<template>
  <div class="p-6">
    <!-- 页面头部 -->
    <div class="flex items-center mb-6">
      <el-button @click="goBack" class="mr-4">
        返回
      </el-button>
      <h1 class="text-2xl font-bold text-gray-800">
        {{ accountDetail?.account_info.account_name }}
      </h1>
    </div>

    <!-- 账户基本信息 -->
    <el-card v-loading="loading" class="mb-4">
      <template #header>
        <div class="font-semibold">账户信息</div>
      </template>
      <el-descriptions :column="3" border>
        <el-descriptions-item label="账户名称">
          {{ accountDetail?.account_info.account_name }}
        </el-descriptions-item>
        <el-descriptions-item label="账户类型">
          {{ accountDetail?.account_info.account_type }}
        </el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag
            :type="accountDetail?.account_info.status === 'active' ? 'success' : 'info'"
          >
            {{ accountDetail?.account_info.status === 'active' ? '活跃' : '已停用' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="创建时间">
          {{ accountDetail?.account_info.created_at }}
        </el-descriptions-item>
      </el-descriptions>
    </el-card>

    <!-- Tab 切换 -->
    <el-card v-loading="loading">
      <el-tabs v-model="activeTab">
        <!-- 概览 Tab -->
        <el-tab-pane label="概览" name="overview">
          <div class="grid grid-cols-3 gap-4">
            <div class="card">
              <div class="text-gray-600 mb-2">总市值</div>
              <div class="text-2xl font-bold text-primary">
                ¥{{ accountDetail?.statistics.total_market_value.toLocaleString() }}
              </div>
            </div>
            <div class="card">
              <div class="text-gray-600 mb-2">总盈亏</div>
              <div
                class="text-2xl font-bold"
                :class="(accountDetail?.statistics.total_profit_loss ?? 0) >= 0 ? 'profit-text' : 'loss-text'"
              >
                {{ (accountDetail?.statistics.total_profit_loss ?? 0) >= 0 ? '+' : '' }}
                ¥{{ accountDetail?.statistics.total_profit_loss.toLocaleString() }}
              </div>
            </div>
            <div class="card">
              <div class="text-gray-600 mb-2">总收益率</div>
              <div
                class="text-2xl font-bold"
                :class="(accountDetail?.statistics.profit_loss_rate ?? 0) >= 0 ? 'profit-text' : 'loss-text'"
              >
                {{ (accountDetail?.statistics.profit_loss_rate ?? 0) >= 0 ? '+' : '' }}
                {{ accountDetail?.statistics.profit_loss_rate.toFixed(2) }}%
              </div>
            </div>
          </div>
        </el-tab-pane>

        <!-- 我的股票 Tab - 双列表设计 ⭐ -->
        <el-tab-pane label="我的股票" name="stocks">
          <!-- 持仓股票列表 -->
          <div class="mb-6">
            <div class="flex justify-between items-center mb-4">
              <h3 class="text-lg font-semibold">持仓股票</h3>
              <el-button type="primary" size="small">
                记录交易
              </el-button>
            </div>
            <HoldingTable
              :holdings="accountDetail?.holdings.list ?? []"
              :loading="loading"
            />
          </div>

          <!-- 关注股票列表 -->
          <div>
            <div class="flex justify-between items-center mb-4">
              <h3 class="text-lg font-semibold">关注股票</h3>
              <el-button type="primary" size="small">
                添加关注
              </el-button>
            </div>
            <WatchlistTable
              :watchlist="accountDetail?.watchlist.list ?? []"
              :loading="loading"
            />
          </div>
        </el-tab-pane>

        <!-- 交易记录 Tab -->
        <el-tab-pane label="交易记录" name="trades">
          <div class="text-gray-500 text-center py-8">
            交易记录组件开发中...
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>
```

---

## 3. 公共组件示例

### 3.1 持仓股票表格组件

**文件**: `src/components/holding/HoldingTable.vue`

```vue
<script setup lang="ts">
import { useRouter } from 'vue-router'
import type { Holding } from '@/types/account'

interface Props {
  holdings: Holding[]
  loading?: boolean
}
const props = withDefaults(defineProps<Props>(), {
  loading: false
})

const router = useRouter()

// 查看股票详情
const viewStockDetail = (holding: Holding) => {
  router.push({
    name: 'StockDetail',
    params: { symbol: holding.symbol }
  })
}

// 记录交易
const recordTrade = (holding: Holding) => {
  router.push({
    name: 'TradeCreate',
    query: { symbol: holding.symbol }
  })
}

// AI 分析
const analyzeStock = (holding: Holding) => {
  router.push({
    name: 'AIAnalysis',
    query: { symbol: holding.symbol }
  })
}
</script>

<template>
  <el-table :data="holdings" :loading="loading" stripe>
    <el-table-column prop="symbol" label="代码" width="100" />
    <el-table-column prop="name" label="名称" width="120" />
    <el-table-column prop="quantity" label="持仓数量" width="100" align="right">
      <template #default="{ row }">
        {{ row.quantity.toLocaleString() }}
      </template>
    </el-table-column>
    <el-table-column prop="avg_cost" label="成本价" width="100" align="right">
      <template #default="{ row }">
        ¥{{ row.avg_cost.toFixed(2) }}
      </template>
    </el-table-column>
    <el-table-column prop="current_price" label="现价" width="100" align="right">
      <template #default="{ row }">
        ¥{{ row.current_price.toFixed(2) }}
      </template>
    </el-table-column>
    <el-table-column prop="market_value" label="市值" width="120" align="right">
      <template #default="{ row }">
        ¥{{ row.market_value.toLocaleString() }}
      </template>
    </el-table-column>
    <el-table-column label="盈亏" width="150" align="right">
      <template #default="{ row }">
        <div :class="row.profit_loss >= 0 ? 'profit-text' : 'loss-text'">
          {{ row.profit_loss >= 0 ? '+' : '' }}¥{{ row.profit_loss.toLocaleString() }}
          <span class="ml-2">
            ({{ row.profit_loss >= 0 ? '+' : '' }}{{ row.profit_loss_rate.toFixed(2) }}%)
          </span>
        </div>
      </template>
    </el-table-column>
    <el-table-column label="操作" width="240" fixed="right">
      <template #default="{ row }">
        <el-button link type="primary" size="small" @click="viewStockDetail(row)">
          详情
        </el-button>
        <el-button link type="primary" size="small" @click="recordTrade(row)">
          记录交易
        </el-button>
        <el-button link type="primary" size="small" @click="analyzeStock(row)">
          AI分析
        </el-button>
      </template>
    </el-table-column>
  </el-table>
</template>
```

### 3.2 关注股票表格组件

**文件**: `src/components/holding/WatchlistTable.vue`

```vue
<script setup lang="ts">
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { WatchlistItem } from '@/types/account'

interface Props {
  watchlist: WatchlistItem[]
  loading?: boolean
}
const props = withDefaults(defineProps<Props>(), {
  loading: false
})

interface Emits {
  (e: 'remove', item: WatchlistItem): void
  (e: 'refresh'): void
}
const emit = defineEmits<Emits>()

const router = useRouter()

// 查看详情
const viewDetail = (item: WatchlistItem) => {
  router.push({
    name: 'StockDetail',
    params: { symbol: item.symbol }
  })
}

// 记录建仓
const recordBuy = (item: WatchlistItem) => {
  router.push({
    name: 'TradeCreate',
    query: {
      symbol: item.symbol,
      action: 'buy'
    }
  })
}

// 移除关注
const removeFromWatchlist = async (item: WatchlistItem) => {
  try {
    await ElMessageBox.confirm(
      `确定要移除关注「${item.name}」吗？`,
      '确认移除',
      { type: 'warning' }
    )
    emit('remove', item)
  } catch (error) {
    // 用户取消
  }
}
</script>

<template>
  <el-table :data="watchlist" :loading="loading" stripe>
    <el-table-column prop="symbol" label="代码" width="100" />
    <el-table-column prop="name" label="名称" width="120" />
    <el-table-column prop="current_price" label="现价" width="100" align="right">
      <template #default="{ row }">
        ¥{{ row.current_price?.toFixed(2) ?? '--' }}
      </template>
    </el-table-column>
    <el-table-column prop="target_price" label="目标价" width="100" align="right">
      <template #default="{ row }">
        <span v-if="row.target_price">
          ¥{{ row.target_price.toFixed(2) }}
        </span>
        <span v-else class="text-gray-400">--</span>
      </template>
    </el-table-column>
    <el-table-column prop="notes" label="备注" min-width="200">
      <template #default="{ row }">
        <span class="text-gray-600">{{ row.notes || '--' }}</span>
      </template>
    </el-table-column>
    <el-table-column prop="created_at" label="关注时间" width="180" />
    <el-table-column label="操作" width="200" fixed="right">
      <template #default="{ row }">
        <el-button link type="primary" size="small" @click="viewDetail(row)">
          详情
        </el-button>
        <el-button link type="success" size="small" @click="recordBuy(row)">
          记录建仓
        </el-button>
        <el-button link type="danger" size="small" @click="removeFromWatchlist(row)">
          移除
        </el-button>
      </template>
    </el-table-column>
  </el-table>
</template>
```

---

## 4. API 调用示例

### 4.1 API 模块定义

**文件**: `src/api/account.ts`

```typescript
import { post } from './request'
import type {
  Account,
  AccountDetail,
  AccountQueryParams,
  AccountQueryResponse,
  AccountDetailResponse
} from '@/types/account'

/**
 * 账户相关 API
 */
export const accountApi = {
  /**
   * 查询账户列表
   */
  query(params: AccountQueryParams) {
    return post<AccountQueryResponse>('/account/query', params)
  },

  /**
   * 获取账户详情
   */
  detail(params: { account_id: number }) {
    return post<AccountDetailResponse>('/account/detail', params)
  },

  /**
   * 创建账户
   */
  create(params: {
    account_name: string
    account_type: string
  }) {
    return post<{ account_id: number }>('/account/create', params)
  },

  /**
   * 更新账户
   */
  update(params: {
    account_id: number
    account_name?: string
    status?: string
  }) {
    return post<{}>('/account/update', params)
  },

  /**
   * 删除账户
   */
  delete(params: { account_id: number }) {
    return post<{}>('/account/delete', params)
  }
}
```

### 4.2 请求封装

**文件**: `src/api/request.ts`

```typescript
import axios, { AxiosRequestConfig } from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'

/**
 * 统一响应格式
 */
export interface ApiResponse<T = any> {
  code: number
  message: string
  data: T
  timestamp: string
}

// 创建 axios 实例
const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
  timeout: 30000
})

// 请求拦截器
request.interceptors.request.use(
  (config) => {
    // 添加 token
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  (response) => {
    const res = response.data as ApiResponse

    // code !== 0 表示业务错误
    if (res.code !== 0) {
      ElMessage.error(res.message || '请求失败')

      // 401 未登录
      if (res.code === 401) {
        router.push('/login')
      }

      return Promise.reject(new Error(res.message || 'Error'))
    }

    return res
  },
  (error) => {
    ElMessage.error(error.message || '网络错误')
    return Promise.reject(error)
  }
)

/**
 * POST 请求封装
 */
export function post<T = any>(
  url: string,
  data?: any,
  config?: AxiosRequestConfig
): Promise<ApiResponse<T>> {
  return request.post(url, data, config)
}

export default request
```

---

## 5. Store 使用示例

### 5.1 账户 Store

**文件**: `src/stores/account.ts`

```typescript
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { accountApi } from '@/api/account'
import type { Account, AccountDetail } from '@/types/account'

export const useAccountStore = defineStore('account', () => {
  // 状态
  const accounts = ref<Account[]>([])
  const currentAccount = ref<AccountDetail | null>(null)
  const loading = ref(false)

  // 计算属性
  const activeAccounts = computed(() =>
    accounts.value.filter(a => a.status === 'active')
  )

  const totalAccounts = computed(() => accounts.value.length)

  // 方法
  const fetchAccounts = async () => {
    loading.value = true
    try {
      const res = await accountApi.query({
        page: 1,
        page_size: 100,
        status: 'active'
      })
      accounts.value = res.data.list
    } finally {
      loading.value = false
    }
  }

  const fetchAccountDetail = async (accountId: number) => {
    loading.value = true
    try {
      const res = await accountApi.detail({ account_id: accountId })
      currentAccount.value = res.data
    } finally {
      loading.value = false
    }
  }

  const createAccount = async (params: {
    account_name: string
    account_type: string
  }) => {
    const res = await accountApi.create(params)
    await fetchAccounts() // 刷新列表
    return res
  }

  const deleteAccount = async (accountId: number) => {
    await accountApi.delete({ account_id: accountId })
    await fetchAccounts() // 刷新列表
  }

  return {
    // 状态
    accounts,
    currentAccount,
    loading,

    // 计算属性
    activeAccounts,
    totalAccounts,

    // 方法
    fetchAccounts,
    fetchAccountDetail,
    createAccount,
    deleteAccount
  }
})
```

### 5.2 在组件中使用 Store

```vue
<script setup lang="ts">
import { onMounted } from 'vue'
import { useAccountStore } from '@/stores/account'
import { storeToRefs } from 'pinia'

const accountStore = useAccountStore()

// 使用 storeToRefs 保持响应性
const { accounts, loading, activeAccounts } = storeToRefs(accountStore)

// 直接调用 action
const { fetchAccounts, deleteAccount } = accountStore

onMounted(() => {
  fetchAccounts()
})
</script>

<template>
  <div>
    <div v-loading="loading">
      <div v-for="account in activeAccounts" :key="account.account_id">
        {{ account.account_name }}
      </div>
    </div>
  </div>
</template>
```

---

## 6. 类型定义示例

**文件**: `src/types/account.ts`

```typescript
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
```

---

## 7. 路由配置示例

**文件**: `src/router/index.ts`

```typescript
import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/views/dashboard/Dashboard.vue'),
    meta: { title: '首页' }
  },
  {
    path: '/account',
    name: 'Account',
    meta: { title: '账户管理' },
    children: [
      {
        path: 'list',
        name: 'AccountList',
        component: () => import('@/views/account/AccountList.vue'),
        meta: { title: '账户列表' }
      },
      {
        path: 'detail/:id',
        name: 'AccountDetail',
        component: () => import('@/views/account/AccountDetail.vue'),
        meta: { title: '账户详情' }
      }
    ]
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/login/Login.vue'),
    meta: { title: '登录', requiresAuth: false }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  // 设置页面标题
  document.title = `${to.meta.title || ''} - 投资管理系统`

  // 检查登录状态
  const token = localStorage.getItem('token')
  if (to.meta.requiresAuth !== false && !token) {
    next('/login')
  } else {
    next()
  }
})

export default router
```

---

## 8. 样式规范

### 8.1 TailwindCSS 优先

优先使用 Tailwind 工具类：

```vue
<template>
  <!-- ✅ 推荐 -->
  <div class="p-4 bg-white rounded-lg shadow-sm">
    <h2 class="text-xl font-bold mb-4">标题</h2>
    <p class="text-gray-600">内容</p>
  </div>

  <!-- ❌ 避免 -->
  <div class="custom-card">
    <h2 class="custom-title">标题</h2>
    <p class="custom-text">内容</p>
  </div>
</template>
```

### 8.2 自定义样式

只在必要时使用 scoped 样式：

```vue
<style scoped>
/* 复杂布局或 Tailwind 无法实现的样式 */
.complex-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1rem;
}

/* 覆盖 Element Plus 样式 */
:deep(.el-table) {
  border-radius: 8px;
}
</style>
```

---

## 9. 开发流程

### 9.1 创建新页面

1. **在 views 目录创建组件**

```bash
touch src/views/account/AccountList.vue
```

2. **定义类型**

```bash
# 在 types 目录添加类型定义
touch src/types/account.ts
```

3. **创建 API 接口**

```bash
touch src/api/account.ts
```

4. **创建 Store（可选）**

```bash
touch src/stores/account.ts
```

5. **添加路由**

在 `src/router/index.ts` 添加路由配置

6. **配置 Mock 数据**

在 `mock/account.ts` 添加 Mock 接口

### 9.2 调试技巧

使用 Vue DevTools：

```typescript
// 在组件中打印调试信息
console.log('[AccountList] accounts:', accounts.value)

// 使用 watchEffect 观察变化
import { watchEffect } from 'vue'

watchEffect(() => {
  console.log('[AccountList] accounts changed:', accounts.value.length)
})
```

---

## 10. 相关文档

- [前端架构设计](../../design/architecture/frontend-architecture.md)
- [Mock 数据方案](./mock-data-guide.md)
- [前端项目初始化](./frontend-setup.md)

---

**创建者**: Claude Code
**日期**: 2025-01-15
**状态**: ✅ 完成
