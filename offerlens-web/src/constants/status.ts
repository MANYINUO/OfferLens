/**
 * 投递状态定义：状态名、展示顺序、阶段配色。
 *
 * 全站唯一来源。此前状态名散落在 DashboardView 与 ApplicationsView 两处，
 * 修改一个状态要同步改两个文件，容易漏。
 */

export type ApplicationStatus =
  | 'applied'
  | 'viewed'
  | 'written'
  | 'first'
  | 'second'
  | 'hr'
  | 'offer'
  | 'rejected'
  | 'no_response'
  | 'abandoned'

/** 状态 key → 中文名 */
export const STATUS_LABELS: Record<string, string> = {
  applied: '已投递',
  viewed: '已查看',
  written: '笔试中',
  first: '一面',
  second: '二面',
  hr: 'HR 面',
  offer: '已 Offer',
  rejected: '未通过',
  no_response: '暂无回复',
  abandoned: '已放弃',
}

/** 正常流转的七阶段顺序（不含终态） */
export const STAGE_ORDER = ['applied', 'viewed', 'written', 'first', 'second', 'hr', 'offer'] as const

/** 漏斗各阶段的进度条配色 */
export const STAGE_COLORS: Record<string, string> = {
  applied: '#9aabc0',
  viewed: '#7e9bbd',
  written: '#6f9fb4',
  first: '#6f9c8b',
  second: '#82926a',
  hr: '#b9905a',
  offer: '#4f8f72',
}

/** 已结束的状态：这些状态下不能再"推进进度" */
export const TERMINAL_STATUSES: readonly string[] = ['offer', 'rejected', 'no_response', 'abandoned']

/** 筛选下拉的选项（含"全部状态"空值项） */
export const STATUS_FILTER_OPTIONS: { key: string; label: string }[] = [
  { key: '', label: '全部状态' },
  ...STAGE_ORDER.map((key) => ({ key, label: STATUS_LABELS[key] })),
  { key: 'rejected', label: STATUS_LABELS.rejected },
  { key: 'no_response', label: STATUS_LABELS.no_response },
  { key: 'abandoned', label: STATUS_LABELS.abandoned },
]

/** 视为"已有回复"的阶段：从"已查看"开始都算拿到了回应 */
export const RESPONDED_STAGES: readonly string[] = ['viewed', 'written', 'first', 'second', 'hr', 'offer']

/** 取状态中文名，未知状态原样返回 */
export function statusLabel(status: string): string {
  return STATUS_LABELS[status] ?? status
}

/** 是否为终态 */
export function isTerminal(status: string): boolean {
  return TERMINAL_STATUSES.includes(status)
}
