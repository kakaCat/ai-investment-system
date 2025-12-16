<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { queryAccounts, createAccount, updateAccount, deleteAccount } from '@/api/account'

const router = useRouter()

interface Account {
  account_id: number
  broker_name: string
  account_no: string
  market: string
  total_assets: number
  available_cash: number
  market_value: number
  profit_loss: number
  profit_loss_rate: number
  status: string
}

const loading = ref(false)
const accounts = ref<Account[]>([])
const showAddAccountDialog = ref(false)
const showEditAccountDialog = ref(false)
const currentAccountId = ref<number | null>(null)

// 表单数据
const accountForm = ref({
  broker_name: '',
  account_no: '',
  market: 'A',
  initial_cash: 0,
  notes: ''
})

// 市场类型选项
const marketTypes = [
  { label: 'A股', value: 'A' },
  { label: '港股', value: 'HK' },
  { label: '美股', value: 'US' }
]

// 券商选项
const brokers = ['华泰证券', '中信证券', '招商证券', '富途证券', '老虎证券', '盈透证券', '雪盈证券', '其他']

// 查询账户列表
const fetchAccounts = async () => {
  loading.value = true
  try {
    const response = await queryAccounts({})
    if (response.data && response.data.items) {
      accounts.value = response.data.items
    } else {
      accounts.value = []
    }
  } catch (error: any) {
    console.error('查询账户列表失败:', error)
    ElMessage.error('查询账户列表失败: ' + (error.message || '请检查网络连接'))
    accounts.value = []
  } finally {
    loading.value = false
  }
}

// 总资产统计
const totalStats = computed(() => {
  const total = accounts.value.reduce((sum, acc) => sum + (acc.total_assets || 0), 0)
  const cash = accounts.value.reduce((sum, acc) => sum + (acc.available_cash || 0), 0)
  const invested = accounts.value.reduce((sum, acc) => sum + (acc.market_value || 0), 0)
  const profitLoss = accounts.value.reduce((sum, acc) => sum + (acc.profit_loss || 0), 0)
  const profitLossRate = invested > 0 ? (profitLoss / invested) * 100 : 0

  return { total, cash, invested, profitLoss, profitLossRate }
})

// 查看账户详情
const viewDetail = (accountId: number) => {
  router.push(`/account/detail/${accountId}`)
}

// 重置表单
const resetForm = () => {
  accountForm.value = {
    broker_name: '',
    account_no: '',
    market: 'A',
    initial_cash: 0,
    notes: ''
  }
}

// 添加账户
const addAccount = () => {
  resetForm()
  currentAccountId.value = null
  showAddAccountDialog.value = true
}

// 编辑账户
const editAccount = (accountId: number) => {
  currentAccountId.value = accountId
  const account = accounts.value.find(a => a.account_id === accountId)
  if (account) {
    accountForm.value = {
      broker_name: account.broker_name,
      account_no: account.account_no,
      market: account.market,
      initial_cash: account.total_assets || 0,
      notes: ''
    }
  }
  showEditAccountDialog.value = true
}

// 提交账户表单
const submitAccount = async () => {
  loading.value = true
  try {
    if (currentAccountId.value) {
      // 编辑账户
      await updateAccount({
        account_id: currentAccountId.value,
        broker_name: accountForm.value.broker_name,
        account_no: accountForm.value.account_no,
        notes: accountForm.value.notes
      })
      ElMessage.success('账户更新成功')
      showEditAccountDialog.value = false
    } else {
      // 新增账户
      await createAccount({
        broker_name: accountForm.value.broker_name,
        account_no: accountForm.value.account_no,
        market: accountForm.value.market,
        initial_cash: accountForm.value.initial_cash,
        notes: accountForm.value.notes
      })
      ElMessage.success('账户添加成功')
      showAddAccountDialog.value = false
    }

    resetForm()
    // 刷新列表
    await fetchAccounts()
  } catch (error: any) {
    console.error('操作失败:', error)
    ElMessage.error('操作失败: ' + (error.message || '请检查网络连接'))
  } finally {
    loading.value = false
  }
}

// 归档账户（删除）
const archiveAccount = async (accountId: number) => {
  try {
    await deleteAccount({ account_id: accountId })
    ElMessage.success('账户已删除')
    await fetchAccounts()
  } catch (error: any) {
    console.error('删除失败:', error)
    ElMessage.error('删除失败: ' + (error.message || ''))
  }
}

// 盈亏颜色
const profitClass = (value: number) => {
  if (value > 0) return 'text-red-600'
  if (value < 0) return 'text-green-600'
  return 'text-gray-600'
}

