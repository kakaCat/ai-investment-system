# 前端开发架构约束

⚠️ **开发前必读** - 违反架构将无法通过Code Review

---

## 📐 强制阅读文档

开发任何前端功能前，必须阅读以下文档：

1. [UI设计规范](../docs/design/ui/) ⭐
2. [组件设计规范](../docs/design/ui/) ⭐
3. [API调用规范](../docs/design/api/) ⭐

**为什么必须阅读**？
- 确保UI符合设计稿
- 避免重复造轮子
- 统一代码风格
- 提高可维护性

---

## ✅ 开发前检查清单

### 新增页面前

- [ ] 已阅读UI设计稿
- [ ] 确认路由配置（在 `router/index.ts` 中）
- [ ] 使用 **Composition API**（不使用Options API）
- [ ] 遵循 `views/` 目录结构
- [ ] 页面文件命名: `{module}/{page-name}.vue`
  - ✅ 正确: `views/account/AccountList.vue`
  - ❌ 错误: `views/AccountList.vue`

### 新增组件前

- [ ] 检查是否已有类似组件（避免重复）
- [ ] 确定组件粒度（原子/分子/生物组件）
- [ ] 编写 TypeScript Props 类型定义
- [ ] 添加组件文档注释
- [ ] 组件文件命名: 大驼峰 `ComponentName.vue`
  - ✅ 正确: `components/common/DataTable.vue`
  - ❌ 错误: `components/common/dataTable.vue`

### 调用API前

- [ ] 使用统一的 API Service（不直接调用axios）
- [ ] 使用 **POST方法**（与后端协议一致）
- [ ] 正确处理 loading/error 状态
- [ ] 添加用户友好的错误提示（ElMessage）
- [ ] API调用放在 `services/api/` 中
  - ✅ 正确: `services/api/account.ts`
  - ❌ 错误: 在组件中直接 `axios.post()`

---

## ❌ 常见违反示例

### 错误1: 使用Options API

```vue
<!-- ❌ 错误 - Options API -->
<script>
export default {
  data() {
    return {
      accountList: []
    }
  },
  methods: {
    fetchAccounts() {
      // ...
    }
  }
}
</script>
```

```vue
<!-- ✅ 正确 - Composition API -->
<script setup lang="ts">
import { ref } from 'vue'

const accountList = ref([])

const fetchAccounts = async () => {
  // ...
}
</script>
```

### 错误2: 组件中直接调用axios

```vue
<!-- ❌ 错误 - 组件中直接调用 -->
<script setup lang="ts">
import axios from 'axios'

const fetchAccounts = async () => {
  const res = await axios.post('/api/v1/account/query', {})
  accountList.value = res.data
}
</script>
```

```vue
<!-- ✅ 正确 - 使用API Service -->
<script setup lang="ts">
import { getAccountList } from '@/services/api/account'

const fetchAccounts = async () => {
  const data = await getAccountList()
  accountList.value = data.accounts
}
</script>
```

### 错误3: 不处理loading和error状态

```vue
<!-- ❌ 错误 - 没有loading和错误处理 -->
<script setup lang="ts">
const fetchAccounts = async () => {
  const data = await getAccountList()
  accountList.value = data.accounts
}
</script>
```

```vue
<!-- ✅ 正确 - 完整的状态处理 -->
<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { getAccountList } from '@/services/api/account'

const loading = ref(false)
const accountList = ref([])

const fetchAccounts = async () => {
  try {
    loading.value = true
    const data = await getAccountList()
    accountList.value = data.accounts
  } catch (error) {
    ElMessage.error('获取账户列表失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div v-loading="loading">
    <!-- 内容 -->
  </div>
</template>
```

### 错误4: Props没有类型定义

```vue
<!-- ❌ 错误 - 没有类型定义 -->
<script setup lang="ts">
defineProps(['accountId', 'accountName'])
</script>
```

```vue
<!-- ✅ 正确 - 完整的类型定义 -->
<script setup lang="ts">
interface Props {
  accountId: number
  accountName: string
  showActions?: boolean  // 可选属性
}

const props = withDefaults(defineProps<Props>(), {
  showActions: true  // 默认值
})
</script>
```

