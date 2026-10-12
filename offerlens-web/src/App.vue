<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink, RouterView, useRoute } from 'vue-router'

const route = useRoute()
const title = computed(() => String(route.meta.title || '总览'))

const navItems = [
  { to: '/', label: '工作台', symbol: '⌂' },
  { to: '/applications', label: '投递记录', symbol: '▤' },
  { to: '/match', label: '职位匹配', symbol: '✳', badge: 'AI' },
  { to: '/resumes', label: '简历版本', symbol: '▧' },
]
</script>

<template>
  <div class="app-shell">
    <a class="sr-only" href="#main-content">跳到主要内容</a>

    <aside class="sidebar">
      <RouterLink class="brand" to="/" aria-label="OfferLens 工作台首页">
        <span class="brand-mark" aria-hidden="true">O</span>
        <span class="brand-copy">
          <strong>OfferLens</strong>
          <small>求职工作台</small>
        </span>
      </RouterLink>

      <div class="sidebar-label" aria-hidden="true">Workspace</div>
      <nav class="main-nav" aria-label="主导航">
        <!--
          不再手写 router-link-active / exact-active 判断：
          RouterLink 默认会给当前路由加 router-link-active，
          用 exact-active-class 保证根路径只在精确匹配时高亮。
        -->
        <RouterLink
          v-for="item in navItems"
          :key="item.to"
          :to="item.to"
          class="nav-link"
          active-class="router-link-active"
          exact-active-class="router-link-exact-active"
        >
          <span class="nav-symbol" aria-hidden="true">{{ item.symbol }}</span>
          <span>{{ item.label }}</span>
          <span v-if="item.badge" class="nav-new">{{ item.badge }}</span>
        </RouterLink>
      </nav>

      <div class="sidebar-bottom">
        <div class="sidebar-tip">
          <span class="tip-spark" aria-hidden="true">✦</span>
          <strong>把求职变成有数据的决策</strong>
          <p>记录每一次投递，逐步找到更适合你的方向。</p>
          <RouterLink to="/match">开始职位分析 <span aria-hidden="true">↗</span></RouterLink>
        </div>
        <div class="profile-row">
          <div class="profile-avatar" aria-hidden="true">U</div>
          <div class="profile-copy">
            <strong>演示用户</strong>
            <small>个人工作区</small>
          </div>
          <span class="profile-dots" aria-hidden="true">···</span>
        </div>
      </div>
    </aside>

    <div class="main-area">
      <header class="topbar">
        <nav class="breadcrumb" aria-label="当前位置">
          <span>工作区</span>
          <b aria-hidden="true">/</b>
          <strong aria-current="page">{{ title }}</strong>
        </nav>
        <div class="topbar-right">
          <span class="service-state"><i aria-hidden="true"></i> 本地演示</span>
          <span class="topbar-avatar" aria-hidden="true">U</span>
        </div>
      </header>

      <main id="main-content" class="page-wrap">
        <RouterView />
      </main>

      <footer class="page-footer">
        OfferLens <span aria-hidden="true">·</span> 让每一次投递都有迹可循
      </footer>
    </div>
  </div>
</template>
