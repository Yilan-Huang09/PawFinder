<script setup lang="ts">
import axios from 'axios'
import { Lock, Message, Phone, User } from '@element-plus/icons-vue'
import { reactive, ref } from 'vue'

import { changePassword, updateProfile } from '@/api/account'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const profile = reactive({ phone: auth.user?.phone || '', email: auth.user?.email || '', avatar_url: auth.user?.avatar_url || '' })
const password = reactive({ current: '', next: '', confirm: '' })
const savingProfile = ref(false)
const savingPassword = ref(false)
const profileMessage = ref('')
const passwordMessage = ref('')
const error = ref('')

function apiMessage(value: unknown, fallback: string) {
  return axios.isAxiosError<{ message?: string }>(value) ? value.response?.data?.message || fallback : fallback
}

async function saveProfile() {
  savingProfile.value = true; error.value = ''; profileMessage.value = ''
  try {
    const user = await updateProfile({ phone: profile.phone || null, email: profile.email || null, avatar_url: profile.avatar_url || null })
    auth.updateUser(user)
    profileMessage.value = '个人资料已保存'
  } catch (value) { error.value = apiMessage(value, '资料保存失败') } finally { savingProfile.value = false }
}

async function savePassword() {
  error.value = ''; passwordMessage.value = ''
  if (password.next.length < 8 || !/[A-Za-z]/.test(password.next) || !/\d/.test(password.next)) { error.value = '新密码需至少 8 位，并同时包含字母和数字'; return }
  if (password.next !== password.confirm) { error.value = '两次输入的新密码不一致'; return }
  savingPassword.value = true
  try {
    await changePassword(password.current, password.next)
    password.current = ''; password.next = ''; password.confirm = ''
    passwordMessage.value = '密码修改成功'
  } catch (value) { error.value = apiMessage(value, '密码修改失败') } finally { savingPassword.value = false }
}
</script>

<template>
  <main class="profile-page workflow-page">
    <div class="pf-container">
      <div class="workflow-heading"><div><span class="workflow-heading__eyebrow">ACCOUNT & PRIVACY</span><h1>个人中心</h1><p>维护联系资料与登录安全，公开页面只展示脱敏信息。</p></div></div>
      <div class="profile-grid">
        <aside class="profile-summary pf-card">
          <div class="profile-avatar"><img v-if="auth.user?.avatar_url" :src="auth.user.avatar_url" alt="头像" /><span v-else>{{ auth.user?.username.slice(0, 1).toUpperCase() }}</span></div>
          <h2>{{ auth.user?.username }}</h2><p>{{ auth.isAdmin ? '平台管理员' : 'PawFinder 平台用户' }}</p>
          <dl><div><dt>账号编号</dt><dd>#{{ auth.user?.user_id }}</dd></div><div><dt>账号状态</dt><dd>{{ auth.user?.status === 'ACTIVE' ? '正常' : '已停用' }}</dd></div><div><dt>角色</dt><dd>{{ auth.user?.role }}</dd></div></dl>
          <nav><RouterLink to="/pets">管理宠物档案 →</RouterLink><RouterLink to="/notifications">查看我的消息 →</RouterLink><RouterLink to="/search-tasks">查看搜寻任务 →</RouterLink></nav>
        </aside>
        <div class="profile-forms">
          <form class="profile-form pf-card" @submit.prevent="saveProfile">
            <header><span><el-icon><User /></el-icon></span><div><h2>联系资料</h2><p>用于事件发布和必要的协作联系</p></div></header>
            <div class="field-grid"><label class="app-form-field"><span><el-icon><Phone /></el-icon> 手机号</span><input v-model="profile.phone" class="app-form-control" inputmode="numeric" placeholder="11 位手机号" /></label><label class="app-form-field"><span><el-icon><Message /></el-icon> 邮箱</span><input v-model="profile.email" class="app-form-control" type="email" placeholder="name@example.com" /></label><label class="app-form-field field-span-2"><span>头像 URL</span><input v-model="profile.avatar_url" class="app-form-control" type="url" placeholder="可选，https://..." /></label></div>
            <p v-if="profileMessage" class="profile-success">{{ profileMessage }}</p><div class="profile-form__actions"><el-button native-type="submit" type="primary" :loading="savingProfile">保存资料</el-button></div>
          </form>
          <form class="profile-form pf-card" @submit.prevent="savePassword">
            <header><span><el-icon><Lock /></el-icon></span><div><h2>登录安全</h2><p>修改密码后请使用新密码再次登录</p></div></header>
            <div class="field-grid field-grid--three"><label class="app-form-field"><span>当前密码</span><input v-model="password.current" class="app-form-control" type="password" required /></label><label class="app-form-field"><span>新密码</span><input v-model="password.next" class="app-form-control" type="password" required /></label><label class="app-form-field"><span>确认新密码</span><input v-model="password.confirm" class="app-form-control" type="password" required /></label></div>
            <p v-if="passwordMessage" class="profile-success">{{ passwordMessage }}</p><p v-if="error" class="workflow-form__error" role="alert">{{ error }}</p><div class="profile-form__actions"><el-button native-type="submit" :loading="savingPassword">修改密码</el-button></div>
          </form>
        </div>
      </div>
    </div>
  </main>
</template>

<style scoped>
.profile-grid { display: grid; grid-template-columns: 265px minmax(0, 1fr); align-items: start; gap: 18px; }
.profile-summary { padding: 25px; text-align: center; }
.profile-avatar { display: grid; width: 92px; height: 92px; margin: 0 auto 12px; overflow: hidden; place-items: center; border: 7px solid #ffe4d9; border-radius: 50%; color: var(--pf-color-sage-dark); background: var(--pf-color-sage-soft); font-size: 36px; font-weight: 900; }
.profile-avatar img { width: 100%; height: 100%; object-fit: cover; }
.profile-summary h2 { margin: 0; font-size: 20px; }.profile-summary > p { margin: 2px 0 18px; color: var(--pf-color-text-tertiary); font-size: 10px; }
.profile-summary dl { margin: 0; }.profile-summary dl div { display: flex; justify-content: space-between; padding: 9px 0; border-bottom: 1px solid var(--pf-color-border); font-size: 10px; }.profile-summary dt { color: var(--pf-color-text-tertiary); }.profile-summary dd { margin: 0; font-weight: 700; }
.profile-summary nav { display: grid; gap: 8px; margin-top: 19px; text-align: left; }.profile-summary nav a { color: var(--pf-color-primary-dark); font-size: 10px; font-weight: 700; }
.profile-forms { display: grid; gap: 16px; }.profile-form { padding: 23px; }.profile-form header { display: flex; align-items: center; gap: 11px; margin-bottom: 20px; }.profile-form header > span { display: grid; width: 38px; height: 38px; place-items: center; border-radius: 10px; color: var(--pf-color-primary-dark); background: #ffe4d9; }.profile-form h2 { margin: 0; font-size: 16px; }.profile-form header p { margin: 1px 0 0; color: var(--pf-color-text-tertiary); font-size: 9px; }.profile-form__actions { display: flex; justify-content: flex-end; margin-top: 16px; }.profile-success { margin: 12px 0 0; color: var(--pf-color-sage-dark); font-size: 10px; }
@media (max-width: 820px) { .profile-grid { grid-template-columns: 1fr; } .profile-summary { text-align: left; } .profile-avatar { margin-left: 0; } }
</style>
