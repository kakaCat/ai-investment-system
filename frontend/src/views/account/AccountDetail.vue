<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft } from '@element-plus/icons-vue'
import { getAccountDetail } from '@/api/account'
import { queryTrades } from '@/api/trade'
import type { AccountDetail, Holding, WatchlistItem } from '@/types/account'
import DepositDialog from '@/components/DepositDialog.vue'
import AddHoldingDialog from '@/components/AddHoldingDialog.vue'
import RecordTradeDialog from '@/components/RecordTradeDialog.vue'
import TransferDialog from '@/components/TransferDialog.vue'
import ExportDialog from '@/components/ExportDialog.vue'

const route = useRoute()
const router = useRouter()

// 状态
const loading = ref(false)
const activeTab = ref('stocks')
const accountDetail = ref<AccountDetail | null>(null)
const expandedWatchlist = ref<Set<string>>(new Set())
const showDepositDialog = ref(false)
const showAddHoldingDialog = ref(false)
const showRecordTradeDialog = ref(false)
const tradeDialogMode = ref<'buy' | 'sell'>('sell')
const selectedStock = ref<{ symbol: string; name: string } | null>(null)
const showTransferDialog = ref(false)
const showExportDialog = ref(false)
const exportType = ref<'account' | 'cash_flow' | 'trades' | 'performance'>('account')
const showAIAnalysis = ref(false)

// 数据状态
const cashFlows = ref([])
const tradeRecords = ref([])
const performanceTimeRange = ref('近6月')
const performanceData = ref(null)

// 计算当前账户ID和名称
const currentAccountId = computed(() => Number(route.params.id))
const currentAccountName = computed(() => accountDetail.value?.account_info.account_name || '')

// 获取账户详情
const fetchAccountDetail = async () => {
  try {
    const res = await getAccountDetail({
      account_id: Number(route.params.id)
    })
    accountDetail.value = res.data
  } catch (error) {
    ElMessage.error('查询账户详情失败')
  }
}

// 获取交易记录
const fetchTrades = async () => {
  try {
    const res = await queryTrades({
      account_id: Number(route.params.id),
      page: 1,
      page_size: 50
    })

    // 转换后端数据格式到前端格式
    if (res.data?.trades) {
      tradeRecords.value = res.data.trades.map((trade: any) => ({
        id: trade.trade_id,
        date: trade.trade_date,
        operation: trade.trade_type === 'buy' ? '买入' : '卖出',
        symbol: trade.symbol,
        name: trade.stock_name,
        quantity: trade.quantity,
        price: trade.price,
        amount: trade.amount,
        profit_loss: trade.profit_loss
      }))
    }
  } catch (error) {
    ElMessage.error('查询交易记录失败')
  }
}

// 返回列表
const goBack = () => {
  router.push({ name: 'AccountList' })
}

// 切换关注股票展开状态
const toggleWatchlistExpand = (symbol: string) => {
  if (expandedWatchlist.value.has(symbol)) {
    expandedWatchlist.value.delete(symbol)
  } else {
    expandedWatchlist.value.add(symbol)
  }
}

// 打开充值弹框
const openDepositDialog = () => {
  showDepositDialog.value = true
}

// 打开添加持仓弹框
const openAddHoldingDialog = () => {
  showAddHoldingDialog.value = true
}

// 充值成功回调
const handleDepositSuccess = () => {
  fetchAccountDetail()
}

// 添加持仓成功回调
const handleAddHoldingSuccess = () => {
  fetchAccountDetail()
}

// 查看股票详情
const viewStockDetail = (symbol: string) => {
  router.push(`/stocks/detail/${symbol}`)
}

// 记录卖出
const recordSell = (holding: Holding) => {
  selectedStock.value = { symbol: holding.symbol, name: holding.name }
  tradeDialogMode.value = 'sell'
  showRecordTradeDialog.value = true
}

// 记录建仓（关注股票转为买入）
const recordBuy = (symbol: string, name: string) => {
  selectedStock.value = { symbol, name }
  tradeDialogMode.value = 'buy'
  showRecordTradeDialog.value = true
}

// 查看AI分析
const viewAIAnalysis = (symbol: string) => {
  router.push({
    path: '/analysis',
    query: { symbol }
  })
}

// 移除关注
const removeFromWatchlist = (symbol: string) => {
  ElMessage.info(`移除关注股票 ${symbol}`)
  // TODO: 调用API移除关注
}

// 交易记录成功回调
const handleTradeSuccess = () => {
  fetchAccountDetail()
  showRecordTradeDialog.value = false
}

// 打开转账弹框
const openTransferDialog = () => {
  showTransferDialog.value = true
}

