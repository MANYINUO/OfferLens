<script setup lang="ts">
/**
 * 漏斗归因面板：把 Python 侧「投递数据统计 + LLM 归因结论」展示出来。
 *
 * 与 Dashboard 上的「投递阶段分布」区别：
 *   - 阶段分布：各阶段当前有多少条投递（纯 Java SQL 统计，即时返回）
 *   - 归因面板：按岗位/渠道/简历/时段/匹配度五个维度算回复率，再由 LLM
 *     解释「为什么」并给出行动建议（要调一次大模型，3~5 秒）
 *
 * 数据量大时结论可能较长，默认折叠为前几行，用户可展开全文。
 */
import { computed, ref } from 'vue'
import { aiApi, errorMessage } from '../api'
import type { FunnelAttribution } from '../types'
import EmptyState from './EmptyState.vue'
import ErrorNotice from './ErrorNotice.vue'

const state = ref<'idle' | 'loading' | 'done' | 'error'>('idle')
const data = ref<FunnelAttribution | null>(null)
const error = ref('')
const expanded = ref(false)

/**
 * 把 LLM 结论拆成段落。
 * 模型输出的排版并不稳定：有时用「1. 2. 3.」编号，有时只用空行分段，
 * 所以两种分隔方式都要认，否则整段会挤成一个 <p>，读起来很累。
 */
const conclusionParagraphs = computed(() => {
  const text = data.value?.conclusion?.trim()
  if (!text) return []
  return text
    .split(/\n{2,}/)
    .flatMap((block) => block.split(/\n(?=\d+\.\s)/))
    .map((part) => part.trim())
    .filter(Boolean)
})

/** 未展开时只显示前 3 段（约一段导语 + 两条主结论），避免把页面撑得过长 */
const visibleParagraphs = computed(() =>
  expanded.value ? conclusionParagraphs.value : conclusionParagraphs.value.slice(0, 3),
)
const canExpand = computed(() => conclusionParagraphs.value.length > 3)

/** 渠道维度里回复率最高的那个，用于给出一句结论式提示 */
const bestChannel = computed(() => {
  const list = data.value?.by_channel ?? []
  if (list.length < 2) return null
  return [...list].sort((a, b) => b.reply_rate - a.reply_rate)[0]
})

/** 匹配度维度里样本最多的有效区间，用来支撑「多少分以上值得投」 */
const matchInsight = computed(() => {
  const list = (data.value?.by_match_score ?? []).filter((item) => item.total > 0)
  if (!list.length) return null
  const withReply = list.filter((item) => item.reply_rate > 0)
  if (!withReply.length) return null
  return withReply.reduce((best, item) => (item.reply_rate > best.reply_rate ? item : best))
})

async function run() {
  state.value = 'loading'
  error.value = ''
  expanded.value = false
  try {
    const result = await aiApi.funnelAttribution()
    data.value = result
    // 没有投递记录时后端只返回 { total: 0, message }，交给模板里的空态分支处理
    state.value = 'done'
  } catch (reason) {
    error.value = errorMessage(reason)
    state.value = 'error'
  }
}
</script>

<template>
  <section class="panel attribution-panel">
    <div class="panel-heading">
      <div>
        <div class="eyebrow">AI attribution</div>
        <h2>投递归因</h2>
      </div>
      <span class="ai-badge"><span aria-hidden="true">✦</span>AI 分析</span>
    </div>

    <!-- 未运行：说明这个面板能回答什么，再给一个明确的触发按钮 -->
    <div v-if="state === 'idle'" class="attribution-intro">
      <p>
        汇总你的投递记录，从<strong>岗位类型、渠道、简历版本、投递时段、匹配度</strong>五个维度
        计算回复率，并解释哪一步出了问题、下一步该往哪投。
      </p>
      <button type="button" class="button button-primary button-compact" @click="run">
        <span aria-hidden="true">✦</span> 开始分析
      </button>
      <small class="attribution-hint">需要几秒钟，会调用一次大模型</small>
    </div>

    <div v-else-if="state === 'loading'" class="attribution-loading" role="status" aria-live="polite">
      <div class="skeleton-bars" aria-hidden="true"><i v-for="n in 4" :key="n"></i></div>
      <p>正在统计投递数据并生成归因结论…</p>
    </div>

    <ErrorNotice v-else-if="state === 'error'" :message="error" retry-label="重试" @retry="run" />

    <EmptyState
      v-else-if="!data || data.total === 0"
      icon="✦"
      title="还没有可分析的投递记录"
      :description="data?.message || '先记录几条投递，再回来看看哪条路更值得走。'"
      compact
    >
      <button type="button" class="button button-outline button-compact" @click="run">重新分析</button>
    </EmptyState>

    <div v-else class="attribution-body">
      <!-- 顶部关键指标 -->
      <div class="attribution-metrics">
        <div>
          <span>样本投递</span>
          <strong>{{ data.total }}<small> 份</small></strong>
        </div>
        <div>
          <span>获得回复</span>
          <strong>{{ data.replied ?? 0 }}<small> 份</small></strong>
        </div>
        <div>
          <span>整体回复率</span>
          <strong>{{ data.overall_reply_rate ?? 0 }}<small>%</small></strong>
        </div>
        <div>
          <span>Offer</span>
          <strong>{{ data.offers ?? 0 }}<small> 份</small></strong>
        </div>
      </div>

      <!-- 两条最有信息量的横向对比，避免把五个维度全铺开 -->
      <div v-if="bestChannel || matchInsight" class="attribution-highlights">
        <p v-if="bestChannel">
          <span class="highlight-label">渠道</span>
          <strong>{{ bestChannel.channel }}</strong> 回复率最高
          （{{ bestChannel.reply_rate }}%，{{ bestChannel.total }} 投 {{ bestChannel.replied }} 回）
        </p>
        <p v-if="matchInsight">
          <span class="highlight-label">匹配度</span>
          <strong>{{ matchInsight.score_range }} 分</strong> 区间回复率 {{ matchInsight.reply_rate }}%
          （{{ matchInsight.total }} 投 {{ matchInsight.replied }} 回）
        </p>
      </div>

      <!-- LLM 结论 -->
      <div v-if="conclusionParagraphs.length" class="attribution-conclusion">
        <h3>归因结论</h3>
        <p v-for="(paragraph, index) in visibleParagraphs" :key="index">{{ paragraph }}</p>
        <button
          v-if="canExpand"
          type="button"
          class="text-link attribution-toggle"
          :aria-expanded="expanded"
          @click="expanded = !expanded"
        >
          {{ expanded ? '收起' : `展开全部 ${conclusionParagraphs.length} 段` }}
          <span aria-hidden="true">{{ expanded ? '↑' : '↓' }}</span>
        </button>
      </div>

      <button type="button" class="text-link attribution-rerun" @click="run">重新分析</button>
    </div>
  </section>
</template>
