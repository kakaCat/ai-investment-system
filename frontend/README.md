# 投资管理系统 - 前端项目

基于 Vue 3 + TypeScript + Vite + Element Plus 的现代化前端应用。

## 技术栈

- **Vue 3.4+** - 组合式 API + `<script setup>` 语法糖
- **TypeScript 5.3+** - 类型安全
- **Vite 5.0+** - 快速构建工具
- **Element Plus 2.5+** - 企业级 UI 组件库
- **Pinia 2.1+** - 状态管理
- **Vue Router 4** - 路由管理
- **TailwindCSS 3.4+** - 原子化 CSS
- **Axios** - HTTP 请求
- **ECharts 5.4+** - 数据可视化

## 目录结构

```
src/
├── api/                 # API 接口封装
│   ├── request.ts       # Axios 封装
│   └── account.ts       # 账户相关接口
├── assets/              # 静态资源
│   └── styles/          # 样式文件
│       └── main.css     # Tailwind CSS
├── components/          # 公共组件
│   └── holding/         # 持仓相关组件
│       ├── HoldingTable.vue
│       └── WatchlistTable.vue
├── router/              # 路由配置
│   └── index.ts
├── stores/              # Pinia 状态管理
│   └── account.ts
├── types/               # TypeScript 类型定义
│   └── account.ts
├── views/               # 页面组件
│   ├── account/         # 账户管理
│   │   ├── AccountList.vue
│   │   └── AccountDetail.vue
│   └── login/           # 登录页面
│       └── Login.vue
├── App.vue              # 根组件
└── main.ts              # 入口文件

mock/                    # Mock 数据
└── account.ts           # 账户 Mock 数据
```

## 快速开始

### 1. 安装依赖

```bash
npm install
```

### 2. 启动开发服务器

```bash
npm run dev
```

浏览器访问：http://localhost:3000

### 3. 构建生产版本

```bash
npm run build
```

### 4. 预览生产版本

```bash
npm run preview
```

## 开发说明

### Mock 数据

当前使用 `vite-plugin-mock` 提供 Mock 数据，所有 API 请求会被拦截并返回模拟数据。

**配置**：
- Mock 文件位于 `mock/` 目录
- 环境变量 `VITE_USE_MOCK=true` 启用 Mock
- 切换真实后端：修改 `.env.production` 中的 `VITE_API_BASE_URL`

### 已实现功能

- ✅ 账户列表查询（筛选、分页）
- ✅ 账户详情展示
- ✅ 持仓股票列表（双列表设计）
- ✅ 关注股票列表
- ✅ 登录页面（开发模式）

### 待实现功能

- [ ] 账户创建/编辑/删除
- [ ] 交易记录管理
- [ ] 股票详情页面
- [ ] AI 投资分析
- [ ] 事件追踪系统
- [ ] 数据可视化图表

## 代码规范

### 组件命名

- 文件名：PascalCase（如 `AccountList.vue`）
- 组件名：PascalCase（如 `<AccountCard>`）
- Props：camelCase（如 `accountId`）
- Events：kebab-case（如 `@update-account`）

### 样式规范

优先使用 TailwindCSS 工具类：

```vue
<template>
  <div class="p-4 bg-white rounded-lg shadow-sm">
    <h2 class="text-xl font-bold mb-4">标题</h2>
  </div>
</template>
```

### TypeScript 规范

所有组件使用 TypeScript + 组合式 API：

```vue
<script setup lang="ts">
import { ref } from 'vue'
import type { Account } from '@/types/account'

interface Props {
  account: Account
  editable?: boolean
}
const props = withDefaults(defineProps<Props>(), {
  editable: false
})
</script>
```

## 相关文档

- [前端项目初始化指南](../docs/guides/setup/frontend-setup.md)
- [Mock 数据方案](../docs/guides/setup/mock-data-guide.md)
- [组件开发指南](../docs/guides/setup/component-guide.md)
- [前端架构设计](../docs/design/architecture/frontend-architecture.md)

## 常见问题

### Q: 如何添加新的 API 接口？

1. 在 `src/types/` 添加类型定义
2. 在 `src/api/` 添加接口封装
3. 在 `mock/` 添加 Mock 数据

### Q: 如何切换到真实后端？

修改 `.env.development` 或 `.env.production`：

```bash
VITE_USE_MOCK=false
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

### Q: Element Plus 组件未自动导入？

检查 `vite.config.ts` 中的 `unplugin-vue-components` 配置。

## License

MIT
