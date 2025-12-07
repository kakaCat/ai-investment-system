<template>
  <div class="events-page">
    <!-- 顶部导航栏 -->
    <div class="top-nav">
      <div class="nav-left">
        <button @click="goBack" class="back-btn">← 返回</button>
        <h1 class="page-title">📋 事件中心</h1>
      </div>
      <div class="nav-right">
        <el-input
          v-model="searchQuery"
          placeholder="搜索事件..."
          prefix-icon="Search"
          clearable
          class="search-input"
        />
        <el-button type="primary" @click="handleBatchAnalysis">
          🤖 AI批量分析
        </el-button>
      </div>
    </div>

    <!-- 主内容区 -->
    <div class="main-content">
      <!-- 事件分类切换 Tab -->
      <div class="category-tabs">
        <div
          :class="['category-tab', activeCategory === 'policy' ? 'active' : '']"
          @click="switchCategory('policy')"
        >
          <div class="tab-content">
            <div class="tab-left">
              <span class="tab-icon">🏛️</span>
              <div class="tab-info">
                <div class="tab-title">政策事件</div>
                <div class="tab-desc">宏观政策 · 行业监管 · 市场环境</div>
              </div>
            </div>
            <div class="tab-count">{{ policyEvents.length }}</div>
          </div>
        </div>

        <div
          :class="['category-tab', activeCategory === 'holdings' ? 'active' : '']"
          @click="switchCategory('holdings')"
        >
          <div class="tab-content">
            <div class="tab-left">
              <span class="tab-icon">📊</span>
              <div class="tab-info">
                <div class="tab-title">持股公司事件</div>
                <div class="tab-desc">我的持仓相关事件</div>
              </div>
            </div>
            <div class="tab-count">{{ holdingsEvents.length }}</div>
          </div>
        </div>
      </div>

      <!-- 政策事件内容 -->
      <div v-if="activeCategory === 'policy'" class="category-content">
        <!-- 统计概览 -->
        <div class="statistics-grid">
          <div class="stat-card">
            <p class="stat-label">政策事件总数</p>
            <p class="stat-value">{{ policyEvents.length }}</p>
          </div>
          <div class="stat-card">
            <p class="stat-label">重要政策</p>
            <p class="stat-value important">{{ importantPolicyCount }}</p>
          </div>
          <div class="stat-card">
            <p class="stat-label">影响我的持仓</p>
            <p class="stat-value impact">{{ policyImpactingHoldings }}</p>
          </div>
          <div class="stat-card">
            <p class="stat-label">今日新增</p>
            <p class="stat-value today">{{ policyTodayCount }}</p>
          </div>
        </div>

        <!-- 筛选器 -->
        <div class="filter-panel">
          <div class="filter-row">
            <div class="filter-item">
              <label class="filter-label">时间范围</label>
              <el-select v-model="policyFilters.timeRange">
                <el-option label="近7天" value="7days" />
                <el-option label="近30天" value="30days" />
                <el-option label="近90天" value="90days" />
                <el-option label="近一年" value="1year" />
              </el-select>
            </div>

            <div class="filter-item">
              <label class="filter-label">政策类型</label>
              <el-select v-model="policyFilters.subtype">
                <el-option label="全部" value="all" />
                <el-option label="货币政策" value="monetary_policy" />
                <el-option label="财政政策" value="fiscal_policy" />
                <el-option label="行业监管" value="regulatory_policy" />
                <el-option label="国际政策" value="international_policy" />
              </el-select>
            </div>

            <div class="filter-item">
              <label class="filter-label">重要性</label>
              <el-select v-model="policyFilters.importance">
                <el-option label="全部" value="all" />
                <el-option label="Critical" value="critical" />
                <el-option label="High" value="high" />
                <el-option label="Medium" value="medium" />
              </el-select>
            </div>

            <div class="filter-item">
              <el-checkbox v-model="policyFilters.onlyMyHoldings" class="holdings-checkbox">
                仅显示影响我的持仓
              </el-checkbox>
            </div>
          </div>
        </div>

        <!-- 政策事件列表 -->
        <div class="events-list">
          <div v-for="(group, index) in groupedPolicyEvents" :key="index">
            <!-- 日期分隔线 -->
            <div class="date-divider">
              <div class="divider-line"></div>
              <span class="divider-text">{{ group.date }}</span>
              <div class="divider-line"></div>
            </div>

            <!-- 该日期的事件 -->
            <div
              v-for="event in group.events"
              :key="event.event_id"
              :class="['event-card', `importance-${event.importance}`]"
            >
              <!-- 事件头部 -->
              <div class="event-header">
                <div class="event-meta">
                  <span :class="['importance-badge', event.importance]">
                    {{ IMPORTANCE_LABELS[event.importance].toUpperCase() }}
                  </span>
                  <span class="event-time">{{ formatEventTime(event.event_time) }}</span>
                  <span class="meta-sep">|</span>
                  <span class="event-type">
                    🏛️ {{ EVENT_SUBTYPE_LABELS[event.subtype] }}
                  </span>
                </div>
                <span v-if="!event.is_read" class="unread-badge">未读</span>
              </div>

              <!-- 事件标题 -->
              <h3 class="event-title">{{ event.title }}</h3>

              <!-- 影响指标 -->
              <div class="impact-metrics">
                <div class="metric-card">
                  <p class="metric-label">影响评分</p>
                  <p :class="['metric-value', event.impact_direction]">
                    {{ IMPACT_DIRECTION_LABELS[event.impact_direction] }} ({{ event.impact_magnitude }}/100)
                  </p>
                </div>
                <div class="metric-card">
                  <p class="metric-label">影响范围</p>
                  <p class="metric-value">
                    {{ event.markets?.length > 1 ? '🌍 全球市场' : `🇨🇳 ${MARKET_TYPE_LABELS[event.markets?.[0] || 'CN']}` }}
                  </p>
                </div>
                <div class="metric-card">
                  <p class="metric-label">市场反应</p>
                  <p class="metric-value">
                    {{ event.markets?.map(m => `${MARKET_TYPE_LABELS[m]}${event.impact_direction === 'negative' ? '-' : '+'}${Math.abs(event.impact_magnitude / 50).toFixed(1)}%`).join(', ') }}
                  </p>
                </div>
              </div>

              <!-- 持仓影响 -->
              <div v-if="event.holding_impacts && event.holding_impacts.length > 0" class="holding-impacts">
                <p class="holding-title">💼 对我的持仓影响:</p>
                <div class="holding-list">
                  <div
                    v-for="impact in event.holding_impacts"
                    :key="impact.symbol"
                    class="holding-item"
                  >
                    <span>• {{ impact.stock_name }} ({{ impact.symbol }})</span>
                    <span :class="['holding-change', impact.impact_direction]">
                      预期{{ impact.expected_change_percent > 0 ? '+' : '' }}{{ impact.expected_change_percent }}%
                      {{ impact.impact_direction === 'positive' ? '📈' : '📉' }}
                    </span>
                  </div>
                </div>
              </div>

              <!-- AI建议 -->
              <div v-if="event.ai_suggestion" class="ai-suggestion">
                <p class="suggestion-title">🤖 AI建议:</p>
                <p class="suggestion-text">{{ event.ai_suggestion }}</p>
              </div>

              <!-- 操作按钮 -->
              <div class="event-actions">
                <el-button type="primary" size="small">查看完整分析</el-button>
                <el-button size="small">🔔 添加提醒</el-button>
                <el-button size="small" @click="toggleReadStatus(event)">
                  ✓ {{ event.is_read ? '标记未读' : '标记已读' }}
                </el-button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 持股公司事件内容 -->
      <div v-if="activeCategory === 'holdings'" class="category-content">
        <!-- 统计概览 -->
        <div class="statistics-grid">
          <div class="stat-card">
            <p class="stat-label">公司事件总数</p>
            <p class="stat-value">{{ holdingsEvents.length }}</p>
          </div>
          <div class="stat-card">
            <p class="stat-label">重要事件</p>
            <p class="stat-value important">{{ importantHoldingsCount }}</p>
          </div>
          <div class="stat-card">
            <p class="stat-label">持仓公司数</p>
            <p class="stat-value companies">{{ uniqueHoldingsCount }}</p>
          </div>
          <div class="stat-card">
            <p class="stat-label">今日新增</p>
            <p class="stat-value today">{{ holdingsTodayCount }}</p>
          </div>
        </div>

        <!-- 筛选器 -->
        <div class="filter-panel">
          <div class="filter-row">
            <div class="filter-item">
              <label class="filter-label">时间范围</label>
              <el-select v-model="holdingsFilters.timeRange">
                <el-option label="近7天" value="7days" />
                <el-option label="近30天" value="30days" />
                <el-option label="近90天" value="90days" />
                <el-option label="近一年" value="1year" />
              </el-select>
            </div>

            <div class="filter-item">
              <label class="filter-label">事件类型</label>
              <el-select v-model="holdingsFilters.subtype">
                <el-option label="全部" value="all" />
                <el-option label="财报公告" value="earnings" />
                <el-option label="公司决策" value="governance" />
                <el-option label="人事变动" value="management" />
                <el-option label="业绩预告" value="forecast" />
              </el-select>
            </div>

            <div class="filter-item">
              <label class="filter-label">重要性</label>
              <el-select v-model="holdingsFilters.importance">
                <el-option label="全部" value="all" />
                <el-option label="Critical" value="critical" />
                <el-option label="High" value="high" />
                <el-option label="Medium" value="medium" />
              </el-select>
            </div>

            <div class="filter-item">
              <label class="filter-label">持仓股票</label>
              <el-select v-model="holdingsFilters.symbol">
                <el-option label="全部" value="all" />
                <el-option
                  v-for="symbol in uniqueSymbols"
                  :key="symbol"
                  :label="symbol"
                  :value="symbol"
                />
              </el-select>
            </div>
          </div>
        </div>

        <!-- 持股公司事件列表(按公司分组) -->
        <div class="events-list">
          <div v-for="(group, index) in groupedHoldingsEvents" :key="index" class="company-group">
            <!-- 公司标题 -->
            <div class="company-header">
              <h3 class="company-name">{{ getCompanyIcon(group.symbol) }} {{ group.companyName }} ({{ group.symbol }})</h3>
              <span class="event-count">{{ group.events.length }}个事件</span>
            </div>

            <!-- 该公司的事件 -->
            <div
              v-for="event in group.events"
              :key="event.event_id"
              :class="['event-card', `importance-${event.importance}`]"
            >
              <!-- 事件头部 -->
              <div class="event-header">
                <div class="event-meta">
                  <span :class="['importance-badge', event.importance]">
                    {{ IMPORTANCE_LABELS[event.importance].toUpperCase() }}
                  </span>
                  <span class="event-time">{{ formatFullTime(event.event_time) }}</span>
                  <span class="meta-sep">|</span>
                  <span class="event-type">
                    📊 {{ EVENT_SUBTYPE_LABELS[event.subtype] }}
                  </span>
                </div>
              </div>

              <!-- 事件标题 -->
              <h4 class="event-title">{{ event.summary || event.title }}</h4>

              <!-- 影响指标 -->
              <div class="impact-metrics">
                <div class="metric-card">
                  <p class="metric-label">影响评分</p>
                  <p :class="['metric-value', event.impact_direction]">
                    {{ IMPACT_DIRECTION_LABELS[event.impact_direction] }} ({{ event.impact_magnitude }}/100)
                  </p>
                </div>
                <div class="metric-card">
                  <p class="metric-label">股价反应</p>
                  <p :class="['metric-value', event.impact_direction === 'positive' ? 'positive' : 'negative']">
                    次日{{ event.impact_direction === 'positive' ? '+' : '-' }}{{ Math.abs(event.impact_magnitude / 20).toFixed(1) }}%
                  </p>
                </div>
                <div class="metric-card">
                  <p class="metric-label">持仓影响</p>
                  <p class="metric-value">
                    {{ event.holding_impacts?.[0] ? `预期${event.holding_impacts[0].expected_change_percent > 0 ? '+' : ''}${event.holding_impacts[0].expected_change_percent}%` : '-' }}
                  </p>
                </div>
              </div>

              <!-- AI分析 -->
              <div v-if="event.ai_suggestion" class="ai-suggestion">
                <p class="suggestion-title">🤖 AI分析:</p>
                <p class="suggestion-text">{{ event.ai_suggestion }}</p>
              </div>

              <!-- 操作按钮 -->
              <div class="event-actions">
                <el-button type="primary" size="small">查看完整财报</el-button>
                <el-button size="small">查看股价走势</el-button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { Event, EventImportance, EventSubtype, MarketType } from '@/types/event'
