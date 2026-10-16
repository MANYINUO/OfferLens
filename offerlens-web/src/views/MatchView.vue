<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { aiApi, applicationApi, errorMessage, resumeApi } from '../api'
import ErrorNotice from '../components/ErrorNotice.vue'
import SuccessNotice from '../components/SuccessNotice.vue'
import type { MatchAnalysis, ResumeRecord } from '../types'

const resumes = ref<ResumeRecord[]>([])
const selectedResumeId = ref('')
const resumeText = ref('')
const jdText = ref('')
const company = ref('')
const position = ref('')
const channel = ref('')
const result = ref<MatchAnalysis | null>(null)
const loading = ref(false)
const saving = ref(false)
const error = ref('')
const savedNotice = ref('')

/** 重新分析时旧结果仍在，只是变暗不可交互，避免内容突然消失 */
const isStale = computed(() => loading.value && result.value !== null)

async function loadResumes() {
  try { resumes.value = await resumeApi.list() }
  catch { /* 简历列表不可用时，仍允许直接粘贴文本分析。 */ }
}

function useResume() {
  const resume = resumes.value.find((item) => String(item.id) === selectedResumeId.value)
  if (resume) resumeText.value = resume.content
}

async function analyze() {
  error.value = ''
  savedNotice.value = ''
  if (!resumeText.value.trim() || !jdText.value.trim()) {
    error.value = '请先填写简历内容和职位描述。'
    return
  }
  // 不清空 result：重新分析时保留上一次结果（CSS 里变暗处理），
  // 首次分析时 result 本来就是 null，不会显示旧内容。
  loading.value = true
  try {
    result.value = await aiApi.analyze(resumeText.value.trim(), jdText.value.trim())
  } catch (reason) {
    error.value = errorMessage(reason)
  } finally {
    loading.value = false
  }
}

async function saveApplication() {
  if (!result.value) return
  if (!company.value.trim() || !position.value.trim()) {
    error.value = '请填写公司和职位名称，再保存到投递记录。'
    return
  }
  saving.value = true
  error.value = ''
  try {
    await applicationApi.create({
      company: company.value.trim(),
      position: position.value.trim(),
      channel: channel.value.trim() || undefined,
      matchScore: result.value.match_score,
      jdId: undefined,
      resumeId: selectedResumeId.value ? Number(selectedResumeId.value) : undefined,
    })
    savedNotice.value = '已保存到投递记录。'
  } catch (reason) {
    error.value = errorMessage(reason)
  } finally {
    saving.value = false
  }
}

onMounted(loadResumes)
</script>

