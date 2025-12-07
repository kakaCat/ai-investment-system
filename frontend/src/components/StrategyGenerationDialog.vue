<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'

interface Props {
  visible: boolean
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'update:visible': [visible: boolean]
  confirm: [data: StrategyConfig]
}>()

interface StrategyConfig {
  risk_preference: string
  investment_goal: string
  time_horizon: string
  capital: number
  market_focus: string[]
  industry_preference: string[]
  exclude_industries: string[]
  max_single_position: number
  include_analysis: boolean
  include_specific_stocks: boolean
  custom_requirements?: string
}

const dialogVisible = computed({
  get: () => props.visible,
  set: (val) => emit('update:visible', val)
})

// 风险偏好
const riskPreference = ref('moderate')
const riskOptions = [
  { value: 'conservative', label: '保守型', description: '追求资金安全，接受较低收益' },
  { value: 'moderate', label: '稳健型', description: '平衡风险和收益' },
  { value: 'aggressive', label: '积极型', description: '追求高收益，可承受较大波动' },
  { value: 'speculative', label: '激进型', description: '追求最高收益，可承受高风险' }
]

// 投资目标
const investmentGoal = ref('growth')
const goalOptions = [
  { value: 'preservation', label: '资金保值', description: '跑赢通胀，保护本金' },
  { value: 'income', label: '稳定收益', description: '获得稳定的股息或分红' },
  { value: 'growth', label: '资本增长', description: '实现资产长期增值' },
  { value: 'aggressive_growth', label: '快速增长', description: '追求短期内的高速增长' }
]

// 投资期限
const timeHorizon = ref('medium')
const horizonOptions = [
  { value: 'short', label: '短期 (< 1年)', description: '快进快出，关注短期机会' },
  { value: 'medium', label: '中期 (1-3年)', description: '中期持有，把握周期机会' },
  { value: 'long', label: '长期 (3-5年)', description: '长期投资，价值成长' },
  { value: 'very_long', label: '超长期 (> 5年)', description: '超长期持有，复利增长' }
]

// 投资资金
const capital = ref(100000)

// 市场偏好
const marketFocus = ref<string[]>(['A'])
const marketOptions = [
  { value: 'A', label: 'A股市场' },
  { value: 'HK', label: '港股市场' },
  { value: 'US', label: '美股市场' }
]

// 行业偏好
const industryPreference = ref<string[]>([])
const industryOptions = [
  { value: 'tech', label: '科技' },
  { value: 'finance', label: '金融' },
  { value: 'healthcare', label: '医疗' },
  { value: 'consumer', label: '消费' },
  { value: 'industry', label: '工业' },
  { value: 'energy', label: '能源' },
  { value: 'materials', label: '材料' },
  { value: 'utilities', label: '公用事业' },
  { value: 'real_estate', label: '房地产' },
  { value: 'telecom', label: '通信' }
]

// 排除行业
const excludeIndustries = ref<string[]>([])

// 单只股票最大仓位
const maxSinglePosition = ref(20)

// 附加选项
const includeAnalysis = ref(true)
const includeSpecificStocks = ref(true)

// 自定义要求
const customRequirements = ref('')

// 预估Token消耗
const estimatedTokens = computed(() => {
  let tokens = 4000 // 基础token
  tokens += marketFocus.value.length * 1000
  tokens += industryPreference.value.length * 500
  if (includeAnalysis.value) tokens += 2000
  if (includeSpecificStocks.value) tokens += 1500
  if (customRequirements.value) tokens += Math.ceil(customRequirements.value.length / 2)
  return tokens
})

