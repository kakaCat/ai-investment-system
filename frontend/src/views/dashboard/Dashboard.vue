<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import AIActionList from '@/components/AIActionList.vue'
import DailyAIAnalysis from '@/components/DailyAIAnalysis.vue'
import { getAccounts, getHoldings, getAISuggestions, getEvents } from '@/api/dashboard'

const router = useRouter()

interface Account {
  account_id: string
  account_name: string
  total_value: number
}

interface AIAction {
  priority: 'urgent' | 'today' | 'week'
  stock: {
    symbol: string
    name: string
  }
  action: 'buy' | 'sell' | 'hold' | 'watch'
  current_price: number
  holding?: {
    quantity: number
    profit_loss_rate: number
  }
  reason: string
  suggestion: string
  target_price?: number
  confidence: number
}

interface Holding {
  symbol: string
  name: string
  quantity: number
  cost_price: number
  current_price: number
  profit_loss: number
  profit_loss_rate: number
  market_value: number
}

interface Event {
  id: string
  title: string
  level: 'critical' | 'high' | 'medium'
  impact: string
  date: string
}

interface StockTrend {
  symbol: string
  name: string
  change_rate: number
  current_price: number
  is_holding: boolean
}

const loading = ref(false)
const accounts = ref<Account[]>([])
const aiActions = ref<AIAction[]>([])
const holdings = ref<Holding[]>([])
const events = ref<Event[]>([])
const topGainers = ref<StockTrend[]>([])
const topLosers = ref<StockTrend[]>([])

// 总览统计 - 基于真实账户和持仓数据计算
const totalStats = computed(() => {
  // 计算总资产 = 所有账户当前资产之和
  const totalValue = accounts.value.reduce((sum, acc) => sum + (acc.total_value || 0), 0)

  // 计算已投资金额 = 所有持仓市值之和
  const investedValue = holdings.value.reduce((sum, h) => sum + (h.market_value || 0), 0)

  // 可用现金 = 总资产 - 已投资金额
  const availableCash = totalValue - investedValue

  // 今日盈亏 = 所有持仓盈亏之和 (这里简化计算,实际应从账户获取)
  const todayProfitLoss = holdings.value.reduce((sum, h) => sum + (h.profit_loss || 0), 0)

  return {
    totalValue,
    todayProfitLoss,
    todayProfitLossRate: totalValue > 0 ? (todayProfitLoss / totalValue) * 100 : 0,
    availableCash,
    investedValue
  }
})

// 获取仪表盘数据
const fetchDashboardData = async () => {
  loading.value = true
  try {
    // 并行调用多个API接口
    const [accountsRes, holdingsRes, suggestionsRes, eventsRes] = await Promise.all([
      // 获取账户列表
      getAccounts({ page: 1, page_size: 100, status: 'active' }),
      // 获取持仓列表
      getHoldings({ page: 1, page_size: 100 }),
      // 获取 AI 建议
      getAISuggestions({ page: 1, page_size: 10 }),
      // 获取重要事件
      getEvents({ level: 'critical,high', page: 1, page_size: 10 })
    ])

    // 处理账户数据
    if (accountsRes.data?.items) {
      accounts.value = accountsRes.data.items.map((acc: any) => ({
        account_id: acc.account_id,
        account_name: acc.account_name || acc.broker,
        total_value: acc.total_value || 0
      }))
    }

    // 处理持仓数据
    if (holdingsRes.data?.items) {
      holdings.value = holdingsRes.data.items.map((h: any) => ({
        symbol: h.symbol,
        name: h.stock_name,
        quantity: h.quantity,
        cost_price: h.cost_price,
        current_price: h.current_price,
        profit_loss: h.profit_loss,
        profit_loss_rate: h.profit_loss_rate,
        market_value: h.market_value
      }))
    }

    // 处理 AI 建议数据
    if (suggestionsRes.data?.items) {
      aiActions.value = suggestionsRes.data.items.map((s: any) => ({
        priority: s.priority || 'today',
        stock: { symbol: s.symbol, name: s.stock_name },
        action: s.action,
        current_price: s.current_price,
        holding: s.holding_info ? {
          quantity: s.holding_info.quantity,
          profit_loss_rate: s.holding_info.profit_loss_rate
        } : undefined,
        reason: s.reason,
        suggestion: s.suggestion,
        target_price: s.target_price,
        confidence: s.confidence
      }))
    }

    // 处理事件数据
    if (eventsRes.data?.items) {
      events.value = eventsRes.data.items.map((e: any) => ({
        id: e.event_id,
        title: e.title,
        level: e.level,
        impact: e.impact_description || e.impact_summary,
        date: e.event_date || e.created_at
      }))
    }

    // 计算涨跌榜（基于持仓数据）
    const sortedByGain = [...holdings.value].sort((a, b) => b.profit_loss_rate - a.profit_loss_rate)
    topGainers.value = sortedByGain.slice(0, 3).map(h => ({
      symbol: h.symbol,
      name: h.name,
      change_rate: h.profit_loss_rate,
      current_price: h.current_price,
      is_holding: true
    }))

    topLosers.value = sortedByGain.slice(-3).reverse().map(h => ({
      symbol: h.symbol,
      name: h.name,
      change_rate: h.profit_loss_rate,
      current_price: h.current_price,
      is_holding: true
    }))

  } catch (error: any) {
    console.error('获取仪表盘数据失败:', error)
    ElMessage.error(error.message || '获取仪表盘数据失败')
  } finally {
    loading.value = false
  }
}

