<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import type {
  Event,
  EventCategory,
  EventSubtype,
  EventImpact,
  ImpactLevel
} from '@/types/event'
import {
  EVENT_CATEGORY_LABELS,
  EVENT_SUBTYPE_LABELS,
  IMPACT_LEVEL_LABELS
} from '@/types/event'
import StockSearchDialog from './StockSearchDialog.vue'
import type { Stock } from '@/types/stock'

interface Props {
  visible: boolean
  event?: Event
  mode: 'create' | 'edit'
}

const props = withDefaults(defineProps<Props>(), {
  mode: 'create'
})

const emit = defineEmits<{
  'update:visible': [visible: boolean]
  confirm: [data: Partial<Event>]
}>()

const dialogVisible = computed({
  get: () => props.visible,
  set: (val) => emit('update:visible', val)
})

const dialogTitle = computed(() => {
  return props.mode === 'create' ? '新建投资事件' : '编辑投资事件'
})

// 表单数据
const formData = ref<Partial<Event>>({
  title: '',
  category: 'policy',
  subtype: 'monetary_policy',
  description: '',
  event_date: new Date().toISOString().split('T')[0],
  source_url: '',
  related_stocks: [],
  ai_impact: undefined
})

// 用户备注
const userNotes = ref('')

// 是否启用 AI 影响评估
const enableAiImpact = ref(false)
const aiImpact = ref<EventImpact>({
  short_term: 3,
  mid_term: 3,
  long_term: 3,
  confidence: 0.7,
  reasoning: ''
})

// 股票搜索对话框
const stockSearchVisible = ref(false)

// 事件类别选项
const categoryOptions = Object.entries(EVENT_CATEGORY_LABELS).map(([value, label]) => ({
  value: value as EventCategory,
  label
}))

// 事件子类型选项（根据类别动态变化）
const subtypeOptions = computed(() => {
  const category = formData.value.category
  const subtypeMap: Record<EventCategory, EventSubtype[]> = {
    policy: ['monetary_policy', 'fiscal_policy', 'regulatory_policy', 'international_policy'],
    company: ['earnings', 'dividend', 'ma', 'governance'],
    market: ['index_volatility', 'sector_rotation', 'sentiment_shift', 'liquidity_change'],
    industry: ['tech_change', 'regulatory_shift', 'competitive_dynamics', 'demand_supply']
  }

  const subtypes = subtypeMap[category!] || []
  return subtypes.map(subtype => ({
    value: subtype,
    label: EVENT_SUBTYPE_LABELS[subtype]
  }))
})

// 影响级别选项
const impactLevelOptions = [
  { value: 1, label: '1 - 极低' },
  { value: 2, label: '2 - 较低' },
  { value: 3, label: '3 - 中等' },
  { value: 4, label: '4 - 较高' },
  { value: 5, label: '5 - 极高' }
] as const

// 关联股票列表
const relatedStocks = ref<Stock[]>([])

// 监听类别变化，更新子类型
watch(() => formData.value.category, (newCategory) => {
  if (newCategory && subtypeOptions.value.length > 0) {
    formData.value.subtype = subtypeOptions.value[0].value
  }
})

// 添加关联股票
const handleStockSelect = (stocks: Stock | Stock[]) => {
  const stockArray = Array.isArray(stocks) ? stocks : [stocks]

  stockArray.forEach(stock => {
    if (!relatedStocks.value.find(s => s.symbol === stock.symbol)) {
      relatedStocks.value.push(stock)
    }
  })

  // 更新 related_stocks
  formData.value.related_stocks = relatedStocks.value.map(s => s.symbol)
}

// 移除关联股票
const removeStock = (symbol: string) => {
  relatedStocks.value = relatedStocks.value.filter(s => s.symbol !== symbol)
  formData.value.related_stocks = relatedStocks.value.map(s => s.symbol)
}

// 请求 AI 评估
const requestingAiImpact = ref(false)
const requestAiImpact = async () => {
  if (!formData.value.title || !formData.value.description) {
    ElMessage.warning('请先填写事件标题和描述')
    return
  }

  requestingAiImpact.value = true
  try {
    // Mock AI 评估
    await new Promise(resolve => setTimeout(resolve, 2000))

    // 模拟 AI 返回的评估结果
    const mockImpact: EventImpact = {
      short_term: Math.floor(Math.random() * 3) + 2 as ImpactLevel, // 2-4
      mid_term: Math.floor(Math.random() * 3) + 2 as ImpactLevel,
      long_term: Math.floor(Math.random() * 3) + 2 as ImpactLevel,
      confidence: 0.6 + Math.random() * 0.3, // 0.6-0.9
      reasoning: '基于当前市场环境和历史数据分析，该事件预计会对相关行业产生中等程度的影响。短期内可能引发市场情绪波动，中长期影响需关注后续政策落地情况。'
    }

    aiImpact.value = mockImpact
    enableAiImpact.value = true

    ElMessage.success('AI 评估完成')
  } catch (error) {
    ElMessage.error('AI 评估失败')
  } finally {
    requestingAiImpact.value = false
  }
}

