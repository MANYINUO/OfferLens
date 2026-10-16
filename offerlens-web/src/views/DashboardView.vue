<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { applicationApi, errorMessage } from '../api'
import EmptyState from '../components/EmptyState.vue'
import ErrorNotice from '../components/ErrorNotice.vue'
import FunnelAttributionPanel from '../components/FunnelAttributionPanel.vue'
import SkeletonTable from '../components/SkeletonTable.vue'
import { RESPONDED_STAGES, STAGE_COLORS, STAGE_ORDER, statusLabel } from '../constants/status'
import type { ApplicationRecord, FunnelStats } from '../types'
import { formatShortDate, percent } from '../utils/format'

const loading = ref(true)
const error = ref('')
const applications = ref<ApplicationRecord[]>([])
const funnel = ref<FunnelStats | null>(null)

const stages = computed(() =>
  STAGE_ORDER.map((key) => ({
    key,
    label: statusLabel(key),
    count: funnel.value?.stages?.[key] ?? 0,
    color: STAGE_COLORS[key],
  })),
)

const total = computed(() => {
  if (!funnel.value) return applications.value.length
  const terminal = Object.values(funnel.value.terminal || {}).reduce((sum, n) => sum + n, 0)
  return funnel.value.totalInFunnel + terminal
})

const responded = computed(() =>
  RESPONDED_STAGES.reduce((sum, key) => sum + (funnel.value?.stages?.[key] ?? 0), 0),
)
const offers = computed(() => funnel.value?.stages?.offer ?? 0)
const replyRate = computed(() => percent(responded.value, total.value))
const maxStage = computed(() => Math.max(1, ...stages.value.map((stage) => stage.count)))
const recent = computed(() => applications.value.slice(0, 5))

/** 面试阶段（一面 / 二面 / HR 面）合计 */
const interviewCount = computed(
  () =>
    (funnel.value?.stages?.first ?? 0) +
    (funnel.value?.stages?.second ?? 0) +
    (funnel.value?.stages?.hr ?? 0),
)

async function load() {
  loading.value = true
  error.value = ''
  const results = await Promise.allSettled([applicationApi.list(), applicationApi.funnel()])
  if (results[0].status === 'fulfilled') applications.value = results[0].value
  else error.value = errorMessage(results[0].reason)
  if (results[1].status === 'fulfilled') funnel.value = results[1].value
  else if (!error.value) error.value = errorMessage(results[1].reason)
  loading.value = false
}

onMounted(load)
</script>

