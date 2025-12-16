<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import ApiKeyConfigDialog from '@/components/ApiKeyConfigDialog.vue'

const router = useRouter()

const activeTab = ref<'profile' | 'security' | 'api' | 'preferences' | 'notifications'>('profile')

// 个人信息表单
const profileForm = ref({
  username: 'demo_user',
  email: 'demo@example.com',
  nickname: '演示用户',
  phone: '138****8888',
  avatar: ''
})

// 密码表单
const passwordForm = ref({
  old_password: '',
  new_password: '',
  confirm_password: ''
})

// 偏好设置
const preferences = ref({
  theme: 'light',
  language: 'zh-CN',
  default_account: null as number | null,
  date_format: 'YYYY-MM-DD',
  currency: 'CNY'
})

// 通知设置
const notifications = ref({
  email_enabled: true,
  sms_enabled: false,
  push_enabled: true,
  event_alerts: true,
  price_alerts: true,
  trade_confirmations: true,
  weekly_report: true
})

// API配置弹框
const apiConfigVisible = ref(false)

// 保存个人信息
const savingProfile = ref(false)
const saveProfile = async () => {
  savingProfile.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 500))
    ElMessage.success('个人信息已保存')
  } catch (error) {
    ElMessage.error('保存失败')
  } finally {
    savingProfile.value = false
  }
}

// 修改密码
const changingPassword = ref(false)
const changePassword = async () => {
  if (!passwordForm.value.old_password) {
    ElMessage.warning('请输入当前密码')
    return
  }
  if (!passwordForm.value.new_password) {
    ElMessage.warning('请输入新密码')
    return
  }
  if (passwordForm.value.new_password !== passwordForm.value.confirm_password) {
    ElMessage.warning('两次输入的密码不一致')
    return
  }
  if (passwordForm.value.new_password.length < 6) {
    ElMessage.warning('密码长度不能少于6位')
    return
  }

  changingPassword.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 500))
    ElMessage.success('密码修改成功，请重新登录')
    // 清空表单
    passwordForm.value = {
      old_password: '',
      new_password: '',
      confirm_password: ''
    }
  } catch (error) {
    ElMessage.error('密码修改失败')
  } finally {
    changingPassword.value = false
  }
}

// 保存偏好设置
const savingPreferences = ref(false)
const savePreferences = async () => {
  savingPreferences.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 500))
    ElMessage.success('偏好设置已保存')
  } catch (error) {
    ElMessage.error('保存失败')
  } finally {
    savingPreferences.value = false
  }
}

// 保存通知设置
const savingNotifications = ref(false)
const saveNotifications = async () => {
  savingNotifications.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 500))
    ElMessage.success('通知设置已保存')
  } catch (error) {
    ElMessage.error('保存失败')
  } finally {
    savingNotifications.value = false
  }
}

// 上传头像
const uploadAvatar = () => {
  ElMessage.info('上传头像功能开发中')
}

// Mock 账户列表
const accounts = ref([
  { account_id: 1, account_name: '中信证券-A股账户' },
  { account_id: 2, account_name: '富途证券-港股账户' },
  { account_id: 3, account_name: '盈透证券-美股账户' }
])

// 返回
const goBack = () => {
  router.back()
}

// 保存设置
const saveSettings = () => {
  ElMessage.success('设置已保存')
}
</script>

