<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const router = useRouter()

const loginForm = ref({
  username: 'testuser',
  password: 'Test123456'
})

const loading = ref(false)

const handleLogin = async () => {
  loading.value = true
  try {
    // 调用真实的后端登录API
    // 后端使用OAuth2PasswordRequestForm，需要发送form-data格式
    const formData = new URLSearchParams()
    formData.append('username', loginForm.value.username)
    formData.append('password', loginForm.value.password)

    const response = await axios.post('http://localhost:8000/api/v1/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    })

    // 保存真实的 token 和用户信息
    localStorage.setItem('token', response.data.access_token)
    localStorage.setItem('user', JSON.stringify(response.data.user))

    ElMessage.success('登录成功')

    // 等待一小段时间确保localStorage写入完成
    await new Promise(resolve => setTimeout(resolve, 100))

    // 跳转到首页
    await router.push('/')
  } catch (error: any) {
    console.error('登录失败:', error)
    ElMessage.error(error.response?.data?.detail || '登录失败，请检查用户名和密码')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-500 to-purple-600">
    <el-card class="w-96">
      <template #header>
        <div class="text-center">
          <h2 class="text-2xl font-bold text-gray-800">投资管理系统</h2>
          <p class="text-gray-500 text-sm mt-2">欢迎登录</p>
        </div>
      </template>

      <el-form :model="loginForm" label-width="80px">
        <el-form-item label="用户名">
          <el-input v-model="loginForm.username" placeholder="请输入用户名" />
        </el-form-item>

        <el-form-item label="密码">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="请输入密码"
            @keyup.enter="handleLogin"
          />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" :loading="loading" class="w-full" @click="handleLogin">
            登录
          </el-button>
        </el-form-item>
      </el-form>

      <div class="text-center text-gray-500 text-sm mt-4">
        <p>测试账号：testuser / Test123456</p>
      </div>
    </el-card>
  </div>
</template>