// 获取市场类型标签
const getMarketLabel = (market: string) => {
  const labels: Record<string, string> = {
    'A': 'A股',
    'HK': '港股',
    'US': '美股'
  }
  return labels[market] || market
}

// 获取市场类型颜色
const getMarketTagType = (market: string) => {
  if (market === 'A') return 'danger'
  if (market === 'HK') return 'warning'
  if (market === 'US') return 'success'
  return ''
}

onMounted(() => {
  fetchAccounts()
})
</script>

<template>
  <div v-loading="loading" class="account-list p-6">
    <!-- 页面标题 -->
    <div class="mb-6">
      <h1 class="text-2xl font-bold text-gray-800">账户管理</h1>
      <p class="text-sm text-gray-500 mt-1">管理您的投资账户，查看资金分布和整体表现</p>
    </div>

    <!-- 总览统计卡片 -->
    <div class="grid grid-cols-1 md:grid-cols-5 gap-4 mb-6">
      <div class="bg-white rounded-lg border shadow-sm p-5">
        <div class="text-sm text-gray-500 mb-2">总资产</div>
        <div class="text-2xl font-bold text-gray-900">
          ¥{{ totalStats.total.toLocaleString() }}
        </div>
      </div>
      <div class="bg-white rounded-lg border shadow-sm p-5">
        <div class="text-sm text-gray-500 mb-2">可用资金</div>
        <div class="text-2xl font-bold text-green-600">
          ¥{{ totalStats.cash.toLocaleString() }}
        </div>
      </div>
      <div class="bg-white rounded-lg border shadow-sm p-5">
        <div class="text-sm text-gray-500 mb-2">已投资</div>
        <div class="text-2xl font-bold text-blue-600">
          ¥{{ totalStats.invested.toLocaleString() }}
        </div>
      </div>
      <div class="bg-white rounded-lg border shadow-sm p-5">
        <div class="text-sm text-gray-500 mb-2">总盈亏</div>
        <div class="text-2xl font-bold" :class="profitClass(totalStats.profitLoss)">
          {{ totalStats.profitLoss >= 0 ? '+' : '' }}¥{{ totalStats.profitLoss.toLocaleString() }}
        </div>
      </div>
      <div class="bg-white rounded-lg border shadow-sm p-5">
        <div class="text-sm text-gray-500 mb-2">收益率</div>
        <div class="text-2xl font-bold" :class="profitClass(totalStats.profitLossRate)">
          {{ totalStats.profitLossRate >= 0 ? '+' : '' }}{{ totalStats.profitLossRate.toFixed(2) }}%
        </div>
      </div>
    </div>

    <!-- 账户列表 -->
    <div class="bg-white rounded-lg border shadow-sm">
      <!-- 列表头部 -->
      <div class="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
        <div>
          <h2 class="text-lg font-semibold text-gray-900">我的账户</h2>
          <p class="text-sm text-gray-500 mt-1">共 {{ accounts.length }} 个账户</p>
        </div>
        <el-button type="primary" @click="addAccount">
          <span class="mr-1">+</span> 添加账户
        </el-button>
      </div>

      <!-- 账户卡片列表 -->
      <div class="p-6 space-y-4">
        <div
          v-for="account in accounts"
          :key="account.account_id"
          class="border border-gray-200 rounded-lg p-5 hover:border-blue-300 hover:shadow-md transition-all cursor-pointer"
          @click="viewDetail(account.account_id)"
        >
          <!-- 账户头部 -->
          <div class="flex items-start justify-between mb-4">
            <div class="flex-1">
              <div class="flex items-center gap-3 mb-2">
                <h3 class="text-lg font-bold text-gray-900">{{ account.broker_name }}</h3>
                <el-tag size="small" :type="getMarketTagType(account.market)">
                  {{ getMarketLabel(account.market) }}
                </el-tag>
                <span class="text-sm text-gray-500">账号: ****{{ account.account_no.slice(-4) }}</span>
              </div>
              <div class="text-sm text-gray-500">
                账户编号: {{ account.account_no }}
              </div>
            </div>

            <!-- 操作按钮 -->
            <div class="flex gap-2">
              <el-button size="small" @click.stop="editAccount(account.account_id)">
                编辑
              </el-button>
              <el-button size="small" type="danger" plain @click.stop="archiveAccount(account.account_id)">
                归档
              </el-button>
            </div>
          </div>

          <!-- 账户数据 -->
          <div class="grid grid-cols-5 gap-6">
            <div>
              <div class="text-xs text-gray-500 mb-1">总资产</div>
              <div class="text-lg font-semibold text-gray-900">
                ¥{{ (account.total_assets || 0).toLocaleString() }}
              </div>
            </div>
            <div>
              <div class="text-xs text-gray-500 mb-1">可用资金</div>
              <div class="text-lg font-semibold text-green-600">
                ¥{{ (account.available_cash || 0).toLocaleString() }}
              </div>
              <div class="text-xs text-gray-500 mt-1">
                {{ account.total_assets > 0 ? ((account.available_cash / account.total_assets) * 100).toFixed(1) : '0.0' }}%
              </div>
            </div>
            <div>
              <div class="text-xs text-gray-500 mb-1">已投资</div>
              <div class="text-lg font-semibold text-blue-600">
                ¥{{ (account.market_value || 0).toLocaleString() }}
              </div>
              <div class="text-xs text-gray-500 mt-1">
                {{ account.total_assets > 0 ? ((account.market_value / account.total_assets) * 100).toFixed(1) : '0.0' }}%
              </div>
            </div>
            <div>
              <div class="text-xs text-gray-500 mb-1">盈亏金额</div>
              <div class="text-lg font-semibold" :class="profitClass(account.profit_loss || 0)">
                {{ (account.profit_loss || 0) >= 0 ? '+' : '' }}¥{{ (account.profit_loss || 0).toLocaleString() }}
              </div>
            </div>
            <div>
              <div class="text-xs text-gray-500 mb-1">收益率</div>
              <div class="text-lg font-semibold" :class="profitClass(account.profit_loss_rate || 0)">
                {{ (account.profit_loss_rate || 0) >= 0 ? '+' : '' }}{{ (account.profit_loss_rate || 0).toFixed(2) }}%
              </div>
            </div>
          </div>

          <!-- 快速操作提示 -->
          <div class="mt-4 pt-4 border-t border-gray-100 text-sm text-gray-500 flex items-center justify-between">
            <span>点击查看详情 →</span>
            <span class="text-xs">
              最后更新: {{ new Date().toLocaleDateString('zh-CN') }}
            </span>
          </div>
        </div>

        <!-- 空状态 -->
        <div
          v-if="accounts.length === 0"
          class="text-center py-16 border-2 border-dashed border-gray-300 rounded-lg"
        >
          <div class="text-6xl mb-4">🏦</div>
          <div class="text-gray-600 mb-4">暂无账户</div>
          <el-button type="primary" @click="addAccount">
            添加第一个账户
          </el-button>
        </div>
      </div>
    </div>

    <!-- 添加账户对话框 -->
    <el-dialog
      v-model="showAddAccountDialog"
      title="添加账户"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form :model="accountForm" label-width="100px">
        <el-form-item label="券商名称" required>
          <el-select v-model="accountForm.broker_name" placeholder="请选择券商" style="width: 100%">
            <el-option v-for="broker in brokers" :key="broker" :label="broker" :value="broker" />
          </el-select>
        </el-form-item>

        <el-form-item label="账户号码" required>
          <el-input v-model="accountForm.account_no" placeholder="例如：1234567890" />
        </el-form-item>

        <el-form-item label="市场类型" required>
          <el-select v-model="accountForm.market" placeholder="请选择市场" style="width: 100%">
            <el-option v-for="market in marketTypes" :key="market.value" :label="market.label" :value="market.value" />
          </el-select>
        </el-form-item>

        <el-form-item label="初始资金">
          <el-input-number
            v-model="accountForm.initial_cash"
            :min="0"
            :step="1000"
            style="width: 100%"
          />
        </el-form-item>

        <el-form-item label="备注">
          <el-input v-model="accountForm.notes" type="textarea" :rows="3" placeholder="选填" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showAddAccountDialog = false">取消</el-button>
        <el-button type="primary" :loading="loading" @click="submitAccount">
          确定
        </el-button>
      </template>
    </el-dialog>

    <!-- 编辑账户对话框 -->
    <el-dialog
      v-model="showEditAccountDialog"
      title="编辑账户"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form :model="accountForm" label-width="100px">
        <el-form-item label="券商名称" required>
          <el-select v-model="accountForm.broker_name" placeholder="请选择券商" style="width: 100%">
            <el-option v-for="broker in brokers" :key="broker" :label="broker" :value="broker" />
          </el-select>
        </el-form-item>

        <el-form-item label="账户号码" required>
          <el-input v-model="accountForm.account_no" placeholder="例如：1234567890" />
        </el-form-item>

        <el-form-item label="备注">
          <el-input v-model="accountForm.notes" type="textarea" :rows="3" placeholder="选填" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showEditAccountDialog = false">取消</el-button>
        <el-button type="primary" :loading="loading" @click="submitAccount">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.account-list {
  min-height: 100vh;
  background-color: #f5f5f5;
}
</style>
