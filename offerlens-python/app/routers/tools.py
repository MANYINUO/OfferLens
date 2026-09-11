"""工具调用测试路由：列出可用工具、手动调用指定工具（验证跨服务对接）。"""

from typing import Any, Dict
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.tools.agent_tools import TOOL_REGISTRY

router = APIRouter(prefix="/api/tools", tags=["工具测试"])


class ToolCallRequest(BaseModel):
    tool_name: str
    args: Dict[str, Any] = {}


@router.get("/list")
def list_tools():
    """列出所有可用工具"""
    return {
        "tools": [
            {
                "name": name,
                "description": func.__doc__.strip().split("\n")[0] if func.__doc__ else "",
            }
            for name, func in TOOL_REGISTRY.items()
        ]
    }


@router.post("/call")
def call_tool(req: ToolCallRequest):
    """手动调用指定工具（测试用）"""
    if req.tool_name not in TOOL_REGISTRY:
        raise HTTPException(status_code=404, detail=f"工具不存在: {req.tool_name}")

    func = TOOL_REGISTRY[req.tool_name]
    try:
        result = func(**req.args)
        return {"tool": req.tool_name, "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"工具执行失败: {str(e)}")