// 查看账户详情
const viewAccount = (accountId: string) => {
  router.push(`/account/detail/${accountId}`)
}

// 查看股票详情
const viewStock = (symbol: string) => {
  router.push(`/stocks/detail/${symbol}`)
}

// 查看事件详情
const viewEvent = (eventId: string) => {
  router.push(`/events/detail/${eventId}`)
}

// 快捷操作
const quickActions = [
  { label: '记录交易', icon: '📝', action: () => router.push('/trades/list') },
  { label: '搜索股票', icon: '🔍', action: () => ElMessage.info('搜索功能开发中') },
  { label: '事件日历', icon: '📅', action: () => router.push('/events/list') },
  { label: '策略复盘', icon: '💼', action: () => router.push('/analysis') }
]

// 涨跌颜色类
const profitClass = (value: number) => {
  if (value > 0) return 'text-red-600'
  if (value < 0) return 'text-green-600'
  return 'text-gray-600'
}

// 事件等级样式
const eventLevelConfig = (level: string) => {
  const configs = {
    critical: { icon: '🔴', color: 'text-red-600 bg-red-50 border-red-200' },
    high: { icon: '🟠', color: 'text-orange-600 bg-orange-50 border-orange-200' },
    medium: { icon: '🟡', color: 'text-yellow-600 bg-yellow-50 border-yellow-200' }
  }
  return configs[level as keyof typeof configs] || configs.medium
}

onMounted(() => {
  fetchDashboardData()
})
</script>

