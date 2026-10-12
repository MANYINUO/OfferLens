/**
 * 格式化工具。
 *
 * 此前 formatDate 在 Dashboard / Applications / Resumes 三个视图里各写了一遍，
 * 且实现不一致：工作台只显示"10月25日"，其它页面显示"2026年10月25日"。
 * 这里统一为两种明确用途。
 */

/** 短日期：10月25日 —— 用于列表、卡片等空间紧张处 */
export function formatShortDate(value?: string | null): string {
  if (!value) return '—'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value.slice(0, 10)
  return new Intl.DateTimeFormat('zh-CN', { month: 'short', day: 'numeric' }).format(date)
}

/** 完整日期：2026年10月25日 —— 用于需要精确日期的表格 */
export function formatFullDate(value?: string | null): string {
  if (!value) return '—'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value.slice(0, 10)
  return new Intl.DateTimeFormat('zh-CN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  }).format(date)
}

/** 截断长文本并加省略号 */
export function truncate(text: string, max: number): string {
  const normalized = text.replace(/\s+/g, ' ').trim()
  return normalized.length > max ? `${normalized.slice(0, max)}…` : normalized
}

/** 百分比展示，避免除零 */
export function percent(value: number, total: number): number {
  return total > 0 ? Math.round((value / total) * 100) : 0
}
