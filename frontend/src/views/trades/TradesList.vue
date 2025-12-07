<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { queryTrades, createTrade } from '@/api/trade'
import { queryAccounts } from '@/api/account'

const router = useRouter()

const loading = ref(false)
const selectedAccount = ref('all')
const selectedType = ref('all')
const showAddTradeDialog = ref(false)

// 交易表单数据
const tradeForm = ref({
  account_id: '',
  trade_type: 'buy',
  symbol: '',
  stock_name: '',
  quantity: 0,
  price: 0,
  trade_date: new Date().toISOString().split('T')[0],
  trade_time: new Date().toTimeString().split(' ')[0].substring(0, 5),
  fee: 0,
  notes: ''
})

// 账户列表
const accounts = ref<any[]>([
  { account_id: 'all', name: '全部账户' }
])

// 交易类型
const tradeTypes = ref([
  { value: 'all', label: '全部类型' },
  { value: 'buy', label: '买入' },
  { value: 'sell', label: '卖出' },
  { value: 'dividend', label: '分红' },
  { value: 'deposit', label: '入金' },
  { value: 'withdraw', label: '出金' }
])

// 交易记录
const trades = ref<any[]>([])

// 筛选后的交易
const filteredTrades = computed(() => {
  return trades.value.filter(trade => {
    let match = true
    if (selectedAccount.value !== 'all') {
      match = match && trade.account_id === Number(selectedAccount.value)
    }
    if (selectedType.value !== 'all') {
      match = match && trade.trade_type === selectedType.value
    }
    return match
  })
})

// 统计数据
const statistics = computed(() => {
  const buyAmount = filteredTrades.value
    .filter(t => t.trade_type === 'buy')
    .reduce((sum, t) => sum + (t.total_amount || 0), 0)
  const sellAmount = filteredTrades.value
    .filter(t => t.trade_type === 'sell')
    .reduce((sum, t) => sum + (t.total_amount || 0), 0)
  const totalFee = filteredTrades.value.reduce((sum, t) => sum + (t.commission || 0) + (t.tax || 0), 0)
  const netFlow = filteredTrades.value.reduce((sum, t) => {
    const amount = t.total_amount || 0
    const fee = (t.commission || 0) + (t.tax || 0)
    if (t.trade_type === 'buy') return sum - amount - fee
    if (t.trade_type === 'sell') return sum + amount - fee
    if (t.trade_type === 'deposit') return sum + amount
    if (t.trade_type === 'withdraw') return sum - amount
    if (t.trade_type === 'dividend') return sum + amount
    return sum
  }, 0)

  return {
    total_count: filteredTrades.value.length,
    buy_amount: buyAmount,
    sell_amount: sellAmount,
    total_fee: totalFee,
    net_flow: netFlow
  }
})

// 获取交易类型标签
const getTypeLabel = (type: string) => {
  const labels: Record<string, string> = {
    buy: '买入',
    sell: '卖出',
    dividend: '分红',
    deposit: '入金',
    withdraw: '出金'
  }
  return labels[type] || type
}

// 获取交易类型颜色
const getTypeColor = (type: string) => {
  const colors: Record<string, string> = {
    buy: 'text-red-600',
    sell: 'text-green-600',
    dividend: 'text-blue-600',
    deposit: 'text-purple-600',
    withdraw: 'text-orange-600'
  }
  return colors[type] || 'text-gray-600'
}

// 获取交易类型背景色
const getTypeBgColor = (type: string) => {
  const colors: Record<string, string> = {
    buy: 'bg-red-50',
    sell: 'bg-green-50',
    dividend: 'bg-blue-50',
    deposit: 'bg-purple-50',
    withdraw: 'bg-orange-50'
  }
  return colors[type] || 'bg-gray-50'
}

// 返回
const goBack = () => {
  router.back()
}

