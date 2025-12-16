<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { queryHoldings } from '@/api/holding'
import { queryAccounts } from '@/api/account'

const router = useRouter()

// 选择的账户
const selectedAccount = ref<number | null>(null)
const loading = ref(false)

// 账户列表
const accounts = ref<any[]>([])

// 持仓概览数据
const portfolioStats = ref({
  market_value: 0,
  total_profit_loss: 0,
  profit_loss_rate: 0,
  stock_count: 0,
  event_count: 0
})

// AI组合建议
const aiSuggestion = ref({
  update_time: '2025-11-14 15:30',
  score: 7.2,
  risk_level: '中等风险',
  risk_desc: '适度集中，需分散',
  urgency: '建议调整',
  urgency_desc: '近期有重要事件',
  suggestions: [
    {
      type: 'reduce',
      title: '减仓腾讯控股10-20%',
      desc: '受美联储加息影响，港股科技股面临估值压力'
    },
    {
      type: 'wait',
      title: '青岛啤酒等待加仓',
      desc: '回调至¥58-60区间分批买入，消费刺激政策有望提振'
    },
    {
      type: 'hold',
      title: '比亚迪继续持有',
      desc: '销量持续超预期，行业龙头地位稳固'
    },
    {
      type: 'add',
      title: '增加防御性配置',
      desc: '建议配置5-10%公用事业或消费必需品，降低组合波动'
    }
  ]
})

// 持仓股票列表
const holdings = ref<any[]>([])

// 事件影响矩阵
const eventMatrix = ref([
  {
    event: '美联储加息25bp',
    date: '2025-11-07',
    type: '政策事件',
    impacts: [
      { stock: '600600', change: -0.5, level: 'light-bearish', desc: '影响较小' },
      { stock: '00700', change: -2.5, level: 'bearish', desc: '估值压力' },
      { stock: '002594', change: -1.8, level: 'light-bearish', desc: '中等影响' }
    ]
  },
  {
    event: '消费刺激政策',
    date: '2025-11-07',
    type: '政策事件',
    impacts: [
      { stock: '600600', change: 2.0, level: 'bullish', desc: '直接受益' },
      { stock: '00700', change: 0, level: 'neutral', desc: '无影响' },
      { stock: '002594', change: 0.8, level: 'light-bullish', desc: '间接利好' }
    ]
  },
  {
    event: '青岛啤酒Q3财报',
    date: '2025-10-28',
    type: '公司事件',
    impacts: [
      { stock: '600600', change: -4.2, level: 'strong-bearish', desc: '业绩不及预期' },
      { stock: '00700', change: 0, level: 'neutral', desc: '-' },
      { stock: '002594', change: 0, level: 'neutral', desc: '-' }
    ]
  },
  {
    event: '复星集团增持',
    date: '2025-11-01',
    type: '公司事件',
    impacts: [
      { stock: '600600', change: 1.8, level: 'light-bullish', desc: '信心提振' },
      { stock: '00700', change: 0, level: 'neutral', desc: '-' },
      { stock: '002594', change: 0, level: 'neutral', desc: '-' }
    ]
  },
  {
    event: '王者荣耀2版号获批',
    date: '2025-11-03',
    type: '公司事件',
    impacts: [
      { stock: '600600', change: 0, level: 'neutral', desc: '-' },
      { stock: '00700', change: 3.5, level: 'bullish', desc: '重大利好' },
      { stock: '002594', change: 0, level: 'neutral', desc: '-' }
    ]
  },
  {
    event: '10月销量50.1万辆',
    date: '2025-11-01',
    type: '公司事件',
    impacts: [
      { stock: '600600', change: 0, level: 'neutral', desc: '-' },
      { stock: '00700', change: 0, level: 'neutral', desc: '-' },
      { stock: '002594', change: 5.2, level: 'bullish', desc: '超预期' }
    ]
  },
  {
    event: 'A股IPO审核放缓',
    date: '2025-11-05',
    type: '政策事件',
    impacts: [
      { stock: '600600', change: 0.5, level: 'light-bullish', desc: '资金分流减少' },
      { stock: '00700', change: 0, level: 'neutral', desc: '-' },
      { stock: '002594', change: 0.8, level: 'light-bullish', desc: '小幅利好' }
    ]
  }
])

// 获取影响单元格的样式类
const getImpactClass = (level: string) => {
  const classes: Record<string, string> = {
    'strong-bearish': 'bg-orange-100 border-orange-300 text-orange-700',
    'bearish': 'bg-red-100 border-red-300 text-red-700',
    'light-bearish': 'bg-red-50 border-red-200 text-red-600',
    'neutral': 'bg-gray-100 border-gray-300 text-gray-600',
    'light-bullish': 'bg-green-50 border-green-200 text-green-600',
    'bullish': 'bg-green-100 border-green-300 text-green-700'
  }
  return classes[level] || classes.neutral
}

// 获取建议图标
const getSuggestionIcon = (type: string) => {
  const icons: Record<string, string> = {
    reduce: '1.',
    wait: '2.',
    hold: '3.',
    add: '4.'
  }
  return icons[type] || '•'
}

