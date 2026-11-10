import {
  createRouter,
  createWebHistory,
  type RouteLocationNormalized,
} from 'vue-router'

import { useAuthStore } from '@/stores/auth'

const AppLayout = () => import('@/layouts/AppLayout.vue')
const PublicLayout = () => import('@/layouts/PublicLayout.vue')
const PlaceholderView = () => import('@/views/PlaceholderView.vue')
const HomeView = () => import('@/views/HomeView.vue')
const CasesView = () => import('@/views/CasesView.vue')
const LoginView = () => import('@/views/LoginView.vue')
const RegisterView = () => import('@/views/RegisterView.vue')
const PetsView = () => import('@/views/PetsView.vue')
const PetEditView = () => import('@/views/PetEditView.vue')
const CaseCreateView = () => import('@/views/CaseCreateView.vue')
const SightingCreateView = () => import('@/views/SightingCreateView.vue')
const CaseDetailView = () => import('@/views/CaseDetailView.vue')
const MatchesView = () => import('@/views/MatchesView.vue')
const SearchMapView = () => import('@/views/SearchMapView.vue')


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
          component: HomeView,
          meta: {
            eyebrow: '让每一次看见，都成为回家的线索',
            title: '一起，把走失的它带回家',
            description: 'PawFinder 正在准备行动优先的首页体验。',
          },
        },
        {
          path: 'cases',
          name: 'cases',
          component: CasesView,
          meta: {
            eyebrow: '公开寻宠信息',
            title: '附近正在寻找',
            description: '按地点、宠物特征和发布时间查找走失事件。',
          },
        },
        {
          path: 'login',
          name: 'login',
          component: LoginView,
          meta: {
            eyebrow: '欢迎回来',
            title: '登录 PawFinder',
            description: '继续管理寻宠事件与志愿任务。',
          },
        },
        {
          path: 'register',
          name: 'register',
          component: RegisterView,
          meta: {
            eyebrow: '加入协作网络',
            title: '创建 PawFinder 账号',
            description: '发布走失、提供线索或参与附近搜寻。',
          },
        },
        {
          path: 'cases/:caseId(\\d+)',
          name: 'case-detail',
          component: CaseDetailView,
          meta: {
            eyebrow: '走失事件',
            title: '事件详情',
            description: '宠物资料、候选线索与协作搜寻信息。',
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
          component: PetsView,
          meta: {
            requiresAuth: true,
            eyebrow: '个人工作台',
            title: '我的宠物档案',
            description: '维护宠物特征、照片和当前状态。',
          },
        },
        {
          path: '/pets/new',
          name: 'pet-create',
          component: PetEditView,
          meta: { requiresAuth: true, title: '创建宠物档案' },
        },
        {
          path: '/pets/:petId(\\d+)/edit',
          name: 'pet-edit',
          component: PetEditView,
          meta: { requiresAuth: true, title: '编辑宠物档案' },
        },
        {
          path: '/search-tasks',
          name: 'search-tasks',
          component: SearchMapView,
          meta: {
            requiresAuth: true,
            eyebrow: '志愿协作',
            title: '附近搜寻任务',
            description: '认领区域、更新进度并提交搜寻反馈。',
          },
        },
        {
          path: '/cases/:caseId(\\d+)/matches',
          name: 'case-matches',
          component: MatchesView,
          meta: {
            requiresAuth: true,
            eyebrow: '智能匹配',
            title: '候选线索审核',
            description: '查看可解释分数并核实线索。',
          },
        },
        {
          path: '/cases/:caseId(\\d+)/search',
          name: 'case-search',
          component: SearchMapView,
          meta: {
            requiresAuth: true,
            eyebrow: '协作搜寻',
            title: '区域与任务',
            description: '规划区域、认领任务并记录进展。',
          },
        },
        {
          path: '/cases/new',
          name: 'case-create',
          component: CaseCreateView,
          meta: {
            requiresAuth: true,
            eyebrow: '发布走失',
            title: '建立寻宠事件',
            description: '填写最后出现时间、地点和宠物特征。',
          },
        },
        {
          path: '/sightings/new',
          name: 'sighting-create',
          component: SightingCreateView,
          meta: {
            requiresAuth: true,
            eyebrow: '提交目击',
            title: '分享你看到的线索',
            description: '独立记录时间、位置和外观信息。',
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

export function authenticationGuard(to: RouteLocationNormalized) {
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
}

router.beforeEach(authenticationGuard)

export default router
