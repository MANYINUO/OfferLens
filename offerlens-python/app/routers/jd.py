"""JD 结构化路由：把职位描述文本拆解成硬性要求/加分项/隐性要求。"""

from fastapi import APIRouter
from pydantic import BaseModel
from app.models import JDParseResult
from app.services.jd_parser import parse_jd

router = APIRouter(prefix="/api/jd", tags=["JD结构化"])


class JDParseRequest(BaseModel):
    text: str


@router.post("/parse", response_model=JDParseResult)
def parse(req: JDParseRequest):
    """解析职位描述文本"""
    return parse_jd(req.text)
