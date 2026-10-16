<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { resumeApi, errorMessage } from '../api'
import EmptyState from '../components/EmptyState.vue'
import ErrorNotice from '../components/ErrorNotice.vue'
import { useModalDismiss } from '../composables/useModalDismiss'
import type { ResumeRecord } from '../types'
import { formatFullDate, truncate } from '../utils/format'

const resumes = ref<ResumeRecord[]>([])
const loading = ref(true)
const saving = ref(false)
const error = ref('')
const modalOpen = ref(false)
const form = ref({ versionName: '', content: '' })
const formError = ref('')
const characterCount = computed(() => form.value.content.length)
const uploading = ref(false)
const uploadHint = ref('')
const fileInput = ref<HTMLInputElement | null>(null)
const dragging = ref(false)
const MAX_TEXT_FILE = 2 * 1024 * 1024
// 必须与后端 app/constants.py 的 MAX_TEXT_CHARS、Java 的 MAX_CONTENT_CHARS 一致
const MAX_RESUME_CHARS = 20_000

async function load() {
  loading.value = true
  error.value = ''
  try { resumes.value = await resumeApi.list() }
  catch (reason) { error.value = errorMessage(reason) }
  finally { loading.value = false }
}

async function createResume() {
  formError.value = ''
  if (uploading.value) return
  if (!form.value.versionName.trim() || !form.value.content.trim()) {
    formError.value = '请填写版本名称和简历内容。'
    return
  }
  if (form.value.content.length > MAX_RESUME_CHARS) {
    formError.value = `简历内容 ${form.value.content.length} 字，超过 ${MAX_RESUME_CHARS} 字上限，请精简后再保存。`
    return
  }
  saving.value = true
  try {
    await resumeApi.create(form.value.versionName.trim(), form.value.content.trim())
    modalOpen.value = false
    form.value = { versionName: '', content: '' }
    uploadHint.value = ''
    await load()
  } catch (reason) { formError.value = errorMessage(reason) }
  finally { saving.value = false }
}

function openModal() {
  uploadHint.value = ''
  formError.value = ''
  modalOpen.value = true
}

function closeModal() {
  if (uploading.value || saving.value) return
  modalOpen.value = false
  uploadHint.value = ''
  formError.value = ''
}

/** Esc 关闭 + 焦点陷阱 + 焦点归还 */
const { bind: bindModal } = useModalDismiss(modalOpen, closeModal)

function pickFile() {
  if (!uploading.value) fileInput.value?.click()
}

/** 把提取结果填进编辑框，超长时截断并明确告知用户 */
function applyContent(raw: string, fileName: string, baseName: string, backendWarning?: string | null) {
  const clipped = raw.length > MAX_RESUME_CHARS
  form.value.content = clipped ? raw.slice(0, MAX_RESUME_CHARS) : raw
  if (!form.value.versionName.trim()) form.value.versionName = baseName

  if (clipped) {
    uploadHint.value = `提取到 ${raw.length} 个字符，已截断到 ${MAX_RESUME_CHARS} 字上限，请检查结尾是否完整。`
  } else if (backendWarning) {
    uploadHint.value = backendWarning
  } else {
    uploadHint.value = `已从 ${fileName} 读入 ${raw.length} 个字符，请核对后保存。`
  }
}

async function readFile(file: File) {
  if (uploading.value) return
  uploadHint.value = ''
  formError.value = ''

  const name = file.name.toLowerCase()
  const baseName = file.name.replace(/\.(pdf|txt|md)$/i, '')

  if (!name.endsWith('.pdf') && !name.endsWith('.txt') && !name.endsWith('.md')) {
    formError.value = '只支持 PDF、txt、md。图片需要 OCR，目前不支持，请先转成可复制文字的 PDF。'
    return
  }

  if (form.value.content.trim() && !window.confirm('导入会替换当前已填写的内容，继续？')) {
    return
  }

  if (name.endsWith('.txt') || name.endsWith('.md')) {
    if (file.size > MAX_TEXT_FILE) {
      formError.value = '文本文件超过 2MB，请检查是否选错文件。'
      return
    }
    let text = ''
    try {
      text = await file.text()
    } catch {
      formError.value = '无法读取这个文本文件，请另存为 UTF-8 后重试。'
      return
    }
    // File.text() 固定按 UTF-8 解码，GBK 文件不会抛异常，只会产生替换字符 U+FFFD
    if (text.includes('\uFFFD')) {
      formError.value = '文件编码可能不是 UTF-8（内容出现乱码）。请另存为 UTF-8，或直接粘贴文本。'
      return
    }
    if (!text.trim()) {
      formError.value = '文件没有可用的文本内容。'
      return
    }
    applyContent(text, file.name, baseName)
    return
  }

  uploading.value = true
  try {
    const result = await resumeApi.extractText(file)
    applyContent(result.text, file.name, baseName, result.warning)
  } catch (reason) {
    formError.value = errorMessage(reason)
  } finally {
    uploading.value = false
  }
}

function onFileChange(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  input.value = ''
  if (file) void readFile(file)
}

function onDrop(event: DragEvent) {
  dragging.value = false
  const file = event.dataTransfer?.files?.[0]
  if (file) void readFile(file)
}

