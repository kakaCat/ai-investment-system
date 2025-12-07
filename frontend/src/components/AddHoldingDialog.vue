<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { ElMessage } from 'element-plus'

// Props 和 Emits
const props = defineProps<{
  visible: boolean
  accountId: number
  accountName: string
}>()

const emit = defineEmits<{
  'update:visible': [value: boolean]
  'success': []
}>()

// 表单数据
const formData = reactive({
  symbol: '',
  stock_name: '',
  quantity: '',
  buy_price: '',
  buy_date: '',
  notes: ''
})

// 表单验证规则
const rules = {
  symbol: [
    { required: true, message: '请输入或选择股票代码', trigger: 'blur' }
  ],
  stock_name: [
    { required: true, message: '请输入股票名称', trigger: 'blur' }
  ],
  quantity: [
    { required: true, message: '请输入持仓数量', trigger: 'blur' },
    {
      validator: (rule: any, value: any, callback: any) => {
        if (value && isNaN(Number(value))) {
          callback(new Error('请输入有效的数字'))
        } else if (Number(value) <= 0) {
          callback(new Error('数量必须大于0'))
        } else if (Number(value) % 100 !== 0 && formData.symbol.startsWith('6')) {
          // A股必须是100的倍数
          callback(new Error('A股必须是100股的倍数'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ],
  buy_price: [
    { required: true, message: '请输入买入价格', trigger: 'blur' },
    {
      validator: (rule: any, value: any, callback: any) => {
        if (value && isNaN(Number(value))) {
          callback(new Error('请输入有效的数字'))
        } else if (Number(value) <= 0) {
          callback(new Error('价格必须大于0'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ],
  buy_date: [
    { required: true, message: '请选择买入日期', trigger: 'change' }
  ]
}

// Mock 股票数据（实际应该调用API搜索）
const stockOptions = ref([
  { symbol: '600519', name: '贵州茅台', market: 'SH' },
  { symbol: '000858', name: '五粮液', market: 'SZ' },
  { symbol: '000333', name: '美的集团', market: 'SZ' },
  { symbol: '601318', name: '中国平安', market: 'SH' },
  { symbol: '00700', name: '腾讯控股', market: 'HK' },
  { symbol: 'AAPL', name: '苹果', market: 'US' },
  { symbol: 'TSLA', name: '特斯拉', market: 'US' }
])

// 股票搜索
const searchStock = (queryString: string, callback: any) => {
  if (!queryString) {
    callback(stockOptions.value)
    return
  }
  const results = stockOptions.value.filter(
    (stock) =>
      stock.symbol.toLowerCase().includes(queryString.toLowerCase()) ||
      stock.name.includes(queryString)
  )
  callback(results)
}

// 选择股票
const handleSelectStock = (item: any) => {
  formData.symbol = item.symbol
  formData.stock_name = item.name
}

// 加载状态
const loading = ref(false)
const formRef = ref()

// 计算总成本
const totalCost = computed(() => {
  const quantity = Number(formData.quantity) || 0
  const price = Number(formData.buy_price) || 0
  return (quantity * price).toFixed(2)
})

// 关闭弹框
const handleClose = () => {
  emit('update:visible', false)
  resetForm()
}

// 重置表单
const resetForm = () => {
  formRef.value?.resetFields()
  formData.symbol = ''
  formData.stock_name = ''
  formData.quantity = ''
  formData.buy_price = ''
  formData.buy_date = ''
  formData.notes = ''
}

// 提交表单
const handleSubmit = async () => {
  try {
    // 验证表单
    await formRef.value?.validate()

    loading.value = true

    // TODO: 调用添加持仓API
    // await holdingApi.create({
    //   account_id: props.accountId,
    //   symbol: formData.symbol,
    //   stock_name: formData.stock_name,
    //   quantity: Number(formData.quantity),
    //   buy_price: Number(formData.buy_price),
    //   buy_date: formData.buy_date,
    //   notes: formData.notes || undefined
    // })

    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1000))

    ElMessage.success(`成功添加 ${formData.stock_name}(${formData.symbol}) 到持仓`)
    emit('success')
    handleClose()
  } catch (error: any) {
    if (error.errors) {
      // 表单验证失败
      return
    }
    ElMessage.error(error.message || '添加持仓失败，请重试')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <el-dialog
    :model-value="visible"
    title="添加持仓"
    width="550px"
    @close="handleClose"
  >
    <!-- 账户信息提示 -->
    <div class="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
      <div class="flex items-center">
        <span class="text-2xl mr-3">📈</span>
        <div>
          <div class="font-semibold text-gray-900">{{ accountName }}</div>
          <div class="text-sm text-gray-600">添加新的持仓股票</div>
        </div>
      </div>
    </div>

    <el-form
      ref="formRef"
      :model="formData"
      :rules="rules"
      label-width="100px"
      label-position="right"
    >
      <!-- 股票搜索 -->
      <el-form-item label="股票代码" prop="symbol">
        <el-autocomplete
          v-model="formData.symbol"
          :fetch-suggestions="searchStock"
          placeholder="输入股票代码或名称搜索"
          class="w-full"
          @select="handleSelectStock"
        >
          <template #default="{ item }">
            <div class="flex justify-between items-center">
              <div>
                <span class="font-semibold">{{ item.symbol }}</span>
                <span class="text-gray-600 ml-2">{{ item.name }}</span>
              </div>
              <span class="text-xs text-gray-500">{{ item.market }}</span>
            </div>
          </template>
        </el-autocomplete>
        <div class="text-xs text-gray-500 mt-1">
          提示：输入代码或名称搜索股票
        </div>
      </el-form-item>

      <el-form-item label="股票名称" prop="stock_name">
        <el-input
          v-model="formData.stock_name"
          placeholder="股票名称（选择股票后自动填充）"
        />
      </el-form-item>

      <el-form-item label="持仓数量" prop="quantity">
        <el-input
          v-model="formData.quantity"
          placeholder="请输入持仓数量"
          type="number"
        >
          <template #append>股</template>
        </el-input>
        <div class="text-xs text-gray-500 mt-1">
          A股：必须是100股的倍数
        </div>
      </el-form-item>

      <el-form-item label="买入价格" prop="buy_price">
        <el-input
          v-model="formData.buy_price"
          placeholder="请输入买入价格"
          type="number"
        >
          <template #prepend>¥</template>
        </el-input>
      </el-form-item>

      <el-form-item label="买入日期" prop="buy_date">
        <el-date-picker
          v-model="formData.buy_date"
          type="date"
          placeholder="选择买入日期"
          class="w-full"
          format="YYYY-MM-DD"
          value-format="YYYY-MM-DD"
        />
      </el-form-item>

      <el-form-item label="备注" prop="notes">
        <el-input
          v-model="formData.notes"
          type="textarea"
          :rows="2"
          placeholder="选填，可以记录买入原因、策略等信息"
          maxlength="200"
          show-word-limit
        />
      </el-form-item>

      <!-- 成本预览 -->
      <div v-if="totalCost !== '0.00'" class="bg-gray-50 border border-gray-200 rounded-lg p-3 mb-4">
        <div class="flex justify-between items-center">
          <span class="text-sm text-gray-600">总成本</span>
          <span class="text-lg font-bold text-gray-900">¥{{ totalCost }}</span>
        </div>
        <div class="text-xs text-gray-500 mt-1">
          {{ formData.quantity }} 股 × ¥{{ formData.buy_price }} = ¥{{ totalCost }}
        </div>
      </div>

      <!-- 操作提示 -->
      <div class="bg-yellow-50 border border-yellow-200 rounded-lg p-3 mb-4">
        <div class="text-sm text-gray-700">
          <div class="font-semibold mb-1">💡 温馨提示</div>
          <ul class="list-disc list-inside text-xs space-y-1 text-gray-600">
            <li>添加持仓后会自动计算盈亏</li>
            <li>可在持仓列表中查看详细信息</li>
            <li>支持后续调整持仓数量和成本</li>
          </ul>
        </div>
      </div>
    </el-form>

    <template #footer>
      <div class="flex justify-end space-x-3">
        <button
          type="button"
          @click="handleClose"
          class="px-4 py-2 text-sm text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition"
        >
          取消
        </button>
        <button
          type="button"
          @click="handleSubmit"
          :disabled="loading"
          class="px-4 py-2 text-sm text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition disabled:bg-gray-400 disabled:cursor-not-allowed"
        >
          {{ loading ? '提交中...' : '确认添加' }}
        </button>
      </div>
    </template>
  </el-dialog>
</template>
