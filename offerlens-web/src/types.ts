export interface ApplicationRecord {
  id: number
  userId: number
  jdId?: number | null
  resumeId?: number | null
  company: string
  position: string
  channel?: string | null
  jobType?: string | null
  matchScore?: number | null
  status: string
  appliedAt?: string | null
  lastFollowupAt?: string | null
  notes?: string | null
}

export interface ResumeRecord {
  id: number
  userId: number
  versionName: string
  content: string
  createdAt?: string | null
}

export interface ExtractTextResult {
  text: string
  chars: number
  filename: string
  warning?: string | null
}

export interface FunnelStats {
  stages: Record<string, number>
  totalInFunnel: number
  terminal: Record<string, number>
  conversionRates: Record<string, number>
  overallRate: number
}

export interface MatchedEvidence {
  skill: string
  evidence: string
}

/** 漏斗归因：单个岗位类型的统计 */
export interface JobTypeStat {
  job_type: string
  total: number
  replied: number
  reply_rate: number
  offers: number
  offer_rate: number
}

/** 漏斗归因：单个渠道的统计 */
export interface ChannelStat {
  channel: string
  total: number
  replied: number
  reply_rate: number
}

/** 漏斗归因：单个简历版本的统计 */
export interface ResumeVersionStat {
  resume_version: string
  total: number
  replied: number
  reply_rate: number
  offers: number
}

/** 漏斗归因：单个时间段的统计 */
export interface TimePeriodStat {
  month: string
  total: number
  replied: number
  reply_rate: number
  no_response: number
}

/** 漏斗归因：单个匹配度区间的统计 */
export interface MatchScoreStat {
  score_range: string
  total: number
  replied: number
  reply_rate: number
}

/**
 * 漏斗归因接口返回。
 * 注意：无投递记录时后端只返回 { total: 0, message }，其余字段都缺省，
 * 所以除 total 外全部可选，调用方必须先判断 total 再读子维度。
 */
export interface FunnelAttribution {
  total: number
  message?: string
  replied?: number
  offers?: number
  overall_reply_rate?: number
  by_job_type?: JobTypeStat[]
  by_channel?: ChannelStat[]
  by_resume_version?: ResumeVersionStat[]
  by_time_period?: TimePeriodStat[]
  by_match_score?: MatchScoreStat[]
  conclusion?: string
}

export interface MatchAnalysis {
  match_score: number
  summary: string
  gap_analysis: string
  suggestions: string[]
  interview_questions: string[]
  hard_met: MatchedEvidence[]
  hard_missing: string[]
  nice_met?: MatchedEvidence[]
  nice_missing?: string[]
}
