<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { applicationApi, errorMessage } from '../api'
import EmptyState from '../components/EmptyState.vue'
import ErrorNotice from '../components/ErrorNotice.vue'
import SkeletonTable from '../components/SkeletonTable.vue'
import { useModalDismiss } from '../composables/useModalDismiss'
import { STATUS_FILTER_OPTIONS, isTerminal, statusLabel } from '../constants/status'
import type { ApplicationRecord } from '../types'
import { formatFullDate } from '../utils/format'

const statusOptions = STATUS_FILTER_OPTIONS
const rows = ref<ApplicationRecord[]>([])
const loading = ref(true)
const busyId = ref<number | null>(null)
const error = ref('')
const query = ref('')
const filterStatus = ref('')
const modalOpen = ref(false)
const saving = ref(false)
const formError = ref('')
const form = ref({ company: '', position: '', channel: '', jobType: '', notes: '' })

const filteredRows = computed(() => {
  const needle = query.value.trim().toLowerCase()
  if (!needle) return rows.value
  return rows.value.filter((row) =>
    `${row.company} ${row.position} ${row.channel || ''} ${row.jobType || ''}`
      .toLowerCase()
      .includes(needle),
  )
})

/** Esc 关闭 + 焦点陷阱 + 焦点归还 */
const { bind: bindModal } = useModalDismiss(modalOpen, () => {
  modalOpen.value = false
})

async function load() {
  loading.value = true
  error.value = ''
  try {
    rows.value = await applicationApi.list(undefined, filterStatus.value || undefined)
  } catch (reason) {
    error.value = errorMessage(reason)
  } finally {
    loading.value = false
  }
}

async function advance(row: ApplicationRecord) {
  busyId.value = row.id
  error.value = ''
  try {
    const updated = await applicationApi.advance(row.id)
    rows.value = rows.value.map((item) => (item.id === row.id ? updated : item))
  } catch (reason) {
    error.value = errorMessage(reason)
  } finally {
    busyId.value = null
  }
}

async function createApplication() {
  formError.value = ''
  if (!form.value.company.trim() || !form.value.position.trim()) {
    formError.value = '请填写公司名称和职位名称。'
    return
  }
  saving.value = true
  try {
    await applicationApi.create({
      company: form.value.company.trim(),
      position: form.value.position.trim(),
      channel: form.value.channel.trim() || undefined,
      jobType: form.value.jobType.trim() || undefined,
      notes: form.value.notes.trim() || undefined,
    })
    modalOpen.value = false
    form.value = { company: '', position: '', channel: '', jobType: '', notes: '' }
    await load()
  } catch (reason) {
    formError.value = errorMessage(reason)
  } finally {
    saving.value = false
  }
}

onMounted(load)
</script>

