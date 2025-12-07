<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import { dailyReview } from '@/api/ai'
import type { DailyReviewResponse } from '@/api/ai'

const router = useRouter()

// 今日日期
const today = ref(new Date().toLocaleDateString('zh-CN', {
  year: 'numeric',
  month: 'long',
  day: 'numeric',
  weekday: 'long'
}))

// AI复盘数据
const loading = ref(false)
const aiReview = ref<DailyReviewResponse | null>(null)

// 加载AI每日复盘
const loadAIReview = async () => {
  loading.value = true
  try {
    const response = await dailyReview({})
    aiReview.value = response.data
    ElMessage.success('AI每日复盘加载成功')
  } catch (error: any) {
    console.error('加载AI复盘失败:', error)
    ElMessage.error(`加载失败: ${error.message || '请稍后重试'}`)
  } finally {
    loading.value = false
  }
}

// 页面加载时获取AI复盘
onMounted(() => {
  // loadAIReview() // 暂时注释，等后端API就绪后启用
})

// 市场总结数据
const marketSummary = ref({
  indexName: '上证指数',
  indexChange: '+0.85%',
  indexPoints: '3,245.67',
  hotSectors: [
    { name: '新能源汽车', change: '+3.2%', leader: '比亚迪 +5.8%' },
    { name: '人工智能', change: '+2.8%', leader: '科大讯飞 +6.2%' },
    { name: 'ChatGPT概念', change: '+2.5%', leader: '汉王科技 +8.5%' }
  ],
  weakSectors: [
    { name: '房地产', change: '-1.8%', leader: '万科A -3.2%' },
    { name: '银行', change: '-0.9%', leader: '工商银行 -1.1%' }
  ]
})

// 持仓表现
const portfolioPerformance = ref({
  todayProfit: 3200,
  todayProfitRate: 0.92,
  topGainers: [
    { symbol: '002594', name: '比亚迪', change: 2.3, value: 1200 },
    { symbol: '300750', name: '宁德时代', change: 1.8, value: 850 },
    { symbol: '600519', name: '贵州茅台', change: 1.2, value: 680 }
  ],
  topLosers: [
    { symbol: '600600', name: '青岛啤酒', change: -4.87, value: -2100 },
    { symbol: '00700', name: '腾讯控股', change: -1.2, value: -980 }
  ]
})

// 重要事件
const importantEvents = ref([
  {
    id: 1,
    type: 'policy',
    title: '美联储加息25个基点',
    impact: '利空',
    affectedStocks: ['腾讯控股', '阿里巴巴'],
    description: '预计科技股短期承压，建议减仓观望'
  },
  {
    id: 2,
    type: 'company',
    title: '青岛啤酒Q3财报不及预期',
    impact: '利空',
    affectedStocks: ['青岛啤酒'],
    description: '成本上升，销量疲软，短期走势偏弱'
  },
  {
    id: 3,
    type: 'policy',
    title: '新能源补贴政策延长',
    impact: '利好',
    affectedStocks: ['比亚迪', '宁德时代'],
    description: '新能源板块迎来政策利好，可积极布局'
  }
])

// 明日预测
const tomorrowPrediction = ref({
  marketOutlook: {
    direction: '震荡上行',
    range: '3,250 - 3,280',
    support: '3,230',
    resistance: '3,280',
    volumeExpectation: '成交量可能放大，资金情绪转暖'
  },
  focusSectors: ['新能源汽车', '人工智能', 'ChatGPT概念', '半导体'],
  risks: ['美联储加息影响尚未完全消化', '部分板块估值偏高', '外资流出压力'],
  suggestions: [
    '新能源板块可逢低加仓',
    '高估值科技股建议减仓',
    '关注政策受益板块',
    '控制仓位，保持灵活'
  ]
})

// 未来一周展望
const weeklyOutlook = ref({
  trend: '震荡偏强',
  keyEvents: [
    '周三: CPI数据公布',
    '周五: 多家科技公司发布财报',
    '周五: MSCI季度调整生效'
  ],
  opportunities: ['新能源汽车产业链', '人工智能应用落地'],
  concerns: ['宏观经济数据低于预期', '地缘政治风险']
})

// 我的投资观点汇总
const myViews = ref([
  {
    symbol: '002594',
    name: '比亚迪',
    myRating: 5,
    aiScore: 8.8,
    alignment: 'high',
    note: '长期看好新能源汽车龙头'
  },
  {
    symbol: '00700',
    name: '腾讯控股',
    myRating: 4,
    aiScore: 8.5,
    alignment: 'high',
    note: '互联网龙头，长期价值稳定'
  },
  {
    symbol: '601398',
    name: '工商银行',
    myRating: 3,
    aiScore: 7.5,
    alignment: 'medium',
    note: '存在观点分歧，需重新评估'
  }
])

