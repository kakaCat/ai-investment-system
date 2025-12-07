<script setup lang="ts">
import { ref, computed } from 'vue'
import { ElMessage, ElProgress } from 'element-plus'

interface Stock {
  symbol: string
  name: string
  market: string
  type: 'holding' | 'watchlist'
  selected: boolean
  currentPrice: number
  changeRate: number
  emoji?: string
}

interface AnalysisResult {
  symbol: string
  name: string
  aiScore: number
  fundamentalScore: number
  technicalScore: number
  valuationScore: number
  suggestion: string
  strategy: {
    targetPrice: string
    positionSize: string
    riskControl: string
  }
  status: 'analyzing' | 'completed' | 'error'
}

// 股票列表
const stocks = ref<Stock[]>([
  { symbol: '600600', name: '青岛啤酒', market: 'A股', type: 'holding', selected: true, currentPrice: 62.5, changeRate: -4.87, emoji: '🍺' },
  { symbol: '002594', name: '比亚迪', market: 'A股', type: 'holding', selected: true, currentPrice: 248.2, changeRate: 2.3, emoji: '🚗' },
  { symbol: '00700', name: '腾讯控股', market: '港股', type: 'holding', selected: true, currentPrice: 382.4, changeRate: -1.2, emoji: '🎮' },
  { symbol: '300750', name: '宁德时代', market: 'A股', type: 'holding', selected: false, currentPrice: 185.6, changeRate: 1.8, emoji: '🔋' },
  { symbol: '601398', name: '工商银行', market: 'A股', type: 'watchlist', selected: false, currentPrice: 5.82, changeRate: 0.5, emoji: '🏦' },
  { symbol: 'AAPL', name: 'Apple', market: '美股', type: 'watchlist', selected: false, currentPrice: 178.5, changeRate: -0.8, emoji: '🍎' },
  { symbol: '600519', name: '贵州茅台', market: 'A股', type: 'watchlist', selected: false, currentPrice: 1678.8, changeRate: 1.2, emoji: '🍶' }
])

// 分析状态
const analysisStatus = ref<'idle' | 'analyzing' | 'completed'>('idle')
const analysisProgress = ref(0)
const currentAnalyzingStock = ref<string | null>(null)

// 分析结果
const analysisResults = ref<AnalysisResult[]>([])

// 计算属性
const selectedStocks = computed(() => stocks.value.filter(s => s.selected))
const selectedCount = computed(() => selectedStocks.value.length)
const estimatedTokens = computed(() => selectedCount.value * 2500) // 每只股票约2500 tokens
const estimatedCost = computed(() => (estimatedTokens.value * 0.00014).toFixed(2)) // ¥0.14/1k tokens

const holdingStocks = computed(() => stocks.value.filter(s => s.type === 'holding'))
const watchlistStocks = computed(() => stocks.value.filter(s => s.type === 'watchlist'))

// 快捷选择
const selectAll = () => {
  stocks.value.forEach(s => s.selected = true)
  ElMessage.success('已选择全部股票')
}

const selectNone = () => {
  stocks.value.forEach(s => s.selected = false)
  ElMessage.info('已取消全部选择')
}

const selectHoldingsOnly = () => {
  stocks.value.forEach(s => s.selected = s.type === 'holding')
  ElMessage.success('已选择持仓股票')
}

const selectWatchlistOnly = () => {
  stocks.value.forEach(s => s.selected = s.type === 'watchlist')
  ElMessage.success('已选择关注股票')
}

// 切换选择状态
const toggleStock = (symbol: string) => {
  const stock = stocks.value.find(s => s.symbol === symbol)
  if (stock) {
    stock.selected = !stock.selected
  }
}

// 开始分析
const startAnalysis = async () => {
  if (selectedCount.value === 0) {
    ElMessage.warning('请至少选择一只股票')
    return
  }

  analysisStatus.value = 'analyzing'
  analysisProgress.value = 0
  analysisResults.value = []

  // 模拟分析过程
  for (let i = 0; i < selectedStocks.value.length; i++) {
    const stock = selectedStocks.value[i]
    currentAnalyzingStock.value = `${stock.name} (${stock.symbol})`

    // 模拟分析延迟
    await new Promise(resolve => setTimeout(resolve, 2000))

    // 生成模拟结果
    const result: AnalysisResult = {
      symbol: stock.symbol,
      name: stock.name,
      aiScore: Math.random() * 3 + 7, // 7-10分
      fundamentalScore: Math.random() * 3 + 7,
      technicalScore: Math.random() * 3 + 7,
      valuationScore: Math.random() * 3 + 7,
      suggestion: Math.random() > 0.5 ? '建议持有' : '建议加仓',
      strategy: {
        targetPrice: `¥${(stock.currentPrice * (1 + Math.random() * 0.2)).toFixed(2)}`,
        positionSize: `建议增持至组合${(Math.random() * 5 + 8).toFixed(1)}%`,
        riskControl: `止损位: ¥${(stock.currentPrice * 0.85).toFixed(2)}`
      },
      status: 'completed'
    }

    analysisResults.value.push(result)
    analysisProgress.value = ((i + 1) / selectedStocks.value.length) * 100
  }

  analysisStatus.value = 'completed'
  currentAnalyzingStock.value = null
  ElMessage.success('分析完成！')
}

