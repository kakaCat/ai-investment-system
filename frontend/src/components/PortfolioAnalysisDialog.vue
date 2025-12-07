<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'

interface Props {
  visible: boolean
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'update:visible': [visible: boolean]
  confirm: [data: PortfolioAnalysisConfig]
}>()

interface PortfolioAnalysisConfig {
  account_ids: number[]
  analysis_goals: string[]
  time_range: string
  include_attribution: boolean
  include_risk_metrics: boolean
  include_suggestions: boolean
  benchmark?: string
  custom_questions?: string
}

const dialogVisible = computed({
  get: () => props.visible,
  set: (val) => emit('update:visible', val)
})

// Mock 账户列表
const accounts = ref([
  { account_id: 1, account_name: '中信证券-A股账户', market_type: 'A', total_value: 250000 },
  { account_id: 2, account_name: '富途证券-港股账户', market_type: 'HK', total_value: 180000 },
  { account_id: 3, account_name: '盈透证券-美股账户', market_type: 'US', total_value: 320000 }
])

// 选中的账户
const selectedAccounts = ref<number[]>([])

// 分析目标
const analysisGoals = ref<string[]>(['performance', 'risk'])

const goalOptions = [
  { value: 'performance', label: '业绩评估', description: '收益率、波动率、夏普比率' },
  { value: 'risk', label: '风险分析', description: '最大回撤、VaR、压力测试' },
  { value: 'attribution', label: '归因分析', description: '收益来源、行业贡献、个股贡献' },
  { value: 'optimization', label: '优化建议', description: '资产配置优化、持仓调整建议' },
  { value: 'diversification', label: '分散度分析', description: '持仓集中度、行业分散度' },
  { value: 'correlation', label: '相关性分析', description: '持仓股票间的相关性' }
]

// 时间范围
const timeRange = ref('1y')
const timeRangeOptions = [
  { value: '1m', label: '近1个月' },
  { value: '3m', label: '近3个月' },
  { value: '6m', label: '近6个月' },
  { value: '1y', label: '近1年' },
  { value: 'ytd', label: '今年以来' },
  { value: 'all', label: '全部时间' }
]

// 基准指数
const benchmark = ref('hs300')
const benchmarkOptions = [
  { value: '', label: '无基准' },
  { value: 'hs300', label: '沪深300' },
  { value: 'csi500', label: '中证500' },
  { value: 'zz1000', label: '中证1000' },
  { value: 'hsi', label: '恒生指数' },
  { value: 'sp500', label: '标普500' },
  { value: 'nasdaq', label: '纳斯达克' }
]

// 附加选项
const includeAttribution = ref(true)
const includeRiskMetrics = ref(true)
const includeSuggestions = ref(true)

// 自定义问题
const customQuestions = ref('')

// 选中账户的总市值
const totalSelectedValue = computed(() => {
  return accounts.value
    .filter(acc => selectedAccounts.value.includes(acc.account_id))
    .reduce((sum, acc) => sum + acc.total_value, 0)
})

// 预估Token消耗
const estimatedTokens = computed(() => {
  let tokens = 3000 // 基础token
  tokens += selectedAccounts.value.length * 1500 // 每个账户约1500 tokens
  tokens += analysisGoals.value.length * 1200 // 每个目标约1200 tokens
  if (includeAttribution.value) tokens += 1000
  if (includeRiskMetrics.value) tokens += 800
  if (includeSuggestions.value) tokens += 1500
  if (benchmark.value) tokens += 500
  if (customQuestions.value) tokens += Math.ceil(customQuestions.value.length / 2)
  return tokens
})

// 快速配置模板
const applyTemplate = (template: string) => {
  switch (template) {
    case 'quick':
      analysisGoals.value = ['performance', 'risk']
      timeRange.value = '3m'
      includeAttribution.value = false
      includeRiskMetrics.value = true
      includeSuggestions.value = false
      benchmark.value = 'hs300'
      customQuestions.value = ''
      ElMessage.success('已应用快速诊断模板')
      break
    case 'comprehensive':
      analysisGoals.value = ['performance', 'risk', 'attribution', 'optimization', 'diversification', 'correlation']
      timeRange.value = '1y'
      includeAttribution.value = true
      includeRiskMetrics.value = true
      includeSuggestions.value = true
      benchmark.value = 'hs300'
      customQuestions.value = ''
      ElMessage.success('已应用全面分析模板')
      break
    case 'risk':
      analysisGoals.value = ['risk', 'diversification', 'correlation']
      timeRange.value = '6m'
      includeAttribution.value = false
      includeRiskMetrics.value = true
      includeSuggestions.value = true
      benchmark.value = ''
      customQuestions.value = '我的投资组合存在哪些主要风险？如何降低风险？'
      ElMessage.success('已应用风险评估模板')
      break
  }
}

