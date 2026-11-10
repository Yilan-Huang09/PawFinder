<script setup lang="ts">
import { Lock, Message, Phone, User } from '@element-plus/icons-vue'
import type { AxiosError } from 'axios'
import { computed, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'

import apiClient from '@/api/client'
import AuthShell from '@/components/auth/AuthShell.vue'
import { useAuthStore } from '@/stores/auth'
import type { UserProfile } from '@/types/domain'

interface RegisterResponse {
  user: UserProfile
  access_token: string
}

const router = useRouter()
const auth = useAuthStore()
const form = reactive({
  username: '',
  phone: '',
  email: '',
  password: '',
  confirmPassword: '',
})
const submitting = ref(false)
const formError = ref('')

const hasRequiredFields = computed(
  () => form.username.trim().length >= 3 && form.password.length >= 8,
)

function validate(): string {
  if (!/^[A-Za-z0-9_]{3,50}$/.test(form.username.trim())) {
    return '用户名只能包含 3–50 位字母、数字或下划线'
  }
  if (form.password.length < 8 || !/[A-Za-z]/.test(form.password) || !/\d/.test(form.password)) {
    return '密码至少 8 位，并同时包含字母和数字'
  }
  if (form.password !== form.confirmPassword) return '两次输入的密码不一致'
  if (form.phone && !/^1\d{10}$/.test(form.phone)) return '请输入正确的 11 位手机号'
  if (form.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) return '邮箱格式不正确'
  return ''
}

async function submitRegistration() {
  formError.value = validate()
  if (formError.value) return

  submitting.value = true
  try {
    const response = await apiClient.post<{ data: RegisterResponse; message: string }>(
      '/auth/register',
      {
        username: form.username.trim().toLowerCase(),
        password: form.password,
        phone: form.phone.trim() || null,
        email: form.email.trim().toLowerCase() || null,
      },
    )
    auth.setSession({
      accessToken: response.data.data.access_token,
      user: response.data.data.user,
    })
    await router.push('/pets')
  } catch (error) {
    const requestError = error as AxiosError<{ message?: string }>
    formError.value = requestError.response?.data?.message || '注册失败，请稍后重试'
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <AuthShell
    eyebrow="加入协作网络"
    title="创建 PawFinder 账号"
    description="联系方式均为选填；公开页面默认脱敏展示。"
  >
    <form class="register-form" novalidate @submit.prevent="submitRegistration">
      <label>
        <span>用户名 <b>*</b></span>
        <span class="register-input">
          <el-icon><User /></el-icon>
          <input
            v-model="form.username"
            name="username"
            autocomplete="username"
            placeholder="例如 linyu_2026"
          />
        </span>
      </label>

      <div class="register-form__row">
        <label>
          <span>手机号</span>
          <span class="register-input">
            <el-icon><Phone /></el-icon>
            <input
              v-model="form.phone"
              name="phone"
              inputmode="numeric"
              autocomplete="tel"
              placeholder="选填"
            />
          </span>
        </label>
        <label>
          <span>邮箱</span>
          <span class="register-input">
            <el-icon><Message /></el-icon>
            <input
              v-model="form.email"
              name="email"
              type="email"
              autocomplete="email"
              placeholder="选填"
            />
          </span>
        </label>
      </div>

      <div class="register-form__row">
        <label>
          <span>密码 <b>*</b></span>
          <span class="register-input">
            <el-icon><Lock /></el-icon>
            <input
              v-model="form.password"
              name="password"
              type="password"
              autocomplete="new-password"
              placeholder="至少 8 位"
            />
          </span>
        </label>
        <label>
          <span>确认密码 <b>*</b></span>
          <span class="register-input">
            <el-icon><Lock /></el-icon>
            <input
              v-model="form.confirmPassword"
              name="confirm_password"
              type="password"
              autocomplete="new-password"
              placeholder="再次输入"
            />
          </span>
        </label>
      </div>

      <p class="register-form__hint">密码需同时包含字母和数字，不少于 8 位。</p>
      <p v-if="formError" class="register-form__error" role="alert">{{ formError }}</p>

      <el-button
        native-type="submit"
        type="primary"
        size="large"
        :loading="submitting"
        :disabled="!hasRequiredFields || submitting"
      >
        同意规则并注册
      </el-button>
    </form>

    <p class="auth-switch">已经有账号？<RouterLink to="/login">直接登录</RouterLink></p>
  </AuthShell>
</template>

<style scoped>
.register-form {
  display: grid;
  gap: 15px;
}

.register-form__row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.register-form label {
  display: grid;
  gap: 6px;
  min-width: 0;
  color: var(--pf-color-text);
  font-size: 11px;
  font-weight: 700;
}

.register-form label b {
  color: var(--pf-color-primary);
}

.register-input {
  display: flex;
  align-items: center;
  gap: 8px;
  height: 44px;
  padding: 0 11px;
  border: 1px solid var(--pf-color-border);
  border-radius: 9px;
  transition: border-color 160ms ease, box-shadow 160ms ease;
}

.register-input:focus-within {
  border-color: var(--pf-color-primary);
  box-shadow: var(--pf-shadow-focus);
}

.register-input .el-icon {
  flex: 0 0 auto;
  color: var(--pf-color-text-tertiary);
}

.register-input input {
  min-width: 0;
  flex: 1;
  border: 0;
  outline: 0;
  background: transparent;
  font-size: 12px;
}

.register-input input::placeholder {
  color: #b6a39a;
}

.register-form__hint,
.register-form__error {
  margin: -4px 0 0;
  font-size: 11px;
}

.register-form__hint {
  color: var(--pf-color-text-tertiary);
}

.register-form__error {
  color: var(--pf-color-danger);
}

.register-form :deep(.el-button) {
  width: 100%;
  margin-top: 2px;
}

.auth-switch {
  margin: 18px 0 0;
  color: var(--pf-color-text-secondary);
  text-align: center;
  font-size: 12px;
}

.auth-switch a {
  margin-left: 4px;
  color: var(--pf-color-primary-dark);
  font-weight: 700;
}

@media (max-width: 520px) {
  .register-form__row {
    grid-template-columns: 1fr;
  }
}
</style>
