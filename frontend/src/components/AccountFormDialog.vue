<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'

interface Account {
  account_id?: number
  account_name: string
  broker_name: string
  account_number: string
  market_type: 'A' | 'HK' | 'US' | 'other'
  initial_capital: number
  currency: string
  notes?: string
  is_active: boolean
}

interface Props {
  visible: boolean
  account?: Account
  mode: 'create' | 'edit'
}

const props = withDefaults(defineProps<Props>(), {
  mode: 'create'
})

const emit = defineEmits<{
  'update:visible': [visible: boolean]
  confirm: [data: Account]
}>()

const dialogVisible = computed({
  get: () => props.visible,
  set: (val) => emit('update:visible', val)
})

const dialogTitle = computed(() => {
  return props.mode === 'create' ? '新建账户' : '编辑账户'
})

// 表单数据
const formData = ref<Account>({
  account_name: '',
  broker_name: '',
  account_number: '',
  market_type: 'A',
  initial_capital: 0,
  currency: 'CNY',
  notes: '',
  is_active: true
})

// 券商列表
const brokerOptions = [
  { label: '中信证券', value: '中信证券' },
  { label: '华泰证券', value: '华泰证券' },
  { label: '国泰君安', value: '国泰君安' },
  { label: '招商证券', value: '招商证券' },
  { label: '广发证券', value: '广发证券' },
  { label: '富途证券', value: '富途证券' },
  { label: '老虎证券', value: '老虎证券' },
  { label: '盈透证券', value: '盈透证券' },
  { label: '嘉信理财', value: '嘉信理财' },
  { label: '其他', value: '其他' }
]

// 市场类型选项
const marketTypeOptions = [
  { label: 'A股市场', value: 'A' },
  { label: '港股市场', value: 'HK' },
  { label: '美股市场', value: 'US' },
  { label: '其他市场', value: 'other' }
]

// 货币选项
const currencyOptions = [
  { label: '人民币 (CNY)', value: 'CNY' },
  { label: '美元 (USD)', value: 'USD' },
  { label: '港币 (HKD)', value: 'HKD' },
  { label: '欧元 (EUR)', value: 'EUR' },
  { label: '日元 (JPY)', value: 'JPY' }
]

// 市场类型和货币联动
watch(() => formData.value.market_type, (newMarket) => {
  // 根据市场类型自动设置默认货币
  const currencyMap: Record<string, string> = {
    'A': 'CNY',
    'HK': 'HKD',
    'US': 'USD',
    'other': 'CNY'
  }

  if (props.mode === 'create') {
    formData.value.currency = currencyMap[newMarket] || 'CNY'
  }
})

// 提交
const submitting = ref(false)
const handleSubmit = async () => {
  // 验证
  if (!formData.value.account_name) {
    ElMessage.warning('请输入账户名称')
    return
  }
  if (!formData.value.broker_name) {
    ElMessage.warning('请选择券商')
    return
  }
  if (!formData.value.account_number) {
    ElMessage.warning('请输入账户号码')
    return
  }
  if (formData.value.initial_capital < 0) {
    ElMessage.warning('初始资金不能为负数')
    return
  }

  submitting.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 500))

    emit('confirm', { ...formData.value })

    const action = props.mode === 'create' ? '创建' : '更新'
    ElMessage.success(`账户${action}成功`)

    dialogVisible.value = false
    if (props.mode === 'create') {
      resetForm()
    }
  } catch (error) {
    ElMessage.error('操作失败')
  } finally {
    submitting.value = false
  }
}

// 重置表单
const resetForm = () => {
  formData.value = {
    account_name: '',
    broker_name: '',
    account_number: '',
    market_type: 'A',
    initial_capital: 0,
    currency: 'CNY',
    notes: '',
    is_active: true
  }
}

// 加载账户数据（编辑模式）
const loadAccountData = () => {
  if (props.mode === 'edit' && props.account) {
    formData.value = { ...props.account }
  } else {
    resetForm()
  }
}

// 监听弹框打开
watch(() => props.visible, (val) => {
  if (val) {
    loadAccountData()
  }
})

// 格式化账户号码（隐藏中间部分）
const maskAccountNumber = ref(true)
const displayAccountNumber = computed(() => {
  if (!maskAccountNumber.value || props.mode === 'create') {
    return formData.value.account_number
  }

  const num = formData.value.account_number
  if (num.length <= 8) return num

  return num.slice(0, 4) + '****' + num.slice(-4)
})
</script>

<template>
  <el-dialog
    v-model="dialogVisible"
    :title="dialogTitle"
    width="600px"
    :close-on-click-modal="false"
    @closed="mode === 'create' ? resetForm() : null"
  >
    <el-form :model="formData" label-width="120px">
      <el-form-item label="账户名称" required>
        <el-input
          v-model="formData.account_name"
          placeholder="例如：中信证券-A股账户"
          maxlength="100"
          show-word-limit
        />
      </el-form-item>

      <el-form-item label="券商" required>
        <el-select
          v-model="formData.broker_name"
          placeholder="选择券商"
          filterable
          allow-create
          style="width: 100%"
        >
          <el-option
            v-for="broker in brokerOptions"
            :key="broker.value"
            :label="broker.label"
            :value="broker.value"
          />
        </el-select>
      </el-form-item>

      <el-form-item label="账户号码" required>
        <div class="flex gap-2" style="width: 100%">
          <el-input
            v-model="formData.account_number"
            :placeholder="mode === 'edit' ? displayAccountNumber : '输入账户号码'"
            maxlength="50"
          />
          <el-button
            v-if="mode === 'edit' && formData.account_number"
            @click="maskAccountNumber = !maskAccountNumber"
          >
            {{ maskAccountNumber ? '显示' : '隐藏' }}
          </el-button>
        </div>
        <div class="text-xs text-gray-500 mt-1">
          账户号码将加密存储，仅用于识别账户
        </div>
      </el-form-item>

      <el-form-item label="市场类型" required>
        <el-select v-model="formData.market_type" placeholder="选择市场类型" style="width: 100%">
          <el-option
            v-for="market in marketTypeOptions"
            :key="market.value"
            :label="market.label"
            :value="market.value"
          />
        </el-select>
      </el-form-item>

      <el-form-item label="初始资金" required>
        <el-input-number
          v-model="formData.initial_capital"
          :min="0"
          :precision="2"
          :step="10000"
          :controls="true"
          style="width: 100%"
        />
        <div class="text-xs text-gray-500 mt-1">
          账户开户时的初始资金金额
        </div>
      </el-form-item>

      <el-form-item label="货币" required>
        <el-select v-model="formData.currency" placeholder="选择货币" style="width: 100%">
          <el-option
            v-for="curr in currencyOptions"
            :key="curr.value"
            :label="curr.label"
            :value="curr.value"
          />
        </el-select>
      </el-form-item>

      <el-form-item label="账户状态">
        <el-switch
          v-model="formData.is_active"
          active-text="启用"
          inactive-text="停用"
        />
        <div class="text-xs text-gray-500 mt-1">
          停用后该账户将不显示在账户列表中
        </div>
      </el-form-item>

      <el-form-item label="备注">
        <el-input
          v-model="formData.notes"
          type="textarea"
          :rows="3"
          placeholder="输入备注信息（可选）"
          maxlength="500"
          show-word-limit
        />
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="dialogVisible = false">取消</el-button>
      <el-button type="primary" :loading="submitting" @click="handleSubmit">
        {{ mode === 'create' ? '创建' : '保存' }}
      </el-button>
    </template>
  </el-dialog>
</template>