import {
  EVENT_SUBTYPE_LABELS,
  IMPORTANCE_LABELS,
  IMPACT_DIRECTION_LABELS,
  MARKET_TYPE_LABELS
} from '@/types/event'

const router = useRouter()

// Tab切换
const activeCategory = ref<'policy' | 'holdings'>('policy')

// 搜索
const searchQuery = ref('')

// 政策事件筛选器
const policyFilters = ref({
  timeRange: '30days',
  subtype: 'all' as EventSubtype | 'all',
  importance: 'all' as EventImportance | 'all',
  onlyMyHoldings: true
})

// 持股事件筛选器
const holdingsFilters = ref({
  timeRange: '30days',
  subtype: 'all' as EventSubtype | 'all',
  importance: 'all' as EventImportance | 'all',
  symbol: 'all'
})

// 模拟数据
const events = ref<Event[]>([
  {
    event_id: 1,
    title: '美联储加息25bp至5.25%-5.50%',
    summary: '美联储宣布将联邦基金利率目标区间上调25个基点',
    category: 'policy',
    subtype: 'monetary_policy',
    importance: 'critical',
    impact_direction: 'negative',
    impact_magnitude: 75,
    symbols: ['00700', '002594', '600600'],
    markets: ['HK', 'CN', 'US'],
    event_time: '2025-11-07T02:00:00Z',
    created_at: '2025-11-07T02:05:00Z',
    source: 'mcp',
    is_read: false,
    holding_impacts: [
      { symbol: '00700', stock_name: '腾讯控股', expected_change_percent: -2.5, impact_direction: 'negative' },
      { symbol: '002594', stock_name: '比亚迪', expected_change_percent: -1.8, impact_direction: 'negative' },
      { symbol: '600600', stock_name: '青岛啤酒', expected_change_percent: -0.5, impact_direction: 'negative' }
    ],
    ai_suggestion: '建议减仓港股科技股10-20%，降低美联储加息带来的估值压力。优先考虑减持腾讯控股。'
  },
  {
    event_id: 2,
    title: '国家发改委推出消费刺激政策',
    summary: '发改委发布消费刺激计划',
    category: 'policy',
    subtype: 'fiscal_policy',
    importance: 'high',
    impact_direction: 'positive',
    impact_magnitude: 68,
    symbols: ['600600'],
    markets: ['CN'],
    event_time: '2025-11-07T14:30:00Z',
    created_at: '2025-11-07T14:35:00Z',
    source: 'mcp',
    is_read: false,
    holding_impacts: [
      { symbol: '600600', stock_name: '青岛啤酒', expected_change_percent: 2.0, impact_direction: 'positive' }
    ],
    ai_suggestion: '消费板块有中期反弹机会，青岛啤酒可考虑加仓。建议回调至¥58-60区间分批买入。'
  },
  {
    event_id: 3,
    title: '证监会宣布A股IPO审核放缓',
    summary: 'A股IPO审核节奏放缓',
    category: 'policy',
    subtype: 'regulatory_policy',
    importance: 'medium',
    impact_direction: 'positive',
    impact_magnitude: 55,
    symbols: ['600600', '002594'],
    markets: ['CN'],
    event_time: '2025-11-05T09:00:00Z',
    created_at: '2025-11-05T09:10:00Z',
    source: 'mcp',
    is_read: false,
    holding_impacts: [
      { symbol: '600600', stock_name: '青岛啤酒', expected_change_percent: 0.5, impact_direction: 'positive' },
      { symbol: '002594', stock_name: '比亚迪', expected_change_percent: 0.8, impact_direction: 'positive' }
    ],
    ai_suggestion: 'IPO放缓有助于缓解市场资金压力，对A股整体偏利好，建议持有观望。'
  },
  {
    event_id: 4,
    title: 'Q3财报：营收同比+5.2%，净利润同比-3.1%',
    summary: '青岛啤酒Q3财报不及预期',
    category: 'company',
    subtype: 'earnings',
    importance: 'high',
    impact_direction: 'negative',
    impact_magnitude: 65,
    symbols: ['600600'],
    markets: ['CN'],
    event_time: '2025-10-28T16:00:00Z',
    created_at: '2025-10-28T16:10:00Z',
    source: 'mcp',
    is_read: false,
    holding_impacts: [
      { symbol: '600600', stock_name: '青岛啤酒', expected_change_percent: -4.2, impact_direction: 'negative' }
    ],
    ai_suggestion: '业绩不及预期主要因成本上涨，但销量增长显示需求韧性。短期承压，中长期关注成本改善信号。建议持有观望，回调至¥58-60可加仓。'
  },
  {
    event_id: 5,
    title: '大股东复星集团增持1.2%股份',
    summary: '青岛啤酒股东增持',
    category: 'company',
    subtype: 'governance',
    importance: 'medium',
    impact_direction: 'positive',
    impact_magnitude: 68,
    symbols: ['600600'],
    markets: ['CN'],
    event_time: '2025-11-01T10:30:00Z',
    created_at: '2025-11-01T10:35:00Z',
    source: 'mcp',
    is_read: false,
    holding_impacts: [
      { symbol: '600600', stock_name: '青岛啤酒', expected_change_percent: 1.8, impact_direction: 'positive' }
    ],
    ai_suggestion: '大股东增持显示对公司长期价值的信心，结合当前估值处于历史低位，具有配置价值。'
  },
  {
    event_id: 6,
    title: '《王者荣耀2》获得游戏版号，预计Q1上线',
    summary: '腾讯游戏版号获批',
    category: 'company',
    subtype: 'earnings',
    importance: 'high',
    impact_direction: 'positive',
    impact_magnitude: 72,
    symbols: ['00700'],
    markets: ['HK'],
    event_time: '2025-11-03T14:00:00Z',
    created_at: '2025-11-03T14:10:00Z',
    source: 'mcp',
    is_read: false,
    holding_impacts: [
      { symbol: '00700', stock_name: '腾讯控股', expected_change_percent: 3.5, impact_direction: 'positive' }
    ],
    ai_suggestion: '版号获批消除不确定性，《王者荣耀2》预期成为爆款。游戏业务有望成为明年业绩增长点，中长期利好。'
  },
  {
    event_id: 7,
    title: '10月新能源汽车销量50.1万辆，同比+66%',
    summary: '比亚迪销量创新高',
    category: 'company',
    subtype: 'earnings',
    importance: 'high',
    impact_direction: 'positive',
    impact_magnitude: 78,
    symbols: ['002594'],
    markets: ['CN'],
    event_time: '2025-11-01T20:00:00Z',
    created_at: '2025-11-01T20:10:00Z',
    source: 'mcp',
    is_read: false,
    holding_impacts: [
      { symbol: '002594', stock_name: '比亚迪', expected_change_percent: 5.2, impact_direction: 'positive' }
    ],
    ai_suggestion: '销量持续超预期，行业龙头地位稳固。出口高增长打开新增长空间，全年业绩确定性强。建议继续持有。'
  }
])