<template>
  <section class="page-heading">
    <div>
      <div class="eyebrow">Application tracker</div>
      <h1>投递记录</h1>
      <p>把申请进展留在一个地方，随时知道每个机会走到哪一步。</p>
    </div>
    <button class="button button-primary" @click="modalOpen = true">
      <span aria-hidden="true">＋</span> 新建投递
    </button>
  </section>

  <ErrorNotice v-if="error" :message="error" retry-label="重试" @retry="load" />

  <section class="panel applications-panel">
    <div class="toolbar">
      <div class="toolbar-title">
        <strong>全部机会</strong>
        <span>{{ filteredRows.length }} 条记录</span>
      </div>
      <div class="toolbar-controls">
        <label class="search-field">
          <span aria-hidden="true">⌕</span>
          <input v-model="query" type="search" placeholder="搜索公司或职位" aria-label="搜索公司或职位" />
        </label>
        <select v-model="filterStatus" class="select-control" aria-label="按状态筛选" @change="load">
          <option v-for="item in statusOptions" :key="item.key" :value="item.key">{{ item.label }}</option>
        </select>
      </div>
    </div>
    <SkeletonTable v-if="loading" :rows="6" :columns="5" />
    <div v-else-if="filteredRows.length" class="table-scroll">
      <table class="data-table application-table">
        <caption class="sr-only">投递记录列表</caption>
        <thead>
          <tr>
            <th scope="col">公司 / 职位</th>
            <th scope="col">岗位类型</th>
            <th scope="col">渠道</th>
            <th scope="col">匹配度</th>
            <th scope="col">当前进展</th>
            <th scope="col">投递日期</th>
            <th scope="col"><span class="sr-only">操作</span></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in filteredRows" :key="row.id">
            <td>
              <strong>{{ row.company }}</strong>
              <small>{{ row.position }}</small>
            </td>
            <td data-label="岗位类型">{{ row.jobType || '—' }}</td>
            <td data-label="渠道">{{ row.channel || '—' }}</td>
            <td data-label="匹配度">
              <span v-if="row.matchScore != null" class="score-pill">{{ row.matchScore }} 分</span>
              <span v-else class="muted">—</span>
            </td>
            <td data-label="当前进展">
              <span class="status-pill" :class="`status-${row.status}`">
                <i aria-hidden="true"></i>{{ statusLabel(row.status) }}
              </span>
            </td>
            <td data-label="投递日期">{{ formatFullDate(row.appliedAt) }}</td>
            <td>
              <button
                class="table-action"
                :disabled="busyId === row.id || isTerminal(row.status)"
                @click="advance(row)"
              >
                {{ busyId === row.id ? '更新中…' : '推进进度 →' }}
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <EmptyState
      v-else
      icon="▤"
      :title="query || filterStatus ? '没有找到匹配的记录' : '你的投递记录会出现在这里'"
      :description="
        query || filterStatus ? '试试调整搜索词或状态筛选。' : '新增第一条投递，开始追踪求职进展。'
      "
    >
      <button v-if="!query && !filterStatus" class="button button-outline" @click="modalOpen = true">
        ＋ 新建投递
      </button>
    </EmptyState>
  </section>

  <div v-if="modalOpen" class="modal-backdrop" @click.self="modalOpen = false">
    <section
      :ref="bindModal"
      class="modal-card"
      role="dialog"
      aria-modal="true"
      aria-labelledby="application-modal-title"
    >
      <div class="modal-heading">
        <div>
          <div class="eyebrow">New application</div>
          <h2 id="application-modal-title">记录一份新投递</h2>
        </div>
        <button class="close-button" aria-label="关闭对话框" @click="modalOpen = false">×</button>
      </div>
      <p class="modal-intro">先记下职位信息，其他内容之后也可以补充。</p>
      <form class="form-grid" @submit.prevent="createApplication">
        <label class="form-field">
          <span>公司名称 <b aria-hidden="true">*</b></span>
          <input v-model="form.company" required placeholder="例如：某某科技" />
        </label>
        <label class="form-field">
          <span>职位名称 <b aria-hidden="true">*</b></span>
          <input v-model="form.position" required placeholder="例如：Java 后端工程师" />
        </label>
        <label class="form-field">
          <span>投递渠道</span>
          <input v-model="form.channel" placeholder="例如：官网、内推、招聘平台" />
        </label>
        <label class="form-field">
          <span>岗位类型</span>
          <input v-model="form.jobType" placeholder="例如：Java 后端" />
        </label>
        <label class="form-field form-field-wide">
          <span>备注</span>
          <textarea v-model="form.notes" rows="3" placeholder="记录投递时想记住的内容…"></textarea>
        </label>
        <p v-if="formError" class="form-error form-field-wide" role="alert">{{ formError }}</p>
        <div class="modal-actions form-field-wide">
          <button type="button" class="button button-quiet" @click="modalOpen = false">取消</button>
          <button class="button button-primary" :disabled="saving">
            {{ saving ? '保存中…' : '保存投递' }}
          </button>
        </div>
      </form>
    </section>
  </div>
</template>
