import { createRouter, createWebHistory } from 'vue-router'

import { useAuthStore } from '@/stores/auth'

const AppLayout = () => import('@/layouts/AppLayout.vue')
const PublicLayout = () => import('@/layouts/PublicLayout.vue')
const PlaceholderView = () => import('@/views/PlaceholderView.vue')


declare module 'vue-router' {
  interface RouteMeta {
    requiresAuth?: boolean
    requiresAdmin?: boolean
    eyebrow?: string
    title?: string
    description?: string
  }
}

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  scrollBehavior: () => ({ top: 0 }),
  routes: [
    {
      path: '/',
      component: PublicLayout,
      children: [
        {
          path: '',
          name: 'home',
          component: PlaceholderView,
          meta: {
            eyebrow: '让每一次看见，都成为回家的线索',
            title: '一起，把走失的它带回家',
            description: 'PawFinder 正在准备行动优先的首页体验。',
          },
        },
        {
          path: 'cases',
          name: 'cases',
          component: PlaceholderView,
          meta: {
            eyebrow: '公开寻宠信息',
            title: '附近正在寻找',
            description: '按地点、宠物特征和发布时间查找走失事件。',
          },
        },
        {
          path: 'login',
          name: 'login',
          component: PlaceholderView,
          meta: {
            eyebrow: '欢迎回来',
            title: '登录 PawFinder',
            description: '继续管理寻宠事件与志愿任务。',
          },
        },
        {
          path: 'register',
          name: 'register',
          component: PlaceholderView,
          meta: {
            eyebrow: '加入协作网络',
            title: '创建 PawFinder 账号',
            description: '发布走失、提供线索或参与附近搜寻。',
          },
        },
      ],
    },
    {
      path: '/app',
      component: AppLayout,
      meta: { requiresAuth: true },
      children: [
        {
          path: '/pets',
          name: 'pets',
          component: PlaceholderView,
          meta: {
            requiresAuth: true,
            eyebrow: '个人工作台',
            title: '我的宠物档案',
            description: '维护宠物特征、照片和当前状态。',
          },
        },
        {
          path: '/search-tasks',
          name: 'search-tasks',
          component: PlaceholderView,
          meta: {
            requiresAuth: true,
            eyebrow: '志愿协作',
            title: '附近搜寻任务',
            description: '认领区域、更新进度并提交搜寻反馈。',
          },
        },
        {
          path: '/notifications',
          name: 'notifications',
          component: PlaceholderView,
          meta: {
            requiresAuth: true,
            eyebrow: '消息中心',
            title: '重要进展，不错过',
            description: '查看匹配线索、任务状态与寻回通知。',
          },
        },
        {
          path: '/profile',
          name: 'profile',
          component: PlaceholderView,
          meta: {
            requiresAuth: true,
            eyebrow: '账号设置',
            title: '个人中心',
            description: '管理联系方式、头像和登录安全。',
          },
        },
        {
          path: '/admin',
          name: 'admin',
          component: PlaceholderView,
          meta: {
            requiresAuth: true,
            requiresAdmin: true,
            eyebrow: '平台管理',
            title: '管理员控制台',
            description: '查看运营统计并处理账号与内容状态。',
          },
        },
      ],
    },
    {
      path: '/:pathMatch(.*)*',
      redirect: '/',
    },
  ],
})

router.beforeEach((to) => {
  const auth = useAuthStore()
  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }
  if (to.meta.requiresAdmin && !auth.isAdmin) {
    return { name: 'pets', query: { forbidden: 'admin' } }
  }
  if ((to.name === 'login' || to.name === 'register') && auth.isAuthenticated) {
    return { name: 'pets' }
  }
  return true
})

export default router