async function removeResume(resume: ResumeRecord) {
  if (!window.confirm(`确定删除「${resume.versionName}」吗？删除后无法恢复。`)) return
  try {
    await resumeApi.delete(resume.id)
    resumes.value = resumes.value.filter((item) => item.id !== resume.id)
  } catch (reason) { error.value = errorMessage(reason) }
}

function preview(content: string) {
  return truncate(content, 180)
}

onMounted(load)
</script>

<template>
  <section class="page-heading">
    <div>
      <div class="eyebrow">Resume library</div>
      <h1>简历版本</h1>
      <p>为不同方向保留简历版本，分析职位时可以直接载入。</p>
    </div>
    <button class="button button-primary" @click="openModal()">
      <span aria-hidden="true">＋</span> 添加简历
    </button>
  </section>

  <ErrorNotice v-if="error" :message="error" retry-label="重试" @retry="load" />

  <section v-if="loading" class="panel table-loading" role="status">正在读取简历版本…</section>
  <section v-else-if="resumes.length" class="resume-grid">
    <article v-for="(resume, index) in resumes" :key="resume.id" class="panel resume-card">
      <div class="resume-card-top">
        <div class="resume-file-icon" :class="`resume-tone-${index % 4}`" aria-hidden="true">▧</div>
        <button
          type="button"
          class="more-button"
          title="删除这个版本"
          :aria-label="`删除${resume.versionName}`"
          @click="removeResume(resume)"
        >
          <span class="more-dots" aria-hidden="true">···</span>
          <span class="more-label" aria-hidden="true">删除</span>
        </button>
      </div>
      <div class="resume-version-label">版本 {{ String(index + 1).padStart(2, '0') }}</div>
      <h2>{{ resume.versionName }}</h2>
      <p class="resume-preview">{{ preview(resume.content) }}</p>
      <div class="resume-card-foot">
        <span>{{ formatFullDate(resume.createdAt) }}</span>
        <span>{{ resume.content.length }} 字</span>
      </div>
    </article>
    <button class="add-resume-card" @click="openModal()">
      <span aria-hidden="true">＋</span>
      <strong>添加另一个版本</strong>
      <small>为不同岗位方向准备简历</small>
    </button>
  </section>

  <section v-else class="panel">
    <EmptyState
      icon="▧"
      title="保存你的第一个简历版本"
      description="保存纯文本简历后，可以在职位匹配页面快速载入。"
    >
      <button class="button button-outline" @click="openModal()">＋ 添加简历</button>
    </EmptyState>
  </section>

  <div v-if="modalOpen" class="modal-backdrop" @click.self="closeModal()">
    <section
      :ref="bindModal"
      class="modal-card resume-modal"
      role="dialog"
      aria-modal="true"
      aria-labelledby="resume-modal-title"
    >
      <div class="modal-heading">
        <div>
          <div class="eyebrow">New resume version</div>
          <h2 id="resume-modal-title">添加简历版本</h2>
        </div>
        <button
          class="close-button"
          aria-label="关闭对话框"
          :disabled="uploading || saving"
          @click="closeModal()"
        >
          ×
        </button>
      </div>
      <p class="modal-intro">仅保存用于匹配分析的简历文本。请勿粘贴不希望发送给 AI 服务的敏感信息。</p>
      <form class="form-grid" @submit.prevent="createResume">
        <label class="form-field form-field-wide">
          <span>版本名称 <b aria-hidden="true">*</b></span>
          <input v-model="form.versionName" required placeholder="例如：Java 后端版、AI 应用版" />
        </label>
        <div class="form-field form-field-wide">
          <span>简历内容 <b aria-hidden="true">*</b></span>
          <div
            class="resume-import-row"
            :class="{ 'is-dragging': dragging }"
            @dragover.prevent="dragging = true"
            @dragleave.prevent="dragging = false"
            @drop.prevent="onDrop"
          >
            <button
              type="button"
              class="button button-outline button-compact"
              :disabled="uploading || saving"
              @click="pickFile"
            >
              {{ uploading ? '正在提取…' : '上传 PDF / txt' }}
            </button>
            <span class="resume-import-hint">也可以拖文件到这里，或直接在下方粘贴</span>
            <input ref="fileInput" type="file" accept=".pdf,.txt,.md" hidden @change="onFileChange" />
          </div>
          <textarea
            v-model="form.content"
            rows="12"
            :disabled="uploading"
            :maxlength="MAX_RESUME_CHARS"
            aria-label="简历内容"
            placeholder="粘贴简历文本，或上传 PDF 后自动填入…"
          ></textarea>
          <small v-if="uploadHint" class="field-hint resume-upload-hint">{{ uploadHint }}</small>
          <small class="field-hint">{{ characterCount }} 字符</small>
        </div>
        <p v-if="formError" class="form-error form-field-wide" role="alert">{{ formError }}</p>
        <div class="modal-actions form-field-wide">
          <button type="button" class="button button-quiet" :disabled="uploading || saving" @click="closeModal()">
            取消
          </button>
          <button class="button button-primary" :disabled="saving || uploading">
            {{ uploading ? '正在提取…' : saving ? '保存中…' : '保存版本' }}
          </button>
        </div>
      </form>
    </section>
  </div>
</template>