// 加载账户列表
const loadAccounts = async () => {
  try {
    const response = await queryAccounts({})
    if (response.data && response.data.items) {
      accounts.value = [
        { account_id: 'all', name: '全部账户' },
        ...response.data.items.map((account: any) => ({
          account_id: account.account_id,
          name: `${account.broker_name} (${account.account_no.slice(-4)})`
        }))
      ]
    }
  } catch (error) {
    console.error('加载账户列表失败:', error)
  }
}

// 加载交易记录
const loadTrades = async () => {
  loading.value = true
  try {
    const params: any = {}
    if (selectedAccount.value !== 'all') {
      params.account_id = Number(selectedAccount.value)
    }
    if (selectedType.value !== 'all') {
      params.trade_type = selectedType.value
    }

    const response = await queryTrades(params)
    if (response.data && response.data.items) {
      trades.value = response.data.items
    }
  } catch (error: any) {
    console.error('加载交易记录失败:', error)
    ElMessage.error('加载失败: ' + (error.message || '请检查网络连接'))
  } finally {
    loading.value = false
  }
}

// 刷新数据
const refresh = () => {
  loadTrades()
  ElMessage.success('数据已刷新')
}

// 导出数据
const exportData = () => {
  ElMessage.info('导出功能开发中')
}

// 重置筛选
const resetFilters = () => {
  selectedAccount.value = 'all'
  selectedType.value = 'all'
}

// 打开添加交易对话框
const openAddTradeDialog = () => {
  // 重置表单
  tradeForm.value = {
    account_id: accounts.value[1]?.account_id || '',
    trade_type: 'buy',
    symbol: '',
    stock_name: '',
    quantity: 0,
    price: 0,
    trade_date: new Date().toISOString().split('T')[0],
    trade_time: new Date().toTimeString().split(' ')[0].substring(0, 5),
    fee: 0,
    notes: ''
  }
  showAddTradeDialog.value = true
}

// 提交交易记录
const submitTrade = async () => {
  loading.value = true
  try {
    const params = {
      account_id: Number(tradeForm.value.account_id),
      trade_type: tradeForm.value.trade_type,
      symbol: tradeForm.value.symbol,
      stock_name: tradeForm.value.stock_name,
      quantity: tradeForm.value.quantity,
      price: tradeForm.value.price,
      trade_date: tradeForm.value.trade_date,
      trade_time: tradeForm.value.trade_time,
      fee: tradeForm.value.fee,
      notes: tradeForm.value.notes
    }

    await createTrade(params)
    ElMessage.success('交易记录添加成功')
    showAddTradeDialog.value = false

    // 刷新列表
    await loadTrades()
  } catch (error: any) {
    console.error('添加交易失败:', error)
    ElMessage.error('添加失败: ' + (error.message || '请检查网络连接'))
  } finally {
    loading.value = false
  }
}

// 计算交易金额
const calculateAmount = computed(() => {
  return tradeForm.value.quantity * tradeForm.value.price
})

onMounted(async () => {
  await loadAccounts()
  await loadTrades()
})
</script>