// 快速配置模板
const applyTemplate = (template: string) => {
  switch (template) {
    case 'conservative':
      riskPreference.value = 'conservative'
      investmentGoal.value = 'income'
      timeHorizon.value = 'long'
      capital.value = 100000
      marketFocus.value = ['A']
      industryPreference.value = ['finance', 'utilities', 'consumer']
      excludeIndustries.value = ['tech']
      maxSinglePosition.value = 15
      customRequirements.value = '偏好大盘蓝筹股，追求稳定分红'
      ElMessage.success('已应用保守稳健模板')
      break
    case 'balanced':
      riskPreference.value = 'moderate'
      investmentGoal.value = 'growth'
      timeHorizon.value = 'medium'
      capital.value = 200000
      marketFocus.value = ['A', 'HK']
      industryPreference.value = ['tech', 'consumer', 'healthcare']
      excludeIndustries.value = []
      maxSinglePosition.value = 20
      customRequirements.value = ''
      ElMessage.success('已应用均衡成长模板')
      break
    case 'growth':
      riskPreference.value = 'aggressive'
      investmentGoal.value = 'aggressive_growth'
      timeHorizon.value = 'medium'
      capital.value = 300000
      marketFocus.value = ['A', 'HK', 'US']
      industryPreference.value = ['tech', 'healthcare']
      excludeIndustries.value = ['utilities', 'real_estate']
      maxSinglePosition.value = 25
      customRequirements.value = '关注成长性强的科技和医疗行业龙头'
      ElMessage.success('已应用积极成长模板')
      break
  }
}

