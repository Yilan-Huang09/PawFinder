<script setup lang="ts">
import { Hide, Lock, User, View } from '@element-plus/icons-vue'
import type { AxiosError } from 'axios'
import { computed, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import apiClient from '@/api/client'
import AuthShell from '@/components/auth/AuthShell.vue'
import { useAuthStore } from '@/stores/auth'
import type { UserProfile } from '@/types/domain'

interface LoginResponse {
  user: UserProfile
  access_token: string
}

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const form = reactive({ username: '', password: '' })
const passwordVisible = ref(false)
const submitting = ref(false)
const formError = ref('')

const canSubmit = computed(
  () => form.username.trim().length >= 3 && form.password.length > 0 && !submitting.value,
)

function fillDemoAccount() {
  form.username = 'linyu'
  form.password = 'PawFinder123!'
  formError.value = ''
}

async function submitLogin() {
  formError.value = ''
  if (!canSubmit.value) {
    formError.value = '请输入有效的用户名和密码'
    return
  }
  submitting.value = true
  try {
    const response = await apiClient.post<{ data: LoginResponse; message: string }>(
      '/auth/login',
      {
        username: form.username.trim().toLowerCase(),
        password: form.password,
      },
    )
    auth.setSession({
      accessToken: response.data.data.access_token,
      user: response.data.data.user,
    })
    const redirect = typeof route.query.redirect === 'string' ? route.query.redirect : '/pets'
    await router.push(redirect)
  } catch (error) {
    const requestError = error as AxiosError<{ message?: string }>
    formError.value = requestError.response?.data?.message || '登录失败，请稍后重试'
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <AuthShell eyebrow="欢迎回来" title="登录 PawFinder" description="继续跟进线索、任务和宠物状态。">
    <button type="button" class="demo-account" @click="fillDemoAccount">
      <span>演示账号</span>
      <strong>linyu / PawFinder123!</strong>
      <small>点击自动填入</small>
    </button>

    <form class="auth-form" novalidate @submit.prevent="submitLogin">
      <label>
        <span>用户名</span>
        <span class="auth-input">
          <el-icon><User /></el-icon>
          <input
            v-model="form.username"
            name="username"
            autocomplete="username"
            placeholder="3–50 位字母、数字或下划线"
          />
        </span>
      </label>
      <label>
        <span>密码</span>
        <span class="auth-input">
          <el-icon><Lock /></el-icon>
          <input
            v-model="form.password"
            name="password"
            :type="passwordVisible ? 'text' : 'password'"
            autocomplete="current-password"
            placeholder="请输入密码"
          />
          <button
            type="button"
            class="password-toggle"
            :aria-label="passwordVisible ? '隐藏密码' : '显示密码'"
            @click="passwordVisible = !passwordVisible"
          >
            <el-icon><Hide v-if="passwordVisible" /><View v-else /></el-icon>
          </button>
        </span>
      </label>

      <p v-if="formError" class="auth-form__error" role="alert">{{ formError }}</p>

      <el-button
        native-type="submit"
        type="primary"
        size="large"
        :loading="submitting"
        :disabled="!canSubmit"
      >
        登录并继续
      </el-button>
    </form>

    <p class="auth-switch">还没有账号？<RouterLink to="/register">免费注册</RouterLink></p>
  </AuthShell>
</template>

<style scoped>
.demo-account {
  display: grid;
  width: 100%;
  grid-template-columns: auto 1fr;
  gap: 1px 12px;
  padding: 11px 13px;
  border: 1px solid #cfe0d4;
  border-radius: 10px;
  color: var(--pf-color-sage-dark);
  background: #f1f8f3;
  text-align: left;
  cursor: pointer;
}

.demo-account span {
  grid-row: 1 / 3;
  align-self: center;
  padding: 4px 8px;
  border-radius: 6px;
  color: #ffffff;
  background: var(--pf-color-sage);
  font-size: 10px;
  font-weight: 700;
}

.demo-account strong {
  font-size: 12px;
}

.demo-account small {
  font-size: 10px;
  opacity: 0.75;
}

.auth-form {
  display: grid;
  gap: 18px;
  margin-top: 22px;
}

.auth-form label {
  display: grid;
  gap: 7px;
  color: var(--pf-color-text);
  font-size: 12px;
  font-weight: 700;
}

.auth-input {
  display: flex;
  align-items: center;
  gap: 9px;
  height: 46px;
  padding: 0 13px;
  border: 1px solid var(--pf-color-border);
  border-radius: 10px;
  background: #ffffff;
  transition: border-color 160ms ease, box-shadow 160ms ease;
}

.auth-input:focus-within {
  border-color: var(--pf-color-primary);
  box-shadow: var(--pf-shadow-focus);
}

.auth-input > .el-icon {
  color: var(--pf-color-text-tertiary);
}

.auth-input input {
  min-width: 0;
  flex: 1;
  border: 0;
  outline: 0;
  color: var(--pf-color-text);
  background: transparent;
  font-size: 13px;
}

.auth-input input::placeholder {
  color: #b6a39a;
}

.password-toggle {
  display: grid;
  width: 30px;
  height: 30px;
  padding: 0;
  border: 0;
  place-items: center;
  color: var(--pf-color-text-tertiary);
  background: transparent;
  cursor: pointer;
}

.auth-form__error {
  margin: -7px 0 -5px;
  color: var(--pf-color-danger);
  font-size: 12px;
}

.auth-form :deep(.el-button) {
  width: 100%;
}

.auth-switch {
  margin: 21px 0 0;
  color: var(--pf-color-text-secondary);
  text-align: center;
  font-size: 12px;
}

.auth-switch a {
  margin-left: 4px;
  color: var(--pf-color-primary-dark);
  font-weight: 700;
}
</style>
