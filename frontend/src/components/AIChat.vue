<script setup lang="ts">
import { ref, computed, nextTick, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { chat } from '@/api/ai'
import type { ChatRequest } from '@/api/ai'

interface Message {
  id: number
  type: 'user' | 'assistant' | 'system'
  content: string
  timestamp: Date
  isStreaming?: boolean
}

interface Props {
  modelValue: boolean
  symbol?: string
  stockName?: string
  context?: string // 上下文信息（如之前的AI分析结果）
}

interface Emits {
  (e: 'update:modelValue', value: boolean): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

// 对话数据
const messages = ref<Message[]>([
  {
    id: 1,
    type: 'system',
    content: '您好！我是AI投资助手，可以帮您分析股票、解答疑问。请问有什么可以帮您的？',
    timestamp: new Date()
  }
])

const userInput = ref('')
const isAIThinking = ref(false)
const messageListRef = ref<HTMLElement | null>(null)

// 计算属性
const dialogVisible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const contextInfo = computed(() => {
  if (props.symbol && props.stockName) {
    return `当前股票: ${props.stockName} (${props.symbol})`
  }
  return ''
})

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
  await nextTick()
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
      context: context.slice(0, -1), // 排除刚添加的用户消息（它已经在message字段中）
      symbol: props.symbol,
      stock_name: props.stockName
    }

    // 调用AI API
    const response = await chat(request)

    // 添加AI回复
    const aiMessage: Message = {
      id: messages.value.length + 1,
      type: 'assistant',
      content: response.data.reply,
      timestamp: new Date(response.data.created_at),
      isStreaming: false
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
    await nextTick()
    scrollToBottom()
  }
}

// 备注: 已移除 generateAIResponse Mock函数
// 现在直接调用真实的AI API

// 滚动到底部
const scrollToBottom = () => {
  if (messageListRef.value) {
    messageListRef.value.scrollTop = messageListRef.value.scrollHeight
  }
}

// 获取消息时间格式
const formatTime = (date: Date) => {
  return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

// 快捷问题
const quickQuestions = [
  '现在适合加仓吗？',
  '止损位设在哪里？',
  '这只股票有什么风险？',
  '未来走势如何？'
]

// 点击快捷问题
const askQuickQuestion = (question: string) => {
  userInput.value = question
  sendMessage()
}

// 清空对话
const clearMessages = () => {
  messages.value = [
    {
      id: 1,
      type: 'system',
      content: '对话已清空。有什么可以帮您的？',
      timestamp: new Date()
    }
  ]
}

// 监听对话框打开
watch(() => props.modelValue, (newVal) => {
  if (newVal) {
    nextTick(() => {
      scrollToBottom()
    })
  }
})
</script>

<template>
  <el-dialog
    v-model="dialogVisible"
    :title="`💬 AI对话${contextInfo ? ` - ${contextInfo}` : ''}`"
    width="700px"
    :close-on-click-modal="false"
  >
    <div class="ai-chat">
      <!-- 上下文提示 -->
      <div v-if="context" class="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-lg text-sm text-blue-800">
        <div class="font-semibold mb-1">📌 上下文信息:</div>
        <div class="text-xs">{{ context }}</div>
      </div>

      <!-- 消息列表 -->
      <div ref="messageListRef" class="message-list mb-4 p-4 bg-gray-50 rounded-lg" style="height: 400px; overflow-y: auto;">
        <div
          v-for="message in messages"
          :key="message.id"
          class="message-item mb-4 last:mb-0"
        >
          <!-- 系统消息 -->
          <div v-if="message.type === 'system'" class="text-center">
            <div class="inline-block px-4 py-2 bg-gray-200 text-gray-700 rounded-full text-sm">
              {{ message.content }}
            </div>
          </div>

          <!-- 用户消息 -->
          <div v-else-if="message.type === 'user'" class="flex justify-end">
            <div class="max-w-[80%]">
              <div class="bg-blue-600 text-white rounded-lg px-4 py-2">
                {{ message.content }}
              </div>
              <div class="text-xs text-gray-500 mt-1 text-right">
                {{ formatTime(message.timestamp) }}
              </div>
            </div>
          </div>

          <!-- AI消息 -->
          <div v-else class="flex justify-start">
            <div class="max-w-[80%]">
              <div class="flex items-start gap-2">
                <div class="w-8 h-8 bg-gradient-to-br from-purple-400 to-purple-600 rounded-full flex items-center justify-center text-white font-bold flex-shrink-0">
                  AI
                </div>
                <div class="flex-1">
                  <div class="bg-white border border-gray-200 rounded-lg px-4 py-2 shadow-sm">
                    <div class="whitespace-pre-wrap text-sm">{{ message.content }}</div>
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
          <div class="flex items-start gap-2">
            <div class="w-8 h-8 bg-gradient-to-br from-purple-400 to-purple-600 rounded-full flex items-center justify-center text-white font-bold">
              AI
            </div>
            <div class="bg-white border border-gray-200 rounded-lg px-4 py-3 shadow-sm">
              <div class="flex gap-1">
                <span class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0s"></span>
                <span class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.2s"></span>
                <span class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.4s"></span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 快捷问题 -->
      <div v-if="messages.length <= 1" class="mb-4">
        <div class="text-xs text-gray-500 mb-2">💡 快捷提问:</div>
        <div class="flex flex-wrap gap-2">
          <button
            v-for="(question, index) in quickQuestions"
            :key="index"
            class="px-3 py-1 text-xs bg-white border border-gray-300 rounded-full hover:bg-blue-50 hover:border-blue-300 transition-colors"
            @click="askQuickQuestion(question)"
          >
            {{ question }}
          </button>
        </div>
      </div>

      <!-- 输入区 -->
      <div class="flex gap-2">
        <el-input
          v-model="userInput"
          placeholder="输入您的问题..."
          :disabled="isAIThinking"
          @keyup.enter="sendMessage"
        >
          <template #append>
            <el-button :loading="isAIThinking" type="primary" @click="sendMessage">
              发送
            </el-button>
          </template>
        </el-input>
      </div>

      <!-- 底部操作 -->
      <div class="mt-3 flex items-center justify-between text-xs text-gray-500">
        <div>
          提示: 按 Enter 发送消息
        </div>
        <button class="text-blue-600 hover:underline" @click="clearMessages">
          清空对话
        </button>
      </div>
    </div>
  </el-dialog>
</template>

<style scoped>
.ai-chat {
  /* 自定义样式 */
}

.message-list::-webkit-scrollbar {
  width: 6px;
}

.message-list::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.message-list::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 3px;
}

.message-list::-webkit-scrollbar-thumb:hover {
  background: #555;
}

@keyframes bounce {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-5px);
  }
}
</style>