// 转账成功回调
const handleTransferSuccess = () => {
  fetchAccountDetail()
}

// 打开导出弹框
const openExportDialog = (type: 'account' | 'cash_flow' | 'trades' | 'performance' = 'account') => {
  exportType.value = type
  showExportDialog.value = true
}

onMounted(async () => {
  loading.value = true
  try {
    await Promise.all([
      fetchAccountDetail(),
      fetchTrades()
    ])
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="min-h-screen bg-gray-50">
    <!-- 页面头部 -->
    <div class="bg-white border-b border-gray-200 sticky top-0 z-10">
      <div class="max-w-7xl mx-auto px-6 py-4">
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-4">
            <button
              @click="goBack"
              class="flex items-center text-gray-600 hover:text-gray-900 transition"
            >
              <ArrowLeft class="w-5 h-5 mr-1" />
              返回
            </button>
            <h1 class="text-xl font-bold text-gray-900">
              {{ accountDetail?.account_info.account_name }}
            </h1>
          </div>
          <div class="flex space-x-2">
            <button
              @click="openDepositDialog"
              class="px-4 py-2 text-sm text-white bg-green-600 rounded-lg hover:bg-green-700 transition"
            >
              充值
            </button>
            <button
              @click="openTransferDialog"
              class="px-4 py-2 text-sm text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              转账
            </button>
            <button
              @click="openExportDialog('account')"
              class="px-4 py-2 text-sm text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              导出
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 主内容区 -->
    <div class="max-w-7xl mx-auto px-6 py-6">
      <!-- 账户概览卡片 -->
      <div class="bg-gradient-to-br from-blue-600 to-indigo-700 rounded-xl shadow-lg p-8 mb-6 text-white">
        <div class="flex items-center justify-between mb-6">
          <div>
            <h2 class="text-2xl font-bold mb-2">{{ accountDetail?.account_info.account_name || '华泰证券' }}</h2>
            <p class="text-blue-100">账户号: 8888 · A股账户</p>
          </div>
          <div class="text-right">
            <p class="text-sm text-blue-100 mb-1">账户状态</p>
            <span class="inline-block px-3 py-1 bg-green-500 text-white text-sm font-semibold rounded">
              ✓ 正常
            </span>
          </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div>
            <p class="text-sm text-blue-100 mb-2">总资产</p>
            <p class="text-3xl font-bold">¥586,234</p>
          </div>
          <div>
            <p class="text-sm text-blue-100 mb-2">持仓市值</p>
            <p class="text-3xl font-bold">¥456,234</p>
          </div>
          <div>
            <p class="text-sm text-blue-100 mb-2">可用资金</p>
            <p class="text-3xl font-bold">¥130,000</p>
          </div>
          <div>
            <p class="text-sm text-blue-100 mb-2">累计收益</p>
            <p class="text-3xl font-bold text-green-300">+¥86,234</p>
            <p class="text-sm text-green-200 mt-1">+17.2% ↗</p>
          </div>
        </div>
      </div>

      <!-- AI账户分析 折叠面板 -->
      <div class="bg-white rounded-lg shadow-md mb-6 overflow-hidden">
        <button
          @click="showAIAnalysis = !showAIAnalysis"
          class="w-full px-6 py-4 flex items-center justify-between hover:bg-gray-50 transition-all"
        >
          <div class="flex items-center gap-3">
            <span class="text-2xl">🤖</span>
            <div class="text-left">
              <h3 class="text-lg font-bold text-gray-900">AI账户分析</h3>
              <p class="text-sm text-gray-600">点击展开查看智能诊断和调仓建议</p>
            </div>
          </div>
          <div class="flex items-center gap-3">
            <span class="px-3 py-1 bg-blue-100 text-blue-700 text-sm font-semibold rounded">
              综合评分: B+
            </span>
            <svg
              :class="{'rotate-180': showAIAnalysis}"
              class="w-6 h-6 text-gray-500 transition-transform duration-300"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
            </svg>
          </div>
        </button>

        <!-- AI分析内容 -->
        <div v-show="showAIAnalysis" class="border-t border-gray-200 p-6 bg-gray-50">
          <div class="bg-gradient-to-br from-purple-50 to-blue-50 rounded-lg p-6 border-2 border-purple-200">
            <div class="flex items-center justify-between mb-4">
              <div>
                <h3 class="text-xl font-bold">🤖 AI账户量化分析</h3>
                <p class="text-sm text-gray-600 mt-1">基于持仓结构、风险收益、事件影响的综合诊断与优化建议</p>
              </div>
              <button class="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 text-sm">
                刷新分析
              </button>
            </div>

            <!-- 账户健康度评分 -->
            <div class="bg-white rounded-lg p-6">
              <h4 class="font-bold text-lg mb-4">📊 账户健康度评分</h4>
              <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div class="text-center">
                  <div class="text-5xl font-bold text-green-600 mb-2">B+</div>
                  <p class="text-sm text-gray-600">综合评级</p>
                  <div class="text-xs text-gray-500 mt-1">良好，需优化</div>
                </div>
                <div>
                  <p class="text-sm text-gray-600 mb-2">收益能力</p>
                  <div class="flex items-center gap-2">
                    <div class="flex-1 bg-gray-200 rounded-full h-3">
                      <div class="bg-green-600 h-3 rounded-full" style="width: 78%"></div>
                    </div>
                    <span class="text-sm font-bold">78</span>
                  </div>
                </div>
                <div>
                  <p class="text-sm text-gray-600 mb-2">风险控制</p>
                  <div class="flex items-center gap-2">
                    <div class="flex-1 bg-gray-200 rounded-full h-3">
                      <div class="bg-blue-600 h-3 rounded-full" style="width: 65%"></div>
                    </div>
                    <span class="text-sm font-bold">65</span>
                  </div>
                </div>
                <div>
                  <p class="text-sm text-gray-600 mb-2">持仓健康</p>
                  <div class="flex items-center gap-2">
                    <div class="flex-1 bg-gray-200 rounded-full h-3">
                      <div class="bg-yellow-500 h-3 rounded-full" style="width: 72%"></div>
                    </div>
                    <span class="text-sm font-bold">72</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Tab 导航 -->
      <div class="bg-white rounded-t-lg shadow-sm border border-b-0 border-gray-200">
        <div class="flex items-center justify-between border-b border-gray-200">
          <div class="flex">
            <button
              @click="activeTab = 'stocks'"
              :class="[
                'px-6 py-3 text-sm font-medium transition',
                activeTab === 'stocks'
                  ? 'text-blue-600 border-b-2 border-blue-600'
                  : 'text-gray-600 hover:text-gray-900'
              ]"
            >
              我的股票
            </button>
          <button
            @click="activeTab = 'cash'"
            :class="[
              'px-6 py-3 text-sm font-medium transition',
              activeTab === 'cash'
                ? 'text-blue-600 border-b-2 border-blue-600'
                : 'text-gray-600 hover:text-gray-900'
            ]"
          >
            资金流水
          </button>
          <button
            @click="activeTab = 'trades'"
            :class="[
              'px-6 py-3 text-sm font-medium transition',
              activeTab === 'trades'
                ? 'text-blue-600 border-b-2 border-blue-600'
                : 'text-gray-600 hover:text-gray-900'
            ]"
          >
            交易记录
          </button>
            <button
              @click="activeTab = 'performance'"
              :class="[
                'px-6 py-3 text-sm font-medium transition',
                activeTab === 'performance'
                  ? 'text-blue-600 border-b-2 border-blue-600'
                  : 'text-gray-600 hover:text-gray-900'
              ]"
            >
              绩效分析
            </button>
          </div>

          <!-- 添加持仓按钮 -->
          <div class="px-4 py-2">
            <button
              v-if="activeTab === 'stocks'"
              @click="openAddHoldingDialog"
              class="px-4 py-1.5 text-sm text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition"
            >
              + 添加持仓
            </button>
          </div>
        </div>
      </div>

      <!-- Tab 内容 -->
      <div class="bg-white rounded-b-lg shadow-sm border border-gray-200 p-6">
        <!-- 我的股票 Tab -->
        <div v-show="activeTab === 'stocks'" class="space-y-6">
          <!-- 持仓股票 -->
          <div>
            <div class="flex items-center justify-between mb-4">
              <h3 class="text-lg font-semibold text-gray-900">
                💼 持仓股票 ({{ accountDetail?.holdings.total }}只)
              </h3>
              <button class="px-4 py-2 text-sm text-white bg-blue-600 rounded-lg hover:bg-blue-700">
                记录交易
              </button>
            </div>

            <!-- 持仓汇总 -->
            <div class="bg-blue-50 rounded-lg p-4 mb-4">
              <div class="flex items-center space-x-8 text-sm">
                <div>
                  <span class="text-gray-600">市值: </span>
                  <span class="font-semibold text-gray-900">
                    ¥{{ accountDetail?.statistics.total_market_value.toLocaleString() }}
                  </span>
                </div>
                <div>
                  <span class="text-gray-600">成本: </span>
                  <span class="font-semibold text-gray-900">¥132,150</span>
                </div>
                <div>
                  <span class="text-gray-600">盈亏: </span>
                  <span
                    class="font-semibold"
                    :class="(accountDetail?.statistics.total_profit_loss ?? 0) >= 0 ? 'text-green-600' : 'text-red-600'"
                  >
                    {{ (accountDetail?.statistics.total_profit_loss ?? 0) >= 0 ? '+' : '' }}
                    ¥{{ accountDetail?.statistics.total_profit_loss.toLocaleString() }}
                    ({{ (accountDetail?.statistics.profit_loss_rate ?? 0) >= 0 ? '+' : '' }}{{ accountDetail?.statistics.profit_loss_rate.toFixed(2) }}%)
                  </span>
                </div>
              </div>
            </div>

            <!-- 持仓列表 -->
            <div class="border border-gray-200 rounded-lg overflow-hidden">
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
                    <th class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">操作</th>
                  </tr>
                </thead>
                <tbody class="bg-white divide-y divide-gray-200">
                  <tr v-for="holding in accountDetail?.holdings.list" :key="holding.symbol" class="hover:bg-gray-50">
                    <td class="px-4 py-3 text-sm font-medium text-gray-900">{{ holding.symbol }}</td>
                    <td class="px-4 py-3 text-sm text-gray-900">{{ holding.name }}</td>
                    <td class="px-4 py-3 text-sm text-right text-gray-900">{{ holding.quantity.toLocaleString() }}</td>
                    <td class="px-4 py-3 text-sm text-right text-gray-700">¥{{ holding.avg_cost.toFixed(2) }}</td>
                    <td class="px-4 py-3 text-sm text-right font-medium text-gray-900">¥{{ holding.current_price.toFixed(2) }}</td>
                    <td class="px-4 py-3 text-sm text-right font-semibold text-gray-900">¥{{ holding.market_value.toLocaleString() }}</td>
                    <td class="px-4 py-3 text-sm text-right">
                      <div
                        class="font-semibold"
                        :class="holding.profit_loss >= 0 ? 'text-green-600' : 'text-red-600'"
                      >
                        {{ holding.profit_loss >= 0 ? '+' : '' }}¥{{ holding.profit_loss.toLocaleString() }}
                        <div class="text-xs">
                          {{ holding.profit_loss >= 0 ? '+' : '' }}{{ holding.profit_loss_rate.toFixed(2) }}%
                        </div>
                      </div>
                    </td>
                    <td class="px-4 py-3 text-sm text-right">
                      <div class="flex justify-end space-x-2">
                        <button
                          @click="viewStockDetail(holding.symbol)"
                          class="text-blue-600 hover:text-blue-800"
                        >
                          详情
                        </button>
                        <button
                          @click="recordBuy(holding.symbol, holding.name)"
                          class="text-green-600 hover:text-green-800"
                        >
                          买入
                        </button>
                        <button
                          @click="recordSell(holding)"
                          class="text-red-600 hover:text-red-800"
                        >
                          卖出
                        </button>
                        <button
                          @click="viewAIAnalysis(holding.symbol)"
                          class="text-purple-600 hover:text-purple-800"
                        >
                          AI分析
                        </button>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- 关注股票 -->
          <div>
            <div class="flex items-center justify-between mb-4">
              <h3 class="text-lg font-semibold text-gray-900">
                ⭐ 关注股票 ({{ accountDetail?.watchlist.total }}只)
              </h3>
              <button class="px-4 py-2 text-sm text-white bg-green-600 rounded-lg hover:bg-green-700">
                添加关注
              </button>
            </div>

            <!-- 关注列表 -->
            <div class="space-y-3">
              <div
                v-for="item in accountDetail?.watchlist.list"
                :key="item.symbol"
                class="border border-gray-200 rounded-lg overflow-hidden hover:border-blue-300 transition"
              >
                <!-- 主行 -->
                <div class="bg-white p-4">
                  <div class="grid grid-cols-8 gap-4 items-center">
                    <div class="col-span-1">
                      <div class="text-sm font-medium text-gray-900">{{ item.symbol }}</div>
                      <div class="text-xs text-gray-500">{{ item.name }}</div>
                    </div>
                    <div class="col-span-1 text-right">
                      <div class="text-sm font-medium text-gray-900">¥{{ item.current_price?.toFixed(2) }}</div>
                      <div class="text-xs text-gray-500">现价</div>
                    </div>
                    <div class="col-span-1 text-right">
                      <div class="text-sm font-medium text-gray-700">
                        {{ item.target_price ? `¥${item.target_price.toFixed(2)}` : '--' }}
                      </div>
                      <div class="text-xs text-gray-500">目标价</div>
                    </div>
                    <div class="col-span-1 text-center">
                      <div class="text-sm font-medium text-green-600">+5.0%</div>
                      <div class="text-xs text-gray-500">偏离度</div>
                    </div>
                    <div class="col-span-1 text-center">
                      <div class="text-sm">⭐⭐⭐</div>
                      <div class="text-xs text-gray-500">关注度</div>
                    </div>
                    <div class="col-span-1 text-center">
                      <span class="inline-block px-2 py-1 text-xs font-medium text-yellow-700 bg-yellow-100 rounded">
                        观望
                      </span>
                    </div>
                    <div class="col-span-2 text-right">
                      <div class="flex justify-end space-x-2">
                        <button
                          @click="viewStockDetail(item.symbol)"
                          class="text-blue-600 hover:text-blue-800 text-sm"
                        >
                          详情
                        </button>
                        <button
                          @click="recordBuy(item.symbol, item.name)"
                          class="text-green-600 hover:text-green-800 text-sm"
                        >
                          建仓
                        </button>
                        <button
                          @click="removeFromWatchlist(item.symbol)"
                          class="text-red-600 hover:text-red-800 text-sm"
                        >
                          移除
                        </button>
                        <button
                          @click="toggleWatchlistExpand(item.symbol)"
                          class="text-gray-600 hover:text-gray-800 text-sm"
                        >
                          {{ expandedWatchlist.has(item.symbol) ? '▲' : '▼' }}
                        </button>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- 展开详情 -->
                <div v-show="expandedWatchlist.has(item.symbol)" class="bg-gray-50 border-t border-gray-200 p-4">
                  <div class="space-y-3">
                    <div class="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <span class="text-gray-600">目标价: </span>
                        <span class="font-medium text-gray-900">
                          ¥{{ item.target_price?.toFixed(2) }}
                        </span>
                        <span class="text-gray-500 ml-2">
                          (当前价 ¥{{ item.current_price?.toFixed(2) }}, +5.0%)
                        </span>
                      </div>
                      <div>
                        <span class="text-gray-600">关注度: </span>
                        <span class="text-gray-900">⭐⭐⭐ (High)</span>
                      </div>
                    </div>
                    <div class="text-sm">
                      <span class="text-gray-600">关注理由: </span>
                      <span class="text-gray-900">{{ item.notes || '等待回调' }}</span>
                    </div>
                    <div class="bg-blue-50 border border-blue-200 rounded p-3">
                      <div class="text-sm">
                        <span class="font-medium text-blue-900">AI建议: </span>
                        <span class="text-blue-800">[观望] 当前价格偏高，建议等待回调至目标价附近</span>
                      </div>
                      <div class="text-xs text-blue-600 mt-1">建议时间: {{ item.created_at }}</div>
                    </div>
                    <div class="flex space-x-2 pt-2">
                      <button
                        @click="recordBuy(item.symbol, item.name)"
                        class="px-3 py-1.5 text-sm text-white bg-green-600 rounded hover:bg-green-700"
                      >
                        记录建仓
                      </button>
                      <button
                        @click="removeFromWatchlist(item.symbol)"
                        class="px-3 py-1.5 text-sm text-gray-700 bg-white border border-gray-300 rounded hover:bg-gray-50"
                      >
                        移除关注
                      </button>
                      <button
                        @click="viewStockDetail(item.symbol)"
                        class="px-3 py-1.5 text-sm text-gray-700 bg-white border border-gray-300 rounded hover:bg-gray-50"
                      >
                        查看详情
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 资金流水 Tab -->
        <div v-show="activeTab === 'cash'">
          <div class="mb-4">
            <h3 class="text-lg font-semibold text-gray-900 mb-2">资金流水 (近30天)</h3>
            <p class="text-sm text-gray-500">显示账户资金变动记录</p>
          </div>

          <!-- 流水列表 -->
          <div v-if="cashFlows.length > 0" class="border border-gray-200 rounded-lg overflow-hidden">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">日期</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">类型</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">摘要</th>
                  <th class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">金额</th>
                  <th class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">余额</th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr v-for="flow in cashFlows" :key="flow.id" class="hover:bg-gray-50">
                  <td class="px-4 py-3 text-sm text-gray-900">{{ flow.date }}</td>
                  <td class="px-4 py-3 text-sm">
                    <span
                      :class="{
                        'px-2 py-1 text-xs font-medium rounded': true,
                        'bg-blue-100 text-blue-700': flow.type === '充值',
                        'bg-red-100 text-red-700': flow.type === '买入',
                        'bg-green-100 text-green-700': flow.type === '卖出',
                        'bg-yellow-100 text-yellow-700': flow.type === '股票分红',
                        'bg-gray-100 text-gray-700': !['充值', '买入', '卖出', '股票分红'].includes(flow.type)
                      }"
                    >
                      {{ flow.type }}
                    </span>
                  </td>
                  <td class="px-4 py-3 text-sm text-gray-700">{{ flow.description }}</td>
                  <td class="px-4 py-3 text-sm text-right font-medium"
                      :class="flow.amount >= 0 ? 'text-green-600' : 'text-red-600'">
                    {{ flow.amount >= 0 ? '+' : '' }}¥{{ flow.amount.toLocaleString() }}
                  </td>
                  <td class="px-4 py-3 text-sm text-right text-gray-900">
                    ¥{{ flow.balance.toLocaleString() }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- 空状态 -->
          <div v-else class="text-center py-12 bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
            <div class="text-gray-400 text-4xl mb-2">💰</div>
            <p class="text-gray-500">暂无资金流水</p>
            <p class="text-sm text-gray-400 mt-1">资金变动记录将显示在这里</p>
          </div>

          <!-- 底部按钮 -->
          <div class="mt-4 flex justify-between">
            <button class="px-4 py-2 text-sm text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50">
              显示更多
            </button>
            <button
              @click="openExportDialog('cash_flow')"
              class="px-4 py-2 text-sm text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              导出流水
            </button>
          </div>
        </div>
        <!-- 交易记录 Tab -->
        <div v-show="activeTab === 'trades'">
          <div class="mb-4 flex items-center justify-between">
            <div>
              <h3 class="text-lg font-semibold text-gray-900 mb-2">交易记录 (近30天)</h3>
              <p class="text-sm text-gray-500">显示买入卖出记录</p>
            </div>
            <!-- 筛选器 -->
            <div class="flex space-x-2">
              <select class="px-3 py-1.5 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">
                <option>筛选: 全部</option>
                <option>买入</option>
                <option>卖出</option>
              </select>
              <select class="px-3 py-1.5 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">
                <option>股票: 全部</option>
                <option>00700 腾讯控股</option>
                <option>600600 青岛啤酒</option>
                <option>002594 比亚迪</option>
              </select>
              <select class="px-3 py-1.5 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">
                <option>时间: 近30天</option>
                <option>近7天</option>
                <option>近3月</option>
                <option>近6月</option>
                <option>全部</option>
              </select>
            </div>
          </div>

          <!-- 交易列表 -->
          <div v-if="tradeRecords.length > 0" class="border border-gray-200 rounded-lg overflow-hidden">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">日期</th>
                  <th class="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase">操作</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">股票</th>
                  <th class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">数量</th>
                  <th class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">价格</th>
                  <th class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">金额</th>
                  <th class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">盈亏</th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr v-for="trade in tradeRecords" :key="trade.id" class="hover:bg-gray-50">
                  <td class="px-4 py-3 text-sm text-gray-900">{{ trade.date }}</td>
                  <td class="px-4 py-3 text-sm text-center">
                    <span
                      :class="{
                        'px-2 py-1 text-xs font-medium rounded': true,
                        'bg-red-100 text-red-700': trade.operation === '买入',
                        'bg-green-100 text-green-700': trade.operation === '卖出'
                      }"
                    >
                      {{ trade.operation }}
                    </span>
                  </td>
                  <td class="px-4 py-3 text-sm">
                    <div class="font-medium text-gray-900">{{ trade.symbol }}</div>
                    <div class="text-xs text-gray-500">{{ trade.name }}</div>
                  </td>
                  <td class="px-4 py-3 text-sm text-right text-gray-900">{{ trade.quantity }}</td>
                  <td class="px-4 py-3 text-sm text-right text-gray-700">¥{{ trade.price.toFixed(2) }}</td>
                  <td class="px-4 py-3 text-sm text-right font-medium"
                      :class="trade.operation === '买入' ? 'text-red-600' : 'text-green-600'">
                    {{ trade.operation === '买入' ? '-' : '+' }}¥{{ trade.amount.toLocaleString() }}
                  </td>
                  <td class="px-4 py-3 text-sm text-right">
                    <span v-if="trade.profit_loss !== null" class="font-semibold"
                          :class="trade.profit_loss >= 0 ? 'text-green-600' : 'text-red-600'">
                      {{ trade.profit_loss >= 0 ? '+' : '' }}¥{{ trade.profit_loss.toLocaleString() }} ✅
                    </span>
                    <span v-else class="text-gray-400">-</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- 空状态 -->
          <div v-else class="text-center py-12 bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
            <div class="text-gray-400 text-4xl mb-2">📊</div>
            <p class="text-gray-500">暂无交易记录</p>
            <p class="text-sm text-gray-400 mt-1">记录您的第一笔交易吧</p>
          </div>

          <!-- 底部按钮 -->
          <div class="mt-4 flex justify-between">
            <button class="px-4 py-2 text-sm text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50">
              显示更多
            </button>
            <button
              @click="openExportDialog('trades')"
              class="px-4 py-2 text-sm text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              导出记录
            </button>
          </div>
        </div>
        <!-- 绩效分析 Tab -->
        <div v-show="activeTab === 'performance'" class="space-y-6">
          <!-- 时间范围选择 -->
          <div class="flex items-center justify-between">
            <h3 class="text-lg font-semibold text-gray-900">绩效分析</h3>
            <div class="flex space-x-2">
              <button
                v-for="range in ['近1月', '近3月', '近6月', '今年', '全部']"
                :key="range"
                @click="performanceTimeRange = range"
                :class="{
                  'px-4 py-1.5 text-sm rounded-lg transition': true,
                  'bg-blue-600 text-white': performanceTimeRange === range,
                  'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50': performanceTimeRange !== range
                }"
              >
                {{ range }}
              </button>
            </div>
          </div>

          <!-- 暂无数据提示 -->
          <div v-if="!performanceData" class="text-center py-12 bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
            <div class="text-gray-400 text-4xl mb-2">📈</div>
            <p class="text-gray-500">暂无绩效数据</p>
            <p class="text-sm text-gray-400 mt-1">进行交易后将生成绩效分析</p>
          </div>

          <!-- 绩效详细数据 -->
          <template v-if="performanceData">
            <!-- 收益曲线 -->
            <div class="bg-white border border-gray-200 rounded-lg p-6">
              <h4 class="text-md font-semibold text-gray-900 mb-4">收益曲线</h4>
              <div class="bg-gray-50 border border-gray-200 rounded p-8 text-center">
                <div class="text-sm text-gray-500 mb-4">净值走势图</div>
                <div class="text-xs text-gray-400">[收益曲线图表区域 - 需要ECharts实现]</div>
                <div class="text-xs text-gray-400 mt-2">对比基准: 沪深300 +8.3% | 恒生指数 +5.7%</div>
              </div>
              <div class="grid grid-cols-3 gap-6 mt-4 text-sm">
                <div>
                  <span class="text-gray-600">累计收益率: </span>
                  <span class="font-semibold text-green-600">+{{ performanceData.cumulative_return }}%</span>
                </div>
                <div>
                  <span class="text-gray-600">年化收益率: </span>
                  <span class="font-semibold text-green-600">+{{ performanceData.annualized_return }}%</span>
                </div>
                <div>
                  <span class="text-gray-600">超额收益: </span>
                  <span class="font-semibold text-green-600">+13.3%</span>
                </div>
              </div>
            </div>

            <!-- 收益明细 -->
            <div class="bg-white border border-gray-200 rounded-lg p-6">
            <h4 class="text-md font-semibold text-gray-900 mb-4">收益明细</h4>
            <div class="grid grid-cols-4 gap-4">
              <div class="bg-gradient-to-br from-green-50 to-green-100 rounded-lg p-4">
                <div class="text-sm text-gray-600 mb-1">累计盈亏</div>
                <div class="text-2xl font-bold text-green-600">
                  +¥{{ performanceData.total_profit_loss.toLocaleString() }}
                </div>
                <div class="text-xs text-green-600 mt-1">+{{ performanceData.cumulative_return }}%</div>
              </div>
              <div class="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-4">
                <div class="text-sm text-gray-600 mb-1">浮动盈亏</div>
                <div class="text-2xl font-bold text-blue-600">
                  +¥{{ performanceData.floating_profit_loss.toLocaleString() }}
                </div>
                <div class="text-xs text-gray-500 mt-1">当前持仓</div>
              </div>
              <div class="bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg p-4">
                <div class="text-sm text-gray-600 mb-1">已实现</div>
                <div class="text-2xl font-bold text-purple-600">
                  +¥{{ performanceData.realized_profit_loss.toLocaleString() }}
                </div>
                <div class="text-xs text-gray-500 mt-1">已平仓盈亏</div>
              </div>
              <div class="bg-gradient-to-br from-yellow-50 to-yellow-100 rounded-lg p-4">
                <div class="text-sm text-gray-600 mb-1">分红收入</div>
                <div class="text-2xl font-bold text-yellow-600">
                  +¥{{ performanceData.dividend_income.toLocaleString() }}
                </div>
                <div class="text-xs text-gray-500 mt-1">股息收入</div>
              </div>
            </div>
          </div>

          <!-- 风险指标 -->
          <div class="bg-white border border-gray-200 rounded-lg p-6">
            <h4 class="text-md font-semibold text-gray-900 mb-4">风险指标</h4>
            <div class="grid grid-cols-4 gap-4">
              <div class="bg-gray-50 rounded-lg p-4">
                <div class="text-sm text-gray-600 mb-1">最大回撤</div>
                <div class="text-2xl font-bold text-red-600">
                  {{ performanceData.max_drawdown }}%
                </div>
                <div class="text-xs text-gray-500 mt-1">(青岛啤酒)</div>
              </div>
              <div class="bg-gray-50 rounded-lg p-4">
                <div class="text-sm text-gray-600 mb-1">夏普比率</div>
                <div class="text-2xl font-bold text-gray-900">
                  {{ performanceData.sharpe_ratio }}
                </div>
                <div class="text-xs text-green-600 mt-1">(优秀)</div>
              </div>
              <div class="bg-gray-50 rounded-lg p-4">
                <div class="text-sm text-gray-600 mb-1">胜率</div>
                <div class="text-2xl font-bold text-gray-900">
                  {{ performanceData.win_rate }}%
                </div>
                <div class="text-xs text-gray-500 mt-1">{{ performanceData.winning_trades }}/{{ performanceData.total_trades }}</div>
              </div>
              <div class="bg-gray-50 rounded-lg p-4">
                <div class="text-sm text-gray-600 mb-1">盈亏比</div>
                <div class="text-2xl font-bold text-gray-900">
                  {{ performanceData.profit_loss_ratio }}:1
                </div>
                <div class="text-xs text-gray-500 mt-1">平均盈亏</div>
              </div>
            </div>
          </div>

          <!-- 交易统计 -->
          <div class="bg-white border border-gray-200 rounded-lg p-6">
            <h4 class="text-md font-semibold text-gray-900 mb-4">交易统计</h4>
            <div class="space-y-3 text-sm">
              <div class="flex justify-between">
                <span class="text-gray-600">总交易次数:</span>
                <span class="font-medium text-gray-900">{{ performanceData.total_trades }}次</span>
              </div>
              <div class="pl-4 space-y-2">
                <div class="flex justify-between">
                  <span class="text-gray-600">• 盈利交易:</span>
                  <span class="text-green-600 font-medium">{{ performanceData.winning_trades }}次 ({{ performanceData.win_rate }}%)</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-gray-600">• 亏损交易:</span>
                  <span class="text-red-600 font-medium">{{ performanceData.losing_trades }}次 ({{ (100 - performanceData.win_rate).toFixed(1) }}%)</span>
                </div>
              </div>
              <div class="border-t border-gray-200 pt-3 flex justify-between">
                <span class="text-gray-600">平均持仓周期:</span>
                <span class="font-medium text-gray-900">{{ performanceData.avg_holding_days }}天</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-600">换手率:</span>
                <span class="font-medium text-gray-900">{{ performanceData.turnover_rate }}次/月</span>
              </div>
              <div class="border-t border-gray-200 pt-3 flex justify-between">
                <span class="text-gray-600">最佳交易:</span>
                <span class="text-green-600 font-medium">
                  {{ performanceData.best_trade.stock }} +¥{{ performanceData.best_trade.profit.toLocaleString() }} (+{{ performanceData.best_trade.rate }}%)
                </span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-600">最差交易:</span>
                <span class="text-red-600 font-medium">
                  {{ performanceData.worst_trade.stock }} ¥{{ performanceData.worst_trade.profit.toLocaleString() }} ({{ performanceData.worst_trade.rate }}%)
                </span>
              </div>
            </div>
          </div>

            <!-- 导出按钮 -->
            <div class="flex justify-end">
              <button
                @click="openExportDialog('performance')"
                class="px-6 py-2 text-sm text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition"
              >
                导出绩效报告
              </button>
            </div>
          </template>
        </div>
      </div>
    </div>

    <!-- 充值弹框 -->
    <DepositDialog
      v-model:visible="showDepositDialog"
      :account-id="currentAccountId"
      :account-name="currentAccountName"
      @success="handleDepositSuccess"
    />

    <!-- 添加持仓弹框 -->
    <AddHoldingDialog
      v-model:visible="showAddHoldingDialog"
      :account-id="currentAccountId"
      :account-name="currentAccountName"
      @success="handleAddHoldingSuccess"
    />

    <!-- 记录交易弹框 -->
    <RecordTradeDialog
      v-model:visible="showRecordTradeDialog"
      :account-id="currentAccountId"
      :mode="tradeDialogMode"
      :pre-selected-stock="selectedStock"
      @success="handleTradeSuccess"
    />

    <!-- 转账弹框 -->
    <TransferDialog
      v-model:visible="showTransferDialog"
      :account-id="currentAccountId"
      :account-name="currentAccountName"
      @success="handleTransferSuccess"
    />

    <!-- 导出数据弹框 -->
    <ExportDialog
      v-model:visible="showExportDialog"
      :account-id="currentAccountId"
      :account-name="currentAccountName"
      :export-type="exportType"
    />
  </div>
</template>
