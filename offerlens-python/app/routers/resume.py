"""简历解析路由：支持文本解析、PDF 纯文本提取和 PDF 结构化解析。"""

import os
import tempfile
from typing import Optional

from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel, Field, field_validator
from app.constants import MAX_TEXT_CHARS, MAX_UPLOAD_BYTES
from app.models import ResumeParseResult
from app.services.resume_parser import (
    parse_resume_text,
    parse_resume_pdf,
    extract_resume_text,
    EmptyTextError,
    EmptyResumeTextError,
    EncryptedPdfError,
    BrokenPdfError,
    TooManyPagesError,
    MIN_WARN_CHARS,
)

router = APIRouter(prefix="/api/resume", tags=["简历解析"])

CHUNK_SIZE = 1024 * 1024


class ResumeTextRequest(BaseModel):
    text: str = Field(min_length=1, max_length=MAX_TEXT_CHARS)

    @field_validator("text")
    @classmethod
    def not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("简历文本不能为空")
        return value


class ExtractTextResponse(BaseModel):
    text: str
    chars: int
    filename: str
    warning: Optional[str] = None


async def _save_upload(file: UploadFile) -> str:
    """边读边计数后写入临时文件，避免一次性将整个文件载入内存。"""
    if file.size is not None and file.size > MAX_UPLOAD_BYTES:
        raise HTTPException(413, "文件超过 10MB，请压缩后再上传")

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    tmp_path = tmp.name
    total = 0
    try:
        while True:
            chunk = await file.read(CHUNK_SIZE)
            if not chunk:
                break
            total += len(chunk)
            if total > MAX_UPLOAD_BYTES:
                raise HTTPException(413, "文件超过 10MB，请压缩后再上传")
            tmp.write(chunk)
        tmp.close()
    except Exception:
        _safe_unlink(tmp_path, tmp)
        raise

    if total == 0:
        _safe_unlink(tmp_path, tmp)
        raise HTTPException(400, "文件是空的")
    return tmp_path


def _safe_unlink(tmp_path: str, handle=None) -> None:
    """删除临时文件，失败不抛——否则会把 422 覆盖成 500。"""
    if handle is not None:
        try:
            handle.close()
        except Exception:
            pass
    try:
        os.unlink(tmp_path)
    except OSError:
        pass


def _require_pdf(file: UploadFile) -> None:
    if not (file.filename or "").lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="目前只支持 PDF。图片（截图、扫描件）需要 OCR，"
                   "请先转成带文字层的 PDF，或直接粘贴简历文本。",
        )


def _pdf_error(error: Exception) -> HTTPException:
    if isinstance(error, (EncryptedPdfError, BrokenPdfError,
                          EmptyResumeTextError, TooManyPagesError)):
        return HTTPException(status_code=422, detail=str(error))
    return HTTPException(status_code=422, detail="PDF 解析失败")


@router.post("/parse-text", response_model=ResumeParseResult)
def parse_text(req: ResumeTextRequest):
    """从纯文本解析简历结构"""
    try:
        return parse_resume_text(req.text)
    except EmptyTextError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error


@router.post("/extract-text", response_model=ExtractTextResponse)
async def extract_text(file: UploadFile = File(...)):
    """只提取 PDF 文字，不做 LLM 结构化。"""
    _require_pdf(file)
    tmp_path = await _save_upload(file)
    try:
        text = extract_resume_text(tmp_path)
    except (EncryptedPdfError, BrokenPdfError, EmptyResumeTextError,
            TooManyPagesError) as error:
        raise _pdf_error(error) from error
    finally:
        _safe_unlink(tmp_path)

    chars = len(text)
    if chars > MAX_TEXT_CHARS:
        warning = (
            f"提取到 {chars} 个字符，超过 {MAX_TEXT_CHARS} 字上限，"
            "超出部分不会保存。建议只保留与岗位相关的段落。"
        )
    elif chars < MIN_WARN_CHARS:
        warning = f"只提取到 {chars} 个字符，内容可能不完整，请核对后再保存。"
    else:
        warning = None

    return ExtractTextResponse(
        text=text,
        chars=chars,
        filename=file.filename or "",
        warning=warning,
    )


@router.post("/parse-pdf", response_model=ResumeParseResult)
async def parse_pdf(file: UploadFile = File(...)):
    """从 PDF 解析简历结构（走 LLM，消耗 token）。"""
    _require_pdf(file)
    tmp_path = await _save_upload(file)
    try:
        return parse_resume_pdf(tmp_path)
    except (EncryptedPdfError, BrokenPdfError, EmptyResumeTextError,
            TooManyPagesError) as error:
        raise _pdf_error(error) from error
    finally:
        _safe_unlink(tmp_path)
