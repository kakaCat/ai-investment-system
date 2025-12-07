<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import AIChat from '@/components/AIChat.vue'
import SingleStockAnalysisDialog from '@/components/SingleStockAnalysisDialog.vue'

const router = useRouter()

const activeTab = ref<'single' | 'chat' | 'daily'>('single')

// 单股分析对话框
const singleAnalysisVisible = ref(false)

// AI对话
const chatVisible = ref(false)

// 打开单股分析
const openSingleAnalysis = () => {
  singleAnalysisVisible.value = true
}

// 打开AI对话
const openChat = () => {
  chatVisible.value = true
}

// 跳转到每日复盘
const goToDailyReview = () => {
  router.push('/review/daily')
}
</script>

<template>
  <div class="analysis-hub p-6">
    <!-- 页面标题 -->
    <div class="mb-6">
      <h1 class="text-2xl font-bold text-gray-900">🤖 AI分析中心</h1>
      <p class="text-gray-600 text-sm mt-1">基于真实AI和股票数据的智能投资分析</p>
      <div class="mt-2 text-xs text-gray-500">
        💡 支持 Ollama本地模型 / DeepSeek云端API | 数据源: Tushare / AkShare
      </div>
    </div>

    <!-- 功能卡片 -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
      <div
        @click="openSingleAnalysis"
        class="bg-white rounded-lg border shadow-sm p-6 cursor-pointer hover:shadow-md hover:border-blue-400 transition group"
      >
        <div class="text-4xl mb-3 group-hover:scale-110 transition-transform">📈</div>
        <h3 class="text-lg font-semibold text-gray-900 mb-2">单股AI分析</h3>
        <p class="text-sm text-gray-600 mb-3">基本面、技术面、估值的深度AI分析</p>
        <el-tag type="success" size="small">✅ 已集成真实AI</el-tag>
      </div>

      <div
        @click="openChat"
        class="bg-white rounded-lg border shadow-sm p-6 cursor-pointer hover:shadow-md hover:border-purple-400 transition group"
      >
        <div class="text-4xl mb-3 group-hover:scale-110 transition-transform">💬</div>
        <h3 class="text-lg font-semibold text-gray-900 mb-2">AI投资对话</h3>
        <p class="text-sm text-gray-600 mb-3">与AI助手实时对话，咨询投资问题</p>
        <el-tag type="success" size="small">✅ 已集成真实AI</el-tag>
      </div>

      <div
        @click="goToDailyReview"
        class="bg-white rounded-lg border shadow-sm p-6 cursor-pointer hover:shadow-md hover:border-orange-400 transition group"
      >
        <div class="text-4xl mb-3 group-hover:scale-110 transition-transform">📅</div>
        <h3 class="text-lg font-semibold text-gray-900 mb-2">每日市场复盘</h3>
        <p class="text-sm text-gray-600 mb-3">AI生成每日市场总结和明日关注点</p>
        <el-tag type="warning" size="small">⏳ 开发中</el-tag>
      </div>
    </div>

    <!-- AI功能介绍 -->
    <div class="bg-white rounded-lg border shadow-sm p-6">
      <h2 class="text-lg font-semibold text-gray-900 mb-4">✨ AI功能亮点</h2>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div class="flex gap-3">
          <div class="text-2xl">🎯</div>
          <div>
            <h4 class="font-semibold text-gray-900 text-sm">真实AI分析</h4>
            <p class="text-xs text-gray-600 mt-1">基于Ollama本地模型或DeepSeek云端API，提供专业级投资分析</p>
          </div>
        </div>

        <div class="flex gap-3">
          <div class="text-2xl">📊</div>
          <div>
            <h4 class="font-semibold text-gray-900 text-sm">真实股票数据</h4>
            <p class="text-xs text-gray-600 mt-1">集成Tushare/AkShare数据源，获取实时行情和基本面数据</p>
          </div>
        </div>

        <div class="flex gap-3">
          <div class="text-2xl">⚡</div>
          <div>
            <h4 class="font-semibold text-gray-900 text-sm">快速响应</h4>
            <p class="text-xs text-gray-600 mt-1">单次分析约30秒，云端API响应更快（约3秒）</p>
          </div>
        </div>

        <div class="flex gap-3">
          <div class="text-2xl">💰</div>
          <div>
            <h4 class="font-semibold text-gray-900 text-sm">零成本方案</h4>
            <p class="text-xs text-gray-600 mt-1">Ollama本地+AkShare免费数据源，完全免费使用</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 组件：单股分析对话框 -->
    <SingleStockAnalysisDialog
      v-model:visible="singleAnalysisVisible"
    />

    <!-- 组件：AI对话 -->
    <AIChat
      v-model="chatVisible"
    />
  </div>
</template>

<style scoped>
.analysis-hub {
  background-color: #f5f5f5;
}
</style>
