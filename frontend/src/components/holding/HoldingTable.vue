<script setup lang="ts">
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { Holding } from '@/types/account'

interface Props {
  holdings: Holding[]
  loading?: boolean
}
const props = withDefaults(defineProps<Props>(), {
  loading: false
})

const router = useRouter()

// 查看股票详情
const viewStockDetail = (holding: Holding) => {
  ElMessage.info(`查看股票详情: ${holding.name} (${holding.symbol})`)
  // router.push({
  //   name: 'StockDetail',
  //   params: { symbol: holding.symbol }
  // })
}

// 记录交易
const recordTrade = (holding: Holding) => {
  ElMessage.info(`记录交易: ${holding.name} (${holding.symbol})`)
  // router.push({
  //   name: 'TradeCreate',
  //   query: { symbol: holding.symbol }
  // })
}

// AI 分析
const analyzeStock = (holding: Holding) => {
  ElMessage.info(`AI分析: ${holding.name} (${holding.symbol})`)
  // router.push({
  //   name: 'AIAnalysis',
  //   query: { symbol: holding.symbol }
  // })
}
</script>

<template>
  <el-table :data="holdings" :loading="loading" stripe>
    <el-table-column prop="symbol" label="代码" width="100" />
    <el-table-column prop="name" label="名称" width="120" />
    <el-table-column prop="quantity" label="持仓数量" width="100" align="right">
      <template #default="{ row }">
        {{ row.quantity.toLocaleString() }}
      </template>
    </el-table-column>
    <el-table-column prop="avg_cost" label="成本价" width="100" align="right">
      <template #default="{ row }"> ¥{{ row.avg_cost.toFixed(2) }} </template>
    </el-table-column>
    <el-table-column prop="current_price" label="现价" width="100" align="right">
      <template #default="{ row }"> ¥{{ row.current_price.toFixed(2) }} </template>
    </el-table-column>
    <el-table-column prop="market_value" label="市值" width="120" align="right">
      <template #default="{ row }"> ¥{{ row.market_value.toLocaleString() }} </template>
    </el-table-column>
    <el-table-column label="盈亏" width="150" align="right">
      <template #default="{ row }">
        <div :class="row.profit_loss >= 0 ? 'profit-text' : 'loss-text'">
          {{ row.profit_loss >= 0 ? '+' : '' }}¥{{ row.profit_loss.toLocaleString() }}
          <span class="ml-2">
            ({{ row.profit_loss >= 0 ? '+' : '' }}{{ row.profit_loss_rate.toFixed(2) }}%)
          </span>
        </div>
      </template>
    </el-table-column>
    <el-table-column label="操作" width="240" fixed="right">
      <template #default="{ row }">
        <el-button link type="primary" size="small" @click="viewStockDetail(row)">
          详情
        </el-button>
        <el-button link type="primary" size="small" @click="recordTrade(row)">
          记录交易
        </el-button>
        <el-button link type="primary" size="small" @click="analyzeStock(row)">
          AI分析
        </el-button>
      </template>
    </el-table-column>
  </el-table>
</template>
