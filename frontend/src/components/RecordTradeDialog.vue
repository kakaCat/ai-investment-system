<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import type { TradeType } from '@/types/trade'
import { TRADE_TYPE_LABELS } from '@/types/trade'

interface Props {
  visible: boolean
  accountId?: number
  symbol?: string // 预填充股票代码
}

const props = withDefaults(defineProps<Props>(), {
  visible: false
})

const emit = defineEmits<{
  'update:visible': [visible: boolean]
  confirm: [data: any]
}>()

const dialogVisible = computed({
  get: () => props.visible,
  set: (val) => emit('update:visible', val)
})

// 表单数据
const formData = ref({
  account_id: props.accountId || null as number | null,
  symbol: '',
  stock_name: '',
  trade_type: 'buy' as TradeType,
  quantity: null as number | null,
  price: null as number | null,
  fee: 0,
  trade_date: new Date().toISOString().split('T')[0],
  notes: ''
})

// Mock 账户列表
const accounts = ref([
  { account_id: 1, account_name: '中信证券-A股账户' },
  { account_id: 2, account_name: '富途证券-港股账户' },
  { account_id: 3, account_name: '盈透证券-美股账户' }
])

// 计算总金额
const totalAmount = computed(() => {
  const qty = formData.value.quantity || 0
  const price = formData.value.price || 0
  return qty * price
})

// 计算实际金额（含手续费）
const actualAmount = computed(() => {
  const total = totalAmount.value
  const fee = formData.value.fee || 0

  if (formData.value.trade_type === 'buy') {
    return total + fee // 买入：总金额 + 手续费
  } else if (formData.value.trade_type === 'sell') {
    return total - fee // 卖出：总金额 - 手续费
  }
  return total
})

// 搜索股票
const searchingStock = ref(false)
const searchStock = async () => {
  if (!formData.value.symbol) {
    ElMessage.warning('请输入股票代码')
    return
  }

  searchingStock.value = true
  try {
    // Mock 搜索股票
    await new Promise(resolve => setTimeout(resolve, 500))

    // 简单的Mock数据
    const mockStocks: Record<string, string> = {
      '600519': '贵州茅台',
      '000858': '五粮液',
      '00700': '腾讯控股',
      'AAPL': 'Apple Inc.'
    }

    const name = mockStocks[formData.value.symbol]
    if (name) {
      formData.value.stock_name = name
      ElMessage.success('股票信息已获取')
    } else {
      ElMessage.warning('未找到该股票')
      formData.value.stock_name = ''
    }
  } catch (error) {
    ElMessage.error('搜索失败')
  } finally {
    searchingStock.value = false
  }
}

// 重置表单
const resetForm = () => {
  formData.value = {
    account_id: props.accountId || null,
    symbol: '',
    stock_name: '',
    trade_type: 'buy',
    quantity: null,
    price: null,
    fee: 0,
    trade_date: new Date().toISOString().split('T')[0],
    notes: ''
  }
}

// 提交
const submitting = ref(false)
const handleSubmit = async () => {
  // 验证
  if (!formData.value.account_id) {
    ElMessage.warning('请选择账户')
    return
  }
  if (!formData.value.symbol || !formData.value.stock_name) {
    ElMessage.warning('请输入并搜索股票')
    return
  }
  if (!formData.value.quantity || formData.value.quantity <= 0) {
    ElMessage.warning('请输入有效的数量')
    return
  }
  if (!formData.value.price || formData.value.price <= 0) {
    ElMessage.warning('请输入有效的价格')
    return
  }

  submitting.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 500))

    // 提交数据
    emit('confirm', {
      ...formData.value,
      amount: totalAmount.value,
      actual_amount: actualAmount.value
    })

    ElMessage.success('交易记录已保存')
    dialogVisible.value = false
    resetForm()
  } catch (error) {
    ElMessage.error('保存失败')
  } finally {
    submitting.value = false
  }
}

