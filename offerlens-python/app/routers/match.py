"""匹配度评分路由：对比简历和 JD，给出分数+缺口分析+证据链。"""

from fastapi import APIRouter, HTTPException
from app.models import MatchResult, ResumeParseResult, JDParseResult
from app.services.matcher import match_resume_jd
from app.services.resume_parser import EmptyTextError

router = APIRouter(prefix="/api/match", tags=["匹配度评分"])


@router.post("", response_model=MatchResult)
def match(resume: ResumeParseResult, jd: JDParseResult):
    """对比简历和 JD，返回匹配度分析

    两个入参模型的所有字段都有默认值，空对象也能通过 pydantic 校验，
    真正的空内容校验在 match_resume_jd() 里。
    """
    try:
        return match_resume_jd(resume, jd)
    except EmptyTextError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
