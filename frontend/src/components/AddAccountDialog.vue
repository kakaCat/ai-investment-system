<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { accountApi } from '@/api/account'

// Props 和 Emits
const props = defineProps<{
  visible: boolean
}>()

const emit = defineEmits<{
  'update:visible': [value: boolean]
  'success': []
}>()

// 表单数据
const formData = reactive({
  account_name: '',
  account_type: '',
  market: '',
  initial_balance: '',
  notes: ''
})

// 表单验证规则
const rules = {
  account_name: [
    { required: true, message: '请输入账户名称', trigger: 'blur' },
    { min: 2, max: 50, message: '账户名称长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  account_type: [
    { required: true, message: '请选择账户类型', trigger: 'change' }
  ],
  market: [
    { required: true, message: '请选择交易市场', trigger: 'change' }
  ],
  initial_balance: [
    { required: true, message: '请输入初始资金', trigger: 'blur' },
    {
      validator: (rule: any, value: any, callback: any) => {
        if (value && isNaN(Number(value))) {
          callback(new Error('请输入有效的数字'))
        } else if (Number(value) < 0) {
          callback(new Error('初始资金不能为负数'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

// 账户类型选项
const accountTypes = [
  { label: '证券账户', value: 'stock' },
  { label: '期货账户', value: 'futures' },
  { label: '虚拟账户', value: 'virtual' }
]

// 交易市场选项
const markets = [
  { label: 'A股（沪深）', value: 'CN' },
  { label: '港股', value: 'HK' },
  { label: '美股', value: 'US' }
]

// 加载状态
const loading = ref(false)
const formRef = ref()

// 关闭弹框
const handleClose = () => {
  emit('update:visible', false)
  resetForm()
}

// 重置表单
const resetForm = () => {
  formRef.value?.resetFields()
  formData.account_name = ''
  formData.account_type = ''
  formData.market = ''
  formData.initial_balance = ''
  formData.notes = ''
}

// 提交表单
const handleSubmit = async () => {
  try {
    // 验证表单
    await formRef.value?.validate()

    loading.value = true

    // 调用API
    await accountApi.create({
      account_name: formData.account_name,
      account_type: formData.account_type,
      market: formData.market,
      initial_balance: Number(formData.initial_balance),
      notes: formData.notes || undefined
    })

    ElMessage.success('账户添加成功')
    emit('success')
    handleClose()
  } catch (error: any) {
    if (error.errors) {
      // 表单验证失败
      return
    }
    ElMessage.error(error.message || '添加账户失败，请重试')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <el-dialog
    :model-value="visible"
    title="添加账户"
    width="500px"
    @close="handleClose"
  >
    <el-form
      ref="formRef"
      :model="formData"
      :rules="rules"
      label-width="100px"
      label-position="right"
    >
      <el-form-item label="账户名称" prop="account_name">
        <el-input
          v-model="formData.account_name"
          placeholder="请输入账户名称，如：招商证券A股账户"
          maxlength="50"
          show-word-limit
        />
      </el-form-item>

      <el-form-item label="账户类型" prop="account_type">
        <el-select
          v-model="formData.account_type"
          placeholder="请选择账户类型"
          class="w-full"
        >
          <el-option
            v-for="item in accountTypes"
            :key="item.value"
            :label="item.label"
            :value="item.value"
          />
        </el-select>
      </el-form-item>

      <el-form-item label="交易市场" prop="market">
        <el-select
          v-model="formData.market"
          placeholder="请选择交易市场"
          class="w-full"
        >
          <el-option
            v-for="item in markets"
            :key="item.value"
            :label="item.label"
            :value="item.value"
          />
        </el-select>
      </el-form-item>

      <el-form-item label="初始资金" prop="initial_balance">
        <el-input
          v-model="formData.initial_balance"
          placeholder="请输入初始资金金额"
        >
          <template #prepend>¥</template>
        </el-input>
        <div class="text-xs text-gray-500 mt-1">
          提示：后续可通过充值功能追加资金
        </div>
      </el-form-item>

      <el-form-item label="备注" prop="notes">
        <el-input
          v-model="formData.notes"
          type="textarea"
          :rows="3"
          placeholder="选填，可以记录账户用途、开户时间等信息"
          maxlength="200"
          show-word-limit
        />
      </el-form-item>
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
