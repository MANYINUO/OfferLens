"""漏斗归因接口：从投递数据里找出规律。"""

from fastapi import APIRouter, HTTPException
from app.services.funnel_analysis import run_full_analysis

router = APIRouter(prefix="/api/funnel", tags=["漏斗归因"])


@router.get("/analysis")
def get_analysis(user_id: int):
    """
    获取完整的漏斗归因分析
    返回：各维度统计 + LLM 生成的归因结论 + 行动建议
    """
    try:
        result = run_full_analysis(user_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"归因分析失败: {str(e)}")