<template>
  <div v-loading="loading" class="dashboard p-6">
    <!-- 资产总览（简洁版） -->
    <div class="bg-white rounded-lg border shadow-sm p-6 mb-6">
      <div class="grid grid-cols-4 gap-6">
        <div class="text-center">
          <div class="text-sm text-gray-500 mb-2">总资产</div>
          <div class="text-3xl font-bold text-gray-900">
            ¥{{ totalStats.totalValue.toLocaleString() }}
          </div>
        </div>
        <div class="text-center">
          <div class="text-sm text-gray-500 mb-2">今日盈亏</div>
          <div class="text-3xl font-bold" :class="profitClass(totalStats.todayProfitLoss)">
            {{ totalStats.todayProfitLoss >= 0 ? '+' : '' }}¥{{ totalStats.todayProfitLoss.toLocaleString() }}
          </div>
          <div class="text-sm mt-1" :class="profitClass(totalStats.todayProfitLossRate)">
            {{ totalStats.todayProfitLossRate >= 0 ? '+' : '' }}{{ totalStats.todayProfitLossRate.toFixed(2) }}%
          </div>
        </div>
        <div class="text-center">
          <div class="text-sm text-gray-500 mb-2">可用资金</div>
          <div class="text-2xl font-bold text-gray-900">
            ¥{{ totalStats.availableCash.toLocaleString() }}
          </div>
        </div>
        <div class="text-center">
          <div class="text-sm text-gray-500 mb-2">已投资</div>
          <div class="text-2xl font-bold text-gray-900">
            ¥{{ totalStats.investedValue.toLocaleString() }}
          </div>
        </div>
      </div>
    </div>

    <!-- AI操作建议（核心模块） -->
    <div class="bg-white rounded-lg border shadow-sm p-6 mb-6">
      <div class="flex items-center justify-between mb-4">
        <div class="flex items-center gap-3">
          <span class="text-2xl">🤖</span>
          <h2 class="text-xl font-bold text-gray-900">AI操作建议</h2>
          <span class="text-sm text-gray-500">基于持仓和市场分析的操作指引</span>
        </div>
        <div class="flex gap-2">
          <el-button size="small" @click="fetchDashboardData">刷新建议</el-button>
          <el-button type="primary" size="small" @click="router.push('/analysis')">
            查看完整分析报告
          </el-button>
        </div>
      </div>
      <ai-action-list :actions="aiActions" />
    </div>

    <!-- 每日AI分析模块 (v3.2) -->
    <div class="mb-6">
      <DailyAIAnalysis />
    </div>

    <!-- 持仓状态 -->
    <div class="bg-white rounded-lg border shadow-sm p-6 mb-6">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-lg font-bold text-gray-900">📊 我的持仓</h2>
        <div class="flex gap-2">
          <el-button size="small" @click="router.push('/holdings/list')">查看完整持仓</el-button>
          <el-button type="primary" size="small" @click="router.push('/analysis')">AI持仓分析</el-button>
        </div>
      </div>

      <div class="overflow-hidden border border-gray-200 rounded-lg">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">代码</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">名称</th>
              <th class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">数量</th>
              <th class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">成本价</th>
              <th class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">现价</th>
              <th class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">市值</th>
              <th class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">盈亏</th>
              <th class="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase">状态</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr
              v-for="holding in holdings"
              :key="holding.symbol"
              class="hover:bg-gray-50 cursor-pointer"
              @click="viewStock(holding.symbol)"
            >
              <td class="px-4 py-3 text-sm font-medium text-gray-900">{{ holding.symbol }}</td>
              <td class="px-4 py-3 text-sm text-gray-900">{{ holding.name }}</td>
              <td class="px-4 py-3 text-sm text-right">{{ holding.quantity.toLocaleString() }}</td>
              <td class="px-4 py-3 text-sm text-right text-gray-700">¥{{ holding.cost_price.toFixed(2) }}</td>
              <td class="px-4 py-3 text-sm text-right font-medium">¥{{ holding.current_price.toFixed(2) }}</td>
              <td class="px-4 py-3 text-sm text-right font-semibold">¥{{ holding.market_value.toLocaleString() }}</td>
              <td class="px-4 py-3 text-sm text-right">
                <div :class="profitClass(holding.profit_loss)">
                  <div class="font-semibold">
                    {{ holding.profit_loss >= 0 ? '+' : '' }}¥{{ Math.abs(holding.profit_loss).toLocaleString() }}
                  </div>
                  <div class="text-xs">
                    {{ holding.profit_loss_rate >= 0 ? '+' : '' }}{{ holding.profit_loss_rate.toFixed(2) }}%
                  </div>
                </div>
              </td>
              <td class="px-4 py-3 text-center">
                <span
                  v-if="holding.profit_loss_rate < -15"
                  class="inline-block px-2 py-1 text-xs font-semibold text-red-700 bg-red-100 rounded"
                >
                  🔴 需关注
                </span>
                <span
                  v-else-if="holding.profit_loss_rate < 0"
                  class="inline-block px-2 py-1 text-xs font-semibold text-yellow-700 bg-yellow-100 rounded"
                >
                  🟡 观察
                </span>
                <span
                  v-else
                  class="inline-block px-2 py-1 text-xs font-semibold text-green-700 bg-green-100 rounded"
                >
                  🟢 健康
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 底部：事件提醒 + 涨跌榜 + 账户 + 快捷操作 -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- 左列 -->
      <div class="space-y-6">
        <!-- 事件提醒 -->
        <div class="bg-white rounded-lg border shadow-sm p-6">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-lg font-bold text-gray-900">📢 事件提醒</h2>
            <el-button type="text" size="small" @click="router.push('/events/list')">
              查看全部 →
            </el-button>
          </div>

          <div class="space-y-3">
            <div
              v-for="event in events.slice(0, 3)"
              :key="event.id"
              :class="['border rounded-lg p-3 cursor-pointer hover:shadow-md transition', eventLevelConfig(event.level).color]"
              @click="viewEvent(event.id)"
            >
              <div class="flex items-start gap-2">
                <span class="text-lg">{{ eventLevelConfig(event.level).icon }}</span>
                <div class="flex-1">
                  <div class="font-semibold text-sm mb-1">{{ event.title }}</div>
                  <div class="text-xs text-gray-600">{{ event.impact }}</div>
                  <div class="text-xs text-gray-500 mt-1">{{ event.date }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 账户列表 -->
        <div class="bg-white rounded-lg border shadow-sm p-6">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-lg font-bold text-gray-900">🏦 我的账户</h2>
            <el-button type="text" size="small" @click="router.push('/account/list')">
              管理 →
            </el-button>
          </div>

          <div class="space-y-3">
            <div
              v-for="account in accounts"
              :key="account.account_id"
              class="border border-gray-200 rounded-lg p-3 hover:border-blue-300 hover:bg-blue-50 cursor-pointer transition"
              @click="viewAccount(account.account_id)"
            >
              <div class="font-semibold text-gray-900">{{ account.account_name }}</div>
              <div class="text-sm text-gray-600 mt-1">
                总资产: ¥{{ account.total_value.toLocaleString() }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 右列 -->
      <div class="space-y-6">
        <!-- 涨跌榜（仅持仓+关注） -->
        <div class="bg-white rounded-lg border shadow-sm p-6">
          <h2 class="text-lg font-bold text-gray-900 mb-4">📊 持仓涨跌</h2>

          <!-- 今日涨幅 -->
          <div class="mb-4">
            <div class="text-sm font-semibold text-gray-700 mb-2 flex items-center gap-2">
              <span>📈</span>
              <span>今日涨幅</span>
            </div>
            <div class="space-y-2">
              <div
                v-for="stock in topGainers"
                :key="stock.symbol"
                class="flex items-center justify-between p-2 border border-gray-100 rounded hover:bg-red-50 cursor-pointer"
                @click="viewStock(stock.symbol)"
              >
                <div class="flex items-center gap-2">
                  <span v-if="stock.is_holding" class="text-xs">💼</span>
                  <span class="font-medium text-sm">{{ stock.name }}</span>
                  <span class="text-xs text-gray-500">{{ stock.symbol }}</span>
                </div>
                <div class="text-right">
                  <div class="text-sm font-semibold text-red-600">
                    +{{ stock.change_rate.toFixed(2) }}%
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 今日跌幅 -->
          <div>
            <div class="text-sm font-semibold text-gray-700 mb-2 flex items-center gap-2">
              <span>📉</span>
              <span>今日跌幅</span>
            </div>
            <div class="space-y-2">
              <div
                v-for="stock in topLosers"
                :key="stock.symbol"
                class="flex items-center justify-between p-2 border border-gray-100 rounded hover:bg-green-50 cursor-pointer"
                @click="viewStock(stock.symbol)"
              >
                <div class="flex items-center gap-2">
                  <span v-if="stock.is_holding" class="text-xs">💼</span>
                  <span class="font-medium text-sm">{{ stock.name }}</span>
                  <span class="text-xs text-gray-500">{{ stock.symbol }}</span>
                </div>
                <div class="text-right">
                  <div class="text-sm font-semibold text-green-600">
                    {{ stock.change_rate.toFixed(2) }}%
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="text-xs text-gray-500 mt-3 text-center">
            💼 标识表示当前持仓股票
          </div>
        </div>

        <!-- 快速操作 -->
        <div class="bg-white rounded-lg border shadow-sm p-6">
          <h2 class="text-lg font-bold text-gray-900 mb-4">⚡ 快速操作</h2>
          <div class="grid grid-cols-2 gap-3">
            <button
              v-for="(item, index) in quickActions"
              :key="index"
              @click="item.action"
              class="flex flex-col items-center justify-center p-4 border border-gray-200 rounded-lg hover:bg-blue-50 hover:border-blue-300 cursor-pointer transition"
            >
              <span class="text-3xl mb-2">{{ item.icon }}</span>
              <span class="text-sm font-medium text-gray-700">{{ item.label }}</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.dashboard {
  min-height: 100vh;
  background-color: #f5f5f5;
}
</style>
