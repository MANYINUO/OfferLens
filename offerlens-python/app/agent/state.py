"""LangGraph 工作流状态定义：在节点之间传递的数据。"""

from typing import List, Optional, TypedDict

from app.models import ResumeParseResult, JDParseResult, MatchResult


class AgentState(TypedDict):
    """工作流状态：每个节点读取并更新这个字典"""
    # 输入
    user_id: int
    resume_text: str
    jd_text: str

    # 中间结果（节点逐步填充）
    resume_structured: Optional[ResumeParseResult]
    jd_structured: Optional[JDParseResult]
    match_result: Optional[MatchResult]
    gap_analysis: str
    suggestions: List[str]
    interview_questions: List[str]

    # 错误信息
    error: Optional[str]
