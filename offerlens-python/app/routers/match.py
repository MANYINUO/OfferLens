"""匹配度评分路由：对比简历和 JD，给出分数+缺口分析+证据链。"""

from fastapi import APIRouter
from app.models import MatchResult, ResumeParseResult, JDParseResult
from app.services.matcher import match_resume_jd

router = APIRouter(prefix="/api/match", tags=["匹配度评分"])


@router.post("", response_model=MatchResult)
def match(resume: ResumeParseResult, jd: JDParseResult):
    """对比简历和 JD，返回匹配度分析"""
    return match_resume_jd(resume, jd)
