"""JD 结构化路由：把职位描述文本拆解成硬性要求/加分项/隐性要求。"""

from fastapi import APIRouter
from pydantic import BaseModel, Field, field_validator
from app.constants import MAX_TEXT_CHARS
from app.models import JDParseResult
from app.services.jd_parser import parse_jd

router = APIRouter(prefix="/api/jd", tags=["JD结构化"])


class JDParseRequest(BaseModel):
    text: str = Field(min_length=1, max_length=MAX_TEXT_CHARS)

    @field_validator("text")
    @classmethod
    def not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("职位描述不能为空")
        return value


@router.post("/parse", response_model=JDParseResult)
def parse(req: JDParseRequest):
    """解析职位描述文本"""
    return parse_jd(req.text)
