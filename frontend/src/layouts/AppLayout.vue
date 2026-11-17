<script setup lang="ts">
import {
  Bell,
  Close,
  DataAnalysis,
  House,
  Location,
  Menu,
  Setting,
  SwitchButton,
  User,
} from '@element-plus/icons-vue'
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const mobileOpen = ref(false)

const navigation = computed(() => [
  { label: '宠物档案', to: '/pets', icon: House },
  { label: '搜寻任务', to: '/search-tasks', icon: Location },
  { label: '消息中心', to: '/notifications', icon: Bell },
  { label: '个人中心', to: '/profile', icon: User },
  ...(auth.isAdmin
    ? [{ label: '管理控制台', to: '/admin', icon: DataAnalysis }]
    : []),
])

watch(
  () => route.fullPath,
  () => {
    mobileOpen.value = false
  },
)

function logout() {
  auth.clearSession()
  void router.push('/')
}
</script>

<template>
  <div class="app-layout">
    <aside class="app-sidebar" :class="{ 'app-sidebar--open': mobileOpen }">
      <div class="app-sidebar__brand">
        <RouterLink to="/" class="app-brand">
          <span class="app-brand__mark">P</span>
          <span>
            <strong>PawFinder</strong>
            <small>寻爪工作台</small>
          </span>
        </RouterLink>
        <button
          class="app-sidebar__close"
          type="button"
          aria-label="关闭菜单"
          @click="mobileOpen = false"
        >
          <el-icon><Close /></el-icon>
        </button>
      </div>

      <nav class="app-sidebar__nav" aria-label="工作台导航">
        <RouterLink v-for="item in navigation" :key="item.to" :to="item.to">
          <el-icon :size="19"><component :is="item.icon" /></el-icon>
          <span>{{ item.label }}</span>
        </RouterLink>
      </nav>

      <div class="app-sidebar__footer">
        <div class="account-summary">
          <span class="account-summary__avatar">
            {{ auth.user?.username.slice(0, 1).toUpperCase() }}
          </span>
          <span>
            <strong>{{ auth.user?.username }}</strong>
            <small>{{ auth.isAdmin ? '管理员' : '平台用户' }}</small>
          </span>
        </div>
        <button type="button" class="logout-button" title="退出登录" @click="logout">
          <el-icon><SwitchButton /></el-icon>
        </button>
      </div>
    </aside>

    <Transition name="sidebar-mask">
      <button
        v-if="mobileOpen"
        class="sidebar-mask"
        type="button"
        aria-label="关闭菜单"
        @click="mobileOpen = false"
      />
    </Transition>

    <section class="app-workspace">
      <header class="app-topbar">
        <button
          class="app-topbar__menu"
          type="button"
          aria-label="打开菜单"
          @click="mobileOpen = true"
        >
          <el-icon :size="21"><Menu /></el-icon>
        </button>
        <div>
          <span class="app-topbar__eyebrow">PawFinder</span>
          <strong>{{ route.meta.title || '协作工作台' }}</strong>
        </div>
        <div class="app-topbar__actions">
          <RouterLink to="/" title="返回公开首页">
            <el-icon :size="19"><House /></el-icon>
          </RouterLink>
          <RouterLink to="/profile" title="账号设置">
            <el-icon :size="19"><Setting /></el-icon>
          </RouterLink>
        </div>
      </header>

      <div class="app-workspace__content">
        <RouterView />
      </div>
    </section>
  </div>
</template>

<style scoped>
.app-layout {
  display: grid;
  grid-template-columns: 248px minmax(0, 1fr);
  min-height: 100vh;
  background: var(--pf-color-background);
}

.app-sidebar {
  position: sticky;
  z-index: 1200;
  top: 0;
  display: flex;
  flex-direction: column;
  height: 100vh;
  padding: 22px 16px;
  border-right: 1px solid var(--pf-color-border);
  background: #26362f;
  color: #ffffff;
}

.app-sidebar__brand {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 8px 26px;
}

.app-brand {
  display: inline-flex;
  align-items: center;
  gap: 11px;
}

.app-brand__mark {
  display: grid;
  width: 39px;
  height: 39px;
  place-items: center;
  border-radius: 13px;
  color: #ffffff;
  background: var(--pf-color-primary);
  font-size: 20px;
  font-weight: 900;
}

.app-brand > span:last-child {
  display: grid;
  line-height: 1.15;
}

.app-brand strong {
  font-size: 16px;
}

.app-brand small {
  margin-top: 4px;
  color: #cdbdb5;
  font-size: 10px;
  letter-spacing: 0.1em;
}

.app-sidebar__close {
  display: none;
}

