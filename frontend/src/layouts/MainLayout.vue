<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

// 导航菜单项
const menuItems = [
  {
    name: 'dashboard',
    path: '/dashboard',
    icon: '📊',
    label: '首页'
  },
  {
    name: 'accounts',
    path: '/account/list',
    icon: '💼',
    label: '账户管理'
  },
  {
    name: 'holdings',
    path: '/holdings',
    icon: '📈',
    label: '持仓管理'
  },
  {
    name: 'trades',
    path: '/trades',
    icon: '💸',
    label: '交易记录'
  },
  {
    name: 'events',
    path: '/events',
    icon: '📢',
    label: '事件中心'
  },
  {
    name: 'analysis',
    path: '/analysis',
    icon: '🤖',
    label: 'AI分析'
  },
  {
    name: 'ai-chat',
    path: '/ai-chat',
    icon: '💬',
    label: 'AI对话'
  },
  {
    name: 'settings',
    path: '/settings',
    icon: '⚙️',
    label: '系统设置'
  }
]

// 判断菜单项是否激活
const isActive = (path: string) => {
  return route.path.startsWith(path)
}

// 导航到指定路径
const navigateTo = (path: string) => {
  router.push(path)
}

// 用户信息
const userInfo = ref({
  name: '开发用户',
  email: 'dev@example.com'
})

// 退出登录
const logout = () => {
  localStorage.removeItem('token')
  router.push('/login')
}
</script>

<template>
  <div class="flex h-screen bg-gray-100">
    <!-- 侧边栏 -->
    <div class="w-64 bg-white border-r border-gray-200 flex flex-col">
      <!-- Logo -->
      <div class="h-16 flex items-center justify-center border-b border-gray-200">
        <h1 class="text-xl font-bold text-gray-900">💰 投资管理系统</h1>
      </div>

      <!-- 导航菜单 -->
      <nav class="flex-1 overflow-y-auto py-4">
        <div
          v-for="item in menuItems"
          :key="item.name"
          :class="[
            'mx-3 mb-1 px-4 py-3 rounded-lg cursor-pointer transition-all',
            isActive(item.path)
              ? 'bg-blue-50 text-blue-700 font-semibold border border-blue-200'
              : 'text-gray-700 hover:bg-gray-100'
          ]"
          @click="navigateTo(item.path)"
        >
          <div class="flex items-center space-x-3">
            <span class="text-xl">{{ item.icon }}</span>
            <span class="text-sm">{{ item.label }}</span>
          </div>
        </div>
      </nav>

      <!-- 用户信息 -->
      <div class="border-t border-gray-200 p-4">
        <div class="flex items-center space-x-3 mb-3">
          <div class="w-10 h-10 bg-blue-500 rounded-full flex items-center justify-center text-white font-semibold">
            {{ userInfo.name[0] }}
          </div>
          <div class="flex-1 min-w-0">
            <div class="text-sm font-medium text-gray-900 truncate">{{ userInfo.name }}</div>
            <div class="text-xs text-gray-500 truncate">{{ userInfo.email }}</div>
          </div>
        </div>
        <button
          class="w-full px-4 py-2 text-sm text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition"
          @click="logout"
        >
          退出登录
        </button>
      </div>
    </div>

    <!-- 主内容区域 -->
    <div class="flex-1 overflow-auto">
      <router-view />
    </div>
  </div>
</template>

<style scoped>
/* 滚动条样式 */
nav::-webkit-scrollbar {
  width: 6px;
}

nav::-webkit-scrollbar-track {
  background: transparent;
}

nav::-webkit-scrollbar-thumb {
  background: #e5e7eb;
  border-radius: 3px;
}

nav::-webkit-scrollbar-thumb:hover {
  background: #d1d5db;
}
</style>