// 获取建议颜色
const getSuggestionColor = (type: string) => {
  const colors: Record<string, string> = {
    reduce: 'text-red-600',
    wait: 'text-yellow-600',
    hold: 'text-green-600',
    add: 'text-blue-600'
  }
  return colors[type] || 'text-gray-600'
}

// 返回
const goBack = () => {
  router.back()
}

// 刷新AI分析
const refreshAI = async () => {
  ElMessage.info('正在刷新数据...')
  await loadHoldings()
  ElMessage.success('数据已刷新')
}

// 监听账户切换
const handleAccountChange = async () => {
  await loadHoldings()
}

// 查看详细分析
const viewDetailedAnalysis = () => {
  router.push('/analysis')
}

// 生成调仓方案
const generateRebalancePlan = () => {
  ElMessage.info('调仓方案功能开发中')
}

// 保存建议
const saveSuggestion = () => {
  ElMessage.success('建议已保存')
}

// 加载账户列表
const loadAccounts = async () => {
  try {
    const response = await queryAccounts({})
    if (response.data && response.data.items) {
      accounts.value = response.data.items
      if (accounts.value.length > 0) {
        selectedAccount.value = accounts.value[0].account_id
      }
    }
  } catch (error) {
    console.error('加载账户列表失败:', error)
  }
}

// 加载持仓数据
const loadHoldings = async () => {
  if (!selectedAccount.value) return

  loading.value = true
  try {
    const response = await queryHoldings({ account_id: selectedAccount.value })
    if (response.data) {
      holdings.value = response.data.holdings || []

      // 更新统计数据
      if (response.data.summary) {
        portfolioStats.value = {
          market_value: response.data.summary.total_value || 0,
          total_profit_loss: response.data.summary.total_profit_loss || 0,
          profit_loss_rate: response.data.summary.total_profit_loss_percent || 0,
          stock_count: response.data.summary.total_holdings || 0,
          event_count: 0 // TODO: 从事件API获取
        }
      }
    }
  } catch (error: any) {
    console.error('加载持仓数据失败:', error)
    ElMessage.error('加载失败: ' + (error.message || '请检查网络连接'))
    holdings.value = []
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await loadAccounts()
  await loadHoldings()
})
</script>