<template>
  <section class="page-heading">
    <div>
      <div class="eyebrow">AI job match</div>
      <h1>先看清匹配，再决定投入。</h1>
      <p>对照简历与职位要求，找出匹配依据和需要关注的差距。</p>
    </div>
    <div class="ai-badge"><span aria-hidden="true">✳</span> AI 辅助分析</div>
  </section>

  <ErrorNotice v-if="error" :message="error" />
  <SuccessNotice v-if="savedNotice" :message="savedNotice" />

  <section class="match-input-grid">
    <article class="panel input-panel">
      <div class="input-panel-heading">
        <div class="input-icon resume-input-icon" aria-hidden="true">▧</div>
        <div>
          <h2>你的简历</h2>
          <p>粘贴简历文本，或从已有版本载入。</p>
        </div>
      </div>
      <label v-if="resumes.length" class="resume-picker">
        <span>载入已保存版本</span>
        <select v-model="selectedResumeId" @change="useResume">
          <option value="">选择一个简历版本</option>
          <option v-for="resume in resumes" :key="resume.id" :value="String(resume.id)">
            {{ resume.versionName }}
          </option>
        </select>
      </label>
      <textarea
        v-model="resumeText"
        class="large-textarea"
        rows="12"
        aria-label="简历内容"
        placeholder="粘贴简历内容…"
      ></textarea>
      <div class="textarea-foot">
        <span>{{ resumeText.length }} 字符</span>
        <RouterLink to="/resumes">管理简历版本 ↗</RouterLink>
      </div>
    </article>

    <article class="panel input-panel">
      <div class="input-panel-heading">
        <div class="input-icon jd-input-icon" aria-hidden="true">⌕</div>
        <div>
          <h2>目标职位</h2>
          <p>粘贴职位描述，补充公司和职位名称。</p>
        </div>
      </div>
      <div class="job-meta-fields">
        <input v-model="company" aria-label="公司名称" placeholder="公司名称（如：某某科技）" />
        <input v-model="position" aria-label="职位名称" placeholder="职位名称（如：后端工程师）" />
      </div>
      <textarea
        v-model="jdText"
        class="large-textarea"
        rows="10"
        aria-label="职位描述"
        placeholder="粘贴职位描述（JD）…"
      ></textarea>
      <div class="textarea-foot">
        <span>{{ jdText.length }} 字符</span>
        <input
          v-model="channel"
          class="inline-channel"
          aria-label="投递渠道"
          placeholder="投递渠道（可选）"
        />
      </div>
    </article>
  </section>

  <div class="match-submit-row">
    <p>
      提交后，简历和 JD 会发送到配置的 AI 服务。建议先移除电话、邮箱等敏感信息；匹配分数与证据片段由 AI 生成。
    </p>
    <button class="button button-primary button-analyze" :disabled="loading" @click="analyze">
      <span aria-hidden="true">✳</span>{{ loading ? '正在分析…' : '开始匹配分析' }}
      <span aria-hidden="true">→</span>
    </button>
  </div>

  <section v-if="loading" class="panel analysis-loading" aria-live="polite">
    <span class="loading-orbit" aria-hidden="true">✳</span>
    <strong>{{ result ? '正在重新分析' : '正在对照简历与职位要求' }}</strong>
    <p>模型正在整理匹配项、缺口和建议，通常需要一些时间。</p>
  </section>

  <section v-if="result" class="analysis-result" :class="{ 'is-stale': isStale }">
    <article class="panel result-summary">
      <div class="result-score">
        <div class="score-ring" :aria-label="`匹配度 ${result.match_score} 分，满分 100`">
          <strong>{{ result.match_score }}</strong><small>/ 100</small>
        </div>
        <span>AI 匹配度</span>
      </div>
      <div class="result-summary-copy">
        <div class="eyebrow">Match summary</div>
        <h2>{{ result.summary || '匹配分析已完成' }}</h2>
        <p>{{ result.gap_analysis }}</p>
      </div>
      <button class="button button-outline save-match-button" :disabled="saving" @click="saveApplication">
        {{ saving ? '保存中…' : '＋ 保存为投递记录' }}
      </button>
    </article>

    <div class="analysis-columns">
      <article class="panel analysis-card">
        <div class="panel-heading compact-heading">
          <div>
            <div class="eyebrow">Requirements</div>
            <h2>要求对照</h2>
          </div>
        </div>
        <div class="requirement-group">
          <h3>
            <span class="requirement-check" aria-hidden="true">✓</span> 已匹配
            <small>{{ result.hard_met?.length || 0 }}</small>
          </h3>
          <div v-if="result.hard_met?.length" class="evidence-list">
            <div
              v-for="(item, index) in result.hard_met"
              :key="`${item.skill}-${index}`"
              class="evidence-item"
            >
              <strong>{{ item.skill }}</strong>
              <blockquote>“{{ item.evidence }}”</blockquote>
            </div>
          </div>
          <p v-else class="result-empty-line">暂无明确的已匹配项。</p>
        </div>
        <div class="requirement-group missing-group">
          <h3>
            <span class="requirement-missing" aria-hidden="true">−</span> 待关注
            <small>{{ result.hard_missing?.length || 0 }}</small>
          </h3>
          <ul v-if="result.hard_missing?.length">
            <li v-for="(item, index) in result.hard_missing" :key="`${item}-${index}`">{{ item }}</li>
          </ul>
          <p v-else class="result-empty-line">未识别到缺失的硬性要求。</p>
        </div>
      </article>
      <article class="panel analysis-card">
        <div class="panel-heading compact-heading">
          <div>
            <div class="eyebrow">Next steps</div>
            <h2>接下来可以做什么</h2>
          </div>
        </div>
        <ol v-if="result.suggestions?.length" class="suggestion-list">
          <li v-for="(item, index) in result.suggestions" :key="index">
            <span aria-hidden="true">{{ String(index + 1).padStart(2, '0') }}</span>
            <p>{{ item }}</p>
          </li>
        </ol>
        <p v-else class="result-empty-line">暂无建议。</p>

        <div class="questions-block">
          <h3>面试准备提示</h3>
          <ol v-if="result.interview_questions?.length">
            <li v-for="(item, index) in result.interview_questions" :key="index">{{ item }}</li>
          </ol>
          <p v-else class="result-empty-line">暂无面试题。</p>
        </div>
      </article>
    </div>
    <div class="analysis-disclaimer">AI 输出是辅助信息。建议回到简历与职位原文核对具体要求。</div>
  </section>
</template>
