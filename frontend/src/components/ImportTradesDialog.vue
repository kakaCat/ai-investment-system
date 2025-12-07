<script setup lang="ts">
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import type { UploadFile } from 'element-plus'

interface Props {
  visible: boolean
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'update:visible': [visible: boolean]
  confirm: [data: any[]]
}>()

const dialogVisible = computed({
  get: () => props.visible,
  set: (val) => emit('update:visible', val)
})

const fileList = ref<UploadFile[]>([])
const uploading = ref(false)
const importStep = ref(1) // 1: 上传文件, 2: 字段映射, 3: 预览确认
const parsedData = ref<any[]>([])

// 字段映射
const fieldMapping = ref({
  symbol: '',
  stock_name: '',
  trade_type: '',
  quantity: '',
  price: '',
  fee: '',
  trade_date: '',
  notes: ''
})

// 可选字段列表
const availableFields = ref<string[]>([])

// 文件上传前
const beforeUpload = (file: File) => {
  const isCSVOrExcel =
    file.type === 'text/csv' ||
    file.type === 'application/vnd.ms-excel' ||
    file.type === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

  if (!isCSVOrExcel) {
    ElMessage.error('只支持 CSV 和 Excel 文件')
    return false
  }

  const isLt10M = file.size / 1024 / 1024 < 10
  if (!isLt10M) {
    ElMessage.error('文件大小不能超过 10MB')
    return false
  }

  return true
}

// 文件上传
const handleUpload = async (options: any) => {
  uploading.value = true
  try {
    // Mock 解析文件
    await new Promise(resolve => setTimeout(resolve, 1000))

    // Mock 解析后的数据
    availableFields.value = [
      '股票代码',
      '股票名称',
      '交易类型',
      '数量',
      '价格',
      '手续费',
      '交易日期',
      '备注'
    ]

    parsedData.value = [
      {
        股票代码: '600519',
        股票名称: '贵州茅台',
        交易类型: '买入',
        数量: '100',
        价格: '1650.00',
        手续费: '82.5',
        交易日期: '2025-01-10',
        备注: ''
      },
      {
        股票代码: '000858',
        股票名称: '五粮液',
        交易类型: '买入',
        数量: '500',
        价格: '165.00',
        手续费: '41.25',
        交易日期: '2025-01-12',
        备注: ''
      }
    ]

    ElMessage.success('文件解析成功')
    importStep.value = 2
  } catch (error) {
    ElMessage.error('文件解析失败')
  } finally {
    uploading.value = false
  }
}

// 下一步
const nextStep = () => {
  if (importStep.value === 2) {
    // 验证字段映射
    if (
      !fieldMapping.value.symbol ||
      !fieldMapping.value.trade_type ||
      !fieldMapping.value.quantity ||
      !fieldMapping.value.price
    ) {
      ElMessage.warning('请完成必填字段的映射')
      return
    }
    importStep.value = 3
  }
}

// 上一步
const prevStep = () => {
  if (importStep.value > 1) {
    importStep.value--
  }
}

// 确认导入
const submitting = ref(false)
const handleConfirm = async () => {
  submitting.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 1000))

    // 转换数据格式
    const trades = parsedData.value.map(row => ({
      symbol: row[fieldMapping.value.symbol],
      stock_name: row[fieldMapping.value.stock_name] || '',
      trade_type: mapTradeType(row[fieldMapping.value.trade_type]),
      quantity: parseFloat(row[fieldMapping.value.quantity]),
      price: parseFloat(row[fieldMapping.value.price]),
      fee: fieldMapping.value.fee ? parseFloat(row[fieldMapping.value.fee] || 0) : 0,
      trade_date: row[fieldMapping.value.trade_date] || new Date().toISOString().split('T')[0],
      notes: fieldMapping.value.notes ? row[fieldMapping.value.notes] : ''
    }))

    emit('confirm', trades)
    ElMessage.success(`成功导入 ${trades.length} 条交易记录`)
    dialogVisible.value = false
    resetForm()
  } catch (error) {
    ElMessage.error('导入失败')
  } finally {
    submitting.value = false
  }
}

// 映射交易类型
const mapTradeType = (type: string) => {
  const mapping: Record<string, string> = {
    买入: 'buy',
    卖出: 'sell',
    分红: 'dividend',
    拆股: 'split'
  }
  return mapping[type] || 'buy'
}

// 重置表单
const resetForm = () => {
  fileList.value = []
  importStep.value = 1
  parsedData.value = []
  availableFields.value = []
  fieldMapping.value = {
    symbol: '',
    stock_name: '',
    trade_type: '',
    quantity: '',
    price: '',
    fee: '',
    trade_date: '',
    notes: ''
  }
}

// 下载模板
const downloadTemplate = () => {
  ElMessage.info('下载模板功能开发中')
  // TODO: 实现模板下载
}
</script>