// 查看完整历史
const viewHistory = () => {
  ElMessage.info('历史复盘功能开发中')
}

// 查看股票详情
const viewStock = (symbol: string) => {
  router.push(`/stocks/detail/${symbol}`)
}

// 导出复盘报告
const exportReport = () => {
  ElMessage.success('导出功能开发中')
}

// 获取对齐度标签
const getAlignmentLabel = (alignment: string) => {
  const labels: Record<string, string> = {
    high: '✅ 高度一致',
    medium: '⚠️ 存在分歧',
    low: '❌ 观点相反'
  }
  return labels[alignment] || ''
}

// 获取对齐度颜色
const getAlignmentColor = (alignment: string) => {
  const colors: Record<string, string> = {
    high: 'text-green-600',
    medium: 'text-yellow-600',
    low: 'text-red-600'
  }
  return colors[alignment] || 'text-gray-600'
}

onMounted(() => {
  // TODO: 加载真实数据
})
</script>

<template>
  <div class="daily-review min-h-screen bg-gray-50 p-6">
    <!-- 头部 -->
    <div class="mb-6">
      <div class="flex items-center justify-between mb-2">
        <h1 class="text-3xl font-bold text-gray-900">📊 每日复盘</h1>
        <div class="flex gap-2">
          <button
            @click="viewHistory"
            class="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
          >
            📜 历史复盘
          </button>
          <button
            @click="exportReport"
            class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            📥 导出报告
          </button>
        </div>
      </div>
      <p class="text-gray-600">{{ today }}</p>
    </div>

    <!-- 主内容区 -->
    <div class="space-y-6">
      <!-- 1. 市场总结 -->
      <div class="bg-white rounded-lg shadow-md p-6">
        <h2 class="text-xl font-bold text-gray-900 mb-4 flex items-center">
          <span class="mr-2">📈</span>
          市场总结
        </h2>

        <!-- 大盘表现 -->
        <div class="mb-6 p-4 bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-lg">
          <div class="flex items-center justify-between">
            <div>
              <h3 class="text-lg font-semibold text-gray-900">{{ marketSummary.indexName }}</h3>
              <div class="text-3xl font-bold text-blue-600 mt-2">
                {{ marketSummary.indexPoints }}
                <span class="text-lg ml-2 text-green-600">{{ marketSummary.indexChange }}</span>
              </div>
            </div>
            <div class="text-5xl">📊</div>
          </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <!-- 热点板块 -->
          <div>
            <h4 class="text-lg font-semibold text-gray-900 mb-3">🔥 热点板块 (涨幅前3):</h4>
            <div class="space-y-2">
              <div
                v-for="(sector, index) in marketSummary.hotSectors"
                :key="index"
                class="p-3 bg-red-50 border border-red-200 rounded-lg"
              >
                <div class="flex items-center justify-between mb-1">
                  <span class="font-semibold text-gray-900">{{ sector.name }}</span>
                  <span class="text-red-600 font-bold">{{ sector.change }}</span>
                </div>
                <div class="text-sm text-gray-600">领涨: {{ sector.leader }}</div>
              </div>
            </div>
          </div>

          <!-- 疲软板块 -->
          <div>
            <h4 class="text-lg font-semibold text-gray-900 mb-3">📉 疲软板块 (跌幅前2):</h4>
            <div class="space-y-2">
              <div
                v-for="(sector, index) in marketSummary.weakSectors"
                :key="index"
                class="p-3 bg-green-50 border border-green-200 rounded-lg"
              >
                <div class="flex items-center justify-between mb-1">
                  <span class="font-semibold text-gray-900">{{ sector.name }}</span>
                  <span class="text-green-600 font-bold">{{ sector.change }}</span>
                </div>
                <div class="text-sm text-gray-600">领跌: {{ sector.leader }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 2. 持仓表现 -->
      <div class="bg-white rounded-lg shadow-md p-6">
        <h2 class="text-xl font-bold text-gray-900 mb-4 flex items-center">
          <span class="mr-2">💼</span>
          持仓表现
        </h2>

        <!-- 今日盈亏 -->
        <div class="mb-6 p-4 bg-gradient-to-r from-green-50 to-emerald-50 border border-green-200 rounded-lg">
          <div class="text-center">
            <div class="text-sm text-gray-600 mb-2">今日盈亏</div>
            <div class="text-4xl font-bold text-red-600">
              +¥{{ portfolioPerformance.todayProfit.toLocaleString() }}
            </div>
            <div class="text-lg text-red-500 mt-1">
              +{{ portfolioPerformance.todayProfitRate.toFixed(2) }}%
            </div>
          </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <!-- 涨幅前3 -->
          <div>
            <h4 class="text-lg font-semibold text-gray-900 mb-3">📈 涨幅前3:</h4>
            <div class="space-y-2">
              <div
                v-for="stock in portfolioPerformance.topGainers"
                :key="stock.symbol"
                class="flex items-center justify-between p-3 bg-red-50 border border-red-200 rounded-lg cursor-pointer hover:shadow-md transition"
                @click="viewStock(stock.symbol)"
              >
                <div>
                  <div class="font-semibold text-gray-900">{{ stock.name }}</div>
                  <div class="text-xs text-gray-500">{{ stock.symbol }}</div>
                </div>
                <div class="text-right">
                  <div class="text-lg font-bold text-red-600">+{{ stock.change.toFixed(2) }}%</div>
                  <div class="text-sm text-gray-600">+¥{{ stock.value }}</div>
                </div>
              </div>
            </div>
          </div>

          <!-- 跌幅前2 -->
          <div>
            <h4 class="text-lg font-semibold text-gray-900 mb-3">📉 跌幅前2:</h4>
            <div class="space-y-2">
              <div
                v-for="stock in portfolioPerformance.topLosers"
                :key="stock.symbol"
                class="flex items-center justify-between p-3 bg-green-50 border border-green-200 rounded-lg cursor-pointer hover:shadow-md transition"
                @click="viewStock(stock.symbol)"
              >
                <div>
                  <div class="font-semibold text-gray-900">{{ stock.name }}</div>
                  <div class="text-xs text-gray-500">{{ stock.symbol }}</div>
                </div>
                <div class="text-right">
                  <div class="text-lg font-bold text-green-600">{{ stock.change.toFixed(2) }}%</div>
                  <div class="text-sm text-gray-600">¥{{ stock.value }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 3. 重要事件影响 -->
      <div class="bg-white rounded-lg shadow-md p-6">
        <h2 class="text-xl font-bold text-gray-900 mb-4 flex items-center">
          <span class="mr-2">⚠️</span>
          重要事件影响
        </h2>

        <div class="space-y-4">
          <div
            v-for="event in importantEvents"
            :key="event.id"
            class="p-4 rounded-lg border-2"
            :class="{
              'bg-red-50 border-red-200': event.impact === '利空',
              'bg-green-50 border-green-200': event.impact === '利好'
            }"
          >
            <div class="flex items-start justify-between mb-2">
              <div>
                <span
                  class="inline-block px-2 py-1 text-xs font-semibold rounded mr-2"
                  :class="{
                    'bg-red-600 text-white': event.impact === '利空',
                    'bg-green-600 text-white': event.impact === '利好'
                  }"
                >
                  {{ event.impact }}
                </span>
                <span class="text-xs text-gray-500">{{ event.type === 'policy' ? '政策事件' : '公司事件' }}</span>
              </div>
            </div>
            <h4 class="font-semibold text-gray-900 mb-2">{{ event.title }}</h4>
            <p class="text-sm text-gray-700 mb-2">{{ event.description }}</p>
            <div class="text-xs text-gray-600">
              影响股票: {{ event.affectedStocks.join(', ') }}
            </div>
          </div>
        </div>
      </div>

      <!-- 4. 明日预测 🔮 -->
      <div class="bg-gradient-to-r from-purple-50 to-indigo-50 rounded-lg shadow-md p-6 border-2 border-purple-200">
        <h2 class="text-xl font-bold text-purple-900 mb-4 flex items-center">
          <span class="mr-2">🔮</span>
          明日预测 (AI生成)
        </h2>

        <!-- 大盘研判 -->
        <div class="mb-6 p-4 bg-white rounded-lg border border-purple-200">
          <h4 class="text-lg font-semibold text-purple-900 mb-3">🎯 大盘研判:</h4>
          <div class="space-y-2 text-sm text-purple-900">
            <div>• 预计{{ tomorrowPrediction.marketOutlook.direction }}，关注 {{ tomorrowPrediction.marketOutlook.range }} 区间</div>
            <div>• {{ tomorrowPrediction.marketOutlook.volumeExpectation }}</div>
            <div>
              • <strong>支撑位:</strong> {{ tomorrowPrediction.marketOutlook.support }}
              <strong class="ml-4">阻力位:</strong> {{ tomorrowPrediction.marketOutlook.resistance }}
            </div>
          </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <!-- 关注板块 -->
          <div class="p-4 bg-white rounded-lg border border-purple-200">
            <h4 class="text-sm font-semibold text-purple-900 mb-2">👀 关注板块:</h4>
            <ul class="space-y-1 text-sm text-purple-800">
              <li v-for="(sector, index) in tomorrowPrediction.focusSectors" :key="index">
                • {{ sector }}
              </li>
            </ul>
          </div>

          <!-- 风险提示 -->
          <div class="p-4 bg-white rounded-lg border border-purple-200">
            <h4 class="text-sm font-semibold text-purple-900 mb-2">⚠️ 风险提示:</h4>
            <ul class="space-y-1 text-sm text-purple-800">
              <li v-for="(risk, index) in tomorrowPrediction.risks" :key="index">
                • {{ risk }}
              </li>
            </ul>
          </div>
        </div>

        <!-- 明日操作建议 -->
        <div class="mt-4 p-4 bg-white rounded-lg border border-purple-200">
          <h4 class="text-sm font-semibold text-purple-900 mb-2">💡 明日操作建议:</h4>
          <ul class="space-y-1 text-sm text-purple-800">
            <li v-for="(suggestion, index) in tomorrowPrediction.suggestions" :key="index">
              • {{ suggestion }}
            </li>
          </ul>
        </div>
      </div>

      <!-- 5. 未来一周展望 -->
      <div class="bg-white rounded-lg shadow-md p-6">
        <h2 class="text-xl font-bold text-gray-900 mb-4 flex items-center">
          <span class="mr-2">📅</span>
          未来一周展望
        </h2>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h4 class="text-lg font-semibold text-gray-900 mb-3">📊 整体趋势:</h4>
            <p class="text-gray-700 mb-4">{{ weeklyOutlook.trend }}</p>

            <h4 class="text-lg font-semibold text-gray-900 mb-3">🗓️ 关键事件:</h4>
            <ul class="space-y-2 text-sm text-gray-700">
              <li v-for="(event, index) in weeklyOutlook.keyEvents" :key="index" class="flex items-start">
                <span class="mr-2">•</span>
                <span>{{ event }}</span>
              </li>
            </ul>
          </div>

          <div>
            <h4 class="text-lg font-semibold text-gray-900 mb-3">✨ 潜在机会:</h4>
            <ul class="space-y-2 text-sm text-green-700 mb-4">
              <li v-for="(opp, index) in weeklyOutlook.opportunities" :key="index">
                • {{ opp }}
              </li>
            </ul>

            <h4 class="text-lg font-semibold text-gray-900 mb-3">⚠️ 需要关注:</h4>
            <ul class="space-y-2 text-sm text-red-700">
              <li v-for="(concern, index) in weeklyOutlook.concerns" :key="index">
                • {{ concern }}
              </li>
            </ul>
          </div>
        </div>
      </div>

      <!-- 6. 我的投资观点汇总 -->
      <div class="bg-white rounded-lg shadow-md p-6">
        <h2 class="text-xl font-bold text-gray-900 mb-4 flex items-center">
          <span class="mr-2">💭</span>
          我的投资观点汇总
        </h2>

        <div class="p-4 bg-blue-50 border border-blue-200 rounded-lg mb-4">
          <h4 class="text-sm font-semibold text-blue-900 mb-2">💡 AI与我的观点对比:</h4>
          <div class="space-y-3">
            <div
              v-for="view in myViews"
              :key="view.symbol"
              class="flex items-center justify-between p-3 bg-white rounded-lg"
            >
              <div class="flex items-center gap-4">
                <span class="font-semibold text-gray-900">{{ view.name }}</span>
                <span class="text-xs text-gray-500">AI {{ view.aiScore }}分 vs 我 {{ view.myRating }}星</span>
              </div>
              <div class="flex items-center gap-3">
                <span class="text-sm" :class="getAlignmentColor(view.alignment)">
                  {{ getAlignmentLabel(view.alignment) }}
                </span>
                <button
                  @click="viewStock(view.symbol)"
                  class="text-xs text-blue-600 hover:underline"
                >
                  查看 →
                </button>
              </div>
            </div>
          </div>
        </div>

        <div class="text-sm text-gray-600 text-center">
          基于您的股票评价与AI分析对比生成
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.daily-review {
  /* 自定义样式 */
}
</style>
