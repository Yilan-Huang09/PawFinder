<script setup lang="ts">
import {
  ArrowRight,
  CircleCheck,
  DocumentAdd,
  Location,
  Position,
  Search,
  UserFilled,
} from '@element-plus/icons-vue'
import { onMounted, ref } from 'vue'

import { fetchCases } from '@/api/cases'
import CaseCard from '@/components/cases/CaseCard.vue'
import EmptyState from '@/components/common/EmptyState.vue'
import type { LostCase } from '@/types/domain'

const nearbyCases = ref<LostCase[]>([])
const loadingCases = ref(true)
const loadFailed = ref(false)

const actions = [
  {
    title: '发布走失',
    description: '建立宠物档案，记录最后出现的时间与地点',
    to: '/cases/new',
    icon: DocumentAdd,
    tone: 'coral',
  },
  {
    title: '提交目击',
    description: '不用先认领事件，也能独立分享可靠线索',
    to: '/sightings/new',
    icon: Location,
    tone: 'sage',
  },
  {
    title: '加入搜寻',
    description: '认领附近区域，与其他志愿者协同行动',
    to: '/search-tasks',
    icon: UserFilled,
    tone: 'sand',
  },
]

async function loadNearbyCases() {
  loadingCases.value = true
  loadFailed.value = false
  try {
    const result = await fetchCases({ page: 1, per_page: 4, status: 'SEARCHING' })
    nearbyCases.value = result.items
  } catch {
    nearbyCases.value = []
    loadFailed.value = true
  } finally {
    loadingCases.value = false
  }
}

onMounted(loadNearbyCases)
</script>