// 提交
const submitting = ref(false)
const handleSubmit = async () => {
  // 验证
  if (!capital.value || capital.value <= 0) {
    ElMessage.warning('请输入有效的投资资金')
    return
  }
  if (marketFocus.value.length === 0) {
    ElMessage.warning('请至少选择一个市场')
    return
  }

  submitting.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 2500))

    const config: StrategyConfig = {
      risk_preference: riskPreference.value,
      investment_goal: investmentGoal.value,
      time_horizon: timeHorizon.value,
      capital: capital.value,
      market_focus: marketFocus.value,
      industry_preference: industryPreference.value,
      exclude_industries: excludeIndustries.value,
      max_single_position: maxSinglePosition.value,
      include_analysis: includeAnalysis.value,
      include_specific_stocks: includeSpecificStocks.value,
      custom_requirements: customRequirements.value || undefined
    }

    emit('confirm', config)
    ElMessage.success('策略生成任务已提交，正在生成方案...')
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
  riskPreference.value = 'moderate'
  investmentGoal.value = 'growth'
  timeHorizon.value = 'medium'
  capital.value = 100000
  marketFocus.value = ['A']
  industryPreference.value = []
  excludeIndustries.value = []
  maxSinglePosition.value = 20
  includeAnalysis.value = true
  includeSpecificStocks.value = true
  customRequirements.value = ''
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
    title="投资策略生成"
    width="750px"
    :close-on-click-modal="false"
  >
    <!-- 快速模板 -->
    <div class="mb-6">
      <div class="mb-2 text-sm font-semibold">快速模板</div>
      <div class="flex gap-2">
        <el-button size="small" @click="applyTemplate('conservative')">
          保守稳健
        </el-button>
        <el-button size="small" @click="applyTemplate('balanced')">
          均衡成长
        </el-button>
        <el-button size="small" @click="applyTemplate('growth')">
          积极成长
        </el-button>
      </div>
    </div>

    <el-form label-width="120px">
      <!-- 基本设置 -->
      <el-divider content-position="left">基本设置</el-divider>

      <el-form-item label="风险偏好" required>
        <el-radio-group v-model="riskPreference" class="w-full">
          <div class="space-y-2">
            <el-radio
              v-for="option in riskOptions"
              :key="option.value"
              :label="option.value"
              class="w-full mb-2"
            >
              <div class="flex flex-col">
                <span class="font-medium">{{ option.label }}</span>
                <span class="text-xs text-gray-500">{{ option.description }}</span>
              </div>
            </el-radio>
          </div>
        </el-radio-group>
      </el-form-item>

      <el-form-item label="投资目标" required>
        <el-radio-group v-model="investmentGoal" class="w-full">
          <div class="space-y-2">
            <el-radio
              v-for="option in goalOptions"
              :key="option.value"
              :label="option.value"
              class="w-full mb-2"
            >
              <div class="flex flex-col">
                <span class="font-medium">{{ option.label }}</span>
                <span class="text-xs text-gray-500">{{ option.description }}</span>
              </div>
            </el-radio>
          </div>
        </el-radio-group>
      </el-form-item>

      <el-form-item label="投资期限" required>
        <el-radio-group v-model="timeHorizon" class="w-full">
          <div class="space-y-2">
            <el-radio
              v-for="option in horizonOptions"
              :key="option.value"
              :label="option.value"
              class="w-full mb-2"
            >
              <div class="flex flex-col">
                <span class="font-medium">{{ option.label }}</span>
                <span class="text-xs text-gray-500">{{ option.description }}</span>
              </div>
            </el-radio>
          </div>
        </el-radio-group>
      </el-form-item>

      <el-form-item label="投资资金" required>
        <el-input-number
          v-model="capital"
          :min="10000"
          :max="10000000"
          :step="10000"
          :precision="0"
          :controls="true"
          style="width: 100%"
        />
        <div class="text-xs text-gray-500 mt-1">
          用于此策略的总资金（¥）
        </div>
      </el-form-item>

      <!-- 市场与行业 -->
      <el-divider content-position="left">市场与行业</el-divider>

      <el-form-item label="市场偏好" required>
        <el-checkbox-group v-model="marketFocus">
          <el-checkbox
            v-for="option in marketOptions"
            :key="option.value"
            :label="option.value"
          >
            {{ option.label }}
          </el-checkbox>
        </el-checkbox-group>
      </el-form-item>

      <el-form-item label="偏好行业">
        <el-checkbox-group v-model="industryPreference">
          <el-checkbox
            v-for="option in industryOptions"
            :key="option.value"
            :label="option.value"
          >
            {{ option.label }}
          </el-checkbox>
        </el-checkbox-group>
        <div class="text-xs text-gray-500 mt-1">
          不选择表示无偏好，AI将自动配置
        </div>
      </el-form-item>

      <el-form-item label="排除行业">
        <el-checkbox-group v-model="excludeIndustries">
          <el-checkbox
            v-for="option in industryOptions"
            :key="option.value"
            :label="option.value"
            :disabled="industryPreference.includes(option.value)"
          >
            {{ option.label }}
          </el-checkbox>
        </el-checkbox-group>
      </el-form-item>

      <!-- 高级设置 -->
      <el-divider content-position="left">高级设置</el-divider>

      <el-form-item label="单股最大仓位">
        <div class="flex items-center gap-4" style="width: 100%">
          <el-slider
            v-model="maxSinglePosition"
            :min="5"
            :max="50"
            :step="5"
            :format-tooltip="(val: number) => `${val}%`"
            style="flex: 1"
          />
          <span class="text-sm font-semibold" style="width: 50px">
            {{ maxSinglePosition }}%
          </span>
        </div>
        <div class="text-xs text-gray-500 mt-1">
          控制单只股票的最大持仓比例
        </div>
      </el-form-item>

      <el-form-item label="附加选项">
        <div class="space-y-2">
          <div>
            <el-checkbox v-model="includeAnalysis">
              包含详细分析
            </el-checkbox>
            <div class="ml-6 text-xs text-gray-500">
              提供策略逻辑和市场环境分析
            </div>
          </div>
          <div>
            <el-checkbox v-model="includeSpecificStocks">
              推荐具体股票
            </el-checkbox>
            <div class="ml-6 text-xs text-gray-500">
              AI推荐符合策略的具体股票池
            </div>
          </div>
        </div>
      </el-form-item>

      <!-- 自定义要求 -->
      <el-form-item label="自定义要求">
        <el-input
          v-model="customRequirements"
          type="textarea"
          :rows="3"
          placeholder="输入您的特殊要求或偏好（可选）&#10;例如：只考虑大盘股、避开ST股、关注高ROE公司等"
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
        :disabled="!capital || marketFocus.length === 0"
        @click="handleSubmit"
      >
        {{ submitting ? '生成中...' : '生成策略' }}
      </el-button>
    </template>
  </el-dialog>
</template>
