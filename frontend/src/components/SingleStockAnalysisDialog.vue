<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import StockSearchDialog from './StockSearchDialog.vue'
import AIAnalysisResult from './AIAnalysisResult.vue'
import { singleAnalysis } from '@/api/ai'
import type { Stock } from '@/types/stock'
import type { SingleAnalysisRequest, SingleAnalysisResponse } from '@/api/ai'

interface Props {
  visible: boolean
  symbol?: string  // 可以直接传入股票代码
  stockName?: string
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'update:visible': [visible: boolean]
}>()

interface AnalysisConfig {
  stock: Stock
  dimensions: string[]
  time_range: string
  include_events: boolean
  include_financials: boolean
  compare_peers: boolean
  custom_questions?: string
}

const dialogVisible = computed({
  get: () => props.visible,
  set: (val) => emit('update:visible', val)
})

// 股票搜索对话框
const stockSearchVisible = ref(false)

// 选中的股票
const selectedStock = ref<Stock | null>(null)

// 分析维度
const selectedDimensions = ref<string[]>(['fundamentals', 'technicals'])

const dimensionOptions = [
  { value: 'fundamentals', label: '基本面分析', description: '财务指标、盈利能力、成长性' },
  { value: 'technicals', label: '技术面分析', description: 'K线形态、技术指标、支撑阻力' },
  { value: 'valuation', label: '估值分析', description: 'PE、PB、PEG等估值指标' },
  { value: 'industry', label: '行业分析', description: '行业地位、竞争格局、发展趋势' },
  { value: 'risk', label: '风险评估', description: '经营风险、财务风险、市场风险' },
  { value: 'sentiment', label: '市场情绪', description: '资金流向、投资者情绪、舆情分析' }
]

// 时间范围
const timeRange = ref('6m')
const timeRangeOptions = [
  { value: '1m', label: '近1个月' },
  { value: '3m', label: '近3个月' },
  { value: '6m', label: '近6个月' },
  { value: '1y', label: '近1年' },
  { value: '3y', label: '近3年' },
  { value: '5y', label: '近5年' }
]

// 附加选项
const includeEvents = ref(true)
const includeFinancials = ref(true)
const comparePeers = ref(false)

// 自定义问题
const customQuestions = ref('')

// 预估Token消耗
const estimatedTokens = computed(() => {
  let tokens = 2000 // 基础token
  tokens += selectedDimensions.value.length * 1000 // 每个维度约1000 tokens
  if (includeEvents.value) tokens += 500
  if (includeFinancials.value) tokens += 800
  if (comparePeers.value) tokens += 1500
  if (customQuestions.value) tokens += Math.ceil(customQuestions.value.length / 2)
  return tokens
})

// 处理股票选择
const handleStockSelect = (stock: Stock | Stock[]) => {
  if (Array.isArray(stock)) {
    selectedStock.value = stock[0]
  } else {
    selectedStock.value = stock
  }
}

// 移除选中的股票
const removeStock = () => {
  selectedStock.value = null
}

// 快速配置模板
const applyTemplate = (template: string) => {
  switch (template) {
    case 'quick':
      selectedDimensions.value = ['fundamentals', 'technicals']
      timeRange.value = '3m'
      includeEvents.value = false
      includeFinancials.value = true
      comparePeers.value = false
      customQuestions.value = ''
      ElMessage.success('已应用快速分析模板')
      break
    case 'comprehensive':
      selectedDimensions.value = ['fundamentals', 'technicals', 'valuation', 'industry', 'risk', 'sentiment']
      timeRange.value = '1y'
      includeEvents.value = true
      includeFinancials.value = true
      comparePeers.value = true
      customQuestions.value = ''
      ElMessage.success('已应用全面分析模板')
      break
    case 'value':
      selectedDimensions.value = ['fundamentals', 'valuation', 'industry']
      timeRange.value = '3y'
      includeEvents.value = true
      includeFinancials.value = true
      comparePeers.value = true
      customQuestions.value = '这只股票当前是否被低估？适合长期价值投资吗？'
      ElMessage.success('已应用价值投资模板')
      break
  }
}

// 分析状态和结果
const analyzing = ref(false)
const analysisResult = ref<SingleAnalysisResponse | null>(null)
const showResult = ref(false)

// 提交分析
const handleSubmit = async () => {
  // 验证
  if (!selectedStock.value) {
    ElMessage.warning('请选择要分析的股票')
    return
  }
  if (selectedDimensions.value.length === 0) {
    ElMessage.warning('请至少选择一个分析维度')
    return
  }

  analyzing.value = true
  analysisResult.value = null
  showResult.value = false

  try {
    // 构建请求
    const request: SingleAnalysisRequest = {
      symbol: selectedStock.value.symbol,
      stock_name: selectedStock.value.name,
      dimensions: selectedDimensions.value,
      include_fundamentals: includeFinancials.value,
      include_technicals: selectedDimensions.value.includes('technicals')
    }

    // 调用AI分析API
    const response = await singleAnalysis(request)

    // 保存结果
    analysisResult.value = response.data
    showResult.value = true

    ElMessage.success('AI分析完成！')
  } catch (error: any) {
    console.error('AI分析失败:', error)
    ElMessage.error(`分析失败: ${error.message || '请检查网络连接或稍后重试'}`)
  } finally {
    analyzing.value = false
  }
}

// 返回配置
const backToConfig = () => {
  showResult.value = false
}

// 重置表单
const resetForm = () => {
  selectedStock.value = null
  selectedDimensions.value = ['fundamentals', 'technicals']
  timeRange.value = '6m'
  includeEvents.value = true
  includeFinancials.value = true
  comparePeers.value = false
  customQuestions.value = ''
}

