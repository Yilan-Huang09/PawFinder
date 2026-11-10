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
            让每一次看见，都成为回家的线索
          </span>
          <h1>一起，把走失的它<br /><em>带回家</em></h1>
          <p>连接宠物主人、目击者与志愿者，用时空线索匹配和清晰任务协作，让每一份善意更有效。</p>
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
          <div class="hero-pet" aria-hidden="true">
            <span class="hero-pet__ear hero-pet__ear--left" />
            <span class="hero-pet__ear hero-pet__ear--right" />
            <span class="hero-pet__face">
              <i class="hero-pet__eye hero-pet__eye--left" />
              <i class="hero-pet__eye hero-pet__eye--right" />
              <i class="hero-pet__nose" />
              <i class="hero-pet__smile" />
            </span>
            <span class="hero-pet__collar" />
          </div>
          <span class="hero-paw hero-paw--one">· ·<b>●</b></span>
          <span class="hero-paw hero-paw--two">· ·<b>●</b></span>

          <form class="quick-search pf-card" action="/cases" method="get">
            <label for="home-search">快速寻找</label>
            <p>输入地点、宠物名字或品种</p>
            <div class="quick-search__field">
              <el-icon><Search /></el-icon>
              <input id="home-search" name="keyword" placeholder="例如：文三路 / 豆包" />
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
            <span class="section-heading__eyebrow">NEARBY SEARCHES</span>
            <h2>附近正在寻找</h2>
            <p>优先展示最新发布的事件，也许你刚好见过它。</p>
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
          <div class="map-preview__roads" />
          <span class="map-marker map-marker--case"><i />走失地点</span>
          <span class="map-marker map-marker--sighting"><i />新目击</span>
          <span class="map-radius" />
          <div class="map-preview__legend">
            <span><i class="legend-dot legend-dot--coral" /> 事件</span>
            <span><i class="legend-dot legend-dot--sage" /> 目击</span>
            <span><i class="legend-ring" /> 搜寻区</span>
          </div>
        </div>
        <div class="collaboration-copy">
          <span class="section-heading__eyebrow">COLLABORATIVE MAP</span>
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

    <section class="home-stats">
      <div class="pf-container home-stats__grid">
        <div><strong>4</strong><span>演示事件正在寻找</span></div>
        <div><strong>15</strong><span>结构化目击线索</span></div>
        <div><strong>12</strong><span>可解释候选匹配</span></div>
        <div><strong>1</strong><span>完整寻回样例</span></div>
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
  background:
    radial-gradient(circle at 84% 2%, rgb(255 255 255 / 68%) 0 11rem, transparent 11.2rem),
    linear-gradient(125deg, #fff0da, #ffe1d5 64%, #f8cab8);
}

.home-hero__inner {
  display: grid;
  min-height: 520px;
  grid-template-columns: 1.1fr 0.9fr;
  align-items: center;
  gap: 70px;
  padding-top: 58px;
  padding-bottom: 92px;
}

.home-hero__eyebrow {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 7px 12px;
  border: 1px solid rgb(255 255 255 / 70%);
  border-radius: var(--pf-radius-pill);
  color: var(--pf-color-primary-dark);
  background: rgb(255 255 255 / 56%);
  font-size: 12px;
  font-weight: 700;
}

.home-hero__live-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--pf-color-primary);
  box-shadow: 0 0 0 4px rgb(232 111 71 / 13%);
}

.home-hero h1 {
  margin: 22px 0 18px;
  font-size: clamp(46px, 5.1vw, 72px);
  line-height: 1.08;
  letter-spacing: -0.055em;
}

.home-hero h1 em {
  position: relative;
  color: var(--pf-color-primary-dark);
  font-style: normal;
}

.home-hero h1 em::after {
  position: absolute;
  z-index: -1;
  right: -4px;
  bottom: 3px;
  left: -4px;
  height: 12px;
  border-radius: 50%;
  background: rgb(255 255 255 / 72%);
  content: '';
}

.home-hero__copy > p {
  max-width: 570px;
  margin: 0;
  color: var(--pf-color-text-secondary);
  font-size: 16px;
  line-height: 1.85;
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
  border-radius: 11px;
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
  box-shadow: 0 12px 24px rgb(202 83 48 / 22%);
}