// 监听弹框打开，预填充数据
watch(() => props.visible, (val) => {
  if (val) {
    if (props.accountId) {
      formData.value.account_id = props.accountId
    }
    if (props.symbol) {
      formData.value.symbol = props.symbol
      searchStock()
    }
  }
})
</script>

<template>
  <el-dialog
    v-model="dialogVisible"
    title="记录交易"
    width="600px"
    :close-on-click-modal="false"
    @closed="resetForm"
  >
    <el-form :model="formData" label-width="100px">
      <el-form-item label="账户" required>
        <el-select v-model="formData.account_id" placeholder="选择账户" style="width: 100%">
          <el-option
            v-for="account in accounts"
            :key="account.account_id"
            :label="account.account_name"
            :value="account.account_id"
          />
        </el-select>
      </el-form-item>

      <el-form-item label="股票代码" required>
        <div class="flex gap-2" style="width: 100%">
          <el-input
            v-model="formData.symbol"
            placeholder="输入股票代码"
            @keyup.enter="searchStock"
          />
          <el-button :loading="searchingStock" @click="searchStock">搜索</el-button>
        </div>
      </el-form-item>

      <el-form-item label="股票名称">
        <el-input v-model="formData.stock_name" disabled placeholder="搜索后自动填充" />
      </el-form-item>

      <el-form-item label="交易类型" required>
        <el-radio-group v-model="formData.trade_type">
          <el-radio label="buy">{{ TRADE_TYPE_LABELS.buy }}</el-radio>
          <el-radio label="sell">{{ TRADE_TYPE_LABELS.sell }}</el-radio>
          <el-radio label="dividend">{{ TRADE_TYPE_LABELS.dividend }}</el-radio>
          <el-radio label="split">{{ TRADE_TYPE_LABELS.split }}</el-radio>
        </el-radio-group>
      </el-form-item>

      <el-form-item label="数量" required>
        <el-input-number
          v-model="formData.quantity"
          :min="1"
          :step="100"
          style="width: 100%"
          placeholder="输入数量"
        />
      </el-form-item>

      <el-form-item label="价格" required>
        <el-input-number
          v-model="formData.price"
          :min="0.01"
          :precision="2"
          :step="0.1"
          style="width: 100%"
          placeholder="输入价格"
        />
      </el-form-item>

      <el-form-item label="手续费">
        <el-input-number
          v-model="formData.fee"
          :min="0"
          :precision="2"
          :step="1"
          style="width: 100%"
          placeholder="输入手续费"
        />
      </el-form-item>

      <el-form-item label="交易日期" required>
        <el-date-picker
          v-model="formData.trade_date"
          type="date"
          placeholder="选择交易日期"
          style="width: 100%"
          value-format="YYYY-MM-DD"
        />
      </el-form-item>

      <el-form-item label="备注">
        <el-input
          v-model="formData.notes"
          type="textarea"
          :rows="2"
          placeholder="输入备注信息（可选）"
        />
      </el-form-item>

      <!-- 金额汇总 -->
      <el-form-item label="金额汇总">
        <div class="rounded-lg bg-gray-50 p-4" style="width: 100%">
          <div class="flex items-center justify-between">
            <span class="text-sm text-gray-600">交易金额:</span>
            <span class="font-semibold">¥{{ totalAmount.toLocaleString() }}</span>
          </div>
          <div class="mt-2 flex items-center justify-between">
            <span class="text-sm text-gray-600">手续费:</span>
            <span class="font-semibold">¥{{ (formData.fee || 0).toFixed(2) }}</span>
          </div>
          <div class="mt-2 flex items-center justify-between border-t pt-2">
            <span class="text-sm font-semibold">实际金额:</span>
            <span class="text-lg font-bold text-blue-600">
              ¥{{ actualAmount.toLocaleString() }}
            </span>
          </div>
        </div>
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="dialogVisible = false">取消</el-button>
      <el-button type="primary" :loading="submitting" @click="handleSubmit">
        确定
      </el-button>
    </template>
  </el-dialog>
</template>