<template>
  <main class="home-page">
    <section class="home-hero">
      <div class="pf-container home-hero__inner">
        <div class="home-hero__copy">
          <span class="home-hero__eyebrow">
            <span class="home-hero__live-dot" />
            重庆 · 北碚区 · 西南大学周边
          </span>
          <h1>今天，重庆还有宠物<br />正在<em>等待线索</em></h1>
          <p>查看附近走失信息、提交目击位置，或认领一段搜寻路线。每一条准确记录，都可能缩短它回家的距离。</p>
          <div class="home-hero__buttons">
            <RouterLink to="/cases/new" class="hero-button hero-button--primary">
              <el-icon><DocumentAdd /></el-icon>
              发布走失
            </RouterLink>
            <RouterLink to="/sightings/new" class="hero-button hero-button--secondary">
              <el-icon><Location /></el-icon>
              提交目击
            </RouterLink>
          </div>
          <div class="home-hero__trust">
            <span><el-icon><CircleCheck /></el-icon> 联系方式脱敏</span>
            <span><el-icon><CircleCheck /></el-icon> 匹配理由可解释</span>
          </div>
        </div>

        <div class="home-hero__visual">
          <aside class="campus-board" aria-label="西南大学周边寻宠概况">
            <header>
              <div>
                <span>当前服务区域</span>
                <strong>西南大学北碚校区</strong>
              </div>
              <em>实时更新</em>
            </header>
            <dl>
              <div><dt>寻找中</dt><dd>4 <small>起</small></dd></div>
              <div><dt>有效目击</dt><dd>15 <small>条</small></dd></div>
              <div><dt>待认领任务</dt><dd>3 <small>项</small></dd></div>
            </dl>
            <div class="campus-board__update">
              <span>最近更新</span>
              <p><strong>点点</strong> · 天生路附近新增目击记录</p>
              <time>10 分钟前</time>
            </div>
          </aside>

          <form class="quick-search" action="/cases" method="get">
            <label for="home-search">搜索附近事件</label>
            <div class="quick-search__field">
              <el-icon><Search /></el-icon>
              <input id="home-search" name="keyword" placeholder="例如：天生路 / 点点" />
              <button type="submit" aria-label="搜索">
                <el-icon><ArrowRight /></el-icon>
              </button>
            </div>
            <div class="quick-search__chips">
              <RouterLink to="/cases?species=DOG">狗狗</RouterLink>
              <RouterLink to="/cases?species=CAT">猫咪</RouterLink>
              <RouterLink to="/cases?status=SEARCHING">寻找中</RouterLink>
            </div>
          </form>
        </div>
      </div>
    </section>

    <section class="home-actions" aria-label="快速参与">
      <div class="pf-container home-actions__grid">
        <RouterLink
          v-for="action in actions"
          :key="action.title"
          :to="action.to"
          class="action-card pf-card"
          :class="`action-card--${action.tone}`"
        >
          <span class="action-card__icon"><el-icon><component :is="action.icon" /></el-icon></span>
          <span class="action-card__content">
            <strong>{{ action.title }}</strong>
            <small>{{ action.description }}</small>
          </span>
          <span class="action-card__arrow">→</span>
        </RouterLink>
      </div>
    </section>

    <section class="home-section home-cases">
      <div class="pf-container">
        <header class="section-heading">
          <div>
            <span class="section-heading__eyebrow">西南大学周边</span>
            <h2>附近正在寻找</h2>
            <p>按发布时间展示重庆北碚区的最新事件，也许你刚好见过它。</p>
          </div>
          <RouterLink to="/cases" class="section-heading__link">
            查看全部 <el-icon><ArrowRight /></el-icon>
          </RouterLink>
        </header>

        <div v-if="loadingCases" class="case-grid" aria-label="正在加载走失事件">
          <div v-for="item in 4" :key="item" class="case-skeleton pf-card">
            <el-skeleton animated>
              <template #template>
                <el-skeleton-item variant="image" class="case-skeleton__image" />
                <div class="case-skeleton__body">
                  <el-skeleton-item variant="h3" style="width: 58%" />
                  <el-skeleton-item variant="text" />
                  <el-skeleton-item variant="text" style="width: 78%" />
                </div>
              </template>
            </el-skeleton>
          </div>
        </div>
        <div v-else-if="nearbyCases.length" class="case-grid">
          <CaseCard v-for="item in nearbyCases" :key="item.case_id" :lost-case="item" />
        </div>
        <EmptyState
          v-else
          :title="loadFailed ? '暂时无法连接案例服务' : '附近暂时没有寻找中的事件'"
          :description="loadFailed ? '请确认 Flask 服务已经启动，然后重新加载。' : '愿每一只宠物都平安在家。'"
          :action-label="loadFailed ? '重新加载' : ''"
          @action="loadNearbyCases"
        />
      </div>
    </section>

    <section class="home-section home-collaboration">
      <div class="pf-container collaboration-grid">
        <div class="map-preview">
          <iframe
            src="https://www.openstreetmap.org/export/embed.html?bbox=106.4073%2C29.8149%2C106.4433%2C29.8389&amp;layer=mapnik&amp;marker=29.8269%2C106.4253"
            title="西南大学北碚校区附近真实地图"
            loading="lazy"
            referrerpolicy="strict-origin-when-cross-origin"
          />
          <a href="https://www.openstreetmap.org/?mlat=29.8269&amp;mlon=106.4253#map=15/29.8269/106.4253" target="_blank" rel="noreferrer">查看完整地图 ↗</a>
        </div>
        <div class="collaboration-copy">
          <span class="section-heading__eyebrow">协作搜寻地图</span>
          <h2>把“我去找找”变成<br />清楚的协作行动</h2>
          <p>主人划分搜寻区域，志愿者认领任务并更新进度。所有人看见同一份状态，减少重复搜寻。</p>
          <ul>
            <li><span>01</span><div><strong>圈定范围</strong><small>以最后出现位置建立搜寻区域</small></div></li>
            <li><span>02</span><div><strong>认领行动</strong><small>单一志愿者负责，避免任务冲突</small></div></li>
            <li><span>03</span><div><strong>反馈结果</strong><small>进度与报告进入事件时间线</small></div></li>
          </ul>
          <RouterLink to="/search-tasks" class="inline-action">
            <el-icon><Position /></el-icon> 打开协作任务
          </RouterLink>
        </div>
      </div>
    </section>

    <section class="home-reunion">
      <div class="pf-container reunion-card">
        <div class="reunion-card__icon"><el-icon><CircleCheck /></el-icon></div>
        <div>
          <span>重逢记录 · 演示数据</span>
          <h2>雪球已经平安回家</h2>
          <p>从停车场目击，到志愿者确认，再到主人完成寻回归档——一条线索最终变成了回家的路。</p>
        </div>
        <RouterLink to="/cases?status=REUNITED">查看寻回事件 <el-icon><ArrowRight /></el-icon></RouterLink>
      </div>
    </section>
  </main>
