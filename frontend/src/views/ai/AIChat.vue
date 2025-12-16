<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { chat } from '@/api/ai'
import type { ChatRequest } from '@/api/ai'

const route = useRoute()

// 从URL参数获取股票信息
const symbol = ref(route.query.symbol as string || '')
const stockName = ref(route.query.stockName as string || '')

interface Message {
  id: number
  type: 'user' | 'assistant' | 'system'
  content: string
  timestamp: Date
}

// 对话数据
const messages = ref<Message[]>([])
const userInput = ref('')
const isAIThinking = ref(false)
const messageListRef = ref<HTMLElement | null>(null)

// 初始化欢迎消息
const initWelcomeMessage = () => {
  let welcomeContent = '您好！我是AI投资助手，可以帮您分析股票、解答投资疑问。'

  if (symbol.value && stockName.value) {
    welcomeContent += `\n\n当前上下文：${stockName.value}（${symbol.value}）`
  }

  welcomeContent += '\n\n请问有什么可以帮您的？'

  messages.value = [{
    id: 1,
    type: 'system',
    content: welcomeContent,
    timestamp: new Date()
  }]
}

// 发送消息
const sendMessage = async () => {
  const content = userInput.value.trim()
  if (!content) {
    ElMessage.warning('请输入消息')
    return
  }

  // 添加用户消息
  const userMessage: Message = {
    id: messages.value.length + 1,
    type: 'user',
    content,
    timestamp: new Date()
  }
  messages.value.push(userMessage)
  userInput.value = ''

  // 滚动到底部
  scrollToBottom()

  // 调用真实AI API
  isAIThinking.value = true

  try {
    // 构建对话上下文（最近10条消息）
    const context = messages.value
      .filter(m => m.type !== 'system')
      .slice(-10)
      .map(m => ({
        role: m.type === 'user' ? 'user' as const : 'assistant' as const,
        content: m.content
      }))

    // 构建请求
    const request: ChatRequest = {
      message: content,
      context: context.slice(0, -1), // 排除刚添加的用户消息
      symbol: symbol.value || undefined,
      stock_name: stockName.value || undefined
    }

    // 调用AI API
    const response = await chat(request)

    // 添加AI回复
    const aiMessage: Message = {
      id: messages.value.length + 1,
      type: 'assistant',
      content: response.data.reply,
      timestamp: new Date(response.data.created_at)
    }

    messages.value.push(aiMessage)
  } catch (error: any) {
    console.error('AI对话失败:', error)

    // 添加错误消息
    const errorMessage: Message = {
      id: messages.value.length + 1,
      type: 'assistant',
      content: `抱歉，AI服务暂时不可用。错误信息: ${error.message || '未知错误'}\n\n请稍后再试，或联系管理员。`,
      timestamp: new Date()
    }
    messages.value.push(errorMessage)
  } finally {
    isAIThinking.value = false
    scrollToBottom()
  }
}

// 滚动到底部
const scrollToBottom = () => {
  setTimeout(() => {
    if (messageListRef.value) {
      messageListRef.value.scrollTop = messageListRef.value.scrollHeight
    }
  }, 100)
}

