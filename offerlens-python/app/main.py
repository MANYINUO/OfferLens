"""OfferLens AI 服务入口。

启动方式（在 offerlens-python 目录下）：
    .venv\\Scripts\\activate
    uvicorn app.main:app --reload --port 8000
"""

from fastapi import FastAPI
from app.routers import resume, jd, match, tools, agent

app = FastAPI(title="OfferLens Agent", version="0.3.0")

# 注册路由
app.include_router(resume.router)
app.include_router(jd.router)
app.include_router(match.router)
app.include_router(tools.router)
app.include_router(agent.router)


@app.get("/api/health")
def health():
    """健康检查：用于 Java 侧和运维探活。"""
    return {"status": "ok", "service": "offerlens-agent"}