</template>

<style scoped>
.home-page {
  overflow: hidden;
}

.home-hero {
  position: relative;
  border-bottom: 1px solid var(--pf-color-border);
  background: #ece9e2;
}

.home-hero__inner {
  display: grid;
  min-height: 530px;
  grid-template-columns: 1.04fr 0.96fr;
  align-items: center;
  gap: 72px;
  padding-top: 64px;
  padding-bottom: 70px;
}

.home-hero__eyebrow {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: var(--pf-color-sage-dark);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.04em;
}

.home-hero__live-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--pf-color-primary);
  box-shadow: 0 0 0 4px rgb(217 87 53 / 12%);
}

.home-hero h1 {
  margin: 22px 0 20px;
  max-width: 680px;
  font-family: var(--pf-font-serif);
  font-size: clamp(42px, 4.5vw, 62px);
  font-weight: 700;
  line-height: 1.22;
  letter-spacing: -0.035em;
}

.home-hero h1 em {
  color: var(--pf-color-primary-dark);
  font-style: normal;
}

.home-hero__copy > p {
  max-width: 600px;
  margin: 0;
  color: var(--pf-color-text-secondary);
  font-size: 15px;
  line-height: 1.9;
}

.home-hero__buttons {
  display: flex;
  gap: 12px;
  margin-top: 29px;
}

.hero-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 47px;
  gap: 8px;
  padding: 0 20px;
  border: 1px solid transparent;
  border-radius: var(--pf-radius-sm);
  font-size: 14px;
  font-weight: 700;
  transition: transform 160ms ease, box-shadow 160ms ease;
}

.hero-button:hover {
  transform: translateY(-2px);
}

.hero-button--primary {
  color: #ffffff;
  background: var(--pf-color-primary);
  box-shadow: none;
}

.hero-button--secondary {
  border-color: #b9b4aa;
  color: var(--pf-color-text);
  background: transparent;
}

.home-hero__trust {
  display: flex;
  gap: 20px;
  margin-top: 21px;
  color: var(--pf-color-text-secondary);
  font-size: 11px;
}

.home-hero__trust span {
  display: flex;
  align-items: center;
  gap: 5px;
}

.home-hero__trust .el-icon {
  color: var(--pf-color-sage-dark);
}

.home-hero__visual {
  display: grid;
  gap: 12px;
}