// 政策事件
const policyEvents = computed(() => {
  return events.value.filter(e => e.category === 'policy')
})

// 持股公司事件
const holdingsEvents = computed(() => {
  return events.value.filter(e => e.category === 'company')
})

// 政策事件统计
const importantPolicyCount = computed(() => {
  return policyEvents.value.filter(e => e.importance === 'critical' || e.importance === 'high').length
})

const policyImpactingHoldings = computed(() => {
  return policyEvents.value.filter(e => e.holding_impacts && e.holding_impacts.length > 0).length
})

const policyTodayCount = computed(() => {
  const today = new Date().toISOString().split('T')[0]
  return policyEvents.value.filter(e => e.event_time.startsWith(today)).length
})

// 持股事件统计
const importantHoldingsCount = computed(() => {
  return holdingsEvents.value.filter(e => e.importance === 'critical' || e.importance === 'high').length
})

const uniqueHoldingsCount = computed(() => {
  const symbols = new Set(holdingsEvents.value.flatMap(e => e.symbols || []))
  return symbols.size
})

const holdingsTodayCount = computed(() => {
  const today = new Date().toISOString().split('T')[0]
  return holdingsEvents.value.filter(e => e.event_time.startsWith(today)).length
})

// 持仓股票列表
const uniqueSymbols = computed(() => {
  const symbols = new Set(holdingsEvents.value.flatMap(e => e.symbols || []))
  return Array.from(symbols)
})

