import axios from 'axios'
import type {
  ApplicationRecord,
  ExtractTextResult,
  FunnelAttribution,
  FunnelStats,
  MatchAnalysis,
  ResumeRecord,
} from './types'

export const DEMO_USER_ID = 1

const javaClient = axios.create({ baseURL: '/api', timeout: 15000 })
const aiClient = axios.create({ baseURL: '/ai', timeout: 120000 })

interface JavaResult<T> {
  code: number
  message: string
  data: T
}

async function javaRequest<T>(request: Promise<{ data: JavaResult<T> }>): Promise<T> {
  const response = await request
  if (response.data.code !== 200) {
    throw new Error(response.data.message || '请求失败')
  }
  return response.data.data
}

export const applicationApi = {
  list(userId = DEMO_USER_ID, status?: string) {
    return javaRequest<ApplicationRecord[]>(javaClient.get('/applications', {
      params: { userId, ...(status ? { status } : {}) },
    }))
  },
  create(payload: Partial<ApplicationRecord> & { company: string; position: string }) {
    return javaRequest<ApplicationRecord>(javaClient.post('/applications', {
      userId: DEMO_USER_ID,
      ...payload,
    }))
  },
  advance(id: number) {
    return javaRequest<ApplicationRecord>(javaClient.post(`/applications/${id}/advance`))
  },
  funnel(userId = DEMO_USER_ID) {
    return javaRequest<FunnelStats>(javaClient.get('/stats/funnel', { params: { userId } }))
  },
}

export const resumeApi = {
  list(userId = DEMO_USER_ID) {
    return javaRequest<ResumeRecord[]>(javaClient.get('/resumes', { params: { userId } }))
  },
  create(versionName: string, content: string) {
    return javaRequest<ResumeRecord>(javaClient.post('/resumes', {
      userId: DEMO_USER_ID,
      versionName,
      content,
    }))
  },
  delete(id: number) {
    return javaRequest<void>(javaClient.delete(`/resumes/${id}`))
  },
  async extractText(file: File) {
    const body = new FormData()
    body.append('file', file)
    const response = await aiClient.post<ExtractTextResult>('/resume/extract-text', body)
    return response.data
  },
}

export const aiApi = {
  analyze(resumeText: string, jdText: string) {
    return aiClient.post<MatchAnalysis>('/agent/analyze', {
      user_id: DEMO_USER_ID,
      resume_text: resumeText,
      jd_text: jdText,
    }).then((response) => response.data)
  },

  /**
   * 漏斗归因：由 Python 侧汇总投递数据后交给 LLM 生成结论。
   * 耗时通常在 3~5 秒（含一次 LLM 调用），比普通查询慢，前端要给加载态。
   */
  funnelAttribution(userId = DEMO_USER_ID) {
    return aiClient.get<FunnelAttribution>('/funnel/analysis', {
      params: { user_id: userId },
    }).then((response) => response.data)
  },
}

export function errorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const data = error.response?.data
    const detail = data?.detail
    const message = data?.message

    // FastAPI 的 422 校验错误里 detail 是数组，形如
    // [{"type":"value_error","loc":["body","text"],"msg":"Value error, 文本不能为空"}]
    if (Array.isArray(detail) && detail.length > 0) {
      const first = detail[0]
      if (typeof first?.msg === 'string') {
        return first.msg.replace(/^Value error,\s*/, '')
      }
    }
    if (typeof detail === 'string') return detail
    if (typeof message === 'string') return message
    if (error.code === 'ECONNABORTED') return '请求超时，请稍后重试。'
    if (!error.response) return '无法连接服务，请确认 Java 和 Python 服务已启动。'
    return `请求失败（HTTP ${error.response.status}）`
  }
  return error instanceof Error ? error.message : '发生未知错误'
}
