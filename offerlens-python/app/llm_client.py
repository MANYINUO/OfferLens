"""LLM 客户端封装：统一调用 DeepSeek（OpenAI 兼容接口）。"""

import json
from openai import OpenAI
from app.config import settings


class LLMClient:
    def __init__(self):
        self.client = OpenAI(
            api_key=settings.DEEPSEEK_API_KEY,
            base_url=settings.DEEPSEEK_BASE_URL,
        )
        self.model = settings.LLM_MODEL

    def chat(self, system_prompt: str, user_prompt: str, temperature: float = 0.3) -> str:
        """普通对话，返回文本"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
        )
        return response.choices[0].message.content

    def chat_json(self, system_prompt: str, user_prompt: str, temperature: float = 0.1) -> dict:
        """结构化输出：要求 LLM 返回 JSON，自动解析"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt + "\n\n必须只输出 JSON，不要任何解释文字。"},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            # 兜底：去掉可能的 markdown 代码块标记
            cleaned = content.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
            return json.loads(cleaned)


llm_client = LLMClient()