// 按日期分组的政策事件
const groupedPolicyEvents = computed(() => {
  const groups: { date: string; events: Event[] }[] = []
  const dateMap = new Map<string, Event[]>()

  policyEvents.value.forEach(event => {
    const date = event.event_time.split('T')[0]
    if (!dateMap.has(date)) {
      dateMap.set(date, [])
    }
    dateMap.get(date)!.push(event)
  })

  // 转换为数组并排序
  Array.from(dateMap.entries())
    .sort((a, b) => b[0].localeCompare(a[0]))
    .forEach(([date, events]) => {
      groups.push({ date, events })
    })

  return groups
})

// 按公司分组的持股事件
const groupedHoldingsEvents = computed(() => {
  const groups: { symbol: string; companyName: string; events: Event[] }[] = []
  const symbolMap = new Map<string, Event[]>()

  holdingsEvents.value.forEach(event => {
    const symbol = event.symbols?.[0]
    if (symbol) {
      if (!symbolMap.has(symbol)) {
        symbolMap.set(symbol, [])
      }
      symbolMap.get(symbol)!.push(event)
    }
  })

  // 转换为数组
  symbolMap.forEach((events, symbol) => {
    const companyName = events[0].holding_impacts?.[0]?.stock_name || symbol
    groups.push({ symbol, companyName, events })
  })

  return groups
})

