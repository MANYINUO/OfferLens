"""简历解析路由：支持文本解析和 PDF 文件上传解析。"""

import os
import tempfile
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from app.models import ResumeParseResult
from app.services.resume_parser import parse_resume_text, parse_resume_pdf

router = APIRouter(prefix="/api/resume", tags=["简历解析"])


class ResumeTextRequest(BaseModel):
    text: str


@router.post("/parse-text", response_model=ResumeParseResult)
def parse_text(req: ResumeTextRequest):
    """从纯文本解析简历结构"""
    return parse_resume_text(req.text)


@router.post("/parse-pdf", response_model=ResumeParseResult)
async def parse_pdf(file: UploadFile = File(...)):
    """从 PDF 文件解析简历结构"""
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="只支持 PDF 文件")

    # 保存到临时文件
    suffix = os.path.splitext(file.filename)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        result = parse_resume_pdf(tmp_path)
        return result
    finally:
        os.unlink(tmp_path)