---

## ✅ 正确示例（完整）

### 页面组件示例

```vue
<!-- views/account/AccountList.vue -->
<template>
  <div class="account-list-container">
    <!-- 标题栏 -->
    <div class="header">
      <h2>账户管理</h2>
      <el-button type="primary" @click="handleAdd">
        添加账户
      </el-button>
    </div>

    <!-- 数据表格 -->
    <el-table
      v-loading="loading"
      :data="accountList"
      border
      stripe
    >
      <el-table-column prop="account_name" label="账户名称" />
      <el-table-column prop="market" label="市场" />
      <el-table-column prop="total_value" label="总市值" />
      <el-table-column label="操作" width="200">
        <template #default="{ row }">
          <el-button size="small" @click="handleDetail(row.account_id)">
            详情
          </el-button>
          <el-button size="small" type="danger" @click="handleDelete(row.account_id)">
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getAccountList, deleteAccount } from '@/services/api/account'
import type { Account } from '@/types/account'

const router = useRouter()
const loading = ref(false)
const accountList = ref<Account[]>([])

// 获取账户列表
const fetchAccounts = async () => {
  try {
    loading.value = true
    const data = await getAccountList()
    accountList.value = data.accounts
  } catch (error) {
    ElMessage.error('获取账户列表失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

// 添加账户
const handleAdd = () => {
  router.push('/account/add')
}

// 查看详情
const handleDetail = (accountId: number) => {
  router.push(`/account/detail/${accountId}`)
}

// 删除账户
const handleDelete = async (accountId: number) => {
  try {
    await ElMessageBox.confirm('确定要删除此账户吗？', '提示', {
      type: 'warning'
    })

    loading.value = true
    await deleteAccount(accountId)
    ElMessage.success('删除成功')
    await fetchAccounts()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  } finally {
    loading.value = false
  }
}

// 页面加载时获取数据
onMounted(() => {
  fetchAccounts()
})
</script>

<style scoped lang="scss">
.account-list-container {
  padding: 20px;

  .header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;

    h2 {
      margin: 0;
      font-size: 24px;
      font-weight: 600;
    }
  }
}
</style>
```

### 可复用组件示例

```vue
<!-- components/account/AccountCard.vue -->
<template>
  <el-card class="account-card" shadow="hover">
    <template #header>
      <div class="card-header">
        <span class="account-name">{{ accountName }}</span>
        <el-tag :type="marketType">{{ marketLabel }}</el-tag>
      </div>
    </template>

    <div class="account-stats">
      <div class="stat-item">
        <div class="stat-label">总市值</div>
        <div class="stat-value">{{ formatMoney(totalValue) }}</div>
      </div>
      <div class="stat-item">
        <div class="stat-label">盈亏</div>
        <div class="stat-value" :class="profitClass">
          {{ formatMoney(profitLoss) }}
        </div>
      </div>
    </div>

    <div class="card-actions">
      <slot name="actions" />
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  accountId: number
  accountName: string
  market: string
  totalValue: number
  profitLoss: number
}

const props = defineProps<Props>()

// 市场类型映射
const marketMap: Record<string, { label: string; type: string }> = {
  'A_SHARE': { label: 'A股', type: 'success' },
  'HK_STOCK': { label: '港股', type: 'warning' },
  'US_STOCK': { label: '美股', type: 'primary' }
}

const marketLabel = computed(() => marketMap[props.market]?.label || props.market)
const marketType = computed(() => marketMap[props.market]?.type || 'info')

const profitClass = computed(() => {
  return props.profitLoss >= 0 ? 'profit' : 'loss'
})

// 格式化金额
const formatMoney = (value: number) => {
  return new Intl.NumberFormat('zh-CN', {
    style: 'currency',
    currency: 'CNY'
  }).format(value)
}
</script>

<style scoped lang="scss">
.account-card {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;

    .account-name {
      font-size: 16px;
      font-weight: 600;
    }
  }

  .account-stats {
    display: flex;
    justify-content: space-around;
    margin: 16px 0;

    .stat-item {
      text-align: center;

      .stat-label {
        font-size: 12px;
        color: #909399;
        margin-bottom: 8px;
      }

      .stat-value {
        font-size: 18px;
        font-weight: 600;

        &.profit {
          color: #67c23a;
        }

        &.loss {
          color: #f56c6c;
        }
      }
    }
  }

  .card-actions {
    margin-top: 16px;
  }
}
</style>
```

