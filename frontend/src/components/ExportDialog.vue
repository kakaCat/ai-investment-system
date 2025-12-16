<script setup lang="ts">
import { ref, watch } from 'vue'
import { ElMessage } from 'element-plus'

interface Props {
  visible: boolean
  accountId: number
  accountName: string
  exportType?: 'account' | 'cash_flow' | 'trades' | 'performance' // 导出类型
}

const props = withDefaults(defineProps<Props>(), {
  exportType: 'account'
})

const emit = defineEmits<{
  (e: 'update:visible', value: boolean): void
}>()

// 表单数据
const formData = ref({
  format: 'xlsx', // xlsx, csv, pdf
  dateRange: 'all', // all, 30days, 90days, 180days, custom
  customStartDate: '',
  customEndDate: '',
  includeCharts: true, // 仅PDF格式有效
  includeDetails: true
})

// 导出类型标题映射
const exportTypeLabels = {
  account: '账户数据',
  cash_flow: '资金流水',
  trades: '交易记录',
  performance: '绩效报告'
}

// 重置表单
const resetForm = () => {
  formData.value = {
    format: 'xlsx',
    dateRange: 'all',
    customStartDate: '',
    customEndDate: '',
    includeCharts: true,
    includeDetails: true
  }
}

// 关闭弹框
const close = () => {
  emit('update:visible', false)
  resetForm()
}

// 导出数据
const loading = ref(false)
const handleExport = async () => {
  // 验证自定义日期范围
  if (formData.value.dateRange === 'custom') {
    if (!formData.value.customStartDate || !formData.value.customEndDate) {
      ElMessage.warning('请选择日期范围')
      return
    }
    if (new Date(formData.value.customStartDate) > new Date(formData.value.customEndDate)) {
      ElMessage.warning('开始日期不能晚于结束日期')
      return
    }
  }

  loading.value = true
  try {
    // 模拟导出
    await new Promise(resolve => setTimeout(resolve, 1000))

    const formatLabel = formData.value.format.toUpperCase()
    const typeLabel = exportTypeLabels[props.exportType]

    ElMessage.success(`${typeLabel}已导出为 ${formatLabel} 格式`)
    close()
  } catch (error) {
    ElMessage.error('导出失败')
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
    :title="`导出${exportTypeLabels[exportType]}`"
    width="550px"
    :close-on-click-modal="false"
    @update:model-value="emit('update:visible', $event)"
  >
    <div class="space-y-4">
      <!-- 账户信息 -->
      <div class="bg-blue-50 border border-blue-200 rounded-lg p-3">
        <div class="text-sm text-gray-600">导出账户</div>
        <div class="text-lg font-semibold text-gray-900">{{ accountName }}</div>
      </div>

      <!-- 导出格式 -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">
          导出格式 <span class="text-red-500">*</span>
        </label>
        <el-radio-group v-model="formData.format">
          <el-radio label="xlsx">Excel (.xlsx)</el-radio>
          <el-radio label="csv">CSV (.csv)</el-radio>
          <el-radio label="pdf">PDF (.pdf)</el-radio>
        </el-radio-group>
      </div>

      <!-- 日期范围 -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">
          日期范围 <span class="text-red-500">*</span>
        </label>
        <el-select v-model="formData.dateRange" class="w-full">
          <el-option label="全部数据" value="all" />
          <el-option label="近30天" value="30days" />
          <el-option label="近90天" value="90days" />
          <el-option label="近180天" value="180days" />
          <el-option label="自定义范围" value="custom" />
        </el-select>
      </div>

      <!-- 自定义日期范围 -->
      <div v-if="formData.dateRange === 'custom'" class="grid grid-cols-2 gap-3">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">开始日期</label>
          <el-date-picker
            v-model="formData.customStartDate"
            type="date"
            placeholder="选择日期"
            class="w-full"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">结束日期</label>
          <el-date-picker
            v-model="formData.customEndDate"
            type="date"
            placeholder="选择日期"
            class="w-full"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
          />
        </div>
      </div>

      <!-- PDF专属选项 -->
      <div v-if="formData.format === 'pdf'" class="space-y-3">
        <el-checkbox v-model="formData.includeCharts">
          包含图表（绩效曲线、分布图等）
        </el-checkbox>
        <el-checkbox v-model="formData.includeDetails">
          包含详细数据表格
        </el-checkbox>
      </div>

      <!-- 导出说明 -->
      <div class="bg-gray-50 border border-gray-200 rounded p-3">
        <div class="text-xs text-gray-700">
          <div class="font-semibold mb-1">📄 导出内容说明:</div>
          <ul class="list-disc list-inside space-y-0.5">
            <li v-if="exportType === 'account'">
              包含账户概况、持仓明细、关注股票等信息
            </li>
            <li v-else-if="exportType === 'cash_flow'">
              包含资金流水记录、余额变化等信息
            </li>
            <li v-else-if="exportType === 'trades'">
              包含交易记录、盈亏统计等信息
            </li>
            <li v-else-if="exportType === 'performance'">
              包含收益曲线、风险指标、交易统计等信息
            </li>
            <li>数据将按选定的日期范围进行筛选</li>
            <li>导出文件将自动保存到本地下载文件夹</li>
          </ul>
        </div>
      </div>
    </div>

    <template #footer>
      <div class="flex justify-end space-x-2">
        <el-button :disabled="loading" @click="close">取消</el-button>
        <el-button type="primary" :loading="loading" @click="handleExport">
          <span v-if="!loading">导出</span>
          <span v-else>导出中...</span>
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>