// 提交
const submitting = ref(false)
const handleSubmit = async () => {
  // 验证
  if (!formData.value.title) {
    ElMessage.warning('请输入事件标题')
    return
  }
  if (!formData.value.description) {
    ElMessage.warning('请输入事件描述')
    return
  }
  if (!formData.value.event_date) {
    ElMessage.warning('请选择事件日期')
    return
  }

  submitting.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 500))

    const data: Partial<Event> = {
      ...formData.value,
      ai_impact: enableAiImpact.value ? aiImpact.value : undefined
    }

    // 如果有用户备注，添加到 data 中（虽然 Event 接口没有这个字段，但实际可能会用到）
    if (userNotes.value) {
      (data as any).user_notes = userNotes.value
    }

    emit('confirm', data)

    const action = props.mode === 'create' ? '创建' : '更新'
    ElMessage.success(`事件${action}成功`)

    dialogVisible.value = false
    if (props.mode === 'create') {
      resetForm()
    }
  } catch (error) {
    ElMessage.error('操作失败')
  } finally {
    submitting.value = false
  }
}

// 重置表单
const resetForm = () => {
  formData.value = {
    title: '',
    category: 'policy',
    subtype: 'monetary_policy',
    description: '',
    event_date: new Date().toISOString().split('T')[0],
    source_url: '',
    related_stocks: []
  }
  relatedStocks.value = []
  userNotes.value = ''
  enableAiImpact.value = false
  aiImpact.value = {
    short_term: 3,
    mid_term: 3,
    long_term: 3,
    confidence: 0.7,
    reasoning: ''
  }
}

// 加载事件数据（编辑模式）
const loadEventData = () => {
  if (props.mode === 'edit' && props.event) {
    formData.value = { ...props.event }

    if (props.event.ai_impact) {
      enableAiImpact.value = true
      aiImpact.value = { ...props.event.ai_impact }
    }

    // 加载关联股票（这里需要根据 symbol 获取完整的 Stock 对象）
    // Mock 实现
    if (props.event.related_stocks && props.event.related_stocks.length > 0) {
      // TODO: 实际应该调用 API 获取股票详情
      relatedStocks.value = props.event.related_stocks.map(symbol => ({
        symbol,
        name: '股票名称',
        market: 'A' as const,
        current_price: 0,
        change_rate: 0,
        volume: 0,
        turnover: 0
      }))
    }
  } else {
    resetForm()
  }
}

// 监听弹框打开
watch(() => props.visible, (val) => {
  if (val) {
    loadEventData()
  }
})
</script>

