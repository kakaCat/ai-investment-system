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
  amount: '',
  deposit_type: 'bank_transfer',
  notes: ''
})

// 表单验证规则
const rules = {
  amount: [
    { required: true, message: '请输入充值金额', trigger: 'blur' },
    {
      validator: (rule: any, value: any, callback: any) => {
        if (value && isNaN(Number(value))) {
          callback(new Error('请输入有效的数字'))
        } else if (Number(value) <= 0) {
          callback(new Error('充值金额必须大于0'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ],
  deposit_type: [
    { required: true, message: '请选择充值方式', trigger: 'change' }
  ]
}

// 充值方式选项
const depositTypes = [
  { label: '银行转账', value: 'bank_transfer' },
  { label: '证券转入', value: 'securities_transfer' },
  { label: '现金存入', value: 'cash_deposit' },
  { label: '其他', value: 'other' }
]

// 加载状态
const loading = ref(false)
const formRef = ref()

// 计算充值后的预估余额（示例）
const estimatedBalance = computed(() => {
  const amount = Number(formData.amount) || 0
  // 这里可以从props传入当前余额
  return amount
})

// 关闭弹框
const handleClose = () => {
  emit('update:visible', false)
  resetForm()
}

// 重置表单
const resetForm = () => {
  formRef.value?.resetFields()
  formData.amount = ''
  formData.deposit_type = 'bank_transfer'
  formData.notes = ''
}

// 提交表单
const handleSubmit = async () => {
  try {
    // 验证表单
    await formRef.value?.validate()

    loading.value = true

    // TODO: 调用充值API
    // await accountApi.deposit({
    //   account_id: props.accountId,
    //   amount: Number(formData.amount),
    //   deposit_type: formData.deposit_type,
    //   notes: formData.notes || undefined
    // })

    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1000))

    ElMessage.success(`成功向 ${props.accountName} 充值 ¥${formData.amount}`)
    emit('success')
    handleClose()
  } catch (error: any) {
    if (error.errors) {
      // 表单验证失败
      return
    }
    ElMessage.error(error.message || '充值失败，请重试')
  } finally {
    loading.value = false
  }
}

// 快速金额按钮
const quickAmounts = [1000, 5000, 10000, 50000, 100000]
const selectQuickAmount = (amount: number) => {
  formData.amount = amount.toString()
}
</script>

<template>
  <el-dialog
    :model-value="visible"
    title="账户充值"
    width="500px"
    @close="handleClose"
  >
    <!-- 账户信息提示 -->
    <div class="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
      <div class="flex items-center">
        <span class="text-2xl mr-3">💰</span>
        <div>
          <div class="font-semibold text-gray-900">{{ accountName }}</div>
          <div class="text-sm text-gray-600">账户ID: {{ accountId }}</div>
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
      <el-form-item label="充值金额" prop="amount">
        <el-input
          v-model="formData.amount"
          placeholder="请输入充值金额"
          type="number"
        >
          <template #prepend>¥</template>
        </el-input>

        <!-- 快速金额选择 -->
        <div class="mt-2 flex flex-wrap gap-2">
          <button
            v-for="amount in quickAmounts"
            :key="amount"
            type="button"
            @click="selectQuickAmount(amount)"
            class="px-3 py-1 text-xs text-gray-700 bg-gray-100 rounded hover:bg-gray-200 transition"
          >
            {{ amount >= 10000 ? `${amount / 10000}万` : amount }}
          </button>
        </div>
      </el-form-item>

      <el-form-item label="充值方式" prop="deposit_type">
        <el-select
          v-model="formData.deposit_type"
          placeholder="请选择充值方式"
          class="w-full"
        >
          <el-option
            v-for="item in depositTypes"
            :key="item.value"
            :label="item.label"
            :value="item.value"
          />
        </el-select>
      </el-form-item>

      <el-form-item label="备注" prop="notes">
        <el-input
          v-model="formData.notes"
          type="textarea"
          :rows="3"
          placeholder="选填，可以记录资金来源、充值日期等信息"
          maxlength="200"
          show-word-limit
        />
      </el-form-item>

      <!-- 充值提示 -->
      <div class="bg-yellow-50 border border-yellow-200 rounded-lg p-3 mb-4">
        <div class="text-sm text-gray-700">
          <div class="font-semibold mb-1">💡 温馨提示</div>
          <ul class="list-disc list-inside text-xs space-y-1 text-gray-600">
            <li>充值金额将直接计入账户可用资金</li>
            <li>建议保留充值凭证以便核对</li>
            <li>充值记录可在交易记录中查看</li>
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
          class="px-4 py-2 text-sm text-white bg-green-600 rounded-lg hover:bg-green-700 transition disabled:bg-gray-400 disabled:cursor-not-allowed"
        >
          {{ loading ? '处理中...' : '确认充值' }}
        </button>
      </div>
    </template>
  </el-dialog>
</template>