// 切换分类
const switchCategory = (category: 'policy' | 'holdings') => {
  activeCategory.value = category
}

// 返回
const goBack = () => {
  router.back()
}

// 格式化时间
const formatEventTime = (time: string) => {
  const date = new Date(time)
  return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

const formatFullTime = (time: string) => {
  const date = new Date(time)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 切换阅读状态
const toggleReadStatus = (event: Event) => {
  event.is_read = !event.is_read
  ElMessage.success(event.is_read ? '已标记为已读' : '已标记为未读')
}

// 批量分析
const handleBatchAnalysis = () => {
  ElMessage.info('AI批量分析功能开发中...')
}

// 获取公司图标
const getCompanyIcon = (symbol: string) => {
  const iconMap: Record<string, string> = {
    '600600': '🍺',
    '00700': '🎮',
    '002594': '🚗'
  }
  return iconMap[symbol] || '📊'
}
</script>

<style scoped lang="scss">
.events-page {
  min-height: 100vh;
  background: #f5f7fa;
}

// 顶部导航
.top-nav {
  position: sticky;
  top: 0;
  z-index: 50;
  background: white;
  border-bottom: 1px solid #e5e7eb;
  padding: 0 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 64px;

  .nav-left {
    display: flex;
    align-items: center;
    gap: 16px;

    .back-btn {
      color: #6b7280;
      background: none;
      border: none;
      cursor: pointer;
      font-size: 14px;

      &:hover {
        color: #111827;
      }
    }

    .page-title {
      font-size: 20px;
      font-weight: bold;
      margin: 0;
    }
  }

  .nav-right {
    display: flex;
    align-items: center;
    gap: 16px;

    .search-input {
      width: 300px;
    }
  }
}

// 主内容
.main-content {
  max-width: 1280px;
  margin: 0 auto;
  padding: 24px;
}

// 分类Tab
.category-tabs {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  margin-bottom: 24px;

  .category-tab {
    background: white;
    border: 2px solid #e5e7eb;
    border-radius: 12px;
    padding: 24px 32px;
    cursor: pointer;
    transition: all 0.3s;

    &:hover {
      border-color: #667eea;
      background: #f9fafb;
    }

    &.active {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      border-color: transparent;
      box-shadow: 0 4px 6px rgba(102, 126, 234, 0.3);
    }

    .tab-content {
      display: flex;
      align-items: center;
      justify-content: space-between;

      .tab-left {
        display: flex;
        align-items: center;
        gap: 12px;

        .tab-icon {
          font-size: 32px;
        }

        .tab-info {
          text-align: left;

          .tab-title {
            font-size: 18px;
            font-weight: bold;
          }

          .tab-desc {
            font-size: 14px;
            opacity: 0.9;
            margin-top: 4px;
          }
        }
      }

      .tab-count {
        font-size: 32px;
        font-weight: bold;
      }
    }
  }
}

// 统计卡片
.statistics-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;

  .stat-card {
    background: white;
    border-radius: 8px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    padding: 24px;

    .stat-label {
      font-size: 14px;
      color: #6b7280;
      margin: 0 0 8px 0;
    }

    .stat-value {
      font-size: 32px;
      font-weight: bold;
      color: #111827;
      margin: 0;

      &.important {
        color: #dc2626;
      }

      &.impact {
        color: #f97316;
      }

      &.companies {
        color: #3b82f6;
      }

      &.today {
        color: #10b981;
      }
    }
  }
}

// 筛选面板
.filter-panel {
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  padding: 24px;
  margin-bottom: 24px;

  .filter-row {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;

    .filter-item {
      .filter-label {
        display: block;
        font-size: 14px;
        font-weight: 500;
        color: #374151;
        margin-bottom: 8px;
      }

      .el-select {
        width: 100%;
      }

      .holdings-checkbox {
        margin-top: 32px;
      }
    }
  }
}

// 事件列表
.events-list {
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  padding: 24px;
}

// 日期分隔线
.date-divider {
  display: flex;
  align-items: center;
  margin: 32px 0 24px 0;

  &:first-child {
    margin-top: 0;
  }

  .divider-line {
    flex: 1;
    height: 1px;
    background: #d1d5db;
  }

  .divider-text {
    padding: 0 16px;
    font-size: 14px;
    font-weight: 600;
    color: #6b7280;
  }
}

// 公司分组
.company-group {
  margin-bottom: 32px;

  &:last-child {
    margin-bottom: 0;
  }

  .company-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 16px;

    .company-name {
      font-size: 18px;
      font-weight: bold;
      color: #111827;
      margin: 0;
    }

    .event-count {
      font-size: 14px;
      color: #6b7280;
    }
  }
}

