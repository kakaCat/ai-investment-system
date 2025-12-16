<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import type { Stock } from '@/types/stock'

interface Props {
  visible: boolean
  multiple?: boolean
  excludeSymbols?: string[]
}

const props = withDefaults(defineProps<Props>(), {
  multiple: false,
  excludeSymbols: () => []
})

const emit = defineEmits<{
  'update:visible': [visible: boolean]
  confirm: [stocks: Stock | Stock[]]
}>()

const dialogVisible = computed({
  get: () => props.visible,
  set: (val) => emit('update:visible', val)
})

// 搜索条件
const searchKeyword = ref('')
const selectedMarket = ref<'all' | 'A' | 'HK' | 'US'>('all')

// 搜索结果
const searchResults = ref<Stock[]>([])
const searching = ref(false)

// 选中的股票
const selectedStocks = ref<Stock[]>([])
const selectedSymbols = computed(() => selectedStocks.value.map(s => s.symbol))

// 执行搜索 - 调用真实API
const handleSearch = async () => {
  if (!searchKeyword.value.trim()) {
    searchResults.value = []
    return
  }

  searching.value = true
  try {
    // 调用股票搜索API
    const response = await fetch('/api/v1/stock/search', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      },
      body: JSON.stringify({
        keyword: searchKeyword.value.trim(),
        market: selectedMarket.value === 'all' ? undefined : selectedMarket.value,
        limit: 50
      })
    })

    if (!response.ok) {
      throw new Error('搜索失败')
    }

    const data = await response.json()
    let results = data.data || []

    // 排除已选择的股票
    if (props.excludeSymbols.length > 0) {
      results = results.filter((stock: Stock) => !props.excludeSymbols.includes(stock.symbol))
    }

    searchResults.value = results

    if (results.length === 0) {
      ElMessage.info('未找到匹配的股票，请尝试其他关键词')
    }
  } catch (error: any) {
    console.error('搜索失败:', error)
    ElMessage.error('搜索失败: ' + (error.message || '请检查网络连接'))
    searchResults.value = []
  } finally {
    searching.value = false
  }
}

// 切换市场时重新搜索
watch(selectedMarket, () => {
  if (searchKeyword.value) {
    handleSearch()
  }
})

// 选择/取消选择股票
const toggleStock = (stock: Stock) => {
  if (props.multiple) {
    const index = selectedStocks.value.findIndex(s => s.symbol === stock.symbol)
    if (index > -1) {
      selectedStocks.value.splice(index, 1)
    } else {
      selectedStocks.value.push(stock)
    }
  } else {
    // 单选模式
    if (selectedSymbols.value.includes(stock.symbol)) {
      selectedStocks.value = []
    } else {
      selectedStocks.value = [stock]
    }
  }
}

// 确认选择
const handleConfirm = () => {
  if (selectedStocks.value.length === 0) {
    ElMessage.warning('请选择股票')
    return
  }

  if (props.multiple) {
    emit('confirm', [...selectedStocks.value])
  } else {
    emit('confirm', selectedStocks.value[0])
  }

  dialogVisible.value = false
  resetForm()
}

// 重置表单
const resetForm = () => {
  searchKeyword.value = ''
  selectedMarket.value = 'all'
  searchResults.value = []
  selectedStocks.value = []
}

// 获取价格变动样式
const getPriceChangeClass = (changeRate: number) => {
  if (changeRate > 0) return 'text-red-600'
  if (changeRate < 0) return 'text-green-600'
  return 'text-gray-600'
}

// 格式化涨跌幅
const formatChangeRate = (rate: number) => {
  return rate > 0 ? `+${rate.toFixed(2)}%` : `${rate.toFixed(2)}%`
}

// 格式化成交量
const formatVolume = (volume: number) => {
  if (volume >= 100000000) {
    return `${(volume / 100000000).toFixed(2)}亿`
  }
  if (volume >= 10000) {
    return `${(volume / 10000).toFixed(2)}万`
  }
  return volume.toString()
}

// 快捷搜索热门股票
const quickSearch = (keyword: string) => {
  searchKeyword.value = keyword
  handleSearch()
}

// 热门股票
const popularStocks = [
  { name: '贵州茅台', symbol: '600519' },
  { name: '腾讯控股', symbol: '00700' },
  { name: 'Apple', symbol: 'AAPL' },
  { name: 'NVIDIA', symbol: 'NVDA' }
]
</script>

