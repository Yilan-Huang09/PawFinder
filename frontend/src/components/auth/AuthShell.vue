<script setup lang="ts">
import { CircleCheck, Connection, Lock } from '@element-plus/icons-vue'

defineProps<{
  eyebrow: string
  title: string
  description: string
}>()
</script>

<template>
  <main class="auth-page">
    <div class="pf-container auth-shell pf-card">
      <section class="auth-shell__story">
        <RouterLink to="/" class="auth-shell__back">← 返回首页</RouterLink>
        <div class="auth-shell__illustration" aria-hidden="true">
          <span class="auth-pet__ear auth-pet__ear--left" />
          <span class="auth-pet__ear auth-pet__ear--right" />
          <span class="auth-pet__face">
            <i class="auth-pet__eye auth-pet__eye--left" />
            <i class="auth-pet__eye auth-pet__eye--right" />
            <i class="auth-pet__nose" />
          </span>
          <span class="auth-shell__pulse auth-shell__pulse--one" />
          <span class="auth-shell__pulse auth-shell__pulse--two" />
        </div>
        <h2>让善意有方向，让线索有回应</h2>
        <p>从发布信息到确认回家，每一步都清楚、可协作、可追踪。</p>
        <ul>
          <li><el-icon><Connection /></el-icon> 时空与外观线索匹配</li>
          <li><el-icon><CircleCheck /></el-icon> 志愿任务进度协同</li>
          <li><el-icon><Lock /></el-icon> 联系方式脱敏展示</li>
        </ul>
      </section>

      <section class="auth-shell__form">
        <span class="auth-shell__eyebrow">{{ eyebrow }}</span>
        <h1>{{ title }}</h1>
        <p class="auth-shell__description">{{ description }}</p>
        <slot />
      </section>
    </div>
  </main>
</template>

<style scoped>
.auth-page {
  min-height: calc(100vh - var(--pf-header-height));
  padding: 52px 0 70px;
  background:
    radial-gradient(circle at 90% 10%, rgb(255 217 202 / 70%), transparent 24rem),
    var(--pf-color-background);
}

.auth-shell {
  display: grid;
  max-width: 980px;
  min-height: 630px;
  grid-template-columns: 0.9fr 1.1fr;
  overflow: hidden;
}

.auth-shell__story {
  position: relative;
  display: flex;
  flex-direction: column;
  padding: 38px 42px;
  overflow: hidden;
  color: #ffffff;
  background:
    radial-gradient(circle at 18% 5%, rgb(255 255 255 / 18%), transparent 11rem),
    linear-gradient(155deg, #ef825d, #df603d 58%, #bd432c);
}

.auth-shell__back {
  position: relative;
  z-index: 2;
  width: fit-content;
  color: rgb(255 255 255 / 86%);
  font-size: 12px;
  font-weight: 700;
}

.auth-shell__illustration {
  position: relative;
  width: 230px;
  height: 225px;
  margin: 34px auto 12px;
}

.auth-pet__ear {
  position: absolute;
  z-index: 1;
  top: 23px;
  width: 72px;
  height: 100px;
  border-radius: 64% 15% 48% 45%;
  background: #8b4d3b;
}

.auth-pet__ear--left {
  left: 25px;
  transform: rotate(-23deg);
}

.auth-pet__ear--right {
  right: 25px;
  border-radius: 15% 64% 45% 48%;
  transform: rotate(23deg);
}

.auth-pet__face {
  position: absolute;
  z-index: 2;
  right: 28px;
  bottom: 10px;
  left: 28px;
  height: 174px;
  border-radius: 48% 48% 42% 42%;
  background: #f6c18d;
  box-shadow: inset 0 -15px 0 rgb(176 91 56 / 12%), 0 18px 30px rgb(91 37 23 / 20%);
}

.auth-pet__eye,
.auth-pet__nose {
  position: absolute;
  display: block;
  background: #51372e;
}

.auth-pet__eye {
  top: 66px;
  width: 14px;
  height: 18px;
  border-radius: 50%;
}

.auth-pet__eye--left {
  left: 47px;
}

.auth-pet__eye--right {
  right: 47px;
}

.auth-pet__nose {
  bottom: 48px;
  left: 50%;
  width: 24px;
  height: 17px;
  border-radius: 55% 55% 48% 48%;
  transform: translateX(-50%);
}

.auth-shell__pulse {
  position: absolute;
  border: 1px solid rgb(255 255 255 / 42%);
  border-radius: 50%;
}

.auth-shell__pulse--one {
  inset: 0;
}

.auth-shell__pulse--two {
  inset: 18px;
}

.auth-shell__story h2 {
  position: relative;
  z-index: 2;
  margin: 10px 0 8px;
  font-size: 24px;
  line-height: 1.35;
}

.auth-shell__story > p {
  position: relative;
  z-index: 2;
  margin: 0;
  color: rgb(255 255 255 / 78%);
  font-size: 13px;
}

.auth-shell__story ul {
  position: relative;
  z-index: 2;
  display: grid;
  gap: 9px;
  margin: 25px 0 0;
  padding: 0;
  list-style: none;
  color: rgb(255 255 255 / 88%);
  font-size: 12px;
}

.auth-shell__story li {
  display: flex;
  align-items: center;
  gap: 8px;
}

.auth-shell__form {
  align-self: center;
  padding: 52px 62px;
}

.auth-shell__eyebrow {
  color: var(--pf-color-primary);
  font-size: 12px;
  font-weight: 800;
  letter-spacing: 0.08em;
}

.auth-shell__form h1 {
  margin: 8px 0 8px;
  font-size: 32px;
  letter-spacing: -0.03em;
}

.auth-shell__description {
  margin: 0 0 28px;
  color: var(--pf-color-text-secondary);
  font-size: 13px;
}

@media (max-width: 820px) {
  .auth-shell {
    max-width: 570px;
    grid-template-columns: 1fr;
  }

  .auth-shell__story {
    display: none;
  }
}

@media (max-width: 640px) {
  .auth-page {
    padding: 24px 0 46px;
  }

  .auth-shell__form {
    padding: 36px 24px 42px;
  }
}
</style>
