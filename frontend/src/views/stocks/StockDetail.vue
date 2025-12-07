<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import StockReview from '@/components/StockReview.vue'
import { getStockDetail } from '@/api/stock'
import { queryHoldings } from '@/api/holding'
import { queryEvents } from '@/api/event'
import { queryStrategies, createStrategy, deleteStrategy, executeStrategy } from '@/api/strategy'

const route = useRoute()
const router = useRouter()

const symbol = computed(() => route.params.symbol as string)
const loading = ref(false)
const activeTab = ref('events') // 默认事件时间线

// 股票信息
const stockInfo = ref<any>({
  symbol: '',
  name: '',
  market: '',
  industry: '',
  sector: '',
  current_price: 0,
  change_amount: 0,
  change_rate: 0,
  update_time: '',
  open: 0,
  high: 0,
  low: 0,
  prev_close: 0,
  volume: 0,
  turnover: 0
})

// 持仓信息
const positionInfo = ref<any>(null)

// 事件数据
const events = ref<any[]>([])

// 操作策略
const strategies = ref<any[]>([])

const pendingStrategiesCount = computed(() =>
  strategies.value.filter(s => s.status === 'pending').length
)

const completedStrategiesCount = computed(() =>
  strategies.value.filter(s => s.status === 'completed').length
)

// 返回
const goBack = () => {
  router.back()
}

// AI分析
const analyzeStock = () => {
  router.push({
    path: '/analysis',
    query: { symbol: symbol.value }
  })
}

// 添加到关注
const addToWatchlist = () => {
  ElMessage.success('已添加到关注列表')
}

// 涨跌颜色
const priceClass = computed(() => {
  return stockInfo.value.change_rate > 0 ? 'text-red-500' : 'text-green-600'
})

// 获取事件重要性颜色
const getImportanceColor = (importance: string) => {
  const colors: Record<string, string> = {
    High: 'orange',
    Medium: 'yellow',
    Low: 'gray'
  }
  return colors[importance] || 'gray'
}

// 获取事件背景色类名
const getEventBgClass = (color: string) => {
  const classes: Record<string, string> = {
    orange: 'bg-orange-50 border-orange-200',
    green: 'bg-green-50 border-green-200',
    yellow: 'bg-yellow-50 border-yellow-200',
    gray: 'bg-gray-50 border-gray-200'
  }
  return classes[color] || 'bg-gray-50 border-gray-200'
}

// 获取时间线圆点颜色
const getDotColor = (color: string) => {
  const classes: Record<string, string> = {
    orange: 'bg-orange-500',
    green: 'bg-green-500',
    yellow: 'bg-yellow-400',
    gray: 'bg-gray-400'
  }
  return classes[color] || 'bg-gray-400'
}

// 获取股票详情
const fetchStockDetail = async () => {
  if (!symbol.value) return
  try {
    const response = await getStockDetail({ symbol: symbol.value })
    if (response.data) {
      stockInfo.value = {
        symbol: response.data.symbol || symbol.value,
        name: response.data.stock_name || response.data.name || '',
        market: response.data.market || 'A股',
        industry: response.data.industry || '',
        sector: response.data.sector || '',
        current_price: response.data.current_price || 0,
        change_amount: response.data.change_amount || 0,
        change_rate: response.data.change_rate || 0,
        update_time: response.data.update_time || new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }),
        open: response.data.open || 0,
        high: response.data.high || 0,
        low: response.data.low || 0,
        prev_close: response.data.prev_close || 0,
        volume: response.data.volume || 0,
        turnover: response.data.turnover || 0
      }
    }
  } catch (error: any) {
    console.error('获取股票详情失败:', error)
    // 设置一些默认值，避免页面报错
    stockInfo.value.symbol = symbol.value
  }
}

// 获取持仓信息
const fetchHoldings = async () => {
  if (!symbol.value) return
  try {
    const response = await queryHoldings({ symbol: symbol.value })
    if (response.data && response.data.items && response.data.items.length > 0) {
      const holding = response.data.items[0]
      positionInfo.value = {
        quantity: holding.quantity || 0,
        avg_cost: holding.cost_price || 0,
        current_price: holding.current_price || stockInfo.value.current_price || 0,
        market_value: holding.market_value || 0,
        profit_loss: holding.profit_loss || 0,
        profit_loss_rate: holding.profit_loss_rate || 0
      }
    } else {
      positionInfo.value = null
    }
  } catch (error: any) {
    console.error('获取持仓信息失败:', error)
    positionInfo.value = null
  }
}