<template>
  <el-dialog
    v-model="dialogVisible"
    :title="dialogTitle"
    width="700px"
    :close-on-click-modal="false"
    @closed="mode === 'create' ? resetForm() : null"
  >
    <el-form :model="formData" label-width="120px">
      <!-- 基本信息 -->
      <el-divider content-position="left">基本信息</el-divider>

      <el-form-item label="事件标题" required>
        <el-input
          v-model="formData.title"
          placeholder="输入事件标题"
          maxlength="200"
          show-word-limit
        />
      </el-form-item>

      <el-form-item label="事件类别" required>
        <el-select v-model="formData.category" placeholder="选择事件类别" style="width: 100%">
          <el-option
            v-for="option in categoryOptions"
            :key="option.value"
            :label="option.label"
            :value="option.value"
          />
        </el-select>
      </el-form-item>

      <el-form-item label="事件子类型" required>
        <el-select v-model="formData.subtype" placeholder="选择事件子类型" style="width: 100%">
          <el-option
            v-for="option in subtypeOptions"
            :key="option.value"
            :label="option.label"
            :value="option.value"
          />
        </el-select>
      </el-form-item>

      <el-form-item label="事件日期" required>
        <el-date-picker
          v-model="formData.event_date"
          type="date"
          placeholder="选择事件发生日期"
          style="width: 100%"
          value-format="YYYY-MM-DD"
        />
      </el-form-item>

      <el-form-item label="事件描述" required>
        <el-input
          v-model="formData.description"
          type="textarea"
          :rows="4"
          placeholder="输入事件详细描述"
          maxlength="1000"
          show-word-limit
        />
      </el-form-item>

      <el-form-item label="来源链接">
        <el-input
          v-model="formData.source_url"
          placeholder="输入新闻或消息来源链接（可选）"
          maxlength="500"
        />
      </el-form-item>

      <!-- 关联股票 -->
      <el-divider content-position="left">关联股票</el-divider>

      <el-form-item label="关联股票">
        <div class="w-full">
          <el-button @click="stockSearchVisible = true">
            添加关联股票
          </el-button>

          <div v-if="relatedStocks.length > 0" class="mt-3 space-y-2">
            <el-tag
              v-for="stock in relatedStocks"
              :key="stock.symbol"
              closable
              class="mr-2"
              @close="removeStock(stock.symbol)"
            >
              {{ stock.name }} ({{ stock.symbol }})
            </el-tag>
          </div>
        </div>
      </el-form-item>

      <!-- AI 影响评估 -->
      <el-divider content-position="left">AI 影响评估</el-divider>

      <el-form-item label="启用 AI 评估">
        <div class="flex items-center gap-4">
          <el-switch v-model="enableAiImpact" />
          <el-button
            v-if="!enableAiImpact"
            :loading="requestingAiImpact"
            @click="requestAiImpact"
          >
            请求 AI 评估
          </el-button>
        </div>
      </el-form-item>

      <div v-if="enableAiImpact" class="ml-[120px] space-y-4 mb-4">
        <el-form-item label="短期影响" label-width="100px">
          <el-select v-model="aiImpact.short_term" placeholder="选择影响级别" style="width: 200px">
            <el-option
              v-for="option in impactLevelOptions"
              :key="option.value"
              :label="option.label"
              :value="option.value"
            />
          </el-select>
          <span class="ml-2 text-sm text-gray-500">(1-3个月)</span>
        </el-form-item>

        <el-form-item label="中期影响" label-width="100px">
          <el-select v-model="aiImpact.mid_term" placeholder="选择影响级别" style="width: 200px">
            <el-option
              v-for="option in impactLevelOptions"
              :key="option.value"
              :label="option.label"
              :value="option.value"
            />
          </el-select>
          <span class="ml-2 text-sm text-gray-500">(3-12个月)</span>
        </el-form-item>

        <el-form-item label="长期影响" label-width="100px">
          <el-select v-model="aiImpact.long_term" placeholder="选择影响级别" style="width: 200px">
            <el-option
              v-for="option in impactLevelOptions"
              :key="option.value"
              :label="option.label"
              :value="option.value"
            />
          </el-select>
          <span class="ml-2 text-sm text-gray-500">(>12个月)</span>
        </el-form-item>

        <el-form-item label="置信度" label-width="100px">
          <el-slider
            v-model="aiImpact.confidence"
            :min="0"
            :max="1"
            :step="0.1"
            :format-tooltip="(val: number) => `${(val * 100).toFixed(0)}%`"
            style="width: 200px"
          />
          <span class="ml-4 text-sm font-semibold">
            {{ (aiImpact.confidence * 100).toFixed(0) }}%
          </span>
        </el-form-item>

        <el-form-item label="分析理由" label-width="100px">
          <el-input
            v-model="aiImpact.reasoning"
            type="textarea"
            :rows="3"
            placeholder="AI 分析的理由和依据"
            maxlength="500"
            show-word-limit
            style="width: 100%"
          />
        </el-form-item>
      </div>

      <!-- 用户备注 -->
      <el-divider content-position="left">用户备注</el-divider>

      <el-form-item label="备注">
        <el-input
          v-model="userNotes"
          type="textarea"
          :rows="3"
          placeholder="输入个人备注和想法（可选）"
          maxlength="1000"
          show-word-limit
        />
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="dialogVisible = false">取消</el-button>
      <el-button type="primary" :loading="submitting" @click="handleSubmit">
        {{ mode === 'create' ? '创建' : '保存' }}
      </el-button>
    </template>

    <!-- 股票搜索对话框 -->
    <stock-search-dialog
      v-model:visible="stockSearchVisible"
      :multiple="true"
      :exclude-symbols="formData.related_stocks"
      @confirm="handleStockSelect"
    />
  </el-dialog>
</template>
