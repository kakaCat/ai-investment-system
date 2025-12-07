import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import MainLayout from '@/layouts/MainLayout.vue'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/',
    component: MainLayout,
    children: [
      // 仪表盘
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/dashboard/Dashboard.vue'),
        meta: { title: '仪表盘' }
      },
      // 账户管理
      {
        path: 'account/list',
        name: 'AccountList',
        component: () => import('@/views/account/AccountList.vue'),
        meta: { title: '账户列表' }
      },
      {
        path: 'account/detail/:id',
        name: 'AccountDetail',
        component: () => import('@/views/account/AccountDetail.vue'),
        meta: { title: '账户详情' }
      },
      // 持仓管理
      {
        path: 'holdings',
        name: 'Holdings',
        component: () => import('@/views/holdings/HoldingsList.vue'),
        meta: { title: '持仓管理' }
      },
      // 交易记录
      {
        path: 'trades',
        name: 'Trades',
        component: () => import('@/views/trades/TradesList.vue'),
        meta: { title: '交易记录' }
      },
      // 股票详情（通过持仓点击进入）
      {
        path: 'stocks/detail/:symbol',
        name: 'StockDetail',
        component: () => import('@/views/stocks/StockDetail.vue'),
        meta: { title: '股票详情' }
      },
      // 事件中心
      {
        path: 'events',
        name: 'Events',
        component: () => import('@/views/events/EventsList.vue'),
        meta: { title: '事件中心' }
      },
      {
        path: 'events/detail/:id',
        name: 'EventDetail',
        component: () => import('@/views/events/EventDetail.vue'),
        meta: { title: '事件详情' }
      },
      // AI分析
      {
        path: 'analysis',
        name: 'Analysis',
        component: () => import('@/views/analysis/AnalysisHub.vue'),
        meta: { title: 'AI分析' }
      },
      // 每日复盘 (v3.2)
      {
        path: 'review/daily',
        name: 'DailyReview',
        component: () => import('@/views/review/DailyReview.vue'),
        meta: { title: '每日复盘' }
      },
      // 系统设置
      {
        path: 'settings',
        name: 'Settings',
        component: () => import('@/views/settings/SettingsPage.vue'),
        meta: { title: '系统设置' }
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

  // 检查登录状态（开发阶段暂时跳过）
  const token = localStorage.getItem('token')
  if (to.meta.requiresAuth !== false && !token) {
    // 开发阶段：自动设置一个假 token
    localStorage.setItem('token', 'dev-token')
    next()
  } else {
    next()
  }
})

export default router
