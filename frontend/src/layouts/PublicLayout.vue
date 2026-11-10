<script setup lang="ts">
import { Close, Menu } from '@element-plus/icons-vue'
import { ref, watch } from 'vue'
import { useRoute } from 'vue-router'

import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const auth = useAuthStore()
const mobileOpen = ref(false)

const navigation = [
  { label: '首页', to: '/' },
  { label: '正在寻找', to: '/cases' },
  { label: '线索地图', to: '/cases?view=map' },
  { label: '志愿行动', to: '/search-tasks' },
]

function isCurrentNavigation(to: string) {
  if (to === '/') return route.path === '/'
  if (to === '/cases') return route.path.startsWith('/cases') && route.query.view !== 'map'
  if (to.includes('view=map')) return route.path === '/cases' && route.query.view === 'map'
  return route.path === to
}

watch(
  () => route.fullPath,
  () => {
    mobileOpen.value = false
  },
)
</script>

<template>
  <div class="public-layout">
    <header class="public-header">
      <div class="pf-container public-header__inner">
        <RouterLink to="/" class="brand" aria-label="PawFinder 首页">
          <span class="brand__mark" aria-hidden="true">
            <span class="brand__pad brand__pad--one" />
            <span class="brand__pad brand__pad--two" />
            <span class="brand__pad brand__pad--three" />
            <span class="brand__palm" />
          </span>
          <span class="brand__copy">
            <strong>PawFinder</strong>
            <small>寻爪计划</small>
          </span>
        </RouterLink>

        <nav class="public-nav" aria-label="主要导航">
          <RouterLink v-for="item in navigation" :key="item.label" :to="item.to" :class="{ 'nav-current': isCurrentNavigation(item.to) }">
            {{ item.label }}
          </RouterLink>
        </nav>

        <div class="public-header__actions">
          <template v-if="auth.isAuthenticated">
            <RouterLink to="/notifications" class="header-text-link">消息</RouterLink>
            <el-button type="primary" round @click="$router.push('/pets')">
              进入工作台
            </el-button>
          </template>
          <template v-else>
            <RouterLink to="/login" class="header-text-link">登录</RouterLink>
            <el-button type="primary" round @click="$router.push('/register')">
              免费加入
            </el-button>
          </template>
        </div>

        <button
          class="mobile-menu-button"
          type="button"
          :aria-expanded="mobileOpen"
          aria-controls="mobile-navigation"
          :aria-label="mobileOpen ? '关闭导航' : '打开导航'"
          @click="mobileOpen = !mobileOpen"
        >
          <el-icon :size="22">
            <Close v-if="mobileOpen" />
            <Menu v-else />
          </el-icon>
        </button>
      </div>

      <Transition name="mobile-nav">
        <div v-if="mobileOpen" id="mobile-navigation" class="mobile-nav">
          <nav class="pf-container" aria-label="移动端导航">
            <RouterLink v-for="item in navigation" :key="item.label" :to="item.to">
              {{ item.label }}
            </RouterLink>
            <RouterLink :to="auth.isAuthenticated ? '/pets' : '/login'">
              {{ auth.isAuthenticated ? '进入工作台' : '登录 / 注册' }}
            </RouterLink>
          </nav>
        </div>
      </Transition>
    </header>

    <RouterView />

    <footer class="public-footer">
      <div class="pf-container public-footer__inner">
        <div>
          <strong>PawFinder 寻爪计划</strong>
          <p>连接主人、目击者与志愿者，让善意更有效。</p>
        </div>
        <div class="public-footer__meta">
          <span>数据库课程设计</span>
          <span>隐私友好的联系方式展示</span>
        </div>
      </div>
    </footer>
  </div>
</template>

<style scoped>
.public-layout {
  min-height: 100vh;
}

.public-header {
  position: sticky;
  z-index: 1000;
  top: 0;
  border-bottom: 1px solid rgb(239 223 213 / 82%);
  background: rgb(255 250 244 / 88%);
  backdrop-filter: blur(16px);
}

.public-header__inner {
  display: flex;
  align-items: center;
  min-height: var(--pf-header-height);
}

.brand {
  display: inline-flex;
  align-items: center;
  flex: 0 0 auto;
  gap: 10px;
}