<template>
  <div class="settings-page p-6">
    <!-- 页面标题 -->
    <div class="mb-6">
      <h1 class="text-2xl font-bold text-gray-900">⚙️ 系统设置</h1>
      <p class="text-gray-600 text-sm mt-1">管理您的账户和应用偏好设置</p>
    </div>

    <!-- Tab 切换 -->
    <div class="bg-white rounded-lg border shadow-sm overflow-hidden">
        <div class="border-b border-gray-200">
          <div class="flex">
            <button
              :class="[
                'px-6 py-4 text-sm font-medium border-b-2 transition',
                activeTab === 'profile'
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-600 hover:text-gray-900'
              ]"
              @click="activeTab = 'profile'"
            >
              个人信息
            </button>
            <button
              :class="[
                'px-6 py-4 text-sm font-medium border-b-2 transition',
                activeTab === 'security'
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-600 hover:text-gray-900'
              ]"
              @click="activeTab = 'security'"
            >
              安全设置
            </button>
            <button
              :class="[
                'px-6 py-4 text-sm font-medium border-b-2 transition',
                activeTab === 'api'
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-600 hover:text-gray-900'
              ]"
              @click="activeTab = 'api'"
            >
              API配置
            </button>
            <button
              :class="[
                'px-6 py-4 text-sm font-medium border-b-2 transition',
                activeTab === 'preferences'
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-600 hover:text-gray-900'
              ]"
              @click="activeTab = 'preferences'"
            >
              偏好设置
            </button>
            <button
              :class="[
                'px-6 py-4 text-sm font-medium border-b-2 transition',
                activeTab === 'notifications'
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-600 hover:text-gray-900'
              ]"
              @click="activeTab = 'notifications'"
            >
              通知设置
            </button>
          </div>
        </div>

      <div class="p-6 max-w-4xl">

      <!-- 个人信息 -->
      <div v-if="activeTab === 'profile'" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-900 mb-2">用户名</label>
          <input v-model="profileForm.username" type="text" disabled class="w-full px-4 py-2 border border-gray-300 rounded-lg bg-gray-50 cursor-not-allowed" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-900 mb-2">昵称</label>
          <input v-model="profileForm.nickname" type="text" placeholder="输入昵称" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-900 mb-2">邮箱</label>
          <input v-model="profileForm.email" type="email" placeholder="输入邮箱" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-900 mb-2">手机号</label>
          <input v-model="profileForm.phone" type="text" placeholder="输入手机号" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" />
        </div>
        <el-button type="primary" @click="saveProfile">保存</el-button>
      </div>

      <!-- 安全设置 -->
      <div v-if="activeTab === 'security'" class="space-y-4">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">修改密码</h3>
        <div>
          <label class="block text-sm font-medium text-gray-900 mb-2">当前密码</label>
          <input v-model="passwordForm.old_password" type="password" placeholder="输入当前密码" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-900 mb-2">新密码</label>
          <input v-model="passwordForm.new_password" type="password" placeholder="输入新密码（至少6位）" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-900 mb-2">确认新密码</label>
          <input v-model="passwordForm.confirm_password" type="password" placeholder="再次输入新密码" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" />
        </div>
        <el-button type="primary" @click="changePassword">修改密码</el-button>
      </div>

      <!-- API配置 -->
      <div v-if="activeTab === 'api'" class="space-y-4">
        <div class="border border-blue-200 bg-blue-50 rounded-lg p-4 mb-4">
          <div class="text-sm text-blue-900">
            配置 API 密钥后即可使用 AI 分析和数据获取功能
          </div>
        </div>

        <div class="border border-gray-200 rounded-lg p-4">
          <div class="mb-2 flex items-center justify-between">
            <div>
              <div class="font-semibold text-gray-900">DeepSeek API</div>
              <div class="text-sm text-gray-500">用于 AI 投资分析功能</div>
            </div>
            <span class="inline-block px-3 py-1 bg-green-100 text-green-800 text-xs font-medium rounded">已配置</span>
          </div>
          <div class="text-sm text-gray-600">
            API Key: sk-*********************
          </div>
        </div>

        <div class="border border-gray-200 rounded-lg p-4">
          <div class="mb-2 flex items-center justify-between">
            <div>
              <div class="font-semibold text-gray-900">Tushare API</div>
              <div class="text-sm text-gray-500">专业金融数据接口</div>
            </div>
            <span class="inline-block px-3 py-1 bg-gray-100 text-gray-800 text-xs font-medium rounded">未配置</span>
          </div>
          <div class="text-sm text-gray-600">Token: 未设置</div>
        </div>

        <div class="border border-gray-200 rounded-lg p-4">
          <div class="mb-2 flex items-center justify-between">
            <div>
              <div class="font-semibold text-gray-900">AkShare</div>
              <div class="text-sm text-gray-500">免费股票数据源</div>
            </div>
            <span class="inline-block px-3 py-1 bg-green-100 text-green-800 text-xs font-medium rounded">已启用</span>
          </div>
          <div class="text-sm text-gray-600">无需 API Key，开箱即用</div>
        </div>

        <el-button type="primary" @click="apiConfigVisible = true">配置 API 密钥</el-button>
      </div>

      <!-- 偏好设置 -->
      <div v-if="activeTab === 'preferences'" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-900 mb-2">主题</label>
          <div class="space-y-2">
            <label class="flex items-center">
              <input v-model="preferences.theme" type="radio" value="light" class="w-4 h-4" />
              <span class="ml-2 text-sm text-gray-700">浅色</span>
            </label>
            <label class="flex items-center">
              <input v-model="preferences.theme" type="radio" value="dark" class="w-4 h-4" />
              <span class="ml-2 text-sm text-gray-700">深色</span>
            </label>
            <label class="flex items-center">
              <input v-model="preferences.theme" type="radio" value="auto" class="w-4 h-4" />
              <span class="ml-2 text-sm text-gray-700">跟随系统</span>
            </label>
          </div>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-900 mb-2">语言</label>
          <select v-model="preferences.language" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">
            <option value="zh-CN">简体中文</option>
            <option value="en-US">English</option>
          </select>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-900 mb-2">默认账户</label>
          <select v-model="preferences.default_account" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">
            <option :value="null">无</option>
            <option v-for="account in accounts" :key="account.account_id" :value="account.account_id">
              {{ account.account_name }}
            </option>
          </select>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-900 mb-2">日期格式</label>
          <select v-model="preferences.date_format" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">
            <option value="YYYY-MM-DD">YYYY-MM-DD</option>
            <option value="MM/DD/YYYY">MM/DD/YYYY</option>
            <option value="DD/MM/YYYY">DD/MM/YYYY</option>
          </select>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-900 mb-2">货币单位</label>
          <select v-model="preferences.currency" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">
            <option value="CNY">人民币 (¥)</option>
            <option value="USD">美元 ($)</option>
            <option value="HKD">港币 (HK$)</option>
          </select>
        </div>

        <el-button type="primary" @click="savePreferences">保存</el-button>
      </div>

      <!-- 通知设置 -->
      <div v-if="activeTab === 'notifications'" class="space-y-6">
        <div>
          <h3 class="text-sm font-semibold text-gray-900 mb-4">消息通道</h3>
          <div class="space-y-3">
            <label class="flex items-center">
              <input v-model="notifications.email_enabled" type="checkbox" class="w-4 h-4" />
              <span class="ml-2 text-sm text-gray-700">邮件通知</span>
            </label>
            <label class="flex items-center">
              <input v-model="notifications.sms_enabled" type="checkbox" class="w-4 h-4" />
              <span class="ml-2 text-sm text-gray-700">短信通知</span>
            </label>
            <label class="flex items-center">
              <input v-model="notifications.push_enabled" type="checkbox" class="w-4 h-4" />
              <span class="ml-2 text-sm text-gray-700">站内推送</span>
            </label>
          </div>
        </div>

        <div class="border-t border-gray-200 pt-6">
          <h3 class="text-sm font-semibold text-gray-900 mb-4">通知类型</h3>
          <div class="space-y-3">
            <div>
              <label class="flex items-center">
                <input v-model="notifications.event_alerts" type="checkbox" class="w-4 h-4" />
                <span class="ml-2 text-sm text-gray-700">事件提醒</span>
              </label>
              <p class="ml-6 text-xs text-gray-500">重要政策、公司公告等事件提醒</p>
            </div>
            <div>
              <label class="flex items-center">
                <input v-model="notifications.price_alerts" type="checkbox" class="w-4 h-4" />
                <span class="ml-2 text-sm text-gray-700">价格提醒</span>
              </label>
              <p class="ml-6 text-xs text-gray-500">股票价格达到目标价时提醒</p>
            </div>
            <div>
              <label class="flex items-center">
                <input v-model="notifications.trade_confirmations" type="checkbox" class="w-4 h-4" />
                <span class="ml-2 text-sm text-gray-700">交易确认</span>
              </label>
              <p class="ml-6 text-xs text-gray-500">交易记录保存后发送确认通知</p>
            </div>
            <div>
              <label class="flex items-center">
                <input v-model="notifications.weekly_report" type="checkbox" class="w-4 h-4" />
                <span class="ml-2 text-sm text-gray-700">周报推送</span>
              </label>
              <p class="ml-6 text-xs text-gray-500">每周发送投资组合周报</p>
            </div>
          </div>
        </div>

        <el-button type="primary" @click="saveNotifications">保存</el-button>
      </div>

      </div>
    </div>

  <!-- API配置弹框 -->
  <api-key-config-dialog
    v-model:visible="apiConfigVisible"
    @confirm="() => ElMessage.success('API 配置已更新')"
  />
  </div>
</template>

<style scoped>
.settings-page {
  background-color: #f5f5f5;
}
</style>