// 提交分析
const submitting = ref(false)
const handleSubmit = async () => {
  // 验证
  if (selectedAccounts.value.length === 0) {
    ElMessage.warning('请至少选择一个账户')
    return
  }
  if (analysisGoals.value.length === 0) {
    ElMessage.warning('请至少选择一个分析目标')
    return
  }

  submitting.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 2000))

    const config: PortfolioAnalysisConfig = {
      account_ids: selectedAccounts.value,
      analysis_goals: analysisGoals.value,
      time_range: timeRange.value,
      include_attribution: includeAttribution.value,
      include_risk_metrics: includeRiskMetrics.value,
      include_suggestions: includeSuggestions.value,
      benchmark: benchmark.value || undefined,
      custom_questions: customQuestions.value || undefined
    }

    emit('confirm', config)
    ElMessage.success('分析任务已提交，正在生成报告...')
    dialogVisible.value = false
    resetForm()
  } catch (error) {
    ElMessage.error('提交失败')
  } finally {
    submitting.value = false
  }
}

// 重置表单
const resetForm = () => {
  selectedAccounts.value = []
  analysisGoals.value = ['performance', 'risk']
  timeRange.value = '1y'
  includeAttribution.value = true
  includeRiskMetrics.value = true
  includeSuggestions.value = true
  benchmark.value = 'hs300'
  customQuestions.value = ''
}

// 监听弹框关闭
watch(() => props.visible, (val) => {
  if (!val) {
    setTimeout(resetForm, 300)
  }
})
</script>

<template>
  <el-dialog
    v-model="dialogVisible"
    title="组合分析配置"
    width="700px"
    :close-on-click-modal="false"
  >
    <!-- 快速模板 -->
    <div class="mb-6">
      <div class="mb-2 text-sm font-semibold">快速模板</div>
      <div class="flex gap-2">
        <el-button size="small" @click="applyTemplate('quick')">
          快速诊断
        </el-button>
        <el-button size="small" @click="applyTemplate('comprehensive')">
          全面分析
        </el-button>
        <el-button size="small" @click="applyTemplate('risk')">
          风险评估
        </el-button>
      </div>
    </div>

    <el-form label-width="120px">
      <!-- 选择账户 -->
      <el-divider content-position="left">选择账户</el-divider>

      <el-form-item label="投资账户" required>
        <el-checkbox-group v-model="selectedAccounts" class="w-full">
          <div class="space-y-2">
            <el-checkbox
              v-for="account in accounts"
              :key="account.account_id"
              :label="account.account_id"
              class="w-full mb-2"
            >
              <div class="flex items-center justify-between flex-1">
                <div class="flex flex-col">
                  <span class="font-medium">{{ account.account_name }}</span>
                  <span class="text-xs text-gray-500">
                    市值: ¥{{ account.total_value.toLocaleString() }}
                  </span>
                </div>
                <el-tag :type="account.market_type === 'A' ? 'danger' : account.market_type === 'HK' ? 'warning' : 'success'" size="small">
                  {{ account.market_type }}
                </el-tag>
              </div>
            </el-checkbox>
          </div>
        </el-checkbox-group>
        <div v-if="selectedAccounts.length > 0" class="mt-2 text-sm text-gray-600">
          已选择 {{ selectedAccounts.length }} 个账户，总市值: ¥{{ totalSelectedValue.toLocaleString() }}
        </div>
      </el-form-item>

      <!-- 分析目标 -->
      <el-divider content-position="left">分析目标</el-divider>

      <el-form-item label="分析维度" required>
        <el-checkbox-group v-model="analysisGoals" class="w-full">
          <div class="space-y-2">
            <el-checkbox
              v-for="option in goalOptions"
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

      <!-- 分析参数 -->
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

      <el-form-item label="基准指数">
        <el-select v-model="benchmark" placeholder="选择对比基准" style="width: 100%">
          <el-option
            v-for="option in benchmarkOptions"
            :key="option.value"
            :label="option.label"
            :value="option.value"
          />
        </el-select>
        <div class="text-xs text-gray-500 mt-1">
          用于对比组合表现的市场基准
        </div>
      </el-form-item>

      <!-- 附加选项 -->
      <el-form-item label="附加选项">
        <div class="space-y-2">
          <div>
            <el-checkbox v-model="includeAttribution">
              包含归因分析
            </el-checkbox>
            <div class="ml-6 text-xs text-gray-500">
              分析收益的主要来源和贡献
            </div>
          </div>
          <div>
            <el-checkbox v-model="includeRiskMetrics">
              包含风险指标
            </el-checkbox>
            <div class="ml-6 text-xs text-gray-500">
              计算波动率、最大回撤、VaR等风险指标
            </div>
          </div>
          <div>
            <el-checkbox v-model="includeSuggestions">
              包含优化建议
            </el-checkbox>
            <div class="ml-6 text-xs text-gray-500">
              AI提供资产配置和持仓调整建议
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
          placeholder="输入您想了解的具体问题（可选）&#10;例如：我的投资组合是否过于集中？如何提高分散度？"
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

    <template #footer>
      <el-button @click="dialogVisible = false">取消</el-button>
      <el-button
        type="primary"
        :loading="submitting"
        :disabled="selectedAccounts.length === 0 || analysisGoals.length === 0"
        @click="handleSubmit"
      >
        {{ submitting ? '分析中...' : '开始分析' }}
      </el-button>
    </template>
  </el-dialog>
</template>