<template>
  <section class="page-heading">
    <div>
      <div class="eyebrow">Your job search, in focus</div>
      <h1>把求职进展，<span>看得更清楚。</span></h1>
      <p>从每一次投递开始，积累属于你的求职判断。</p>
    </div>
    <RouterLink class="button button-primary" to="/applications">
      <span aria-hidden="true">＋</span> 新建投递
    </RouterLink>
  </section>

  <ErrorNotice v-if="error" :message="error" retry-label="重试" @retry="load" />

  <section class="stat-grid" aria-label="投递统计">
    <article class="stat-card stat-card-main">
      <div class="stat-top">
        <span>累计投递</span>
        <span class="stat-icon blue-icon" aria-hidden="true">↗</span>
      </div>
      <div class="stat-value">{{ loading ? '—' : total }}<small> 份</small></div>
      <div class="stat-foot"><span class="stat-dot" aria-hidden="true"></span>持续记录每一次机会</div>
    </article>
    <article class="stat-card">
      <div class="stat-top">
        <span>已获回复</span>
        <span class="stat-icon green-icon" aria-hidden="true">↗</span>
      </div>
      <div class="stat-value">{{ loading ? '—' : responded }}<small> 份</small></div>
      <div class="stat-foot">回复率 <strong>{{ loading ? '—' : `${replyRate}%` }}</strong></div>
    </article>
    <article class="stat-card">
      <div class="stat-top">
        <span>面试进展</span>
        <span class="stat-icon amber-icon" aria-hidden="true">◷</span>
      </div>
      <div class="stat-value">{{ loading ? '—' : interviewCount }}<small> 场</small></div>
      <div class="stat-foot">一面、二面与 HR 阶段</div>
    </article>
    <article class="stat-card">
      <div class="stat-top">
        <span>Offer</span>
        <span class="stat-icon purple-icon" aria-hidden="true">✦</span>
      </div>
      <div class="stat-value">{{ loading ? '—' : offers }}<small> 份</small></div>
      <div class="stat-foot">每一步进展都值得记录</div>
    </article>
  </section>

  <section class="dashboard-grid">
    <article class="panel funnel-panel">
      <div class="panel-heading">
        <div>
          <div class="eyebrow">Application overview</div>
          <h2>投递阶段分布</h2>
        </div>
        <RouterLink to="/applications" class="text-link">查看记录 <span aria-hidden="true">↗</span></RouterLink>
      </div>
      <div v-if="loading" class="skeleton-bars" aria-hidden="true"><i v-for="n in 5" :key="n"></i></div>
      <div v-else class="stage-list">
        <div v-for="stage in stages" :key="stage.key" class="stage-row">
          <span class="stage-name">{{ stage.label }}</span>
          <div class="stage-track" role="img" :aria-label="`${stage.label}：${stage.count} 份`">
            <i
              :style="{
                transform: `scaleX(${Math.max(stage.count ? 0.05 : 0, stage.count / maxStage)})`,
                background: stage.color,
              }"
            ></i>
          </div>
          <strong class="stage-count">{{ stage.count }}</strong>
        </div>
        <div v-if="!total" class="empty-inline">还没有投递记录，新增第一条记录后这里会显示进展。</div>
      </div>
      <div class="chart-caption">
        <span><i class="legend-dot" aria-hidden="true"></i>当前处于各阶段的投递数</span>
        <small>数据来自投递记录</small>
      </div>
    </article>

    <article class="panel insight-panel">
      <div class="insight-decoration" aria-hidden="true">✳</div>
      <div class="eyebrow">A small reminder</div>
      <h2>让数据帮你<br />找到下一步。</h2>
      <p>当投递记录逐渐积累，你可以比较不同岗位、渠道和简历版本的进展。</p>
      <RouterLink to="/match" class="button button-light">
        分析一个职位 <span aria-hidden="true">↗</span>
      </RouterLink>
      <div class="insight-foot">
        <span class="insight-line" aria-hidden="true"></span>
        <span>每一次投递，都是下一次决策的线索</span>
      </div>
    </article>
  </section>

  <FunnelAttributionPanel />

  <section class="panel recent-panel">
    <div class="panel-heading">
      <div>
        <div class="eyebrow">Recent activity</div>
        <h2>最近投递</h2>
      </div>
      <RouterLink to="/applications" class="text-link">全部记录 <span aria-hidden="true">↗</span></RouterLink>
    </div>
    <SkeletonTable v-if="loading" :rows="4" :columns="4" />
    <div v-else-if="recent.length" class="table-scroll">
      <table class="data-table">
        <caption class="sr-only">最近 5 条投递记录</caption>
        <thead>
          <tr>
            <th scope="col">公司 / 职位</th>
            <th scope="col">投递渠道</th>
            <th scope="col">匹配度</th>
            <th scope="col">当前进展</th>
            <th scope="col">投递日期</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in recent" :key="item.id">
            <td>
              <strong>{{ item.company }}</strong>
              <small>{{ item.position }}</small>
            </td>
            <td>{{ item.channel || '—' }}</td>
            <td>
              <span v-if="item.matchScore != null" class="score-pill">{{ item.matchScore }} 分</span>
              <span v-else class="muted">—</span>
            </td>
            <td>
              <span class="status-pill" :class="`status-${item.status}`">
                <i aria-hidden="true"></i>{{ statusLabel(item.status) }}
              </span>
            </td>
            <td>{{ formatShortDate(item.appliedAt) }}</td>
          </tr>
        </tbody>
      </table>
    </div>
    <EmptyState
      v-else
      icon="↗"
      title="还没有投递记录"
      description="把最近投递的职位记下来，开始建立自己的求职数据。"
      compact
    >
      <RouterLink to="/applications" class="button button-outline button-compact">添加第一条投递</RouterLink>
    </EmptyState>
  </section>
</template>

