<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'

interface Holding {
  holding_id?: number
  account_id: number
  account_name?: string
  symbol: string
  stock_name: string
  quantity: number
  cost_price: number
  current_price?: number
  market_value?: number
  profit_loss?: number
  profit_rate?: number
}

interface AdjustmentData {
  adjustment_type: 'quantity' | 'cost' | 'split' | 'merge'
  new_quantity?: number
  new_cost_price?: number
  split_ratio?: string
  reason: string
  notes?: string
}

interface Props {
  visible: boolean
  holding?: Holding
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'update:visible': [visible: boolean]
  confirm: [data: AdjustmentData]
}>()

const dialogVisible = computed({
  get: () => props.visible,
  set: (val) => emit('update:visible', val)
})

// 调整类型
const adjustmentType = ref<'quantity' | 'cost' | 'split' | 'merge'>('quantity')

// 表单数据
const formData = ref<AdjustmentData>({
  adjustment_type: 'quantity',
  new_quantity: 0,
  new_cost_price: 0,
  split_ratio: '',
  reason: '',
  notes: ''
})

// 调整类型选项
const adjustmentTypeOptions = [
  {
    label: '调整数量',
    value: 'quantity',
    description: '手动修正持仓数量'
  },
  {
    label: '调整成本',
    value: 'cost',
    description: '手动修正成本价'
  },
  {
    label: '股票拆股',
    value: 'split',
    description: '如 1股拆成2股'
  },
  {
    label: '股票合股',
    value: 'merge',
    description: '如 10股合并成1股'
  }
]

// 拆股/合股比例预设
const splitRatioPresets = [
  { label: '1拆2 (1:2)', value: '1:2' },
  { label: '1拆3 (1:3)', value: '1:3' },
  { label: '1拆5 (1:5)', value: '1:5' },
  { label: '10合1 (10:1)', value: '10:1' },
  { label: '5合1 (5:1)', value: '5:1' }
]

// 计算拆股后的数量和成本价
const splitCalculation = computed(() => {
  if (!props.holding || !formData.value.split_ratio) {
    return null
  }

  const ratio = formData.value.split_ratio.split(':')
  if (ratio.length !== 2) return null

  const before = parseFloat(ratio[0])
  const after = parseFloat(ratio[1])

  if (isNaN(before) || isNaN(after) || before <= 0 || after <= 0) {
    return null
  }

  const isSplit = adjustmentType.value === 'split'
  const multiplier = isSplit ? after / before : before / after

  return {
    newQuantity: Math.floor(props.holding.quantity * multiplier),
    newCostPrice: props.holding.cost_price / multiplier
  }
})

// 数量变化差异
const quantityDiff = computed(() => {
  if (!props.holding) return 0
  return (formData.value.new_quantity || 0) - props.holding.quantity
})

// 成本价变化差异
const costDiff = computed(() => {
  if (!props.holding) return 0
  return (formData.value.new_cost_price || 0) - props.holding.cost_price
})

// 总成本变化
const totalCostChange = computed(() => {
  if (!props.holding) return 0

  const oldTotalCost = props.holding.quantity * props.holding.cost_price
  const newTotalCost = (formData.value.new_quantity || 0) * (formData.value.new_cost_price || 0)

  return newTotalCost - oldTotalCost
})

// 提交
const submitting = ref(false)
const handleSubmit = async () => {
  // 验证
  if (adjustmentType.value === 'quantity') {
    if (!formData.value.new_quantity || formData.value.new_quantity < 0) {
      ElMessage.warning('请输入有效的新数量')
      return
    }
  }

  if (adjustmentType.value === 'cost') {
    if (!formData.value.new_cost_price || formData.value.new_cost_price <= 0) {
      ElMessage.warning('请输入有效的新成本价')
      return
    }
  }

  if (adjustmentType.value === 'split' || adjustmentType.value === 'merge') {
    if (!formData.value.split_ratio || !splitCalculation.value) {
      ElMessage.warning('请输入有效的拆合比例')
      return
    }

    // 应用计算结果
    formData.value.new_quantity = splitCalculation.value.newQuantity
    formData.value.new_cost_price = splitCalculation.value.newCostPrice
  }

  if (!formData.value.reason) {
    ElMessage.warning('请输入调整原因')
    return
  }

  submitting.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 500))

    const data = {
      ...formData.value,
      adjustment_type: adjustmentType.value
    }

    emit('confirm', data)
    ElMessage.success('持仓调整成功')
    dialogVisible.value = false
    resetForm()
  } catch (error) {
    ElMessage.error('调整失败')
  } finally {
    submitting.value = false
  }
}

// 重置表单
const resetForm = () => {
  adjustmentType.value = 'quantity'
  formData.value = {
    adjustment_type: 'quantity',
    new_quantity: 0,
    new_cost_price: 0,
    split_ratio: '',
    reason: '',
    notes: ''
  }
}

// 加载持仓数据
const loadHoldingData = () => {
  if (props.holding) {
    formData.value.new_quantity = props.holding.quantity
    formData.value.new_cost_price = props.holding.cost_price
  }
}

// 监听弹框打开
watch(() => props.visible, (val) => {
  if (val) {
    loadHoldingData()
  }
})

// 监听调整类型变化
watch(adjustmentType, (newType) => {
  formData.value.adjustment_type = newType
  if (props.holding) {
    formData.value.new_quantity = props.holding.quantity
    formData.value.new_cost_price = props.holding.cost_price
  }
  formData.value.split_ratio = ''
})
</script>