.app-sidebar__nav {
  display: grid;
  gap: 7px;
}

.app-sidebar__nav a {
  display: flex;
  align-items: center;
  gap: 12px;
  min-height: 46px;
  padding: 0 13px;
  border-radius: 11px;
  color: #d9cbc4;
  font-size: 14px;
  font-weight: 600;
  transition: color 160ms ease, background 160ms ease, transform 160ms ease;
}

.app-sidebar__nav a:hover {
  color: #ffffff;
  background: rgb(255 255 255 / 8%);
  transform: translateX(2px);
}

.app-sidebar__nav a.router-link-active {
  color: #ffffff;
  background: var(--pf-color-primary);
  box-shadow: 0 8px 22px rgb(26 15 11 / 20%);
}

.app-sidebar__footer {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: auto;
  padding: 15px 7px 0;
  border-top: 1px solid rgb(255 255 255 / 12%);
}

.account-summary {
  display: flex;
  align-items: center;
  min-width: 0;
  flex: 1;
  gap: 10px;
}

.account-summary__avatar {
  display: grid;
  width: 36px;
  height: 36px;
  flex: 0 0 auto;
  place-items: center;
  border-radius: 50%;
  color: var(--pf-color-sage-dark);
  background: var(--pf-color-sage-soft);
  font-weight: 800;
}

.account-summary > span:last-child {
  display: grid;
  min-width: 0;
  line-height: 1.2;
}

.account-summary strong {
  overflow: hidden;
  font-size: 13px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.account-summary small {
  margin-top: 4px;
  color: #baa89f;
  font-size: 10px;
}

.logout-button,
.app-sidebar__close,
.app-topbar__menu {
  display: grid;
  border: 0;
  place-items: center;
  color: inherit;
  background: transparent;
  cursor: pointer;
}

.logout-button {
  width: 34px;
  height: 34px;
  border-radius: 9px;
  color: #d9cbc4;
}

.logout-button:hover {
  color: #ffffff;
  background: rgb(255 255 255 / 8%);
}

.app-workspace {
  min-width: 0;
}

.app-topbar {
  position: sticky;
  z-index: 900;
  top: 0;
  display: flex;
  align-items: center;
  min-height: 68px;
  padding: 0 32px;
  border-bottom: 1px solid var(--pf-color-border);
  background: rgb(246 244 239 / 92%);
  backdrop-filter: blur(16px);
}

.app-topbar__menu {
  display: none;
}

.app-topbar > div:nth-child(2) {
  display: grid;
  line-height: 1.15;
}

.app-topbar__eyebrow {
  color: var(--pf-color-primary);
  font-size: 10px;
  font-weight: 800;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.app-topbar strong {
  margin-top: 4px;
  font-size: 15px;
}

.app-topbar__actions {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-left: auto;
}

.app-topbar__actions a {
  display: grid;
  width: 38px;
  height: 38px;
  place-items: center;
  border: 1px solid var(--pf-color-border);
  border-radius: 11px;
  color: var(--pf-color-text-secondary);
  background: var(--pf-color-surface);
}

.app-topbar__actions a:hover,
.app-topbar__actions a.router-link-active {
  color: var(--pf-color-primary-dark);
  border-color: #f1c4b4;
}

.app-workspace__content :deep(.placeholder-page) {
  min-height: calc(100vh - 68px);
}

.sidebar-mask {
  display: none;
}

@media (max-width: 820px) {
  .app-layout {
    display: block;
  }

  .app-sidebar {
    position: fixed;
    left: 0;
    width: min(290px, 86vw);
    transform: translateX(-105%);
    transition: transform 200ms ease;
  }

  .app-sidebar--open {
    transform: translateX(0);
  }

  .app-sidebar__close {
    display: grid;
    width: 36px;
    height: 36px;
    border-radius: 9px;
    color: #d9cbc4;
  }

  .sidebar-mask {
    position: fixed;
    z-index: 1100;
    inset: 0;
    display: block;
    padding: 0;
    border: 0;
    background: rgb(48 34 28 / 46%);
    backdrop-filter: blur(2px);
  }

  .app-topbar {
    padding: 0 18px;
  }

  .app-topbar__menu {
    display: grid;
    width: 40px;
    height: 40px;
    margin-right: 10px;
    border: 1px solid var(--pf-color-border);
    border-radius: 11px;
    background: var(--pf-color-surface);
  }

  .sidebar-mask-enter-active,
  .sidebar-mask-leave-active {
    transition: opacity 200ms ease;
  }

  .sidebar-mask-enter-from,
  .sidebar-mask-leave-to {
    opacity: 0;
  }
}
</style>
