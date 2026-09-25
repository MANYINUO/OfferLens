"""OfferLens AI 服务入口。

本地启动：
    cd offerlens-python
    .venv\\Scripts\\python.exe app\\main.py

启动后：
    服务地址   http://127.0.0.1:8000
    健康检查   GET  /api/health
    接口文档   http://127.0.0.1:8000/docs
"""

import sys
from pathlib import Path

from fastapi import FastAPI

# 直接运行本文件时 sys.path[0] 是 app 目录，包内绝对导入（from app.xxx）会失败，
# 需把项目根目录加入搜索路径。
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.routers import resume, jd, match, tools, agent, funnel

app = FastAPI(
    title="OfferLens Agent",
    version="0.4.0",
    description="简历解析、JD 结构化、匹配评分、漏斗归因与 LangGraph 分析工作流。",
)

# 各 router 自带 /api/xxx 前缀，这里按功能顺序注册
app.include_router(resume.router)
app.include_router(jd.router)
app.include_router(match.router)
app.include_router(tools.router)
app.include_router(agent.router)
app.include_router(funnel.router)


@app.get("/api/health", tags=["运维"])
def health():
    """健康检查：用于 Java 侧和运维探活。"""
    return {"status": "ok", "service": "offerlens-agent"}


if __name__ == "__main__":
    import os

    import uvicorn

    # 切到项目根目录，让所有相对路径都按项目根解析。
    # 关键原因：config.py 用的是裸 load_dotenv()，它只从「当前工作目录」找 .env。
    # 不切的话服务照样能启动、健康检查也正常，但 .env 读不到，
    # DEEPSEEK_API_KEY 会是空字符串，AI 分析时才报错——比启动失败更难排查。
    os.chdir(ROOT)

    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