<template>
  <el-dialog
    v-model="dialogVisible"
    title="导入交易记录"
    width="700px"
    :close-on-click-modal="false"
    @closed="resetForm"
  >
    <el-steps :active="importStep - 1" finish-status="success" class="mb-6">
      <el-step title="上传文件" />
      <el-step title="字段映射" />
      <el-step title="预览确认" />
    </el-steps>

    <!-- 步骤1: 上传文件 -->
    <div v-if="importStep === 1">
      <div class="mb-4">
        <el-alert type="info" :closable="false">
          <template #title>
            <div>支持 CSV 和 Excel 文件格式，文件大小不超过 10MB</div>
            <el-button link type="primary" size="small" @click="downloadTemplate">
              下载导入模板
            </el-button>
          </template>
        </el-alert>
      </div>

      <el-upload
        v-model:file-list="fileList"
        drag
        :auto-upload="true"
        :limit="1"
        :before-upload="beforeUpload"
        :http-request="handleUpload"
        accept=".csv,.xls,.xlsx"
      >
        <el-icon class="el-icon--upload"><upload-filled /></el-icon>
        <div class="el-upload__text">
          拖拽文件到此处或<em>点击上传</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">支持 .csv、.xls、.xlsx 格式</div>
        </template>
      </el-upload>
    </div>

    <!-- 步骤2: 字段映射 -->
    <div v-if="importStep === 2">
      <div class="mb-4">
        <el-alert type="info" :closable="false">
          请将文件中的列映射到系统字段
        </el-alert>
      </div>

      <el-form :model="fieldMapping" label-width="120px">
        <el-form-item label="股票代码" required>
          <el-select v-model="fieldMapping.symbol" placeholder="选择对应的列">
            <el-option
              v-for="field in availableFields"
              :key="field"
              :label="field"
              :value="field"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="股票名称">
          <el-select v-model="fieldMapping.stock_name" placeholder="选择对应的列">
            <el-option label="不映射" value="" />
            <el-option
              v-for="field in availableFields"
              :key="field"
              :label="field"
              :value="field"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="交易类型" required>
          <el-select v-model="fieldMapping.trade_type" placeholder="选择对应的列">
            <el-option
              v-for="field in availableFields"
              :key="field"
              :label="field"
              :value="field"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="数量" required>
          <el-select v-model="fieldMapping.quantity" placeholder="选择对应的列">
            <el-option
              v-for="field in availableFields"
              :key="field"
              :label="field"
              :value="field"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="价格" required>
          <el-select v-model="fieldMapping.price" placeholder="选择对应的列">
            <el-option
              v-for="field in availableFields"
              :key="field"
              :label="field"
              :value="field"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="手续费">
          <el-select v-model="fieldMapping.fee" placeholder="选择对应的列">
            <el-option label="不映射" value="" />
            <el-option
              v-for="field in availableFields"
              :key="field"
              :label="field"
              :value="field"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="交易日期">
          <el-select v-model="fieldMapping.trade_date" placeholder="选择对应的列">
            <el-option label="不映射" value="" />
            <el-option
              v-for="field in availableFields"
              :key="field"
              :label="field"
              :value="field"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="备注">
          <el-select v-model="fieldMapping.notes" placeholder="选择对应的列">
            <el-option label="不映射" value="" />
            <el-option
              v-for="field in availableFields"
              :key="field"
              :label="field"
              :value="field"
            />
          </el-select>
        </el-form-item>
      </el-form>
    </div>

    <!-- 步骤3: 预览确认 -->
    <div v-if="importStep === 3">
      <div class="mb-4">
        <el-alert type="success" :closable="false">
          共 {{ parsedData.length }} 条记录，请确认后导入
        </el-alert>
      </div>

      <el-table :data="parsedData.slice(0, 10)" max-height="400" stripe border>
        <el-table-column
          :label="fieldMapping.symbol"
          width="100"
        >
          <template #default="{ row }">
            {{ row[fieldMapping.symbol] }}
          </template>
        </el-table-column>
        <el-table-column
          :label="fieldMapping.stock_name || '股票名称'"
          width="120"
        >
          <template #default="{ row }">
            {{ row[fieldMapping.stock_name] }}
          </template>
        </el-table-column>
        <el-table-column
          :label="fieldMapping.trade_type"
          width="80"
        >
          <template #default="{ row }">
            {{ row[fieldMapping.trade_type] }}
          </template>
        </el-table-column>
        <el-table-column
          :label="fieldMapping.quantity"
          width="100"
        >
          <template #default="{ row }">
            {{ row[fieldMapping.quantity] }}
          </template>
        </el-table-column>
        <el-table-column
          :label="fieldMapping.price"
          width="100"
        >
          <template #default="{ row }">
            {{ row[fieldMapping.price] }}
          </template>
        </el-table-column>
      </el-table>

      <div v-if="parsedData.length > 10" class="mt-2 text-sm text-gray-500">
        仅显示前 10 条，共 {{ parsedData.length }} 条
      </div>
    </div>

    <template #footer>
      <div class="flex justify-between">
        <el-button v-if="importStep > 1" @click="prevStep">上一步</el-button>
        <div v-else />
        <div>
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button
            v-if="importStep < 3"
            type="primary"
            :disabled="importStep === 1 && parsedData.length === 0"
            @click="nextStep"
          >
            下一步
          </el-button>
          <el-button
            v-else
            type="primary"
            :loading="submitting"
            @click="handleConfirm"
          >
            确认导入
          </el-button>
        </div>
      </div>
    </template>
  </el-dialog>
</template>