<template>
  <el-dialog
    v-model="dialogVisible"
    title="股票搜索"
    width="800px"
    :close-on-click-modal="false"
    @closed="resetForm"
  >
    <!-- 搜索区域 -->
    <div class="mb-6">
      <div class="flex gap-4 mb-4">
        <el-input
          v-model="searchKeyword"
          placeholder="输入股票代码或名称"
          :prefix-icon="Search"
          clearable
          style="flex: 1"
          @keyup.enter="handleSearch"
          @clear="searchResults = []"
        />
        <el-button type="primary" :loading="searching" @click="handleSearch">
          搜索
        </el-button>
      </div>

      <!-- 市场筛选 -->
      <div class="flex items-center gap-4">
        <span class="text-sm text-gray-600">市场：</span>
        <el-radio-group v-model="selectedMarket" size="small">
          <el-radio-button label="all">全部</el-radio-button>
          <el-radio-button label="A">A股</el-radio-button>
          <el-radio-button label="HK">港股</el-radio-button>
          <el-radio-button label="US">美股</el-radio-button>
        </el-radio-group>
      </div>

      <!-- 热门股票快捷搜索 -->
      <div v-if="searchResults.length === 0 && !searchKeyword" class="mt-4">
        <div class="text-sm text-gray-600 mb-2">热门股票：</div>
        <div class="flex gap-2 flex-wrap">
          <el-tag
            v-for="stock in popularStocks"
            :key="stock.symbol"
            class="cursor-pointer"
            @click="quickSearch(stock.symbol)"
          >
            {{ stock.name }} ({{ stock.symbol }})
          </el-tag>
        </div>
      </div>
    </div>

    <!-- 搜索结果 -->
    <div v-if="searchResults.length > 0" class="search-results">
      <div class="mb-2 text-sm text-gray-600">
        找到 {{ searchResults.length }} 只股票
        <span v-if="selectedStocks.length > 0" class="ml-2 text-blue-600">
          (已选择 {{ selectedStocks.length }} 只)
        </span>
      </div>

      <el-table
        :data="searchResults"
        max-height="400"
        stripe
        class="cursor-pointer"
        @row-click="toggleStock"
      >
        <el-table-column width="50" align="center">
          <template #default="{ row }">
            <el-checkbox
              :model-value="selectedSymbols.includes(row.symbol)"
              @click.stop="toggleStock(row)"
            />
          </template>
        </el-table-column>

        <el-table-column label="代码" prop="symbol" width="120" />

        <el-table-column label="名称" prop="name" width="150" />

        <el-table-column label="市场" width="80">
          <template #default="{ row }">
            <el-tag :type="row.market === 'A' ? 'danger' : row.market === 'HK' ? 'warning' : 'success'" size="small">
              {{ row.market }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="最新价" width="100" align="right">
          <template #default="{ row }">
            <span :class="getPriceChangeClass(row.change_rate)">
              {{ row.current_price.toFixed(2) }}
            </span>
          </template>
        </el-table-column>

        <el-table-column label="涨跌幅" width="100" align="right">
          <template #default="{ row }">
            <span :class="getPriceChangeClass(row.change_rate)" class="font-semibold">
              {{ formatChangeRate(row.change_rate) }}
            </span>
          </template>
        </el-table-column>

        <el-table-column label="成交量" align="right">
          <template #default="{ row }">
            <span class="text-gray-600">
              {{ formatVolume(row.volume) }}
            </span>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 无结果提示 -->
    <div
      v-else-if="searchKeyword && !searching"
      class="text-center py-12 text-gray-400"
    >
      <el-icon :size="48" class="mb-2"><Search /></el-icon>
      <div>未找到匹配的股票</div>
      <div class="text-sm mt-1">请尝试其他关键词</div>
    </div>

    <!-- 已选择的股票 -->
    <div v-if="selectedStocks.length > 0" class="mt-4 p-3 bg-blue-50 rounded">
      <div class="text-sm font-semibold mb-2">已选择：</div>
      <div class="flex gap-2 flex-wrap">
        <el-tag
          v-for="stock in selectedStocks"
          :key="stock.symbol"
          closable
          @close="toggleStock(stock)"
        >
          {{ stock.name }} ({{ stock.symbol }})
        </el-tag>
      </div>
    </div>

    <template #footer>
      <el-button @click="dialogVisible = false">取消</el-button>
      <el-button
        type="primary"
        :disabled="selectedStocks.length === 0"
        @click="handleConfirm"
      >
        确定 {{ selectedStocks.length > 0 ? `(${selectedStocks.length})` : '' }}
      </el-button>
    </template>
  </el-dialog>
</template>

<style scoped>
.search-results :deep(.el-table__row) {
  cursor: pointer;
}

.search-results :deep(.el-table__row:hover) {
  background-color: #f5f7fa;
}
</style>
