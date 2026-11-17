<script setup lang="ts">
import { Bell, Check, Location, User } from '@element-plus/icons-vue'
import type { AdminStatistics } from '@/types/domain'

defineProps<{ statistics: AdminStatistics }>()
</script>

<template>
  <section class="stats-cards">
    <article class="stat-card pf-card"><span><el-icon><User /></el-icon></span><div><strong>{{ statistics.users.total }}</strong><small>注册用户</small><p>{{ statistics.users.active }} 个活跃 · {{ statistics.users.disabled }} 个停用</p></div></article>
    <article class="stat-card pf-card"><span><el-icon><Location /></el-icon></span><div><strong>{{ statistics.cases.total }}</strong><small>走失事件</small><p>{{ statistics.cases.searching }} 个寻找中 · {{ statistics.cases.reunited }} 个已寻回</p></div></article>
    <article class="stat-card pf-card"><span><el-icon><Bell /></el-icon></span><div><strong>{{ statistics.sightings.total }}</strong><small>目击线索</small><p>{{ statistics.sightings.active }} 条公开 · {{ statistics.sightings.hidden }} 条隐藏</p></div></article>
    <article class="stat-card pf-card"><span><el-icon><Check /></el-icon></span><div><strong>{{ statistics.reunions.total }}</strong><small>成功寻回</small><p>{{ statistics.matches.high_score }} 个高分匹配 · {{ statistics.tasks.completed }} 个任务完成</p></div></article>
  </section>
</template>

<style scoped>
.stats-cards { display: grid; grid-template-columns: repeat(4, 1fr); gap: 13px; }
.stat-card { display: flex; align-items: center; gap: 13px; padding: 17px; }
.stat-card > span { display: grid; width: 42px; height: 42px; flex: 0 0 auto; place-items: center; border-radius: 12px; color: var(--pf-color-primary-dark); background: #ffe3d7; }
.stat-card:nth-child(even) > span { color: var(--pf-color-sage-dark); background: var(--pf-color-sage-soft); }
.stat-card div { display: grid; }
.stat-card strong { font-size: 23px; line-height: 1; }
.stat-card small { margin-top: 3px; color: var(--pf-color-text); font-size: 10px; font-weight: 800; }
.stat-card p { margin: 3px 0 0; color: var(--pf-color-text-tertiary); font-size: 8px; }
@media (max-width: 1000px) { .stats-cards { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 560px) { .stats-cards { grid-template-columns: 1fr; } }
</style>
