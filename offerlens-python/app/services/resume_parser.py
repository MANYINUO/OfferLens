"""简历解析服务：PDF 提取文本 + LLM 结构化。"""

import pdfplumber
from pdfminer.pdfdocument import PDFEncryptionError, PDFPasswordIncorrect
from pdfminer.pdfparser import PDFSyntaxError
from app.constants import MAX_PDF_PAGES
from app.models import ResumeParseResult
from app.llm_client import llm_client


MIN_WARN_CHARS = 300


class EmptyTextError(ValueError):
    """输入文本为空——送进 LLM 只会得到编造内容。"""


class EmptyResumeTextError(EmptyTextError):
    """PDF 里没有可用的文字层（扫描件 / 图片导出）。"""


class EncryptedPdfError(ValueError):
    """PDF 有密码保护。"""


class BrokenPdfError(ValueError):
    """PDF 损坏或不是合法 PDF。"""


class TooManyPagesError(ValueError):
    """PDF 页数过多，解析会占用过多时间和内存。"""


SYSTEM_PROMPT = """你是一个专业的简历解析助手。请从给定的简历文本中提取结构化信息。
要求：
1. 只提取文本中明确存在的信息，不要编造
2. 技能列表提取具体的技术名词（如 Java、Spring Boot、MySQL、Redis）
3. 项目经历的技术栈从描述中提取
4. 输出严格的 JSON 格式"""


def extract_text_from_pdf(pdf_path: str) -> str:
    """用 pdfplumber 从 PDF 提取纯文本"""
    text_parts = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            page_count = len(pdf.pages)
            if page_count > MAX_PDF_PAGES:
                raise TooManyPagesError(
                    f"这个 PDF 有 {page_count} 页，超过 {MAX_PDF_PAGES} 页上限。"
                    "请只保留简历相关页面后再上传。"
                )
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
    except (PDFPasswordIncorrect, PDFEncryptionError) as e:
        raise EncryptedPdfError("这个 PDF 有密码保护，请先解除密码再上传。") from e
    except (PDFSyntaxError, OSError) as e:
        raise BrokenPdfError("这个文件无法作为 PDF 解析，可能已损坏。") from e
    return "\n".join(text_parts)


def extract_resume_text(pdf_path: str) -> str:
    """提取简历 PDF 文字；只拦截完全没有文字的文档。"""
    text = extract_text_from_pdf(pdf_path).strip()
    if not text:
        raise EmptyResumeTextError(
            "这个 PDF 没有提取到任何文字，通常是扫描件或图片导出。"
            "请换一份可以复制文字的 PDF，或直接把简历内容粘贴进去。"
        )
    return text


def parse_resume_text(text: str) -> ResumeParseResult:
    """用 LLM 把简历文本结构化"""
    if not text or not text.strip():
        raise EmptyTextError("简历文本为空")
    user_prompt = f"请解析以下简历文本，输出 JSON：\n\n{text}"
    data = llm_client.chat_json(SYSTEM_PROMPT, user_prompt)
    return ResumeParseResult(**data)


def parse_resume_pdf(pdf_path: str) -> ResumeParseResult:
    """完整流程：PDF → 文本 → 结构化"""
    text = extract_resume_text(pdf_path)
    return parse_resume_text(text)