// 获取事件列表
const fetchEvents = async () => {
  if (!symbol.value) return
  try {
    const response = await queryEvents({ symbol: symbol.value, page_size: 10 })
    if (response.data && response.data.items) {
      events.value = response.data.items.map((event: any) => ({
        id: event.event_id,
        date: event.event_date || event.created_at?.split('T')[0],
        type: event.event_type || '事件',
        importance: event.importance || 'Medium',
        color: getEventColorByImportance(event.importance),
        title: event.title || event.content,
        ai_analysis: event.ai_analysis || null
      }))
    }
  } catch (error: any) {
    console.error('获取事件列表失败:', error)
    events.value = []
  }
}

// 获取策略列表
const fetchStrategies = async () => {
  if (!symbol.value) return
  try {
    const response = await queryStrategies({ symbol: symbol.value })
    if (response.data && response.data.items) {
      strategies.value = response.data.items.map((strategy: any) => ({
        id: strategy.strategy_id,
        type: strategy.strategy_type,
        name: strategy.reason?.substring(0, 20) || getStrategyTypeName(strategy.strategy_type, strategy.is_stop_loss, strategy.is_take_profit),
        status: strategy.status,
        isStopLoss: strategy.is_stop_loss,
        isTarget: strategy.is_take_profit,
        price: strategy.trigger_price ? `¥${strategy.trigger_price}` : '-',
        quantity: strategy.target_quantity ? `${strategy.target_quantity}股` : '-',
        reason: strategy.reason || strategy.notes || ''
      }))
    }
  } catch (error: any) {
    console.error('获取策略列表失败:', error)
    strategies.value = []
  }
}

// 根据重要性获取颜色
const getEventColorByImportance = (importance: string) => {
  const colors: Record<string, string> = {
    'Critical': 'orange',
    'High': 'orange',
    'Medium': 'yellow',
    'Low': 'gray'
  }
  return colors[importance] || 'gray'
}

// 获取策略类型名称
const getStrategyTypeName = (type: string, isStopLoss: boolean, isTakeProfit: boolean) => {
  if (isStopLoss) return '⚠️ 止损位'
  if (isTakeProfit) return '目标位'
  if (type === 'buy') return '买入策略'
  if (type === 'sell') return '卖出策略'
  return '持有策略'
}

// 添加新策略
const handleAddStrategy = async () => {
  // TODO: 打开添加策略对话框
  ElMessage.info('添加策略功能开发中...')
}

// 删除策略
const handleDeleteStrategy = async (strategyId: number) => {
  try {
    await deleteStrategy({ strategy_id: strategyId })
    ElMessage.success('策略已删除')
    await fetchStrategies()
  } catch (error: any) {
    ElMessage.error('删除策略失败: ' + (error.message || ''))
  }
}

// 执行策略
const handleExecuteStrategy = async (strategy: any) => {
  try {
    await executeStrategy({
      strategy_id: strategy.id,
      executed_price: stockInfo.value.current_price,
      executed_quantity: parseFloat(strategy.quantity) || 0
    })
    ElMessage.success('策略已标记为执行')
    await fetchStrategies()
  } catch (error: any) {
    ElMessage.error('执行策略失败: ' + (error.message || ''))
  }
}

