<script setup lang="ts">
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { WatchlistItem } from '@/types/account'

interface Props {
  watchlist: WatchlistItem[]
  loading?: boolean
}
const props = withDefaults(defineProps<Props>(), {
  loading: false
})

interface Emits {
  (e: 'remove', item: WatchlistItem): void
  (e: 'refresh'): void
}
const emit = defineEmits<Emits>()

const router = useRouter()

// 查看详情
const viewDetail = (item: WatchlistItem) => {
  ElMessage.info(`查看详情: ${item.name} (${item.symbol})`)
  // router.push({
  //   name: 'StockDetail',
  //   params: { symbol: item.symbol }
  // })
}

// 记录建仓
const recordBuy = (item: WatchlistItem) => {
  ElMessage.info(`记录建仓: ${item.name} (${item.symbol})`)
  // router.push({
  //   name: 'TradeCreate',
  //   query: {
  //     symbol: item.symbol,
  //     action: 'buy'
  //   }
  // })
}

// 移除关注
const removeFromWatchlist = async (item: WatchlistItem) => {
  try {
    await ElMessageBox.confirm(`确定要移除关注「${item.name}」吗？`, '确认移除', {
      type: 'warning'
    })
    emit('remove', item)
    ElMessage.success('移除成功')
  } catch (error) {
    // 用户取消
  }
}
</script>

<template>
  <el-table :data="watchlist" :loading="loading" stripe>
    <el-table-column prop="symbol" label="代码" width="100" />
    <el-table-column prop="name" label="名称" width="120" />
    <el-table-column prop="current_price" label="现价" width="100" align="right">
      <template #default="{ row }"> ¥{{ row.current_price?.toFixed(2) ?? '--' }} </template>
    </el-table-column>
    <el-table-column prop="target_price" label="目标价" width="100" align="right">
      <template #default="{ row }">
        <span v-if="row.target_price"> ¥{{ row.target_price.toFixed(2) }} </span>
        <span v-else class="text-gray-400">--</span>
      </template>
    </el-table-column>
    <el-table-column prop="notes" label="备注" min-width="200">
      <template #default="{ row }">
        <span class="text-gray-600">{{ row.notes || '--' }}</span>
      </template>
    </el-table-column>
    <el-table-column prop="created_at" label="关注时间" width="180" />
    <el-table-column label="操作" width="200" fixed="right">
      <template #default="{ row }">
        <el-button link type="primary" size="small" @click="viewDetail(row)">
          详情
        </el-button>
        <el-button link type="success" size="small" @click="recordBuy(row)">
          记录建仓
        </el-button>
        <el-button link type="danger" size="small" @click="removeFromWatchlist(row)">
          移除
        </el-button>
      </template>
    </el-table-column>
  </el-table>
</template>
