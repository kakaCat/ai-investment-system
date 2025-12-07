<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'

interface Props {
  visible: boolean
  symbol?: string
  stockName?: string
}

const props = defineProps<Props>()

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
  account_id: null as number | null,
  symbol: '',
  name: '',
  target_price: null as number | null,
  notes: ''
})

// Mock 账户列表
const accounts = ref([
  { account_id: 1, account_name: '中信证券-A股账户' },
  { account_id: 2, account_name: '富途证券-港股账户' },
  { account_id: 3, account_name: '盈透证券-美股账户' }
])

// 重置表单
const resetForm = () => {
  formData.value = {
    account_id: null,
    symbol: '',
    name: '',
    target_price: null,
    notes: ''
  }
}

// 提交
const submitting = ref(false)
const handleSubmit = async () => {
  if (!formData.value.account_id) {
    ElMessage.warning('请选择账户')
    return
  }
  if (!formData.value.symbol) {
    ElMessage.warning('请输入股票代码')
    return
  }

  submitting.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 500))

    emit('confirm', formData.value)
    ElMessage.success('已添加到关注列表')
    dialogVisible.value = false
    resetForm()
  } catch (error) {
    ElMessage.error('添加失败')
  } finally {
    submitting.value = false
  }
}

// 监听弹框打开
watch(() => props.visible, (val) => {
  if (val && props.symbol) {
    formData.value.symbol = props.symbol
    formData.value.name = props.stockName || ''
  }
})
</script>

<template>
  <el-dialog
    v-model="dialogVisible"
    title="添加到关注列表"
    width="500px"
    :close-on-click-modal="false"
    @closed="resetForm"
  >
    <el-form :model="formData" label-width="100px">
      <el-form-item label="选择账户" required>
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
        <el-input v-model="formData.symbol" placeholder="输入股票代码" />
      </el-form-item>

      <el-form-item label="股票名称">
        <el-input v-model="formData.name" placeholder="输入股票名称（可选）" />
      </el-form-item>

      <el-form-item label="目标价">
        <el-input-number
          v-model="formData.target_price"
          :min="0"
          :precision="2"
          :step="1"
          style="width: 100%"
          placeholder="输入目标价（可选）"
        />
      </el-form-item>

      <el-form-item label="备注">
        <el-input
          v-model="formData.notes"
          type="textarea"
          :rows="3"
          placeholder="输入备注信息（可选）"
        />
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