<template>
  <el-dialog
    v-model="dialogVisible"
    title="持仓调整"
    width="600px"
    :close-on-click-modal="false"
    @closed="resetForm"
  >
    <!-- 持仓信息 -->
    <div v-if="holding" class="mb-6 p-4 bg-gray-50 rounded">
      <div class="flex items-center justify-between mb-2">
        <div>
          <span class="font-semibold text-lg">{{ holding.stock_name }}</span>
          <span class="ml-2 text-gray-500">{{ holding.symbol }}</span>
        </div>
        <el-tag>{{ holding.account_name }}</el-tag>
      </div>
      <div class="grid grid-cols-2 gap-4 text-sm">
        <div>
          <span class="text-gray-600">持有数量：</span>
          <span class="font-semibold">{{ holding.quantity }}</span>
        </div>
        <div>
          <span class="text-gray-600">成本价：</span>
          <span class="font-semibold">¥{{ holding.cost_price.toFixed(2) }}</span>
        </div>
        <div>
          <span class="text-gray-600">总成本：</span>
          <span class="font-semibold">¥{{ (holding.quantity * holding.cost_price).toFixed(2) }}</span>
        </div>
        <div v-if="holding.current_price">
          <span class="text-gray-600">当前市值：</span>
          <span class="font-semibold">¥{{ holding.market_value?.toFixed(2) }}</span>
        </div>
      </div>
    </div>

    <!-- 调整类型选择 -->
    <div class="mb-6">
      <div class="mb-2 text-sm font-semibold">调整类型</div>
      <el-radio-group v-model="adjustmentType" class="w-full">
        <el-radio
          v-for="option in adjustmentTypeOptions"
          :key="option.value"
          :label="option.value"
          class="w-full mb-2"
        >
          <div class="flex flex-col">
            <span>{{ option.label }}</span>
            <span class="text-xs text-gray-500">{{ option.description }}</span>
          </div>
        </el-radio>
      </el-radio-group>
    </div>

    <!-- 调整数量 -->
    <div v-if="adjustmentType === 'quantity'" class="mb-6">
      <el-form :model="formData" label-width="100px">
        <el-form-item label="新数量" required>
          <el-input-number
            v-model="formData.new_quantity"
            :min="0"
            :step="100"
            :controls="true"
            style="width: 100%"
          />
          <div v-if="quantityDiff !== 0" class="text-xs mt-1" :class="quantityDiff > 0 ? 'text-red-600' : 'text-green-600'">
            {{ quantityDiff > 0 ? '+' : '' }}{{ quantityDiff }} 股
          </div>
        </el-form-item>
      </el-form>
    </div>

    <!-- 调整成本 -->
    <div v-if="adjustmentType === 'cost'" class="mb-6">
      <el-form :model="formData" label-width="100px">
        <el-form-item label="新成本价" required>
          <el-input-number
            v-model="formData.new_cost_price"
            :min="0"
            :precision="2"
            :step="1"
            :controls="true"
            style="width: 100%"
          />
          <div v-if="costDiff !== 0" class="text-xs mt-1" :class="costDiff > 0 ? 'text-red-600' : 'text-green-600'">
            {{ costDiff > 0 ? '+' : '' }}¥{{ costDiff.toFixed(2) }} / 股
          </div>
        </el-form-item>

        <el-form-item label="总成本变化">
          <div class="text-sm">
            <span :class="totalCostChange > 0 ? 'text-red-600' : 'text-green-600'">
              {{ totalCostChange > 0 ? '+' : '' }}¥{{ totalCostChange.toFixed(2) }}
            </span>
          </div>
        </el-form-item>
      </el-form>
    </div>

    <!-- 拆股/合股 -->
    <div v-if="adjustmentType === 'split' || adjustmentType === 'merge'" class="mb-6">
      <el-form :model="formData" label-width="100px">
        <el-form-item :label="adjustmentType === 'split' ? '拆股比例' : '合股比例'" required>
          <el-select
            v-model="formData.split_ratio"
            placeholder="选择或输入比例（如 1:2）"
            filterable
            allow-create
            style="width: 100%"
          >
            <el-option
              v-for="preset in splitRatioPresets"
              :key="preset.value"
              :label="preset.label"
              :value="preset.value"
            />
          </el-select>
          <div class="text-xs text-gray-500 mt-1">
            格式：旧:新（如1:2表示1股变2股）
          </div>
        </el-form-item>

        <el-form-item v-if="splitCalculation" label="调整后">
          <div class="text-sm space-y-1">
            <div>
              数量：<span class="font-semibold">{{ holding?.quantity }}</span>
              → <span class="font-semibold text-blue-600">{{ splitCalculation.newQuantity }}</span>
            </div>
            <div>
              成本价：<span class="font-semibold">¥{{ holding?.cost_price.toFixed(2) }}</span>
              → <span class="font-semibold text-blue-600">¥{{ splitCalculation.newCostPrice.toFixed(2) }}</span>
            </div>
            <div class="text-xs text-gray-500">
              总成本保持不变：¥{{ (holding!.quantity * holding!.cost_price).toFixed(2) }}
            </div>
          </div>
        </el-form-item>
      </el-form>
    </div>

    <!-- 调整原因和备注 -->
    <el-form :model="formData" label-width="100px">
      <el-form-item label="调整原因" required>
        <el-input
          v-model="formData.reason"
          placeholder="输入调整原因"
          maxlength="200"
          show-word-limit
        />
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
        确认调整
      </el-button>
    </template>
  </el-dialog>
</template>