<template>
  <div class="trades-list p-6">
    <!-- 页面标题 -->
    <div class="mb-6">
      <h1 class="text-2xl font-bold text-gray-900">📝 交易记录</h1>
      <p class="text-gray-600 text-sm mt-1">管理和跟踪所有投资交易</p>
    </div>

    <!-- 统计卡片 -->
    <div class="grid grid-cols-1 md:grid-cols-5 gap-4 mb-6">
      <div class="bg-white rounded-lg border shadow-sm p-6">
          <p class="text-sm text-gray-600 mb-2">交易笔数</p>
          <p class="text-3xl font-bold text-blue-600">{{ statistics.total_count }}</p>
        </div>
        <div class="bg-white rounded-lg border shadow-sm p-6">
          <p class="text-sm text-gray-600 mb-2">买入金额</p>
          <p class="text-3xl font-bold text-red-600">¥{{ statistics.buy_amount.toLocaleString() }}</p>
        </div>
        <div class="bg-white rounded-lg border shadow-sm p-6">
          <p class="text-sm text-gray-600 mb-2">卖出金额</p>
          <p class="text-3xl font-bold text-green-600">¥{{ statistics.sell_amount.toLocaleString() }}</p>
        </div>
        <div class="bg-white rounded-lg border shadow-sm p-6">
          <p class="text-sm text-gray-600 mb-2">手续费</p>
          <p class="text-3xl font-bold text-orange-600">¥{{ statistics.total_fee.toLocaleString() }}</p>
        </div>
        <div class="bg-white rounded-lg border shadow-sm p-6">
          <p class="text-sm text-gray-600 mb-2">净流入</p>
          <p
            class="text-3xl font-bold"
            :class="statistics.net_flow >= 0 ? 'text-red-600' : 'text-green-600'"
          >
            {{ statistics.net_flow >= 0 ? '+' : '' }}¥{{ Math.abs(statistics.net_flow).toLocaleString() }}
          </p>
        </div>
      </div>

    <!-- 筛选栏 -->
    <div class="bg-white rounded-lg border shadow-sm p-4 mb-6">
      <div class="flex items-center gap-4 flex-wrap">
        <div class="flex items-center gap-2">
          <span class="text-sm text-gray-600">账户:</span>
          <select
            v-model="selectedAccount"
            class="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option v-for="account in accounts" :key="account.account_id" :value="account.account_id">
              {{ account.name }}
            </option>
          </select>
        </div>

        <div class="flex items-center gap-2">
          <span class="text-sm text-gray-600">类型:</span>
          <select
            v-model="selectedType"
            class="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option v-for="type in tradeTypes" :key="type.value" :value="type.value">
              {{ type.label }}
            </option>
          </select>
        </div>

        <el-button text type="primary" size="small" @click="resetFilters">
          重置筛选
        </el-button>

        <div class="ml-auto flex gap-2">
          <el-button type="primary" size="small" @click="openAddTradeDialog">
            <span class="mr-1">+</span> 记录交易
          </el-button>
          <el-button size="small" @click="refresh">刷新</el-button>
          <el-button size="small" @click="exportData">导出记录</el-button>
        </div>
      </div>
    </div>

    <!-- 交易记录列表 -->
    <div class="bg-white rounded-lg border shadow-sm overflow-hidden">
        <div class="px-6 py-4 border-b border-gray-200">
          <h3 class="text-lg font-semibold text-gray-900">
            交易明细 <span class="text-blue-600">({{ filteredTrades.length }}笔)</span>
          </h3>
        </div>

        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">日期时间</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">账户</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">类型</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">股票</th>
                <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">数量</th>
                <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">价格</th>
                <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">金额</th>
                <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">手续费</th>
                <th class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">状态</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="trade in filteredTrades" :key="trade.trade_id" class="hover:bg-gray-50 transition">
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="text-sm text-gray-900">{{ trade.trade_date }}</div>
                  <div class="text-xs text-gray-500">{{ trade.trade_time || '-' }}</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {{ accounts.find(a => a.account_id === trade.account_id)?.name || '-' }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span
                    class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                    :class="[getTypeBgColor(trade.trade_type), getTypeColor(trade.trade_type)]"
                  >
                    {{ getTypeLabel(trade.trade_type) }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {{ trade.symbol }} {{ trade.stock_name }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-900">
                  {{ trade.quantity > 0 ? trade.quantity.toLocaleString() : '-' }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-900">
                  {{ trade.price > 0 ? `¥${trade.price.toFixed(2)}` : '-' }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-right font-semibold">
                  <span :class="getTypeColor(trade.trade_type)">
                    {{ trade.trade_type === 'sell' || trade.trade_type === 'deposit' || trade.trade_type === 'dividend' ? '+' : '-' }}¥{{ (trade.total_amount || 0).toLocaleString() }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-600">
                  ¥{{ ((trade.commission || 0) + (trade.tax || 0)).toFixed(2) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-center">
                  <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                    已完成
                  </span>
                </td>
              </tr>
            </tbody>
          </table>

          <!-- 空状态 -->
          <div
            v-if="filteredTrades.length === 0"
            class="text-center py-16"
          >
            <div class="text-6xl mb-4">📝</div>
            <div class="text-gray-600 mb-2">暂无交易记录</div>
            <div class="text-sm text-gray-500">请调整筛选条件或开始新的交易</div>
          </div>
        </div>
    </div>

    <!-- 添加交易对话框 -->
    <el-dialog
      v-model="showAddTradeDialog"
      title="记录交易"
      width="700px"
      :close-on-click-modal="false"
    >
      <el-form :model="tradeForm" label-width="100px">
        <el-form-item label="账户" required>
          <el-select v-model="tradeForm.account_id" placeholder="请选择账户" style="width: 100%">
            <el-option
              v-for="account in accounts.filter(a => a.account_id !== 'all')"
              :key="account.account_id"
              :label="account.name"
              :value="account.account_id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="交易类型" required>
          <el-select v-model="tradeForm.trade_type" placeholder="请选择类型" style="width: 100%">
            <el-option label="买入" value="buy" />
            <el-option label="卖出" value="sell" />
            <el-option label="分红" value="dividend" />
            <el-option label="入金" value="deposit" />
            <el-option label="出金" value="withdraw" />
          </el-select>
        </el-form-item>

        <el-form-item
          v-if="['buy', 'sell', 'dividend'].includes(tradeForm.trade_type)"
          label="股票代码"
          required
        >
          <el-input v-model="tradeForm.symbol" placeholder="例如：600519" />
        </el-form-item>

        <el-form-item
          v-if="['buy', 'sell', 'dividend'].includes(tradeForm.trade_type)"
          label="股票名称"
          required
        >
          <el-input v-model="tradeForm.stock_name" placeholder="例如：贵州茅台" />
        </el-form-item>

        <div class="grid grid-cols-2 gap-4">
          <el-form-item
            v-if="['buy', 'sell'].includes(tradeForm.trade_type)"
            label="数量"
            required
          >
            <el-input-number
              v-model="tradeForm.quantity"
              :min="0"
              :step="100"
              style="width: 100%"
            />
          </el-form-item>

          <el-form-item
            v-if="['buy', 'sell'].includes(tradeForm.trade_type)"
            label="价格"
            required
          >
            <el-input-number
              v-model="tradeForm.price"
              :min="0"
              :precision="2"
              :step="0.01"
              style="width: 100%"
            />
          </el-form-item>
        </div>

        <el-form-item
          v-if="['buy', 'sell'].includes(tradeForm.trade_type)"
          label="交易金额"
        >
          <el-input
            :model-value="`¥${calculateAmount.toLocaleString()}`"
            disabled
          />
        </el-form-item>

        <div class="grid grid-cols-2 gap-4">
          <el-form-item label="交易日期" required>
            <el-date-picker
              v-model="tradeForm.trade_date"
              type="date"
              placeholder="选择日期"
              style="width: 100%"
              value-format="YYYY-MM-DD"
            />
          </el-form-item>

          <el-form-item label="交易时间" required>
            <el-time-picker
              v-model="tradeForm.trade_time"
              placeholder="选择时间"
              style="width: 100%"
              format="HH:mm"
              value-format="HH:mm"
            />
          </el-form-item>
        </div>

        <el-form-item label="手续费">
          <el-input-number
            v-model="tradeForm.fee"
            :min="0"
            :precision="2"
            :step="0.01"
            style="width: 100%"
          />
        </el-form-item>

        <el-form-item label="备注">
          <el-input
            v-model="tradeForm.notes"
            type="textarea"
            :rows="3"
            placeholder="选填"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showAddTradeDialog = false">取消</el-button>
        <el-button type="primary" @click="submitTrade" :loading="loading">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.trades-list {
  background-color: #f5f5f5;
}
</style>