// 获取评分颜色
const getScoreColor = (score: number) => {
  if (score >= 8.5) return 'text-green-600'
  if (score >= 7.5) return 'text-yellow-600'
  return 'text-red-600'
}

// 获取评分背景色
const getScoreBgColor = (score: number) => {
  if (score >= 8.5) return 'from-green-50 to-white'
  if (score >= 7.5) return 'from-yellow-50 to-white'
  return 'from-red-50 to-white'
}
</script>

<template>
  <div class="daily-ai-analysis">
    <!-- 头部 -->
    <div class="mb-6">
      <h2 class="text-2xl font-bold text-gray-900 mb-2">🤖 每日AI分析</h2>
      <p class="text-gray-600">选择股票进行AI分析，获取投资建议和操作策略</p>
    </div>

    <!-- 股票选择区 -->
    <div v-if="analysisStatus === 'idle'" class="bg-white rounded-lg shadow-md p-6 mb-6">
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-lg font-semibold">📋 选择分析股票</h3>
        <div class="flex gap-2">
          <button @click="selectAll" class="px-3 py-1 text-xs bg-blue-600 text-white rounded hover:bg-blue-700">
            全选
          </button>
          <button @click="selectHoldingsOnly" class="px-3 py-1 text-xs bg-green-600 text-white rounded hover:bg-green-700">
            仅持仓
          </button>
          <button @click="selectWatchlistOnly" class="px-3 py-1 text-xs bg-yellow-600 text-white rounded hover:bg-yellow-700">
            仅关注
          </button>
          <button @click="selectNone" class="px-3 py-1 text-xs bg-gray-600 text-white rounded hover:bg-gray-700">
            清空
          </button>
        </div>
      </div>

      <!-- 持仓股票 -->
      <div class="mb-6">
        <h4 class="text-sm font-semibold text-gray-700 mb-3">💼 我的持仓 ({{ holdingStocks.length }})</h4>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          <div
            v-for="stock in holdingStocks"
            :key="stock.symbol"
            @click="toggleStock(stock.symbol)"
            class="bg-white rounded-lg border-2 p-3 cursor-pointer transition-all hover:shadow-md"
            :class="stock.selected ? 'border-blue-500 bg-blue-50' : 'border-gray-200'"
          >
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 bg-gradient-to-br from-blue-400 to-blue-600 rounded-lg flex items-center justify-center text-2xl">
                  {{ stock.emoji }}
                </div>
                <div>
                  <div class="font-semibold text-gray-900">{{ stock.name }}</div>
                  <div class="text-xs text-gray-500">{{ stock.symbol }} · {{ stock.market }}</div>
                </div>
              </div>
              <input type="checkbox" :checked="stock.selected" class="w-5 h-5" />
            </div>
          </div>
        </div>
      </div>

      <!-- 关注股票 -->
      <div>
        <h4 class="text-sm font-semibold text-gray-700 mb-3">👁️ 我的关注 ({{ watchlistStocks.length }})</h4>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          <div
            v-for="stock in watchlistStocks"
            :key="stock.symbol"
            @click="toggleStock(stock.symbol)"
            class="bg-white rounded-lg border-2 p-3 cursor-pointer transition-all hover:shadow-md"
            :class="stock.selected ? 'border-blue-500 bg-blue-50' : 'border-gray-200'"
          >
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 bg-gradient-to-br from-gray-300 to-gray-500 rounded-lg flex items-center justify-center text-2xl">
                  {{ stock.emoji }}
                </div>
                <div>
                  <div class="font-semibold text-gray-900">{{ stock.name }}</div>
                  <div class="text-xs text-gray-500">{{ stock.symbol }} · {{ stock.market }}</div>
                </div>
              </div>
              <input type="checkbox" :checked="stock.selected" class="w-5 h-5" />
            </div>
          </div>
        </div>
      </div>

      <!-- 底部操作栏 -->
      <div class="mt-6 pt-6 border-t border-gray-200 flex items-center justify-between">
        <div class="text-sm text-gray-600">
          <span class="font-semibold text-gray-900">已选择: {{ selectedCount }} 只股票</span>
          <span class="ml-4">预计消耗: {{ estimatedTokens.toLocaleString() }} tokens</span>
          <span class="ml-4">预计费用: ¥{{ estimatedCost }}</span>
        </div>
        <button
          @click="startAnalysis"
          :disabled="selectedCount === 0"
          class="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed font-semibold transition-colors"
        >
          🚀 开始分析
        </button>
      </div>
    </div>

    <!-- 分析进度 -->
    <div v-if="analysisStatus === 'analyzing'" class="bg-white rounded-lg shadow-md p-8 mb-6">
      <div class="text-center mb-6">
        <div class="text-4xl mb-4 animate-bounce">🤖</div>
        <h3 class="text-xl font-semibold text-gray-900 mb-2">AI分析进行中...</h3>
        <p class="text-gray-600">{{ currentAnalyzingStock }}</p>
      </div>
      <el-progress
        :percentage="analysisProgress"
        :stroke-width="20"
        :text-inside="true"
        class="mb-4"
      />
      <div class="text-center text-sm text-gray-500">
        已完成 {{ analysisResults.length }} / {{ selectedCount }} 只股票
      </div>
    </div>

    <!-- 分析结果 -->
    <div v-if="analysisStatus === 'completed'">
      <!-- 重新分析按钮 -->
      <div class="mb-4 flex justify-end">
        <button
          @click="analysisStatus = 'idle'"
          class="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 text-sm"
        >
          ← 重新选择股票
        </button>
      </div>

      <!-- 结果卡片 -->
      <div class="space-y-6">
        <div
          v-for="result in analysisResults"
          :key="result.symbol"
          class="bg-white rounded-lg shadow-md overflow-hidden"
        >
          <div class="bg-gradient-to-r p-6" :class="getScoreBgColor(result.aiScore)">
            <div class="flex items-start justify-between">
              <div>
                <h3 class="text-xl font-bold text-gray-900 mb-1">{{ result.name }}</h3>
                <p class="text-sm text-gray-600">{{ result.symbol }}</p>
              </div>
              <div class="text-right">
                <div class="text-3xl font-bold mb-1" :class="getScoreColor(result.aiScore)">
                  {{ result.aiScore.toFixed(1) }}<span class="text-lg text-gray-400">/10</span>
                </div>
                <div class="text-sm text-gray-600">AI综合评分</div>
              </div>
            </div>
          </div>

          <div class="p-6">
            <!-- 三大维度评分 -->
            <div class="grid grid-cols-3 gap-4 mb-6">
              <div class="text-center p-3 bg-blue-50 rounded-lg">
                <div class="text-sm text-gray-600 mb-1">基本面</div>
                <div class="text-2xl font-bold text-blue-600">{{ result.fundamentalScore.toFixed(1) }}</div>
              </div>
              <div class="text-center p-3 bg-green-50 rounded-lg">
                <div class="text-sm text-gray-600 mb-1">技术面</div>
                <div class="text-2xl font-bold text-green-600">{{ result.technicalScore.toFixed(1) }}</div>
              </div>
              <div class="text-center p-3 bg-yellow-50 rounded-lg">
                <div class="text-sm text-gray-600 mb-1">估值</div>
                <div class="text-2xl font-bold text-yellow-600">{{ result.valuationScore.toFixed(1) }}</div>
              </div>
            </div>

            <!-- 操作策略 -->
            <div class="p-4 bg-gray-50 rounded-lg mb-4">
              <div class="text-sm font-semibold text-gray-900 mb-3">📋 建议操作策略:</div>
              <div class="space-y-2 text-sm">
                <div class="flex items-start">
                  <span class="text-gray-600 w-24 flex-shrink-0">🎯 目标价位:</span>
                  <span class="font-semibold">{{ result.strategy.targetPrice }}</span>
                </div>
                <div class="flex items-start">
                  <span class="text-gray-600 w-24 flex-shrink-0">💰 仓位配置:</span>
                  <span class="font-semibold">{{ result.strategy.positionSize }}</span>
                </div>
                <div class="flex items-start">
                  <span class="text-gray-600 w-24 flex-shrink-0">🛡️ 风险控制:</span>
                  <span class="font-semibold">{{ result.strategy.riskControl }}</span>
                </div>
              </div>
            </div>

            <!-- 操作建议 -->
            <div class="flex items-center justify-between">
              <div class="text-sm">
                <span class="text-gray-600">AI建议: </span>
                <span class="font-semibold text-blue-600">{{ result.suggestion }}</span>
              </div>
              <button class="text-sm text-blue-600 hover:underline">
                查看完整分析 →
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.daily-ai-analysis {
  /* 自定义样式 */
}
</style>
