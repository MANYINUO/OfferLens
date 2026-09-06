"""配置管理：从环境变量读取，.env 文件自动加载。"""

import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # DeepSeek LLM 配置
    DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "")
    DEEPSEEK_BASE_URL: str = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "deepseek-chat")

    # Java 后端地址（Agent 通过 REST 调用 Java，不直连数据库）
    JAVA_BACKEND_URL: str = os.getenv("JAVA_BACKEND_URL", "http://localhost:8080")

    # 服务配置
    PORT: int = int(os.getenv("PORT", "8000"))


settings = Settings()
