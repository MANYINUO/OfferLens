"""LLM 客户端封装：基于 LangChain ChatOpenAI 调用 DeepSeek（OpenAI 兼容接口）。"""

import json
import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from app.config import settings


class LLMClient:
    def __init__(self):
        self._llm = None
        self.model = settings.LLM_MODEL
        self.api_key = settings.DEEPSEEK_API_KEY or "sk-placeholder"
        self.base_url = settings.DEEPSEEK_BASE_URL

    @property
    def llm(self) -> ChatOpenAI:
        """延迟初始化：第一次调用时才创建 ChatOpenAI 实例"""
        if self._llm is None:
            self._llm = ChatOpenAI(
                model=self.model,
                api_key=self.api_key,
                base_url=self.base_url,
                temperature=0.3,
            )
        return self._llm

    def chat(self, system_prompt: str, user_prompt: str, temperature: float = 0.3) -> str:
        """普通对话，返回文本"""
        llm = self.llm if temperature == 0.3 else self.llm.bind(temperature=temperature)
        response = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ])
        return response.content

    def chat_json(self, system_prompt: str, user_prompt: str, temperature: float = 0.1) -> dict:
        """结构化输出：要求 LLM 返回 JSON，自动解析"""
        llm = self.llm.bind(
            temperature=temperature,
            response_format={"type": "json_object"},
        )
        response = llm.invoke([
            SystemMessage(content=system_prompt + "\n\n必须只输出 JSON，不要任何解释文字。"),
            HumanMessage(content=user_prompt),
        ])
        content = response.content
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            cleaned = content.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
            return json.loads(cleaned)


llm_client = LLMClient()