// 事件卡片
.event-card {
  border-radius: 8px;
  padding: 24px;
  margin-bottom: 24px;
  transition: all 0.3s;

  &:hover {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  }

  &.importance-critical {
    background: #fef2f2;
    border: 2px solid #fecaca;
  }

  &.importance-high {
    background: #fff7ed;
    border: 2px solid #fed7aa;
  }

  &.importance-medium {
    background: #fefce8;
    border: 2px solid #fde68a;
  }

  &.importance-low {
    background: #f0fdf4;
    border: 2px solid #bbf7d0;
  }

  .event-header {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    margin-bottom: 16px;

    .event-meta {
      display: flex;
      align-items: center;
      gap: 12px;

      .importance-badge {
        padding: 4px 12px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: bold;
        color: white;

        &.critical {
          background: #dc2626;
        }

        &.high {
          background: #f97316;
        }

        &.medium {
          background: #eab308;
        }

        &.low {
          background: #10b981;
        }
      }

      .event-time {
        font-size: 14px;
        color: #6b7280;
      }

      .meta-sep {
        color: #6b7280;
      }

      .event-type {
        font-size: 14px;
        font-weight: 600;
      }
    }

    .unread-badge {
      padding: 4px 8px;
      background: #dbeafe;
      color: #1e40af;
      font-size: 12px;
      border-radius: 4px;
    }
  }

  .event-title {
    font-size: 18px;
    font-weight: bold;
    color: #111827;
    margin: 0 0 16px 0;
  }

  .impact-metrics {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
    margin-bottom: 16px;

    .metric-card {
      background: white;
      border-radius: 8px;
      padding: 12px;

      .metric-label {
        font-size: 12px;
        color: #6b7280;
        margin: 0 0 4px 0;
      }

      .metric-value {
        font-size: 16px;
        font-weight: 600;
        margin: 0;

        &.negative {
          color: #dc2626;
        }

        &.positive {
          color: #10b981;
        }

        &.neutral {
          color: #6b7280;
        }
      }
    }
  }

  .holding-impacts {
    background: white;
    border-radius: 8px;
    padding: 16px;
    margin-bottom: 16px;

    .holding-title {
      font-size: 14px;
      font-weight: 600;
      color: #111827;
      margin: 0 0 12px 0;
    }

    .holding-list {
      .holding-item {
        display: flex;
        align-items: center;
        justify-content: space-between;
        font-size: 14px;
        margin-bottom: 8px;

        &:last-child {
          margin-bottom: 0;
        }

        .holding-change {
          font-weight: 600;

          &.positive {
            color: #10b981;
          }

          &.negative {
            color: #dc2626;
          }
        }
      }
    }
  }

  .ai-suggestion {
    background: #eff6ff;
    border: 1px solid #bfdbfe;
    border-radius: 8px;
    padding: 16px;
    margin-bottom: 16px;

    .suggestion-title {
      font-size: 14px;
      font-weight: 600;
      color: #1e40af;
      margin: 0 0 8px 0;
    }

    .suggestion-text {
      font-size: 14px;
      color: #374151;
      margin: 0;
      line-height: 1.6;
    }
  }

  .event-actions {
    display: flex;
    gap: 8px;
  }
}
</style>
