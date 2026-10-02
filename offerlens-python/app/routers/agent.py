"""Agent 对话接口：运行 LangGraph 工作流，返回完整分析结果。"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, field_validator
from app.agent.graph import agent_graph
from app.constants import MAX_TEXT_CHARS

router = APIRouter(prefix="/api/agent", tags=["Agent分析"])


class AgentRequest(BaseModel):
    user_id: int
    resume_text: str = Field(min_length=1, max_length=MAX_TEXT_CHARS)
    jd_text: str = Field(min_length=1, max_length=MAX_TEXT_CHARS)

    @field_validator("resume_text", "jd_text")
    @classmethod
    def not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("文本不能为空")
        return value


class AgentResponse(BaseModel):
    match_score: int
    summary: str
    gap_analysis: str
    suggestions: list
    interview_questions: list
    hard_met: list
    hard_missing: list


@router.post("/analyze")
def analyze(req: AgentRequest):
    """运行完整 Agent 分析流程：简历解析→JD解析→匹配→缺口分析→建议→面试题"""
    initial_state = {
        "user_id": req.user_id,
        "resume_text": req.resume_text,
        "jd_text": req.jd_text,
        "resume_structured": None,
        "jd_structured": None,
        "match_result": None,
        "gap_analysis": "",
        "suggestions": [],
        "interview_questions": [],
        "error": None,
    }

    try:
        result = agent_graph.invoke(initial_state)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent执行失败: {str(e)}")

    if result.get("error"):
        raise HTTPException(status_code=500, detail=result["error"])

    match = result.get("match_result")
    if not match:
        raise HTTPException(status_code=500, detail="匹配结果未生成")

    return {
        "match_score": match.score,
        "summary": match.summary,
        "gap_analysis": result.get("gap_analysis", ""),
        "suggestions": result.get("suggestions", []),
        "interview_questions": result.get("interview_questions", []),
        "hard_met": [{"skill": m.skill, "evidence": m.evidence} for m in match.hard_met],
        "hard_missing": match.hard_missing,
        "nice_met": [{"skill": m.skill, "evidence": m.evidence} for m in match.nice_met],
        "nice_missing": match.nice_missing,
    }