// 获取消息时间格式
const formatTime = (date: Date) => {
  return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

// 快捷问题
const quickQuestions = [
  '价值投资的核心是什么？',
  '如何判断一只股票是否值得投资？',
  '什么时候应该止损？',
  '分散投资有什么好处？',
  '如何看待市场波动？',
  '长期持有还是波段操作？'
]

// 点击快捷问题
const askQuickQuestion = (question: string) => {
  userInput.value = question
  sendMessage()
}

// 清空对话
const clearMessages = () => {
  initWelcomeMessage()
  ElMessage.success('对话已清空')
}

// 页面加载
onMounted(() => {
  initWelcomeMessage()
})
</script>

<template>
  <div class="ai-chat-page min-h-screen bg-gradient-to-br from-purple-50 via-blue-50 to-indigo-50 p-6">
    <!-- 头部 -->
    <div class="max-w-5xl mx-auto mb-6">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-3xl font-bold text-gray-900 mb-2">💬 AI投资顾问</h1>
          <p class="text-gray-600">
            <span v-if="symbol && stockName">当前讨论: {{ stockName }} ({{ symbol }})</span>
            <span v-else>与AI智能助手对话，获取投资建议和市场洞察</span>
          </p>
        </div>
        <el-button type="danger" plain @click="clearMessages">
          清空对话
        </el-button>
      </div>
    </div>

    <!-- 主对话区 -->
    <div class="max-w-5xl mx-auto">
      <div class="bg-white rounded-2xl shadow-2xl overflow-hidden" style="height: calc(100vh - 220px);">
        <!-- 消息列表 -->
        <div
          ref="messageListRef"
          class="message-list p-6 overflow-y-auto"
          style="height: calc(100% - 140px);"
        >
          <div
            v-for="message in messages"
            :key="message.id"
            class="message-item mb-6 last:mb-0"
          >
            <!-- 系统消息 -->
            <div v-if="message.type === 'system'" class="text-center">
              <div class="inline-block px-6 py-3 bg-gradient-to-r from-purple-100 to-blue-100 text-gray-800 rounded-2xl text-sm shadow-sm">
                <div class="whitespace-pre-wrap">{{ message.content }}</div>
              </div>
            </div>

            <!-- 用户消息 -->
            <div v-else-if="message.type === 'user'" class="flex justify-end">
              <div class="max-w-[70%]">
                <div class="bg-gradient-to-r from-blue-600 to-blue-500 text-white rounded-2xl px-5 py-3 shadow-lg">
                  <div class="whitespace-pre-wrap">{{ message.content }}</div>
                </div>
                <div class="text-xs text-gray-500 mt-1 text-right">
                  {{ formatTime(message.timestamp) }}
                </div>
              </div>
            </div>

            <!-- AI消息 -->
            <div v-else class="flex justify-start">
              <div class="max-w-[70%]">
                <div class="flex items-start gap-3">
                  <div class="w-10 h-10 bg-gradient-to-br from-purple-500 to-indigo-600 rounded-full flex items-center justify-center text-white font-bold flex-shrink-0 shadow-lg">
                    AI
                  </div>
                  <div class="flex-1">
                    <div class="bg-white border-2 border-gray-100 rounded-2xl px-5 py-3 shadow-lg">
                      <div class="whitespace-pre-wrap text-sm leading-relaxed">{{ message.content }}</div>
                    </div>
                    <div class="text-xs text-gray-500 mt-1">
                      {{ formatTime(message.timestamp) }}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- AI思考中 -->
          <div v-if="isAIThinking" class="flex justify-start">
            <div class="flex items-start gap-3">
              <div class="w-10 h-10 bg-gradient-to-br from-purple-500 to-indigo-600 rounded-full flex items-center justify-center text-white font-bold shadow-lg">
                AI
              </div>
              <div class="bg-white border-2 border-gray-100 rounded-2xl px-5 py-4 shadow-lg">
                <div class="flex gap-1">
                  <span class="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style="animation-delay: 0s"></span>
                  <span class="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style="animation-delay: 0.2s"></span>
                  <span class="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style="animation-delay: 0.4s"></span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 快捷问题 (仅在初始时显示) -->
        <div v-if="messages.length <= 1" class="px-6 py-3 bg-gray-50 border-t">
          <div class="text-xs text-gray-600 mb-2">💡 快捷提问:</div>
          <div class="flex flex-wrap gap-2">
            <button
              v-for="(question, index) in quickQuestions"
              :key="index"
              class="px-3 py-1.5 text-xs bg-white border border-gray-300 rounded-full hover:bg-purple-50 hover:border-purple-300 transition-all shadow-sm hover:shadow"
              @click="askQuickQuestion(question)"
            >
              {{ question }}
            </button>
          </div>
        </div>

        <!-- 输入区 -->
        <div class="p-6 bg-gray-50 border-t-2">
          <div class="flex gap-3">
            <el-input
              v-model="userInput"
              placeholder="输入您的问题，按 Enter 发送..."
              size="large"
              :disabled="isAIThinking"
              class="flex-1"
              @keyup.enter="sendMessage"
            />
            <el-button
              :loading="isAIThinking"
              type="primary"
              size="large"
              class="px-8"
              @click="sendMessage"
            >
              <template v-if="!isAIThinking">
                发送
              </template>
              <template v-else>
                思考中...
              </template>
            </el-button>
          </div>

          <div class="mt-2 text-xs text-gray-500 text-center">
            提示: 按 Enter 快速发送消息
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.message-list::-webkit-scrollbar {
  width: 8px;
}

.message-list::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.message-list::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

.message-list::-webkit-scrollbar-thumb:hover {
  background: #a1a1a1;
}

@keyframes bounce {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-6px);
  }
}
</style>