<template>
  <div class="min-h-screen bg-gray-50">
    <!-- 顶部导航 -->
    <nav class="bg-white border-b border-gray-200 sticky top-0 z-50">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between h-16">
          <div class="flex items-center space-x-4">
            <a class="text-gray-600 hover:text-gray-900 cursor-pointer" @click="goBack">← 返回</a>
            <h1 class="text-xl font-bold">📊 持仓分析</h1>
          </div>
          <div class="flex items-center space-x-4">
            <select
              v-model="selectedAccount"
              class="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              @change="handleAccountChange"
            >
              <option v-for="account in accounts" :key="account.account_id" :value="account.account_id">
                {{ account.broker_name }} ({{ account.account_no.slice(-4) }})
              </option>
            </select>
            <button
              class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
              @click="refreshAI"
            >
              🤖 刷新AI分析
            </button>
          </div>
        </div>
      </div>
    </nav>

    <!-- 主内容 -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">

      <!-- 持仓概览 -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div class="bg-white rounded-lg shadow-md p-6">
          <p class="text-sm text-gray-600 mb-2">持仓市值</p>
          <p class="text-3xl font-bold text-gray-900">¥{{ portfolioStats.market_value.toLocaleString() }}</p>
        </div>
        <div class="bg-white rounded-lg shadow-md p-6">
          <p class="text-sm text-gray-600 mb-2">总盈亏</p>
          <p class="text-3xl font-bold text-green-600">+¥{{ portfolioStats.total_profit_loss.toLocaleString() }}</p>
          <p class="text-sm text-green-600 mt-1">+{{ portfolioStats.profit_loss_rate }}%</p>
        </div>
        <div class="bg-white rounded-lg shadow-md p-6">
          <p class="text-sm text-gray-600 mb-2">持仓股票数</p>
          <p class="text-3xl font-bold text-blue-600">{{ portfolioStats.stock_count }}</p>
        </div>
        <div class="bg-white rounded-lg shadow-md p-6">
          <p class="text-sm text-gray-600 mb-2">关注事件</p>
          <p class="text-3xl font-bold text-orange-600">{{ portfolioStats.event_count }}</p>
        </div>
      </div>

      <!-- AI综合建议 -->
      <div class="bg-gradient-to-br from-purple-50 to-blue-50 border-2 border-purple-200 rounded-xl p-6 mb-6">
        <div class="flex items-start justify-between mb-4">
          <div class="flex items-center gap-3">
            <span class="text-3xl">🤖</span>
            <div>
              <h3 class="text-xl font-bold text-gray-900">AI组合建议</h3>
              <p class="text-sm text-gray-600">基于事件分析和风险评估的智能建议</p>
            </div>
          </div>
          <span class="text-xs text-gray-500">最后更新: {{ aiSuggestion.update_time }}</span>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          <div class="bg-white rounded-lg p-4">
            <p class="text-sm text-gray-600 mb-2">组合评分</p>
            <div class="flex items-baseline gap-2">
              <span class="text-3xl font-bold text-blue-600">{{ aiSuggestion.score }}</span>
              <span class="text-sm text-gray-600">/ 10</span>
            </div>
            <p class="text-xs text-gray-500 mt-1">中等偏好</p>
          </div>
          <div class="bg-white rounded-lg p-4">
            <p class="text-sm text-gray-600 mb-2">风险等级</p>
            <span class="inline-block px-3 py-1 bg-yellow-100 text-yellow-800 text-sm font-bold rounded">
              {{ aiSuggestion.risk_level }}
            </span>
            <p class="text-xs text-gray-500 mt-2">{{ aiSuggestion.risk_desc }}</p>
          </div>
          <div class="bg-white rounded-lg p-4">
            <p class="text-sm text-gray-600 mb-2">调仓紧迫性</p>
            <span class="inline-block px-3 py-1 bg-orange-100 text-orange-800 text-sm font-bold rounded">
              {{ aiSuggestion.urgency }}
            </span>
            <p class="text-xs text-gray-500 mt-2">{{ aiSuggestion.urgency_desc }}</p>
          </div>
        </div>

        <div class="bg-white rounded-lg p-4 mb-4">
          <h4 class="text-sm font-semibold text-gray-900 mb-3">💡 核心建议:</h4>
          <ul class="space-y-2 text-sm text-gray-700">
            <li
              v-for="(suggestion, index) in aiSuggestion.suggestions"
              :key="index"
              class="flex items-start gap-2"
            >
              <span class="font-bold" :class="getSuggestionColor(suggestion.type)">
                {{ getSuggestionIcon(suggestion.type) }}
              </span>
              <span>
                <strong>{{ suggestion.title }}</strong> - {{ suggestion.desc }}
              </span>
            </li>
          </ul>
        </div>

        <div class="flex gap-2">
          <button
            class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm transition"
            @click="viewDetailedAnalysis"
          >
            查看详细分析
          </button>
          <button
            class="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 text-sm transition"
            @click="generateRebalancePlan"
          >
            生成调仓方案
          </button>
          <button
            class="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 text-sm transition"
            @click="saveSuggestion"
          >
            保存建议
          </button>
        </div>
      </div>

      <!-- 事件影响矩阵 -->
      <div class="bg-white rounded-lg shadow-md p-6 mb-6">
        <div class="flex items-center justify-between mb-6">
          <div>
            <h3 class="text-lg font-bold">📋 事件影响矩阵</h3>
            <p class="text-sm text-gray-600">近30天事件对持仓的影响评估</p>
          </div>
          <div class="flex gap-2 text-xs">
            <div class="flex items-center gap-1">
              <div class="w-4 h-4 bg-red-100 border border-red-300 rounded"></div>
              <span>利空</span>
            </div>
            <div class="flex items-center gap-1">
              <div class="w-4 h-4 bg-green-100 border border-green-300 rounded"></div>
              <span>利好</span>
            </div>
            <div class="flex items-center gap-1">
              <div class="w-4 h-4 bg-gray-100 border border-gray-300 rounded"></div>
              <span>中性</span>
            </div>
          </div>
        </div>

        <div class="overflow-x-auto">
          <table class="min-w-full">
            <thead>
              <tr class="border-b-2 border-gray-300">
                <th class="px-4 py-3 text-left text-sm font-semibold text-gray-700 w-64">事件</th>
                <th
                  v-for="holding in holdings"
                  :key="holding.symbol"
                  class="px-4 py-3 text-center text-sm font-semibold text-gray-700"
                >
                  <div>{{ holding.icon }} {{ holding.name }}</div>
                  <div class="text-xs text-gray-500 font-normal">{{ holding.symbol }}</div>
                </th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="(event, index) in eventMatrix"
                :key="index"
                class="border-b border-gray-200"
              >
                <td class="px-4 py-3">
                  <div class="font-semibold text-sm">{{ event.event }}</div>
                  <div class="text-xs text-gray-500">{{ event.date }} · {{ event.type }}</div>
                </td>
                <td
                  v-for="impact in event.impacts"
                  :key="impact.stock"
                  class="px-4 py-3"
                >
                  <div
                    class="matrix-cell border-2 rounded-lg p-3 text-center hover:scale-105 transition-all min-h-[80px] flex flex-col justify-center"
                    :class="getImpactClass(impact.level)"
                  >
                    <div class="text-sm font-bold">
                      {{ impact.change > 0 ? '+' : '' }}{{ impact.change }}%
                    </div>
                    <div class="text-xs text-gray-600 mt-1">{{ impact.desc }}</div>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

    </main>
  </div>
</template>

<style scoped>
.matrix-cell {
  min-height: 80px;
  transition: all 0.2s;
}

.matrix-cell:hover {
  transform: scale(1.05);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}
</style>