onMounted(async () => {
  loading.value = true
  try {
    await Promise.all([
      fetchStockDetail(),
      fetchHoldings(),
      fetchEvents(),
      fetchStrategies()
    ])
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="min-h-screen bg-gray-50">
    <!-- 顶部导航栏 -->
    <nav class="bg-white border-b border-gray-200 sticky top-0 z-50">
      <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between h-16">
          <div class="flex items-center space-x-4">
            <a @click="goBack" class="text-gray-600 hover:text-gray-900 cursor-pointer">← 返回</a>
            <div>
              <h1 class="text-xl font-bold">{{ stockInfo.symbol }} {{ stockInfo.name }}</h1>
              <p class="text-xs text-gray-500">{{ stockInfo.market }} / {{ stockInfo.industry }} / {{ stockInfo.sector }}</p>
            </div>
          </div>
          <div class="flex items-center space-x-2">
            <button
              @click="analyzeStock"
              class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm"
            >
              🤖 AI分析
            </button>
            <button
              @click="addToWatchlist"
              class="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 text-sm"
            >
              ➕ 添加
            </button>
            <button class="p-2 hover:bg-gray-100 rounded-lg">⋮</button>
          </div>
        </div>
      </div>
    </nav>

    <!-- 主内容 -->
    <main class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-6">

      <!-- 基本信息卡片 -->
      <div class="bg-white rounded-lg shadow-md p-6 mb-6">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <!-- 实时价格 -->
          <div>
            <div class="text-4xl font-bold text-gray-900 mb-2">¥{{ stockInfo.current_price.toFixed(2) }}</div>
            <div class="text-xl font-semibold mb-1" :class="priceClass">
              {{ stockInfo.change_amount >= 0 ? '+' : '' }}{{ stockInfo.change_amount.toFixed(2) }}
              ({{ stockInfo.change_amount >= 0 ? '+' : '' }}{{ stockInfo.change_rate.toFixed(2) }}%)
              {{ stockInfo.change_rate >= 0 ? '📈' : '📉' }}
            </div>
            <div class="text-sm text-gray-500">实时更新 {{ stockInfo.update_time }}</div>
          </div>

          <!-- 交易数据 -->
          <div class="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span class="text-gray-600">今开:</span>
              <span class="font-semibold ml-2">¥{{ stockInfo.open.toFixed(2) }}</span>
            </div>
            <div>
              <span class="text-gray-600">最高:</span>
              <span class="font-semibold ml-2">¥{{ stockInfo.high.toFixed(2) }}</span>
            </div>
            <div>
              <span class="text-gray-600">最低:</span>
              <span class="font-semibold ml-2">¥{{ stockInfo.low.toFixed(2) }}</span>
            </div>
            <div>
              <span class="text-gray-600">昨收:</span>
              <span class="font-semibold ml-2">¥{{ stockInfo.prev_close.toFixed(2) }}</span>
            </div>
            <div>
              <span class="text-gray-600">成交量:</span>
              <span class="font-semibold ml-2">{{ stockInfo.volume }}M</span>
            </div>
            <div>
              <span class="text-gray-600">成交额:</span>
              <span class="font-semibold ml-2">¥{{ stockInfo.turnover }}M</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Tabs 导航 -->
      <div class="bg-white rounded-lg shadow-md mb-6">
        <div class="border-b border-gray-200">
          <div class="flex space-x-8 px-6">
            <button
              @click="activeTab = 'chart'"
              :class="[
                'py-4 text-sm font-medium transition',
                activeTab === 'chart'
                  ? 'border-b-2 border-blue-500 text-blue-500'
                  : 'text-gray-500 hover:text-blue-600'
              ]"
            >
              走势图
            </button>
            <button
              @click="activeTab = 'events'"
              :class="[
                'py-4 text-sm font-medium transition',
                activeTab === 'events'
                  ? 'border-b-2 border-blue-500 text-blue-500'
                  : 'text-gray-500 hover:text-blue-600'
              ]"
            >
              事件时间线
            </button>
            <button
              @click="activeTab = 'position'"
              :class="[
                'py-4 text-sm font-medium transition',
                activeTab === 'position'
                  ? 'border-b-2 border-blue-500 text-blue-500'
                  : 'text-gray-500 hover:text-blue-600'
              ]"
            >
              我的持仓
            </button>
            <button
              @click="activeTab = 'ai'"
              :class="[
                'py-4 text-sm font-medium transition',
                activeTab === 'ai'
                  ? 'border-b-2 border-blue-500 text-blue-500'
                  : 'text-gray-500 hover:text-blue-600'
              ]"
            >
              AI分析
            </button>
            <button
              @click="activeTab = 'review'"
              :class="[
                'py-4 text-sm font-medium transition',
                activeTab === 'review'
                  ? 'border-b-2 border-blue-500 text-blue-500'
                  : 'text-gray-500 hover:text-blue-600'
              ]"
            >
              ⭐ 我的评价
            </button>
            <button
              @click="activeTab = 'company'"
              :class="[
                'py-4 text-sm font-medium transition',
                activeTab === 'company'
                  ? 'border-b-2 border-blue-500 text-blue-500'
                  : 'text-gray-500 hover:text-blue-600'
              ]"
            >
              公司信息
            </button>
            <button
              @click="activeTab = 'finance'"
              :class="[
                'py-4 text-sm font-medium transition',
                activeTab === 'finance'
                  ? 'border-b-2 border-blue-500 text-blue-500'
                  : 'text-gray-500 hover:text-blue-600'
              ]"
            >
              财务数据
            </button>
          </div>
        </div>

        <!-- Tab 内容区域 -->
        <div class="p-6">

          <!-- 走势图 Tab -->
          <div v-show="activeTab === 'chart'">
            <div class="bg-gray-100 rounded-lg p-8 text-center">
              <div class="text-6xl mb-4">📈</div>
              <h3 class="text-xl font-semibold text-gray-900 mb-2">K线图</h3>
              <p class="text-gray-600 mb-4">展示股票价格走势、技术指标</p>
              <p class="text-sm text-gray-500">建议集成: TradingView 或 ECharts</p>
            </div>
          </div>

          <!-- 事件时间线 Tab -->
          <div v-show="activeTab === 'events'">
            <div class="flex items-center justify-between mb-6">
              <h3 class="text-lg font-semibold">📅 近90天相关事件 <span class="text-blue-600">({{ events.length }}条)</span></h3>
              <div class="flex gap-2">
                <select class="px-3 py-2 border border-gray-300 rounded-lg text-sm">
                  <option>筛选: 全部</option>
                  <option>政策事件</option>
                  <option>公司事件</option>
                  <option>市场事件</option>
                  <option>行业事件</option>
                </select>
                <select class="px-3 py-2 border border-gray-300 rounded-lg text-sm">
                  <option>重要性: 全部</option>
                  <option>Critical</option>
                  <option>High</option>
                  <option>Medium</option>
                  <option>Low</option>
                </select>
              </div>
            </div>

            <!-- 事件列表 -->
            <div class="space-y-6">
              <div
                v-for="(event, index) in events"
                :key="event.id"
                class="relative pl-12"
              >
                <!-- 时间线圆点 -->
                <div
                  class="absolute left-3 top-3 w-5 h-5 rounded-full border-3 border-white shadow"
                  :class="getDotColor(event.color)"
                ></div>

                <!-- 时间线 -->
                <div
                  v-if="index < events.length - 1"
                  class="absolute left-5 top-8 bottom-0 w-0.5 bg-gray-200"
                ></div>

                <!-- 事件卡片 -->
                <div
                  class="border rounded-lg p-5 hover:shadow-md transition-all cursor-pointer"
                  :class="getEventBgClass(event.color)"
                >
                  <div class="flex items-start justify-between mb-3">
                    <div class="flex items-center gap-2">
                      <span
                        class="inline-block px-2 py-1 text-white text-xs font-semibold rounded"
                        :class="event.importance === 'High' ? 'bg-orange-500' : event.importance === 'Medium' ? 'bg-yellow-400 text-gray-900' : 'bg-gray-500'"
                      >
                        {{ event.importance }}
                      </span>
                      <span class="text-sm font-semibold text-gray-900">{{ event.date }}</span>
                      <span class="text-sm text-gray-600">{{ event.type }}</span>
                    </div>
                  </div>

                  <h4 class="font-semibold text-gray-900 mb-2">{{ event.title }}</h4>

                  <!-- AI分析 -->
                  <div class="bg-white rounded-lg p-4 mt-3">
                    <p class="text-sm font-semibold text-gray-900 mb-3">🤖 AI影响分析:</p>
                    <div class="space-y-2 text-sm">
                      <div class="flex items-center">
                        <span class="text-gray-600 w-24">影响:</span>
                        <span
                          class="font-semibold"
                          :class="event.ai_analysis.impact === '利好' ? 'text-green-600' : 'text-red-600'"
                        >
                          {{ event.ai_analysis.impact }} ({{ event.ai_analysis.score }}/100)
                        </span>
                      </div>
                      <div v-if="event.ai_analysis.stock_change" class="flex items-center">
                        <span class="text-gray-600 w-24">股价影响:</span>
                        <span class="font-semibold">{{ event.ai_analysis.stock_change }}</span>
                      </div>
                      <div v-if="event.ai_analysis.expected_change" class="flex items-center">
                        <span class="text-gray-600 w-24">预期股价:</span>
                        <span class="font-semibold">{{ event.ai_analysis.expected_change }}</span>
                      </div>
                      <div v-if="event.ai_analysis.confidence" class="flex items-center">
                        <span class="text-gray-600 w-24">置信度:</span>
                        <span>{{ event.ai_analysis.confidence }}</span>
                      </div>
                      <div v-if="event.ai_analysis.factors" class="flex items-start">
                        <span class="text-gray-600 w-24">关键因素:</span>
                        <span>{{ event.ai_analysis.factors }}</span>
                      </div>
                      <div v-if="event.ai_analysis.suggestion" class="flex items-start">
                        <span class="text-gray-600 w-24">建议:</span>
                        <span class="text-blue-600 font-medium">{{ event.ai_analysis.suggestion }}</span>
                      </div>
                    </div>
                  </div>

                  <div class="flex gap-2 mt-4">
                    <button class="text-sm text-blue-600 hover:underline">查看完整分析 →</button>
                    <button v-if="event.ai_analysis.stock_change" class="text-sm text-blue-600 hover:underline">关联我的持仓 →</button>
                  </div>
                </div>
              </div>
            </div>

            <button class="mt-6 w-full py-3 border-2 border-dashed border-gray-300 rounded-lg text-gray-600 hover:border-blue-500 hover:text-blue-600 transition-all">
              显示更多事件...
            </button>
          </div>

          <!-- 我的持仓 Tab -->
          <div v-show="activeTab === 'position'">
            <h3 class="text-lg font-semibold mb-4">我的持仓详情</h3>

            <!-- 持仓概况 -->
            <div v-if="positionInfo" class="bg-gray-50 rounded-lg p-6 mb-6">
              <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                <div>
                  <p class="text-sm text-gray-600 mb-1">持仓数量</p>
                  <p class="text-2xl font-bold">{{ positionInfo.quantity }}股</p>
                </div>
                <div>
                  <p class="text-sm text-gray-600 mb-1">成本价格</p>
                  <p class="text-2xl font-bold">¥{{ (positionInfo.avg_cost || 0).toFixed(2) }}</p>
                </div>
                <div>
                  <p class="text-sm text-gray-600 mb-1">当前价格</p>
                  <p class="text-2xl font-bold">¥{{ (positionInfo.current_price || 0).toFixed(2) }}</p>
                </div>
                <div>
                  <p class="text-sm text-gray-600 mb-1">持仓市值</p>
                  <p class="text-2xl font-bold">¥{{ (positionInfo.market_value || 0).toLocaleString() }}</p>
                </div>
              </div>

              <!-- 盈亏情况 -->
              <div class="grid grid-cols-2 gap-4 p-4 bg-white rounded-lg">
                <div>
                  <p class="text-sm text-gray-600 mb-1">盈亏金额</p>
                  <p
                    class="text-3xl font-bold"
                    :class="(positionInfo.profit_loss || 0) >= 0 ? 'text-red-500' : 'text-green-500'"
                  >
                    {{ (positionInfo.profit_loss || 0) >= 0 ? '+' : '' }}¥{{ Math.abs(positionInfo.profit_loss || 0).toLocaleString() }}
                  </p>
                </div>
                <div>
                  <p class="text-sm text-gray-600 mb-1">盈亏比例</p>
                  <p
                    class="text-3xl font-bold"
                    :class="(positionInfo.profit_loss_rate || 0) >= 0 ? 'text-red-500' : 'text-green-500'"
                  >
                    {{ (positionInfo.profit_loss_rate || 0) >= 0 ? '+' : '' }}{{ (positionInfo.profit_loss_rate || 0).toFixed(1) }}%
                    {{ (positionInfo.profit_loss_rate || 0) >= 0 ? '📈' : '📉' }}
                  </p>
                </div>
              </div>
            </div>

            <!-- 暂无持仓 -->
            <div v-else class="bg-gray-50 rounded-lg p-6 mb-6 text-center">
              <div class="text-4xl mb-3">📦</div>
              <p class="text-gray-600">暂无该股票的持仓记录</p>
            </div>

            <!-- 个股操作策略 -->
            <div class="bg-white border-2 border-blue-200 rounded-lg p-6 mb-6">
              <div class="flex items-center justify-between mb-4">
                <div>
                  <h4 class="font-bold text-lg">📋 个股操作策略</h4>
                  <p class="text-sm text-gray-600 mt-1">买入卖出计划和执行记录</p>
                </div>
                <div class="flex items-center gap-2">
                  <span class="text-xs px-2 py-1 bg-red-50 text-red-700 rounded">待执行 {{ pendingStrategiesCount }}</span>
                  <span class="text-xs px-2 py-1 bg-gray-100 text-gray-700 rounded">已完成 {{ completedStrategiesCount }}</span>
                </div>
              </div>

              <!-- 策略列表 -->
              <div v-if="strategies.length > 0" class="space-y-3">
                <div
                  v-for="strategy in strategies"
                  :key="strategy.id"
                  class="border-2 rounded-lg p-4"
                  :class="{
                    'bg-orange-50 border-orange-200': strategy.type === 'sell' && !strategy.isStopLoss && !strategy.isTarget,
                    'bg-blue-50 border-blue-200': strategy.type === 'buy',
                    'bg-red-50 border-red-300': strategy.isStopLoss,
                    'bg-green-50 border-green-200': strategy.isTarget
                  }"
                >
                  <div class="flex items-start justify-between mb-3">
                    <div class="flex items-center gap-2">
                      <span
                        class="px-3 py-1 text-white text-xs font-bold rounded"
                        :class="strategy.type === 'buy' ? 'bg-green-500' : 'bg-red-500'"
                      >
                        {{ strategy.type === 'buy' ? '买入' : '卖出' }}
                      </span>
                      <h5
                        class="font-bold"
                        :class="{
                          'text-orange-800': strategy.type === 'sell' && !strategy.isStopLoss && !strategy.isTarget,
                          'text-blue-800': strategy.type === 'buy',
                          'text-red-800': strategy.isStopLoss,
                          'text-green-800': strategy.isTarget
                        }"
                      >
                        {{ strategy.name }}
                      </h5>
                    </div>
                    <span
                      class="px-2 py-1 text-xs font-semibold rounded"
                      :class="{
                        'bg-orange-100 text-orange-700': strategy.type === 'sell' && !strategy.isStopLoss && !strategy.isTarget && strategy.status === 'pending',
                        'bg-blue-100 text-blue-700': strategy.type === 'buy' && strategy.status === 'pending',
                        'bg-red-100 text-red-700': strategy.isStopLoss && strategy.status === 'pending',
                        'bg-green-100 text-green-700': strategy.isTarget && strategy.status === 'pending',
                        'bg-gray-100 text-gray-700': strategy.status === 'completed'
                      }"
                    >
                      {{ strategy.status === 'pending' ? '待执行' : strategy.status === 'completed' ? '已完成' : '已取消' }}
                    </span>
                  </div>
                  <div class="bg-white rounded p-3 grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
                    <div>
                      <span class="text-gray-600">触发价位:</span>
                      <p
                        class="font-bold"
                        :class="strategy.isStopLoss ? 'text-red-600' : ''"
                      >
                        {{ strategy.price }}
                      </p>
                    </div>
                    <div>
                      <span class="text-gray-600">操作数量:</span>
                      <p
                        class="font-bold"
                        :class="{
                          'text-green-600': strategy.type === 'buy',
                          'text-red-600': strategy.type === 'sell'
                        }"
                      >
                        {{ strategy.quantity }}
                      </p>
                    </div>
                    <div class="col-span-2">
                      <span class="text-gray-600">策略理由:</span>
                      <p class="text-gray-700">{{ strategy.reason }}</p>
                    </div>
                  </div>
                </div>
              </div>

              <!-- 空状态 -->
              <div v-else class="text-center py-8">
                <div class="text-4xl mb-3">📝</div>
                <p class="text-gray-600 mb-4">暂无操作策略</p>
                <p class="text-sm text-gray-500">根据AI分析和自己的判断，制定买入卖出计划</p>
              </div>

              <button
                @click="handleAddStrategy"
                class="mt-4 w-full py-2 border-2 border-dashed border-blue-300 rounded-lg text-blue-600 hover:bg-blue-50 transition-all"
              >
                + 添加新策略
              </button>
            </div>

            <!-- 交易历史 -->
            <div class="bg-gray-50 rounded-lg p-6">
              <h4 class="font-semibold mb-3">📊 交易历史</h4>
              <p class="text-gray-600 text-center py-8">暂无交易记录</p>
            </div>
          </div>

          <!-- AI分析 Tab -->
          <div v-show="activeTab === 'ai'">
            <div class="bg-gray-100 rounded-lg p-8 text-center">
              <div class="text-6xl mb-4">🤖</div>
              <h3 class="text-xl font-semibold text-gray-900 mb-2">AI 深度分析</h3>
              <p class="text-gray-600 mb-4">包含基本面、技术面、资金面分析和投资建议</p>
              <button
                @click="analyzeStock"
                class="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                生成 AI 分析报告
              </button>
            </div>
          </div>

          <!-- 我的评价 Tab -->
          <div v-show="activeTab === 'review'">
            <StockReview :symbol="symbol" :stock-name="stockInfo.name" />
          </div>

          <!-- 公司信息 Tab -->
          <div v-show="activeTab === 'company'">
            <div class="bg-white rounded-lg p-6">
              <h3 class="text-lg font-semibold mb-4">公司简介</h3>
              <p class="text-gray-600 mb-6">
                青岛啤酒股份有限公司是国内最大的啤酒生产企业之一，成立于1903年。
                公司主营业务为啤酒的生产与销售，主要产品有青岛啤酒、崂山啤酒等多个品牌。
              </p>

              <h3 class="text-lg font-semibold mb-4">基本资料</h3>
              <div class="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span class="text-gray-600">股票代码:</span>
                  <span class="ml-2 font-semibold">{{ stockInfo.symbol }}</span>
                </div>
                <div>
                  <span class="text-gray-600">所属行业:</span>
                  <span class="ml-2 font-semibold">{{ stockInfo.industry }}</span>
                </div>
                <div>
                  <span class="text-gray-600">上市时间:</span>
                  <span class="ml-2 font-semibold">1993-08-27</span>
                </div>
                <div>
                  <span class="text-gray-600">注册地:</span>
                  <span class="ml-2 font-semibold">山东青岛</span>
                </div>
              </div>
            </div>
          </div>

          <!-- 财务数据 Tab -->
          <div v-show="activeTab === 'finance'">
            <div class="bg-white rounded-lg p-6">
              <h3 class="text-lg font-semibold mb-4">财务指标</h3>
              <div class="grid grid-cols-3 gap-6 mb-6">
                <div class="text-center">
                  <div class="text-sm text-gray-500">市盈率 (PE)</div>
                  <div class="mt-2 text-2xl font-bold">25.6</div>
                </div>
                <div class="text-center">
                  <div class="text-sm text-gray-500">市净率 (PB)</div>
                  <div class="mt-2 text-2xl font-bold">3.8</div>
                </div>
                <div class="text-center">
                  <div class="text-sm text-gray-500">股息率 (%)</div>
                  <div class="mt-2 text-2xl font-bold">2.1</div>
                </div>
              </div>

              <h3 class="text-lg font-semibold mb-4">财报数据</h3>
              <p class="text-gray-600 text-center py-8">详细财报数据开发中...</p>
            </div>
          </div>

        </div>
      </div>

    </main>
  </div>
</template>

<style scoped>
/* 可以添加一些自定义样式 */
</style>
