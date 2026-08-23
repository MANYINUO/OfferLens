"""OfferLens AI 服务入口。

启动方式（在 offerlens-python 目录下）：
    .venv\\Scripts\\activate
    uvicorn app.main:app --reload --port 8000

Step 0.3 只提供健康检查接口，用于验证服务能跑起来。
后续 Step 2.x 会在这里挂载匹配、PDF 解析、面试题生成等接口。
"""

from fastapi import FastAPI

app = FastAPI(title="OfferLens Agent")


@app.get("/api/health")
def health():
    """健康检查：用于 Java 侧和运维探活。"""
    return {"status": "ok", "service": "offerlens-agent"}