.campus-board {
  overflow: hidden;
  border: 1px solid #c7c2b8;
  border-radius: var(--pf-radius-lg);
  background: var(--pf-color-surface);
  box-shadow: var(--pf-shadow-md);
}
.campus-board header { display: flex; align-items: center; justify-content: space-between; padding: 20px 22px; border-bottom: 1px solid var(--pf-color-border); }
.campus-board header div { display: grid; gap: 2px; }
.campus-board header span { color: var(--pf-color-text-tertiary); font-size: 10px; }
.campus-board header strong { font-family: var(--pf-font-serif); font-size: 19px; }
.campus-board header em { padding: 4px 7px; border-radius: 4px; color: var(--pf-color-sage-dark); background: var(--pf-color-sage-soft); font-size: 9px; font-style: normal; font-weight: 700; }
.campus-board dl { display: grid; grid-template-columns: repeat(3, 1fr); margin: 0; border-bottom: 1px solid var(--pf-color-border); }
.campus-board dl div { display: grid; gap: 5px; padding: 18px 20px; border-right: 1px solid var(--pf-color-border); }
.campus-board dl div:last-child { border-right: 0; }
.campus-board dt { color: var(--pf-color-text-tertiary); font-size: 10px; }
.campus-board dd { margin: 0; color: var(--pf-color-text); font-size: 25px; font-weight: 800; line-height: 1; }
.campus-board dd small { color: var(--pf-color-text-tertiary); font-size: 9px; font-weight: 500; }
.campus-board__update { display: grid; grid-template-columns: auto 1fr auto; align-items: center; gap: 12px; padding: 17px 22px; }
.campus-board__update > span { padding: 3px 6px; border-radius: 3px; color: #fff; background: var(--pf-color-primary); font-size: 9px; font-weight: 700; }
.campus-board__update p { margin: 0; font-size: 11px; }
.campus-board__update time { color: var(--pf-color-text-tertiary); font-size: 9px; }

.quick-search { padding: 16px 17px; border: 1px solid #c7c2b8; border-radius: var(--pf-radius-md); background: rgb(255 255 255 / 72%); }
.quick-search > label { display: block; margin-bottom: 8px; font-size: 11px; font-weight: 800; }
.quick-search__field { display: flex; align-items: center; height: 44px; gap: 8px; padding: 0 6px 0 12px; border: 1px solid var(--pf-color-border); border-radius: var(--pf-radius-sm); background: #fff; }
.quick-search__field > .el-icon { color: var(--pf-color-primary); }
.quick-search__field input { min-width: 0; flex: 1; border: 0; outline: 0; background: transparent; font-size: 12px; }
.quick-search__field button { display: grid; width: 33px; height: 33px; padding: 0; border: 0; place-items: center; border-radius: 4px; color: #fff; background: var(--pf-color-primary); cursor: pointer; }
.quick-search__chips { display: flex; gap: 7px; margin-top: 10px; }
.quick-search__chips a { padding: 3px 0; color: var(--pf-color-text-secondary); font-size: 10px; font-weight: 700; }
.quick-search__chips a + a::before { margin-right: 7px; color: #aaa69e; content: '·'; }

.home-actions { position: relative; z-index: 10; padding-top: 22px; }
.home-actions__grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; }
.action-card { display: flex; align-items: center; min-height: 104px; gap: 14px; padding: 18px; box-shadow: none; transition: border-color 180ms ease, transform 180ms ease; }
.action-card:hover { border-color: #aaa49a; transform: translateY(-2px); }
.action-card__icon { display: grid; width: 43px; height: 43px; flex: 0 0 auto; place-items: center; border-radius: 7px; font-size: 20px; }
.action-card--coral .action-card__icon { color: var(--pf-color-primary-dark); background: #ffe2d7; }
.action-card--sage .action-card__icon { color: var(--pf-color-sage-dark); background: var(--pf-color-sage-soft); }
.action-card--sand .action-card__icon { color: #886635; background: #f5e8cc; }
.action-card__content { display: grid; min-width: 0; gap: 4px; }
.action-card__content strong { font-size: 16px; }
.action-card__content small { color: var(--pf-color-text-secondary); font-size: 11px; line-height: 1.55; }
.action-card__arrow { margin-left: auto; color: var(--pf-color-primary); font-size: 20px; }

.home-section { padding: 82px 0; }
.section-heading { display: flex; align-items: flex-end; justify-content: space-between; gap: 20px; margin-bottom: 30px; }
.section-heading__eyebrow { color: var(--pf-color-sage-dark); font-size: 10px; font-weight: 800; letter-spacing: 0.08em; }
.section-heading h2, .collaboration-copy h2 { margin: 5px 0 4px; font-family: var(--pf-font-serif); font-size: clamp(28px, 3vw, 38px); line-height: 1.3; letter-spacing: -0.025em; }
.section-heading p { margin: 0; color: var(--pf-color-text-secondary); font-size: 13px; }
.section-heading__link { display: inline-flex; align-items: center; gap: 5px; color: var(--pf-color-primary-dark); font-size: 13px; font-weight: 700; }
.case-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 18px; }
.case-skeleton { overflow: hidden; }
.case-skeleton__image { width: 100% !important; height: 188px !important; border-radius: 0 !important; }
.case-skeleton__body { display: grid; gap: 12px; padding: 19px; }

.home-collaboration { border-block: 1px solid var(--pf-color-border); background: #edf1ed; }
.collaboration-grid { display: grid; grid-template-columns: 1.12fr 0.88fr; align-items: center; gap: 80px; }
.map-preview { position: relative; height: 430px; overflow: hidden; border: 1px solid #bfc9c1; border-radius: var(--pf-radius-lg); background: #dbe5de; box-shadow: var(--pf-shadow-sm); }
.map-preview iframe { display: block; width: 100%; height: 100%; border: 0; }
.map-preview > a { position: absolute; z-index: 2; right: 14px; bottom: 14px; padding: 7px 10px; border: 1px solid var(--pf-color-border); border-radius: 5px; color: var(--pf-color-text); background: rgb(255 255 255 / 94%); box-shadow: var(--pf-shadow-sm); font-size: 10px; font-weight: 700; }
.collaboration-copy > p { margin: 16px 0 25px; color: var(--pf-color-text-secondary); font-size: 13px; line-height: 1.85; }
.collaboration-copy ul { display: grid; gap: 15px; margin: 0 0 27px; padding: 0; list-style: none; }
.collaboration-copy li { display: flex; align-items: center; gap: 13px; }
.collaboration-copy li > span { display: grid; width: 34px; height: 34px; flex: 0 0 auto; place-items: center; border: 1px solid #cbd2cc; border-radius: 6px; color: var(--pf-color-sage-dark); background: #fff; font-size: 10px; font-weight: 800; }
.collaboration-copy li div { display: grid; }
.collaboration-copy li strong { font-size: 13px; }
.collaboration-copy li small { color: var(--pf-color-text-secondary); font-size: 10px; }
.inline-action { display: inline-flex; align-items: center; gap: 7px; padding: 11px 16px; border-radius: 9px; color: #fff; background: var(--pf-color-sage-dark); font-size: 12px; font-weight: 700; }

.home-reunion { padding: 70px 0 90px; }
.reunion-card { display: grid; grid-template-columns: auto 1fr auto; align-items: center; gap: 22px; padding: 28px 34px; border: 1px solid var(--pf-color-border); border-radius: var(--pf-radius-lg); background: #fff; box-shadow: none; }
.reunion-card__icon { display: grid; width: 62px; height: 62px; place-items: center; border-radius: 50%; color: #fff; background: var(--pf-color-sage); font-size: 30px; box-shadow: 0 10px 24px rgb(79 113 92 / 20%); }
.reunion-card span { color: var(--pf-color-sage-dark); font-size: 10px; font-weight: 800; letter-spacing: .06em; }
.reunion-card h2 { margin: 3px 0 4px; font-size: 22px; }
.reunion-card p { margin: 0; color: var(--pf-color-text-secondary); font-size: 11px; }
.reunion-card > a { display: inline-flex; align-items: center; gap: 5px; color: var(--pf-color-primary-dark); font-size: 12px; font-weight: 700; }

@media (max-width: 1040px) {
  .home-hero__inner { gap: 25px; }
  .case-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .collaboration-grid { gap: 45px; }
}

@media (max-width: 820px) {
  .home-hero__inner { grid-template-columns: 1fr; padding-top: 48px; }
  .home-hero__copy { position: relative; z-index: 5; }
  .home-actions { padding-top: 20px; }
  .home-actions__grid { grid-template-columns: 1fr; }
  .action-card { min-height: 94px; }
  .collaboration-grid { grid-template-columns: 1fr; }
  .map-preview { height: 360px; }
}

@media (max-width: 640px) {
  .home-hero__inner { min-height: auto; padding-top: 42px; padding-bottom: 52px; }
  .home-hero h1 { font-size: 38px; overflow-wrap: anywhere; }
  .home-hero__copy > p { font-size: 14px; }
  .home-hero__buttons { align-items: stretch; flex-direction: column; }
  .home-hero__trust { align-items: flex-start; flex-direction: column; gap: 6px; }
  .home-section { padding: 68px 0; }
  .section-heading { align-items: flex-start; flex-direction: column; }
  .case-grid { grid-template-columns: 1fr; }
  .map-preview { height: 300px; }
  .campus-board dl div { padding: 15px 12px; }
  .campus-board__update { grid-template-columns: auto 1fr; }
  .campus-board__update time { grid-column: 2; }
  .reunion-card { grid-template-columns: auto 1fr; padding: 24px 20px; }
  .reunion-card > a { grid-column: 1 / -1; justify-content: flex-end; }
}
</style>
