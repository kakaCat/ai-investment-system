# 前端项目初始化指南

**版本**: v1.0
**日期**: 2025-01-15
**技术栈**: Vue 3 + TypeScript + Vite + Element Plus + ECharts

---

## 目录

- [1. 项目初始化](#1-项目初始化)
- [2. 依赖安装](#2-依赖安装)
- [3. 配置文件](#3-配置文件)
- [4. 目录结构创建](#4-目录结构创建)
- [5. Mock 数据配置](#5-mock-数据配置)
- [6. 启动项目](#6-启动项目)

---

## 1. 项目初始化

### 1.1 创建项目

```bash
# 进入项目根目录
cd /Users/mac/Documents/ai/stock

# 使用 Vite 创建 Vue 3 + TypeScript 项目
npm create vite@latest frontend -- --template vue-ts

# 进入前端目录
cd frontend
```

### 1.2 清理模板文件

```bash
# 删除模板示例文件
rm -rf src/components/HelloWorld.vue
rm -rf src/assets/vue.svg
```

---

## 2. 依赖安装

### 2.1 安装生产依赖

```bash
# 核心依赖
npm install vue-router@4 pinia@2

# UI 组件库
npm install element-plus

# 图表库
npm install echarts vue-echarts

# HTTP 请求和工具库
npm install axios dayjs lodash-es

# Vue 工具库
npm install @vueuse/core

# 图标库
npm install @element-plus/icons-vue
```

### 2.2 安装开发依赖

```bash
# Tailwind CSS
npm install -D tailwindcss@3 postcss autoprefixer

# 自动导入（Element Plus 组件和 API）
npm install -D unplugin-vue-components unplugin-auto-import

# TypeScript 类型
npm install -D @types/lodash-es

# 代码质量工具
npm install -D eslint eslint-plugin-vue
npm install -D @typescript-eslint/parser @typescript-eslint/eslint-plugin
npm install -D prettier eslint-config-prettier eslint-plugin-prettier

# Mock 数据
npm install -D vite-plugin-mock mockjs
npm install -D @types/mockjs
```

---

## 3. 配置文件

### 3.1 Vite 配置

创建 `vite.config.ts`：

```typescript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'
import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers'
import { viteMockServe } from 'vite-plugin-mock'

export default defineConfig({
  plugins: [
    vue(),

    // 自动导入 Vue API
    AutoImport({
      imports: ['vue', 'vue-router', 'pinia'],
      resolvers: [ElementPlusResolver()],
      dts: 'src/auto-imports.d.ts'
    }),

    // 自动导入 Element Plus 组件
    Components({
      resolvers: [ElementPlusResolver()],
      dts: 'src/components.d.ts'
    }),

    // Mock 数据
    viteMockServe({
      mockPath: 'mock',
      enable: true
    })
  ],

  resolve: {
    alias: {
      '@': resolve(__dirname, 'src')
    }
  },

  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
})
```

### 3.2 TypeScript 配置

更新 `tsconfig.json`：

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "module": "ESNext",
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "skipLibCheck": true,

    /* Bundler mode */
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "preserve",

    /* Linting */
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,

    /* Path Alias */
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"]
    }
  },
  "include": ["src/**/*.ts", "src/**/*.d.ts", "src/**/*.tsx", "src/**/*.vue"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

### 3.3 Tailwind CSS 配置

```bash
# 初始化 Tailwind
npx tailwindcss init -p
```

更新 `tailwind.config.js`：

```javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#667eea',
        success: '#10b981',
        danger: '#ef4444',
        warning: '#f59e0b',
        profit: '#10b981',  // 盈利绿色
        loss: '#ef4444',    // 亏损红色
      },
    },
  },
  plugins: [],
}
```

创建 `src/assets/styles/main.css`：

```css
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

### 3.4 ESLint 配置

创建 `.eslintrc.cjs`：

```javascript
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

创建 `.prettierrc`：

```json
{
  "semi": false,
  "singleQuote": true,
  "printWidth": 100,
  "trailingComma": "none",
  "arrowParens": "always"
}
```

### 3.5 环境变量配置

创建 `.env.development`：

```bash
# 开发环境配置
VITE_APP_TITLE=投资管理系统
VITE_API_BASE_URL=/api/v1
VITE_USE_MOCK=true
```

创建 `.env.production`：

```bash
# 生产环境配置
VITE_APP_TITLE=投资管理系统
VITE_API_BASE_URL=https://api.example.com/api/v1
VITE_USE_MOCK=false
```

---

## 4. 目录结构创建

```bash
# 在 frontend/src 目录下创建目录结构
mkdir -p src/{views,components,api,stores,router,composables,utils,types,assets/styles,config,mock}

# 创建具体业务目录
mkdir -p src/views/{account,trade,stock,event,login}
mkdir -p src/components/{common,account,trade,holding,charts}
mkdir -p src/stores
mkdir -p src/api
```

---

## 5. Mock 数据配置

### 5.1 创建 Mock 目录结构

```bash
# 在项目根目录创建 mock 目录
mkdir -p mock
```

### 5.2 Mock 数据示例

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
              status: 'active',
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
  }
] as MockMethod[]
```

---

## 6. 启动项目

### 6.1 更新 package.json scripts

```json
{
  "scripts": {
    "dev": "vite",
    "build": "vue-tsc && vite build",
    "preview": "vite preview",
    "lint": "eslint . --ext .vue,.js,.jsx,.cjs,.mjs,.ts,.tsx,.cts,.mts --fix",
    "format": "prettier --write src/"
  }
}
```

### 6.2 启动开发服务器

```bash
npm run dev
```

浏览器访问：http://localhost:3000

---

## 7. 快速开始脚本

创建 `scripts/setup-frontend.sh`：

```bash
#!/bin/bash

echo "🚀 开始初始化前端项目..."

# 1. 创建项目
echo "📦 创建 Vite 项目..."
npm create vite@latest frontend -- --template vue-ts

cd frontend

# 2. 安装依赖
echo "📥 安装依赖..."
npm install

# 3. 安装额外依赖
echo "📥 安装生产依赖..."
npm install vue-router pinia element-plus echarts vue-echarts axios dayjs lodash-es @vueuse/core @element-plus/icons-vue

echo "📥 安装开发依赖..."
npm install -D tailwindcss postcss autoprefixer
npm install -D unplugin-vue-components unplugin-auto-import
npm install -D @types/lodash-es
npm install -D eslint eslint-plugin-vue @typescript-eslint/parser @typescript-eslint/eslint-plugin prettier
npm install -D vite-plugin-mock mockjs @types/mockjs

# 4. 初始化 Tailwind
echo "🎨 初始化 Tailwind CSS..."
npx tailwindcss init -p

# 5. 创建目录结构
echo "📁 创建目录结构..."
mkdir -p src/{views,components,api,stores,router,composables,utils,types,assets/styles,config}
mkdir -p src/views/{account,trade,stock,event,login}
mkdir -p src/components/{common,account,trade,holding,charts}
mkdir -p mock

echo "✅ 前端项目初始化完成！"
echo "📝 下一步："
echo "  1. 配置 vite.config.ts"
echo "  2. 配置 tailwind.config.js"
echo "  3. 创建 src/assets/styles/main.css"
echo "  4. 运行 npm run dev 启动开发服务器"
```

---

## 8. 验证安装

创建简单的测试页面验证环境：

更新 `src/App.vue`：

```vue
<script setup lang="ts">
import { ElButton, ElMessage } from 'element-plus'

const handleClick = () => {
  ElMessage.success('Element Plus 安装成功！')
}
</script>

<template>
  <div class="p-8">
    <h1 class="text-3xl font-bold text-primary mb-4">
      投资管理系统
    </h1>
    <p class="mb-4">技术栈：Vue 3 + TypeScript + Element Plus</p>
    <el-button type="primary" @click="handleClick">
      测试 Element Plus
    </el-button>
  </div>
</template>

<style scoped>
/* Tailwind 样式测试 */
</style>
```

更新 `src/main.ts`：

```typescript
import { createApp } from 'vue'
import App from './App.vue'
import '@/assets/styles/main.css'

const app = createApp(App)

app.mount('#app')
```

---

## 9. 下一步

项目初始化完成后，可以开始：

1. **创建路由配置** - `src/router/index.ts`
2. **创建 API 封装** - `src/api/index.ts`
3. **创建 Store** - `src/stores/user.ts`
4. **创建页面组件** - 按照 PRD 和原型图实现

---

## 10. 相关文档

- [前端架构设计](../../design/architecture/frontend-architecture.md)
- [Mock 数据方案](./mock-data-guide.md)
- [组件开发指南](./component-guide.md)

---

**创建者**: Claude Code
**日期**: 2025-01-15
**状态**: ✅ 完成
