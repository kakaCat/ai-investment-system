<script setup lang="ts">
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'

interface Props {
  visible: boolean
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'update:visible': [visible: boolean]
  confirm: [data: any]
}>()

const dialogVisible = computed({
  get: () => props.visible,
  set: (val) => emit('update:visible', val)
})

// 表单数据
const formData = ref({
  deepseek_api_key: '',
  tushare_api_token: '',
  akshare_enabled: false
})

// 显示/隐藏密钥
const showDeepSeekKey = ref(false)
const showTushareKey = ref(false)

// 获取当前配置
const loadConfig = async () => {
  try {
    // Mock 数据
    await new Promise(resolve => setTimeout(resolve, 300))
    formData.value = {
      deepseek_api_key: 'sk-*********************',
      tushare_api_token: '*********************',
      akshare_enabled: true
    }
  } catch (error) {
    ElMessage.error('加载配置失败')
  }
}

// 测试API密钥
const testing = ref({
  deepseek: false,
  tushare: false
})

const testDeepSeek = async () => {
  if (!formData.value.deepseek_api_key) {
    ElMessage.warning('请输入 DeepSeek API Key')
    return
  }

  testing.value.deepseek = true
  try {
    await new Promise(resolve => setTimeout(resolve, 1000))
    ElMessage.success('DeepSeek API 连接成功')
  } catch (error) {
    ElMessage.error('DeepSeek API 连接失败')
  } finally {
    testing.value.deepseek = false
  }
}

const testTushare = async () => {
  if (!formData.value.tushare_api_token) {
    ElMessage.warning('请输入 Tushare Token')
    return
  }

  testing.value.tushare = true
  try {
    await new Promise(resolve => setTimeout(resolve, 1000))
    ElMessage.success('Tushare API 连接成功')
  } catch (error) {
    ElMessage.error('Tushare API 连接失败')
  } finally {
    testing.value.tushare = false
  }
}

// 提交
const submitting = ref(false)
const handleSubmit = async () => {
  if (!formData.value.deepseek_api_key) {
    ElMessage.warning('请输入 DeepSeek API Key')
    return
  }

  submitting.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 500))

    emit('confirm', formData.value)
    ElMessage.success('API 密钥配置已保存')
    dialogVisible.value = false
  } catch (error) {
    ElMessage.error('保存失败')
  } finally {
    submitting.value = false
  }
}

// 监听弹框打开
import { watch } from 'vue'
watch(() => props.visible, (val) => {
  if (val) {
    loadConfig()
  }
})
</script>

<template>
  <el-dialog
    v-model="dialogVisible"
    title="API 密钥配置"
    width="600px"
    :close-on-click-modal="false"
  >
    <el-form :model="formData" label-width="140px">
      <!-- DeepSeek API -->
      <el-divider content-position="left">
        <span class="font-semibold">DeepSeek API</span>
      </el-divider>

      <el-form-item label="API Key" required>
        <div class="flex gap-2" style="width: 100%">
          <el-input
            v-model="formData.deepseek_api_key"
            :type="showDeepSeekKey ? 'text' : 'password'"
            placeholder="输入 DeepSeek API Key"
            show-password
          />
          <el-button :loading="testing.deepseek" @click="testDeepSeek">
            测试连接
          </el-button>
        </div>
      </el-form-item>

      <el-form-item>
        <el-alert type="info" :closable="false">
          <template #title>
            <div class="text-sm">
              DeepSeek API 用于 AI 投资分析功能。
              <a
                href="https://platform.deepseek.com"
                target="_blank"
                class="text-blue-600"
              >
                获取 API Key
              </a>
            </div>
          </template>
        </el-alert>
      </el-form-item>

      <!-- Tushare API -->
      <el-divider content-position="left">
        <span class="font-semibold">Tushare API</span>
      </el-divider>

      <el-form-item label="Token">
        <div class="flex gap-2" style="width: 100%">
          <el-input
            v-model="formData.tushare_api_token"
            :type="showTushareKey ? 'text' : 'password'"
            placeholder="输入 Tushare Token（可选）"
            show-password
          />
          <el-button :loading="testing.tushare" @click="testTushare">
            测试连接
          </el-button>
        </div>
      </el-form-item>

      <el-form-item>
        <el-alert type="info" :closable="false">
          <template #title>
            <div class="text-sm">
              Tushare 提供专业金融数据接口。
              <a
                href="https://tushare.pro"
                target="_blank"
                class="text-blue-600"
              >
                注册获取 Token
              </a>
            </div>
          </template>
        </el-alert>
      </el-form-item>

      <!-- AkShare -->
      <el-divider content-position="left">
        <span class="font-semibold">AkShare</span>
      </el-divider>

      <el-form-item label="启用 AkShare">
        <el-switch v-model="formData.akshare_enabled" />
        <div class="ml-4 text-sm text-gray-500">
          免费的 A股/港股/美股数据源
        </div>
      </el-form-item>

      <el-form-item>
        <el-alert type="success" :closable="false">
          <template #title>
            <div class="text-sm">
              AkShare 无需 API Key，开启后即可使用。适合个人用户。
            </div>
          </template>
        </el-alert>
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="dialogVisible = false">取消</el-button>
      <el-button type="primary" :loading="submitting" @click="handleSubmit">
        保存配置
      </el-button>
    </template>
  </el-dialog>
</template>