### API Service示例

```typescript
// services/api/account.ts
import request from '@/utils/request'
import type { Account } from '@/types/account'

/**
 * 获取账户列表
 */
export async function getAccountList() {
  return request.post<{ accounts: Account[] }>('/account/query', {})
}

/**
 * 获取账户详情
 */
export async function getAccountDetail(accountId: number) {
  return request.post<{ account: Account; stats: any }>('/account/detail', {
    account_id: accountId
  })
}

/**
 * 创建账户
 */
export async function createAccount(data: Partial<Account>) {
  return request.post('/account/create', data)
}

/**
 * 更新账户
 */
export async function updateAccount(accountId: number, data: Partial<Account>) {
  return request.post('/account/update', {
    account_id: accountId,
    ...data
  })
}

/**
 * 删除账户
 */
export async function deleteAccount(accountId: number) {
  return request.post('/account/delete', {
    account_id: accountId
  })
}
```

---

## 📁 目录结构规范

```
frontend/src/
├── views/                # 页面组件
│   ├── account/          # 账户模块
│   │   ├── AccountList.vue
│   │   ├── AccountDetail.vue
│   │   └── AccountForm.vue
│   ├── holding/          # 持仓模块
│   └── trade/            # 交易模块
│
├── components/           # 公共组件
│   ├── common/           # 通用组件（按钮、表格等）
│   ├── account/          # 账户相关组件
│   ├── holding/          # 持仓相关组件
│   └── layout/           # 布局组件
│
├── services/             # 业务逻辑
│   ├── api/              # API调用（按模块）
│   │   ├── account.ts
│   │   ├── holding.ts
│   │   └── trade.ts
│   └── utils/            # 工具函数
│
├── stores/               # 状态管理（Pinia）
│   ├── user.ts
│   ├── account.ts
│   └── app.ts
│
├── router/               # 路由配置
│   └── index.ts
│
├── types/                # TypeScript类型定义
│   ├── account.ts
│   ├── holding.ts
│   └── api.ts
│
├── utils/                # 工具函数
│   ├── request.ts        # axios封装
│   ├── format.ts         # 格式化函数
│   └── validate.ts       # 验证函数
│
└── assets/               # 静态资源
    ├── styles/           # 样式文件
    └── images/           # 图片
```

---

## 🎨 样式规范

### 使用SCSS

```vue
<style scoped lang="scss">
// ✅ 使用SCSS变量
$primary-color: #409eff;
$danger-color: #f56c6c;

.container {
  padding: 20px;

  .header {
    color: $primary-color;
  }
}
</style>
```

### 使用Scoped样式

```vue
<!-- ✅ 正确 - 使用scoped -->
<style scoped>
.container {
  /* 样式只作用于当前组件 */
}
</style>

<!-- ❌ 错误 - 全局样式污染 -->
<style>
.container {
  /* 影响所有组件 */
}
</style>
```

---

## 🔗 相关资源

- [UI设计规范](../docs/design/ui/)
- [Vue 3 文档](https://vuejs.org/)
- [Element Plus 文档](https://element-plus.org/)
- [TypeScript 文档](https://www.typescriptlang.org/)
- [全局架构守卫规范](~/.claude/CLAUDE.md#️-架构守卫规范)

---

## 💡 最佳实践

1. **组件化思维** - 复用性强的部分抽取成组件
2. **类型安全** - 使用TypeScript类型定义
3. **错误处理** - 所有API调用都要处理错误
4. **Loading状态** - 异步操作添加loading提示
5. **代码分割** - 使用路由懒加载
6. **性能优化** - 使用v-memo、v-once等优化指令

---

**最后更新**: 2025-11-19
**维护者**: Frontend Team