.brand__mark {
  position: relative;
  display: block;
  width: 38px;
  height: 38px;
  border-radius: 13px;
  background: var(--pf-color-primary);
  box-shadow: 0 7px 16px rgb(232 111 71 / 24%);
}

.brand__pad,
.brand__palm {
  position: absolute;
  display: block;
  background: #ffffff;
}

.brand__pad {
  top: 8px;
  width: 6px;
  height: 8px;
  border-radius: 50%;
}

.brand__pad--one {
  left: 8px;
  transform: rotate(-22deg);
}

.brand__pad--two {
  left: 16px;
  top: 6px;
}

.brand__pad--three {
  left: 24px;
  transform: rotate(22deg);
}

.brand__palm {
  left: 10px;
  bottom: 7px;
  width: 18px;
  height: 15px;
  border-radius: 50% 50% 46% 46%;
}

.brand__copy {
  display: grid;
  line-height: 1.08;
}

.brand__copy strong {
  color: var(--pf-color-primary-dark);
  font-size: 18px;
  letter-spacing: -0.02em;
}

.brand__copy small {
  margin-top: 3px;
  color: var(--pf-color-text-secondary);
  font-size: 10px;
  letter-spacing: 0.16em;
}

.public-nav {
  display: flex;
  align-items: center;
  gap: 30px;
  margin-left: auto;
}

.public-nav a,
.header-text-link {
  position: relative;
  color: var(--pf-color-text-secondary);
  font-size: 14px;
  font-weight: 600;
  transition: color 160ms ease;
}

.public-nav a:hover,
.public-nav a.nav-current,
.header-text-link:hover {
  color: var(--pf-color-primary-dark);
}

.public-nav a::after {
  position: absolute;
  right: 0;
  bottom: -10px;
  left: 0;
  height: 2px;
  border-radius: 2px;
  background: var(--pf-color-primary);
  content: '';
  opacity: 0;
  transform: scaleX(0.5);
  transition: opacity 160ms ease, transform 160ms ease;
}

.public-nav a.nav-current::after {
  opacity: 1;
  transform: scaleX(1);
}

.public-header__actions {
  display: flex;
  align-items: center;
  gap: 18px;
  margin-left: 38px;
}

.mobile-menu-button {
  display: none;
  align-items: center;
  justify-content: center;
  width: 42px;
  height: 42px;
  padding: 0;
  border: 1px solid var(--pf-color-border);
  border-radius: 12px;
  color: var(--pf-color-text);
  background: var(--pf-color-surface);
  cursor: pointer;
}

.mobile-nav {
  display: none;
}

.public-footer {
  border-top: 1px solid var(--pf-color-border);
  background: #4a3932;
  color: #ffffff;
}

.public-footer__inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  min-height: 150px;
  gap: 30px;
}

.public-footer strong {
  font-size: 18px;
}

.public-footer p {
  margin: 6px 0 0;
  color: #d9c9c1;
  font-size: 13px;
}

.public-footer__meta {
  display: flex;
  gap: 20px;
  color: #d9c9c1;
  font-size: 12px;
}

.mobile-nav-enter-active,
.mobile-nav-leave-active {
  transition: opacity 160ms ease, transform 160ms ease;
}

.mobile-nav-enter-from,
.mobile-nav-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

@media (max-width: 920px) {
  .public-nav,
  .public-header__actions {
    display: none;
  }

  .mobile-menu-button {
    display: inline-flex;
    margin-left: auto;
  }

  .mobile-nav {
    display: block;
    border-top: 1px solid var(--pf-color-border);
    background: var(--pf-color-surface);
  }

  .mobile-nav nav {
    display: grid;
    padding-block: 10px 18px;
  }

  .mobile-nav a {
    padding: 11px 2px;
    border-bottom: 1px solid #f6ebe4;
    color: var(--pf-color-text-secondary);
    font-weight: 600;
  }

  .mobile-nav a:last-child {
    border-bottom: 0;
    color: var(--pf-color-primary-dark);
  }
}

@media (max-width: 640px) {
  .public-footer__inner {
    align-items: flex-start;
    flex-direction: column;
    justify-content: center;
    padding-block: 38px;
  }

  .public-footer__meta {
    flex-direction: column;
    gap: 4px;
  }
}
</style>