// 监听弹框关闭
watch(() => props.visible, (val) => {
  if (!val) {
    // 延迟重置，避免关闭动画时看到数据清空
    setTimeout(() => {
      resetForm()
      showResult.value = false
      analysisResult.value = null
    }, 300)
  }
})

// 如果传入了symbol，自动设置股票
watch(() => props.symbol, (newSymbol) => {
  if (newSymbol && props.stockName && !selectedStock.value) {
    selectedStock.value = {
      symbol: newSymbol,
      name: props.stockName,
      current_price: 0,
      change_rate: 0
    } as Stock
  }
}, { immediate: true })
</script>

<template>
  <el-dialog
    v-model="dialogVisible"
    :title="showResult ? 'AI分析结果' : '单股分析配置'"
    width="800px"
    :close-on-click-modal="false"
  >
    <!-- 分析结果视图 -->
    <div v-show="showResult">
      <AIAnalysisResult
        :analysis="analysisResult"
        :loading="analyzing"
      />
    </div>

    <!-- 配置视图 -->
    <div v-show="!showResult">
    <!-- 快速模板 -->
    <div class="mb-6">
      <div class="mb-2 text-sm font-semibold">快速模板</div>
      <div class="flex gap-2">
        <el-button size="small" @click="applyTemplate('quick')">
          快速分析
        </el-button>
        <el-button size="small" @click="applyTemplate('comprehensive')">
          全面分析
        </el-button>
        <el-button size="small" @click="applyTemplate('value')">
          价值投资
        </el-button>
      </div>
    </div>

    <el-form label-width="120px">
      <!-- 选择股票 -->
      <el-divider content-position="left">选择股票</el-divider>

      <el-form-item label="股票" required>
        <div class="w-full">
          <el-button v-if="!selectedStock" @click="stockSearchVisible = true">
            选择股票
          </el-button>
          <div v-else class="flex items-center gap-3">
            <div class="flex items-center gap-2 p-3 bg-gray-50 rounded flex-1">
              <div>
                <div class="font-semibold">{{ selectedStock.name }}</div>
                <div class="text-sm text-gray-500">{{ selectedStock.symbol }}</div>
              </div>
              <div class="ml-auto text-right">
                <div class="font-semibold" :class="selectedStock.change_rate > 0 ? 'text-red-600' : 'text-green-600'">
                  ¥{{ selectedStock.current_price.toFixed(2) }}
                </div>
                <div class="text-sm" :class="selectedStock.change_rate > 0 ? 'text-red-600' : 'text-green-600'">
                  {{ selectedStock.change_rate > 0 ? '+' : '' }}{{ selectedStock.change_rate.toFixed(2) }}%
                </div>
              </div>
            </div>
            <el-button @click="removeStock">更换</el-button>
          </div>
        </div>
      </el-form-item>

      <!-- 分析维度 -->
      <el-divider content-position="left">分析维度</el-divider>

      <el-form-item label="选择维度" required>
        <el-checkbox-group v-model="selectedDimensions" class="w-full">
          <div class="space-y-2">
            <el-checkbox
              v-for="option in dimensionOptions"
              :key="option.value"
              :label="option.value"
              class="w-full mb-2"
            >
              <div class="flex flex-col">
                <span class="font-medium">{{ option.label }}</span>
                <span class="text-xs text-gray-500">{{ option.description }}</span>
              </div>
            </el-checkbox>
          </div>
        </el-checkbox-group>
      </el-form-item>

      <!-- 时间范围 -->
      <el-divider content-position="left">分析参数</el-divider>

      <el-form-item label="时间范围">
        <el-select v-model="timeRange" placeholder="选择时间范围" style="width: 100%">
          <el-option
            v-for="option in timeRangeOptions"
            :key="option.value"
            :label="option.label"
            :value="option.value"
          />
        </el-select>
      </el-form-item>

      <!-- 附加选项 -->
      <el-form-item label="附加选项">
        <div class="space-y-2">
          <div>
            <el-checkbox v-model="includeEvents">
              包含相关事件分析
            </el-checkbox>
            <div class="ml-6 text-xs text-gray-500">
              分析近期影响该股票的重大事件
            </div>
          </div>
          <div>
            <el-checkbox v-model="includeFinancials">
              包含最新财报数据
            </el-checkbox>
            <div class="ml-6 text-xs text-gray-500">
              解读最新财务报表和关键指标
            </div>
          </div>
          <div>
            <el-checkbox v-model="comparePeers">
              对比同行业公司
            </el-checkbox>
            <div class="ml-6 text-xs text-gray-500">
              与行业内主要竞争对手进行对比分析
            </div>
          </div>
        </div>
      </el-form-item>

      <!-- 自定义问题 -->
      <el-form-item label="自定义问题">
        <el-input
          v-model="customQuestions"
          type="textarea"
          :rows="3"
          placeholder="输入您想了解的具体问题（可选）&#10;例如：这只股票未来一年的成长潜力如何？当前估值是否合理？"
          maxlength="500"
          show-word-limit
        />
      </el-form-item>

      <!-- Token消耗预估 -->
      <el-form-item label="预估消耗">
        <div class="flex items-center gap-2">
          <el-tag type="info">约 {{ estimatedTokens.toLocaleString() }} Tokens</el-tag>
          <span class="text-sm text-gray-500">
            (约 ¥{{ (estimatedTokens * 0.0001).toFixed(2) }})
          </span>
        </div>
      </el-form-item>
    </el-form>

    <!-- 股票搜索对话框 -->
    <stock-search-dialog
      v-model:visible="stockSearchVisible"
      :multiple="false"
      @confirm="handleStockSelect"
    />
    </div>
    <template #footer>
      <el-button type="primary" @click="dialogVisible = false">关闭</el-button>
    </template>
  </el-dialog>
</template>
