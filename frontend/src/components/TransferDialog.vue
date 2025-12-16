<script setup lang="ts">
import { ref, watch } from 'vue'
import { ElMessage } from 'element-plus'

interface Props {
  visible: boolean
  accountId: number
  accountName: string
}

const props = defineProps<Props>()
const emit = defineEmits<{
  (e: 'update:visible', value: boolean): void
  (e: 'success'): void
}>()

// 表单数据
const formData = ref({
  direction: 'in', // in: 转入, out: 转出
  targetAccountId: null as number | null,
  amount: null as number | null,
  notes: ''
})

// 可用账户列表（mock数据）
const availableAccounts = ref([
  { account_id: 2, account_name: '华泰证券-A股' },
  { account_id: 3, account_name: '富途证券-港股' },
  { account_id: 4, account_name: '盈透证券-美股' }
])

// 重置表单
const resetForm = () => {
  formData.value = {
    direction: 'in',
    targetAccountId: null,
    amount: null,
    notes: ''
  }
}

// 关闭弹框
const close = () => {
  emit('update:visible', false)
  resetForm()
}

// 提交转账
const loading = ref(false)
const submit = async () => {
  // 验证
  if (!formData.value.targetAccountId) {
    ElMessage.warning('请选择对方账户')
    return
  }
  if (!formData.value.amount || formData.value.amount <= 0) {
    ElMessage.warning('请输入正确的转账金额')
    return
  }

  loading.value = true
  try {
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 500))

    const direction = formData.value.direction === 'in' ? '转入' : '转出'
    const targetAccount = availableAccounts.value.find(a => a.account_id === formData.value.targetAccountId)

    ElMessage.success(`成功${direction} ¥${formData.value.amount?.toLocaleString()} ${direction === '转入' ? '从' : '到'} ${targetAccount?.account_name}`)
    emit('success')
    close()
  } catch (error) {
    ElMessage.error('转账失败')
  } finally {
    loading.value = false
  }
}

// 监听visible变化
watch(() => props.visible, (newVal) => {
  if (!newVal) {
    resetForm()
  }
})
</script>

<template>
  <el-dialog
    :model-value="visible"
    title="账户间转账"
    width="500px"
    :close-on-click-modal="false"
    @update:model-value="emit('update:visible', $event)"
  >
    <div class="space-y-4">
      <!-- 当前账户 -->
      <div class="bg-blue-50 border border-blue-200 rounded-lg p-3">
        <div class="text-sm text-gray-600">当前账户</div>
        <div class="text-lg font-semibold text-gray-900">{{ accountName }}</div>
      </div>

      <!-- 转账方向 -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">
          转账方向 <span class="text-red-500">*</span>
        </label>
        <el-radio-group v-model="formData.direction">
          <el-radio label="in">转入（从其他账户转入本账户）</el-radio>
          <el-radio label="out">转出（从本账户转出到其他账户）</el-radio>
        </el-radio-group>
      </div>

      <!-- 对方账户 -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">
          {{ formData.direction === 'in' ? '转出方账户' : '转入方账户' }} <span class="text-red-500">*</span>
        </label>
        <el-select
          v-model="formData.targetAccountId"
          placeholder="请选择账户"
          class="w-full"
        >
          <el-option
            v-for="account in availableAccounts"
            :key="account.account_id"
            :label="account.account_name"
            :value="account.account_id"
          />
        </el-select>
      </div>

      <!-- 转账金额 -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">
          转账金额 <span class="text-red-500">*</span>
        </label>
        <el-input
          v-model.number="formData.amount"
          type="number"
          placeholder="请输入金额"
          :min="0"
          :step="0.01"
        >
          <template #prefix>¥</template>
        </el-input>
        <div class="text-xs text-gray-500 mt-1">
          金额将从{{ formData.direction === 'out' ? '本账户可用资金' : '对方账户' }}中扣除
        </div>
      </div>

      <!-- 备注 -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">
          备注（可选）
        </label>
        <el-input
          v-model="formData.notes"
          type="textarea"
          :rows="3"
          placeholder="请输入备注信息"
          maxlength="200"
          show-word-limit
        />
      </div>

      <!-- 提示信息 -->
      <div class="bg-yellow-50 border border-yellow-200 rounded p-3">
        <div class="text-xs text-yellow-800">
          <div class="font-semibold mb-1">💡 温馨提示:</div>
          <ul class="list-disc list-inside space-y-0.5">
            <li>转账仅在您的账户之间进行，不涉及外部转账</li>
            <li>转账记录将在资金流水中显示</li>
            <li>{{ formData.direction === 'out' ? '请确保本账户有足够的可用资金' : '请确保对方账户有足够的可用资金' }}</li>
          </ul>
        </div>
      </div>
    </div>

    <template #footer>
      <div class="flex justify-end space-x-2">
        <el-button :disabled="loading" @click="close">取消</el-button>
        <el-button type="primary" :loading="loading" @click="submit">
          确认转账
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>
