"""简历解析服务：PDF 提取文本 + LLM 结构化。"""

import pdfplumber
from app.models import ResumeParseResult
from app.llm_client import llm_client


SYSTEM_PROMPT = """你是一个专业的简历解析助手。请从给定的简历文本中提取结构化信息。
要求：
1. 只提取文本中明确存在的信息，不要编造
2. 技能列表提取具体的技术名词（如 Java、Spring Boot、MySQL、Redis）
3. 项目经历的技术栈从描述中提取
4. 输出严格的 JSON 格式"""


def extract_text_from_pdf(pdf_path: str) -> str:
    """用 pdfplumber 从 PDF 提取纯文本"""
    text_parts = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
    return "\n".join(text_parts)


def parse_resume_text(text: str) -> ResumeParseResult:
    """用 LLM 把简历文本结构化"""
    user_prompt = f"请解析以下简历文本，输出 JSON：\n\n{text}"
    data = llm_client.chat_json(SYSTEM_PROMPT, user_prompt)
    return ResumeParseResult(**data)


def parse_resume_pdf(pdf_path: str) -> ResumeParseResult:
    """完整流程：PDF → 文本 → 结构化"""
    text = extract_text_from_pdf(pdf_path)
    return parse_resume_text(text)
