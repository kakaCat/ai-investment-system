# 前端架构设计文档

**版本**: v1.0
**日期**: 2025-01-15
**状态**: 设计中
**技术栈**: Vue 3 + TypeScript + Vite + TailwindCSS + Pinia

---

## 目录

- [1. 技术栈选型](#1-技术栈选型)
- [2. 目录结构](#2-目录结构)
- [3. 路由设计](#3-路由设计)
- [4. 状态管理](#4-状态管理)
- [5. 组件设计](#5-组件设计)
- [6. API 调用](#6-api-调用)
- [7. 样式规范](#7-样式规范)
- [8. 代码规范](#8-代码规范)

---

## 1. 技术栈选型

### 1.1 核心技术栈

| 技术 | 版本 | 用途 | 选择理由 |
|------|------|------|----------|
| **Vue 3** | 3.4+ | 前端框架 | 组合式 API、响应式系统、生态完善 |
| **TypeScript** | 5.3+ | 类型系统 | 类型安全、减少运行时错误、IDE 支持好 |
| **Vite** | 5.0+ | 构建工具 | 极快的开发服务器、HMR、原生 ESM |
| **Vue Router** | 4.2+ | 路由管理 | Vue 官方路由，支持 TypeScript |
| **Pinia** | 2.1+ | 状态管理 | Vue 官方推荐，轻量、TypeScript 优先 |
| **TailwindCSS** | 3.4+ | 样式方案 | 原子化 CSS、快速开发、易于定制 |

### 1.2 UI 组件库 ✅

**选择：Element Plus**

**理由**：
- ✅ 企业级组件库，稳定可靠
- ✅ 表格组件功能强大（排序、筛选、分页、虚拟滚动）- 适合持仓列表、交易记录等场景
- ✅ 表单组件丰富（日期选择、数字输入、级联选择）- 适合记录交易、创建账户等
- ✅ 中文文档完善，开发效率高
- ✅ 社区活跃，问题容易解决
- ✅ 与 Vue 3 + TypeScript 集成良好

### 1.3 图表库 ✅

**选择：ECharts**

**理由**：
- ✅ K 线图支持完善（`candlestick` 类型）- 股票系统核心需求
- ✅ 功能强大：折线图（盈亏曲线）、饼图（持仓分布）、柱状图（交易量）
- ✅ 性能优秀：大量数据渲染流畅
- ✅ 文档丰富：官方示例多，上手快
- ✅ Vue 3 集成：使用 `vue-echarts` 封装

### 1.4 工具库

| 库 | 版本 | 用途 |
|---|------|------|
| **axios** | ^1.6.0 | HTTP 请求 |
| **dayjs** | ^1.11.0 | 日期处理（轻量级） |
| **echarts** | ^5.4.0 | 图表可视化 |
| **vue-echarts** | ^6.6.0 | ECharts Vue 3 封装 |
| **vueuse** | ^10.7.0 | Vue 组合式 API 工具集 |
| **lodash-es** | ^4.17.0 | 工具函数 |
| **element-plus** | ^2.5.0 | UI 组件库 |

---

## 2. 目录结构

```
frontend/
├── public/                          # 静态资源
│   └── favicon.ico
│
├── src/
│   ├── main.ts                      # 入口文件
│   ├── App.vue                      # 根组件
│   │
│   ├── router/                      # 路由配置
│   │   ├── index.ts                 # 路由主文件
│   │   └── routes.ts                # 路由定义
│   │
│   ├── stores/                      # Pinia 状态管理
│   │   ├── index.ts
│   │   ├── user.ts                  # 用户状态
│   │   ├── account.ts               # 账户状态
│   │   └── app.ts                   # 应用全局状态
│   │
│   ├── views/                       # 页面组件（对应路由）
│   │   ├── account/
│   │   │   ├── AccountList.vue      # 账户列表页
│   │   │   └── AccountDetail.vue    # 账户详情页
│   │   ├── trade/
│   │   │   └── TradeList.vue        # 交易记录页
│   │   ├── event/
│   │   │   └── EventCenter.vue      # 事件中心页
│   │   ├── stock/
│   │   │   └── StockDetail.vue      # 股票详情页
│   │   └── login/
│   │       └── Login.vue            # 登录页
│   │
│   ├── components/                  # 公共组件
│   │   ├── common/                  # 通用组件
│   │   │   ├── PageHeader.vue       # 页面头部
│   │   │   ├── EmptyState.vue       # 空状态
│   │   │   └── Loading.vue          # 加载组件
│   │   │
│   │   ├── account/                 # 账户相关组件
│   │   │   ├── AccountCard.vue      # 账户卡片
│   │   │   └── CreateAccountDialog.vue  # 创建账户弹窗
│   │   │
│   │   ├── trade/                   # 交易相关组件
│   │   │   ├── TradeForm.vue        # 交易表单
│   │   │   └── TradeDetailDialog.vue
│   │   │
│   │   ├── holding/                 # 持仓相关组件
│   │   │   ├── HoldingList.vue      # 持仓列表
│   │   │   └── HoldingCard.vue      # 持仓卡片
│   │   │
│   │   └── charts/                  # 图表组件
│   │       ├── KLineChart.vue       # K线图
│   │       └── ProfitChart.vue      # 盈亏曲线
│   │
│   ├── api/                         # API 接口调用
│   │   ├── index.ts                 # axios 配置
│   │   ├── account.ts               # 账户接口
│   │   ├── trade.ts                 # 交易接口
│   │   ├── stock.ts                 # 股票接口
│   │   ├── event.ts                 # 事件接口
│   │   └── types.ts                 # 接口类型定义
│   │
│   ├── composables/                 # 组合式函数（Hooks）
│   │   ├── useAccount.ts            # 账户相关逻辑
│   │   ├── useTrade.ts              # 交易相关逻辑
│   │   └── useAuth.ts               # 认证相关逻辑
│   │
│   ├── utils/                       # 工具函数
│   │   ├── format.ts                # 格式化函数
│   │   ├── validate.ts              # 校验函数
│   │   └── helpers.ts               # 辅助函数
│   │
│   ├── types/                       # TypeScript 类型定义
│   │   ├── account.ts
│   │   ├── trade.ts
│   │   └── common.ts
│   │
│   ├── assets/                      # 资源文件
│   │   ├── styles/                  # 样式
│   │   │   ├── main.css             # 主样式（Tailwind 入口）
│   │   │   └── variables.css        # CSS 变量
│   │   └── images/
│   │
│   └── config/                      # 配置文件
│       └── constants.ts             # 常量配置
│
├── index.html
├── vite.config.ts                   # Vite 配置
├── tsconfig.json                    # TypeScript 配置
├── tailwind.config.js               # Tailwind 配置
├── package.json
└── README.md
```

---

## 3. 路由设计

### 3.1 路由配置

```typescript
// src/router/routes.ts

import type { RouteRecordRaw } from 'vue-router'

export const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/login/Login.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    name: 'Layout',
    component: () => import('@/layouts/DefaultLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      // 账户管理
      {
        path: 'account',
        name: 'AccountList',
        component: () => import('@/views/account/AccountList.vue'),
        meta: {
          title: '账户管理',
          icon: 'wallet'
        }
      },
      {
        path: 'account/:id',
        name: 'AccountDetail',
        component: () => import('@/views/account/AccountDetail.vue'),
        meta: { title: '账户详情' }
      },

      // 交易记录
      {
        path: 'trade',
        name: 'TradeList',
        component: () => import('@/views/trade/TradeList.vue'),
        meta: {
          title: '交易记录',
          icon: 'transaction'
        }
      },

      // 事件中心
      {
        path: 'event',
        name: 'EventCenter',
        component: () => import('@/views/event/EventCenter.vue'),
        meta: {
          title: '事件中心',
          icon: 'bell'
        }
      },

      // 股票详情
      {
        path: 'stock/:symbol',
        name: 'StockDetail',
        component: () => import('@/views/stock/StockDetail.vue'),
        meta: { title: '股票详情' }
      }
    ]
  }
]
```

### 3.2 路由守卫

```typescript
// src/router/index.ts

import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { routes } from './routes'

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 全局前置守卫
router.beforeEach((to, from, next) => {
  const userStore = useUserStore()

  // 需要认证的路由
  if (to.meta.requiresAuth !== false) {
    if (!userStore.isLoggedIn) {
      next({ name: 'Login', query: { redirect: to.fullPath } })
      return
    }
  }

  // 设置页面标题
  if (to.meta.title) {
    document.title = `${to.meta.title} - 投资管理系统`
  }

  next()
})

export default router
```

---

## 4. 状态管理

### 4.1 Store 设计原则

- **按业务模块划分** Store（不要一个大 Store）
- **使用组合式 API 风格**（setup 语法）
- **保持 Store 轻量**（复杂逻辑放 composables）

### 4.2 用户 Store

```typescript
// src/stores/user.ts

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User } from '@/types/user'

export const useUserStore = defineStore('user', () => {
  // State
  const user = ref<User | null>(null)
  const token = ref<string | null>(localStorage.getItem('token'))

  // Getters
  const isLoggedIn = computed(() => !!token.value)
  const userName = computed(() => user.value?.user_name || '')

  // Actions
  function setUser(userData: User) {
    user.value = userData
  }

  function setToken(newToken: string) {
    token.value = newToken
    localStorage.setItem('token', newToken)
  }

  function logout() {
    user.value = null
    token.value = null
    localStorage.removeItem('token')
  }

  return {
    // State
    user,
    token,
    // Getters
    isLoggedIn,
    userName,
    // Actions
    setUser,
    setToken,
    logout
  }
})
```

### 4.3 账户 Store

```typescript
// src/stores/account.ts

import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Account } from '@/types/account'
import { accountApi } from '@/api/account'

export const useAccountStore = defineStore('account', () => {
  // State
  const accounts = ref<Account[]>([])
  const currentAccount = ref<Account | null>(null)
  const loading = ref(false)

  // Actions
  async function fetchAccounts() {
    loading.value = true
    try {
      const res = await accountApi.query({ status: 'active' })
      accounts.value = res.list
    } finally {
      loading.value = false
    }
  }

  async function fetchAccountDetail(accountId: number) {
    loading.value = true
    try {
      currentAccount.value = await accountApi.detail({ account_id: accountId })
    } finally {
      loading.value = false
    }
  }

  function setCurrentAccount(account: Account) {
    currentAccount.value = account
  }

  return {
    accounts,
    currentAccount,
    loading,
    fetchAccounts,
    fetchAccountDetail,
    setCurrentAccount
  }
})
```

---

## 5. 组件设计

### 5.1 组件分类

| 类型 | 位置 | 命名规则 | 示例 |
|------|------|---------|------|
| **页面组件** | `views/` | 大驼峰 | `AccountList.vue` |
| **业务组件** | `components/{模块}/` | 大驼峰 | `CreateAccountDialog.vue` |
| **通用组件** | `components/common/` | 大驼峰 | `PageHeader.vue` |
| **布局组件** | `layouts/` | 大驼峰 + Layout后缀 | `DefaultLayout.vue` |

### 5.2 组件规范

#### 5.2.1 单文件组件结构

```vue
<!-- 推荐：使用 setup 语法糖 + TypeScript -->
<script setup lang="ts">
import { ref, computed } from 'vue'
import type { Account } from '@/types/account'

// Props
interface Props {
  account: Account
  editable?: boolean
}
const props = withDefaults(defineProps<Props>(), {
  editable: false
})

// Emits
interface Emits {
  (e: 'update', account: Account): void
  (e: 'delete', id: number): void
}
const emit = defineEmits<Emits>()

// State
const loading = ref(false)

// Computed
const displayName = computed(() => props.account.account_name)

// Methods
const handleUpdate = () => {
  emit('update', props.account)
}
</script>

<template>
  <div class="account-card">
    <h3>{{ displayName }}</h3>
    <button v-if="editable" @click="handleUpdate">编辑</button>
  </div>
</template>

<style scoped>
/* 组件样式（使用 Tailwind 优先，必要时写 scoped 样式） */
.account-card {
  @apply p-4 border rounded-lg shadow-sm;
}
</style>
```

#### 5.2.2 Props 定义规范

```typescript
// ✅ 推荐：使用 TypeScript 接口
interface Props {
  accountId: number              // 必填
  accountName?: string           // 可选
  status?: 'active' | 'inactive' // 枚举类型
  data?: Account                 // 复杂类型
}

const props = withDefaults(defineProps<Props>(), {
  status: 'active'
})
```

#### 5.2.3 Emits 定义规范

```typescript
// ✅ 推荐：定义清晰的事件类型
interface Emits {
  (e: 'update', value: string): void
  (e: 'delete', id: number): void
  (e: 'submit', data: FormData): void
}

const emit = defineEmits<Emits>()
```

### 5.3 组件通信

| 场景 | 方案 | 示例 |
|------|------|------|
| **父 → 子** | Props | `<Child :data="data" />` |
| **子 → 父** | Emits | `emit('update', value)` |
| **兄弟组件** | Store | Pinia |
| **跨层级** | Provide/Inject | 主题、配置 |
| **全局状态** | Pinia | 用户信息、账户列表 |

---

## 6. API 调用

### 6.1 Axios 配置

```typescript
// src/api/index.ts

import axios from 'axios'
import type { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'
import router from '@/router'

// 响应数据类型
interface Response<T = any> {
  code: number
  message: string
  data: T
  timestamp: string
}

// 创建 axios 实例
const instance: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
  timeout: 10000
})

// 请求拦截器
instance.interceptors.request.use(
  (config) => {
    const userStore = useUserStore()

    // 添加 token
    if (userStore.token) {
      config.headers.Authorization = `Bearer ${userStore.token}`
    }

    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
instance.interceptors.response.use(
  (response: AxiosResponse<Response>) => {
    const { code, message, data } = response.data

    // 业务成功
    if (code === 0) {
      return data
    }

    // 业务错误
    ElMessage.error(message || '请求失败')
    return Promise.reject(new Error(message))
  },
  (error) => {
    // HTTP 错误
    if (error.response) {
      const { status } = error.response

      if (status === 401) {
        ElMessage.error('登录已过期，请重新登录')
        const userStore = useUserStore()
        userStore.logout()
        router.push('/login')
      } else {
        ElMessage.error(error.response.data?.message || '请求失败')
      }
    } else {
      ElMessage.error('网络错误')
    }

    return Promise.reject(error)
  }
)

// 统一的 POST 请求方法
export function post<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
  return instance.post(url, data, config)
}

export default instance
```

### 6.2 API 模块化

```typescript
// src/api/account.ts

import { post } from './index'
import type { Account, AccountDetail } from '@/types/account'

export const accountApi = {
  /**
   * 查询账户列表
   */
  query(params: {
    status?: string
    page?: number
    page_size?: number
  }) {
    return post<{
      total: number
      list: Account[]
    }>('/account/query', params)
  },

  /**
   * 获取账户详情
   */
  detail(params: { account_id: number }) {
    return post<AccountDetail>('/account/detail', params)
  },

  /**
   * 创建账户
   */
  create(params: {
    account_name: string
    account_type: string
    initial_balance?: number
  }) {
    return post<Account>('/account/create', params)
  },

  /**
   * 更新账户
   */
  update(params: {
    account_id: number
    account_name?: string
    status?: string
  }) {
    return post<Account>('/account/update', params)
  },

  /**
   * 删除账户
   */
  delete(params: { account_id: number }) {
    return post<void>('/account/delete', params)
  }
}
```

### 6.3 在组件中使用

```vue
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { accountApi } from '@/api/account'
import type { Account } from '@/types/account'

const accounts = ref<Account[]>([])
const loading = ref(false)

const fetchAccounts = async () => {
  loading.value = true
  try {
    const res = await accountApi.query({ status: 'active' })
    accounts.value = res.list
  } catch (error) {
    console.error('获取账户列表失败', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchAccounts()
})
</script>
```

---

## 7. 样式规范

### 7.1 Tailwind CSS 配置

```javascript
// tailwind.config.js

/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#667eea',     // 主色
        success: '#10b981',     // 成功
        danger: '#ef4444',      // 危险
        warning: '#f59e0b',     // 警告
        profit: '#10b981',      // 盈利（绿色）
        loss: '#ef4444',        // 亏损（红色）
      },
      spacing: {
        '128': '32rem',
      }
    },
  },
  plugins: [],
}
```

### 7.2 样式使用原则

1. **优先使用 Tailwind 工具类**

```vue
<!-- ✅ 推荐 -->
<div class="p-4 bg-white rounded-lg shadow-md">
  <h2 class="text-xl font-bold text-gray-800">标题</h2>
</div>

<!-- ❌ 不推荐 -->
<div class="custom-card">
  <h2 class="custom-title">标题</h2>
</div>
<style scoped>
.custom-card { padding: 1rem; background: white; ... }
</style>
```

2. **复杂样式使用 @apply**

```vue
<style scoped>
.btn-primary {
  @apply px-4 py-2 bg-primary text-white rounded-md hover:bg-primary-dark;
}
</style>
```

3. **全局样式统一管理**

```css
/* src/assets/styles/main.css */

@tailwind base;
@tailwind components;
@tailwind utilities;

/* 全局样式 */
@layer components {
  .card {
    @apply p-4 bg-white rounded-lg shadow-sm border border-gray-200;
  }

  .profit-text {
    @apply text-profit font-semibold;
  }

  .loss-text {
    @apply text-loss font-semibold;
  }
}
```

---

## 8. 代码规范

### 8.1 命名规范

| 类型 | 规则 | 示例 |
|------|------|------|
| **文件名** | 大驼峰 | `AccountList.vue`, `CreateDialog.vue` |
| **组件名** | 大驼峰 | `<AccountCard />` |
| **变量** | 小驼峰 | `accountList`, `userName` |
| **常量** | 大写下划线 | `API_BASE_URL`, `MAX_RETRY` |
| **类型/接口** | 大驼峰 | `interface Account {}` |
| **方法** | 小驼峰 | `fetchAccounts()`, `handleSubmit()` |

### 8.2 TypeScript 规范

```typescript
// ✅ 推荐：明确的类型定义
interface Account {
  account_id: number
  account_name: string
  account_type: 'A股' | '港股' | '美股'
  status: 'active' | 'inactive'
  created_at: string
}

// ✅ 推荐：使用类型推断
const loading = ref(false)  // 自动推断为 Ref<boolean>

// ❌ 不推荐：使用 any
const data: any = {}
```

### 8.3 组件注册规范

```typescript
// ✅ 推荐：自动导入（使用 unplugin-vue-components）
// vite.config.ts
import Components from 'unplugin-vue-components/vite'
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers'

export default {
  plugins: [
    Components({
      resolvers: [ElementPlusResolver()],
    })
  ]
}

// 无需手动导入，直接使用
<template>
  <el-button>按钮</el-button>
</template>
```

### 8.4 代码注释规范

```typescript
/**
 * 获取账户详情
 * @param accountId 账户ID
 * @returns 账户详细信息
 */
async function fetchAccountDetail(accountId: number): Promise<AccountDetail> {
  // 实现...
}
```

---

## 9. 开发工具配置

### 9.1 VSCode 推荐插件

- **Vue - Official** (Vue 语言支持)
- **TypeScript Vue Plugin (Volar)**
- **Tailwind CSS IntelliSense**
- **ESLint**
- **Prettier**

### 9.2 ESLint 配置

```javascript
// .eslintrc.cjs

module.exports = {
  env: {
    browser: true,
    es2021: true,
    node: true
  },
  extends: [
    'eslint:recommended',
    'plugin:vue/vue3-recommended',
    'plugin:@typescript-eslint/recommended',
    'prettier'
  ],
  parser: 'vue-eslint-parser',
  parserOptions: {
    ecmaVersion: 'latest',
    parser: '@typescript-eslint/parser',
    sourceType: 'module'
  },
  rules: {
    'vue/multi-word-component-names': 'off',
    '@typescript-eslint/no-explicit-any': 'warn'
  }
}
```

### 9.3 Prettier 配置

```json
// .prettierrc

{
  "semi": false,
  "singleQuote": true,
  "printWidth": 100,
  "trailingComma": "none",
  "arrowParens": "always"
}
```

---

## 10. 性能优化

### 10.1 路由懒加载

```typescript
// ✅ 推荐：使用动态导入
{
  path: '/account',
  component: () => import('@/views/account/AccountList.vue')
}
```

### 10.2 组件懒加载

```vue
<script setup lang="ts">
import { defineAsyncComponent } from 'vue'

// 懒加载重组件
const HeavyChart = defineAsyncComponent(() =>
  import('@/components/charts/KLineChart.vue')
)
</script>
```

### 10.3 列表虚拟滚动

对于大量数据的列表，使用虚拟滚动：

```vue
<script setup lang="ts">
import { ElTableV2 } from 'element-plus'
</script>

<template>
  <el-table-v2
    :columns="columns"
    :data="data"
    :width="700"
    :height="400"
  />
</template>
```

---

## 11. 开发流程

### 11.1 项目初始化

```bash
# 1. 创建项目
npm create vite@latest frontend -- --template vue-ts

# 2. 安装依赖
cd frontend
npm install

# 3. 安装必要的包
npm install vue-router pinia
npm install axios dayjs lodash-es
npm install element-plus
npm install -D tailwindcss postcss autoprefixer
npm install -D @types/lodash-es

# 4. 初始化 Tailwind
npx tailwindcss init -p

# 5. 启动开发服务器
npm run dev
```

### 11.2 新增页面流程

1. 在 `views/` 下创建页面组件
2. 在 `router/routes.ts` 添加路由
3. 在 `api/` 下创建对应的 API 接口
4. 在 `types/` 下定义 TypeScript 类型
5. 如需全局状态，在 `stores/` 下创建 Store

---

## 12. 技术选型确认 ✅

- [x] **UI 组件库**：Element Plus（企业级表格/表单组件强大）
- [x] **图表库**：ECharts（K 线图支持完善）
- [x] **应用类型**：SPA（单页应用，不使用 SSR）
- [x] **国际化**：不需要（仅中文）
- [x] **主题切换**：不需要（仅亮色模式）

## 13. 完整依赖清单

### 生产依赖

```json
{
  "dependencies": {
    "vue": "^3.4.0",
    "vue-router": "^4.2.0",
    "pinia": "^2.1.0",
    "element-plus": "^2.5.0",
    "axios": "^1.6.0",
    "dayjs": "^1.11.0",
    "echarts": "^5.4.0",
    "vue-echarts": "^6.6.0",
    "@vueuse/core": "^10.7.0",
    "lodash-es": "^4.17.0"
  }
}
```

### 开发依赖

```json
{
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.0.0",
    "typescript": "^5.3.0",
    "vite": "^5.0.0",
    "tailwindcss": "^3.4.0",
    "postcss": "^8.4.0",
    "autoprefixer": "^10.4.0",
    "unplugin-vue-components": "^0.26.0",
    "unplugin-auto-import": "^0.17.0",
    "@types/lodash-es": "^4.17.0",
    "eslint": "^8.56.0",
    "eslint-plugin-vue": "^9.20.0",
    "@typescript-eslint/parser": "^6.19.0",
    "@typescript-eslint/eslint-plugin": "^6.19.0",
    "prettier": "^3.2.0"
  }
}
```

---

## 14. 相关文档

- [后端架构设计](./backend-architecture.md)
- [技术栈选型](./tech-stack.md)
- [数据库设计](../database/schema-v1.md)
- [PRD v3.1](../../prd/v3/main.md)

---

## 15. 修改记录

| 版本 | 日期 | 变更 |
|------|------|------|
| v1.1 | 2025-01-15 | 确认技术选型：Element Plus + ECharts，不需要国际化和暗黑模式 |
| v1.0 | 2025-01-15 | 初始版本：完整的前端架构设计 |

---

**创建者**: Claude Code
**审核**: 待审核
**状态**: ✅ 设计完成（技术选型已确认）