.hero-button--secondary {
  border-color: #edcdbc;
  color: var(--pf-color-primary-dark);
  background: rgb(255 255 255 / 82%);
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
  position: relative;
  min-height: 370px;
}

.hero-pet {
  position: absolute;
  top: -2px;
  right: 5px;
  width: 285px;
  height: 285px;
}

.hero-pet__ear {
  position: absolute;
  z-index: 1;
  top: 45px;
  width: 83px;
  height: 130px;
  border-radius: 70% 18% 50% 40%;
  background: #9a5842;
}

.hero-pet__ear--left { left: 14px; transform: rotate(-28deg); }
.hero-pet__ear--right { right: 14px; border-radius: 18% 70% 40% 50%; transform: rotate(28deg); }

.hero-pet__face {
  position: absolute;
  z-index: 2;
  right: 39px;
  bottom: 18px;
  left: 39px;
  height: 218px;
  border: 8px solid rgb(255 255 255 / 46%);
  border-radius: 48% 48% 44% 44%;
  background: linear-gradient(155deg, #f7c68e, #eca875);
  box-shadow: 0 28px 50px rgb(157 82 55 / 22%);
}

.hero-pet__eye,
.hero-pet__nose,
.hero-pet__smile { position: absolute; display: block; }
.hero-pet__eye { top: 84px; width: 15px; height: 20px; border-radius: 50%; background: #4c342c; }
.hero-pet__eye--left { left: 56px; }
.hero-pet__eye--right { right: 56px; }
.hero-pet__nose { bottom: 59px; left: 50%; width: 29px; height: 20px; border-radius: 54% 54% 48% 48%; background: #4c342c; transform: translateX(-50%); }
.hero-pet__smile { bottom: 39px; left: 50%; width: 42px; height: 22px; border-bottom: 3px solid #8d5742; border-radius: 50%; transform: translateX(-50%); }
.hero-pet__collar { position: absolute; z-index: 3; right: 62px; bottom: 17px; left: 62px; height: 22px; border-radius: 8px; background: var(--pf-color-primary); transform: rotate(-2deg); }

.hero-paw {
  position: absolute;
  color: rgb(185 85 52 / 25%);
  font-size: 18px;
  line-height: 0.45;
  letter-spacing: 2px;
  transform: rotate(-30deg);
}

.hero-paw b { display: block; font-size: 25px; text-align: center; }
.hero-paw--one { top: 20px; left: 15px; }
.hero-paw--two { top: 130px; left: -18px; transform: rotate(-10deg) scale(0.8); }

.quick-search {
  position: absolute;
  z-index: 5;
  right: 85px;
  bottom: -22px;
  width: min(340px, 88%);
  padding: 20px;
  box-shadow: 0 20px 50px rgb(110 66 46 / 18%);
}

.quick-search > label { display: block; font-size: 14px; font-weight: 800; }
.quick-search > p { margin: 1px 0 11px; color: var(--pf-color-text-tertiary); font-size: 10px; }
.quick-search__field { display: flex; align-items: center; height: 44px; gap: 8px; padding: 0 6px 0 12px; border: 1px solid var(--pf-color-border); border-radius: 9px; }
.quick-search__field > .el-icon { color: var(--pf-color-primary); }
.quick-search__field input { min-width: 0; flex: 1; border: 0; outline: 0; background: transparent; font-size: 12px; }
.quick-search__field button { display: grid; width: 33px; height: 33px; padding: 0; border: 0; place-items: center; border-radius: 8px; color: #fff; background: var(--pf-color-primary); cursor: pointer; }
.quick-search__chips { display: flex; gap: 7px; margin-top: 10px; }
.quick-search__chips a { padding: 4px 8px; border-radius: 5px; color: var(--pf-color-primary-dark); background: var(--pf-color-surface-warm); font-size: 10px; font-weight: 700; }

.home-actions { position: relative; z-index: 10; margin-top: -38px; }
.home-actions__grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; }
.action-card { display: flex; align-items: center; min-height: 118px; gap: 14px; padding: 19px; box-shadow: 0 12px 30px rgb(100 65 48 / 10%); transition: transform 180ms ease, box-shadow 180ms ease; }
.action-card:hover { box-shadow: var(--pf-shadow-md); transform: translateY(-4px); }
.action-card__icon { display: grid; width: 48px; height: 48px; flex: 0 0 auto; place-items: center; border-radius: 14px; font-size: 22px; }
.action-card--coral .action-card__icon { color: var(--pf-color-primary-dark); background: #ffe2d7; }
.action-card--sage .action-card__icon { color: var(--pf-color-sage-dark); background: var(--pf-color-sage-soft); }
.action-card--sand .action-card__icon { color: #886635; background: #f5e8cc; }
.action-card__content { display: grid; min-width: 0; gap: 4px; }
.action-card__content strong { font-size: 16px; }
.action-card__content small { color: var(--pf-color-text-secondary); font-size: 11px; line-height: 1.55; }
.action-card__arrow { margin-left: auto; color: var(--pf-color-primary); font-size: 20px; }

.home-section { padding: 92px 0; }
.section-heading { display: flex; align-items: flex-end; justify-content: space-between; gap: 20px; margin-bottom: 30px; }
.section-heading__eyebrow { color: var(--pf-color-primary); font-size: 10px; font-weight: 800; letter-spacing: 0.15em; }
.section-heading h2, .collaboration-copy h2 { margin: 5px 0 4px; font-size: clamp(28px, 3vw, 40px); line-height: 1.25; letter-spacing: -0.035em; }
.section-heading p { margin: 0; color: var(--pf-color-text-secondary); font-size: 13px; }
.section-heading__link { display: inline-flex; align-items: center; gap: 5px; color: var(--pf-color-primary-dark); font-size: 13px; font-weight: 700; }
.case-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 18px; }
.case-skeleton { overflow: hidden; }
.case-skeleton__image { width: 100% !important; height: 188px !important; border-radius: 0 !important; }
.case-skeleton__body { display: grid; gap: 12px; padding: 19px; }

.home-collaboration { background: #f1f7f2; }
.collaboration-grid { display: grid; grid-template-columns: 1.12fr 0.88fr; align-items: center; gap: 80px; }
.map-preview { position: relative; height: 430px; overflow: hidden; border: 10px solid #fff; border-radius: 26px; background: #dbeae0; box-shadow: var(--pf-shadow-md); }
.map-preview::before, .map-preview::after, .map-preview__roads { position: absolute; inset: -30% -20%; content: ''; }
.map-preview::before { background: repeating-linear-gradient(32deg, transparent 0 57px, rgb(255 255 255 / 75%) 58px 69px, transparent 70px 118px); transform: rotate(3deg); }
.map-preview::after { background: repeating-linear-gradient(118deg, transparent 0 84px, rgb(255 255 255 / 72%) 85px 94px, transparent 95px 160px); }
.map-preview__roads { background: linear-gradient(90deg, transparent 48%, rgb(166 201 178 / 50%) 49% 52%, transparent 53%); transform: rotate(21deg); }
.map-radius { position: absolute; z-index: 2; top: 80px; left: 118px; width: 210px; height: 210px; border: 2px dashed var(--pf-color-primary); border-radius: 50%; background: rgb(232 111 71 / 10%); }
.map-marker { position: absolute; z-index: 4; display: flex; align-items: center; gap: 7px; padding: 7px 10px; border-radius: 8px; background: #fff; box-shadow: var(--pf-shadow-sm); font-size: 10px; font-weight: 700; }
.map-marker i { width: 12px; height: 12px; border: 3px solid #fff; border-radius: 50%; box-shadow: 0 0 0 2px currentColor; background: currentColor; }
.map-marker--case { top: 155px; left: 205px; color: var(--pf-color-primary-dark); }
.map-marker--sighting { right: 70px; bottom: 88px; color: var(--pf-color-sage-dark); }
.map-preview__legend { position: absolute; z-index: 5; right: 15px; bottom: 15px; display: flex; gap: 12px; padding: 8px 10px; border-radius: 8px; background: rgb(255 255 255 / 90%); color: var(--pf-color-text-secondary); font-size: 9px; }
.map-preview__legend span { display: flex; align-items: center; gap: 4px; }
.legend-dot { width: 7px; height: 7px; border-radius: 50%; }
.legend-dot--coral { background: var(--pf-color-primary); }
.legend-dot--sage { background: var(--pf-color-sage); }
.legend-ring { width: 9px; height: 9px; border: 1px dashed var(--pf-color-primary); border-radius: 50%; }
.collaboration-copy > p { margin: 16px 0 25px; color: var(--pf-color-text-secondary); font-size: 13px; line-height: 1.85; }
.collaboration-copy ul { display: grid; gap: 15px; margin: 0 0 27px; padding: 0; list-style: none; }
.collaboration-copy li { display: flex; align-items: center; gap: 13px; }
.collaboration-copy li > span { display: grid; width: 34px; height: 34px; flex: 0 0 auto; place-items: center; border-radius: 10px; color: var(--pf-color-sage-dark); background: #fff; font-size: 10px; font-weight: 800; box-shadow: var(--pf-shadow-sm); }
.collaboration-copy li div { display: grid; }
.collaboration-copy li strong { font-size: 13px; }
.collaboration-copy li small { color: var(--pf-color-text-secondary); font-size: 10px; }
.inline-action { display: inline-flex; align-items: center; gap: 7px; padding: 11px 16px; border-radius: 9px; color: #fff; background: var(--pf-color-sage-dark); font-size: 12px; font-weight: 700; }

.home-stats { background: #4b3932; color: #fff; }
.home-stats__grid { display: grid; grid-template-columns: repeat(4, 1fr); }
.home-stats__grid > div { display: grid; justify-items: center; gap: 2px; padding: 29px 20px; border-right: 1px solid rgb(255 255 255 / 12%); }
.home-stats__grid > div:last-child { border-right: 0; }
.home-stats strong { color: #ffb18f; font-size: 30px; line-height: 1; }
.home-stats span { color: #d8c9c1; font-size: 10px; }

.home-reunion { padding: 70px 0 90px; }
.reunion-card { display: grid; grid-template-columns: auto 1fr auto; align-items: center; gap: 22px; padding: 28px 34px; border: 1px solid #eadaca; border-radius: var(--pf-radius-lg); background: linear-gradient(105deg, #fff7e7, #fff 55%, #eef6f0); box-shadow: var(--pf-shadow-sm); }
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
  .home-hero__visual { display: none; }
  .home-actions { margin-top: -44px; }
  .home-actions__grid { grid-template-columns: 1fr; }
  .action-card { min-height: 94px; }
  .collaboration-grid { grid-template-columns: 1fr; }
  .map-preview { height: 360px; }
  .home-stats__grid { grid-template-columns: repeat(2, 1fr); }
  .home-stats__grid > div:nth-child(2) { border-right: 0; }
  .home-stats__grid > div:nth-child(-n + 2) { border-bottom: 1px solid rgb(255 255 255 / 12%); }
}

@media (max-width: 640px) {
  .home-hero__inner { min-height: auto; padding-top: 42px; padding-bottom: 88px; }
  .home-hero h1 { font-size: 42px; overflow-wrap: anywhere; }
  .home-hero__copy > p { font-size: 14px; }
  .home-hero__buttons { align-items: stretch; flex-direction: column; }
  .home-hero__trust { align-items: flex-start; flex-direction: column; gap: 6px; }
  .home-section { padding: 68px 0; }
  .section-heading { align-items: flex-start; flex-direction: column; }
  .case-grid { grid-template-columns: 1fr; }
  .map-preview { height: 300px; }
  .map-radius { top: 55px; left: 45px; width: 170px; height: 170px; }
  .map-marker--case { top: 120px; left: 100px; }
  .map-marker--sighting { right: 28px; bottom: 70px; }
  .map-preview__legend { left: 12px; justify-content: center; }
  .home-stats strong { font-size: 25px; }
  .reunion-card { grid-template-columns: auto 1fr; padding: 24px 20px; }
  .reunion-card > a { grid-column: 1 / -1; justify-content: flex-end; }
}
</style>
