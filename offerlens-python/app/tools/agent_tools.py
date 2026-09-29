"""Agent 工具层：基于 LangChain @tool 装饰器，每个工具无状态、单一职责，全部通过 JavaClient 调用后端。"""

from typing import List, Dict, Any, Optional
from langchain_core.tools import tool
from app.clients.java_client import java_client


@tool
def search_jobs(user_id: int, keyword: str = None) -> List[Dict[str, Any]]:
    """
    查询用户收藏的职位列表，可选关键词过滤（在公司名或职位名中搜索）。

    Args:
        user_id: 用户 ID
        keyword: 可选的搜索关键词
    """
    jobs = java_client.list_jobs(user_id)
    if keyword:
        keyword_lower = keyword.lower()
        jobs = [
            j for j in jobs
            if keyword_lower in (j.get("company", "") + j.get("position", "")).lower()
        ]
    return jobs


@tool
def get_job_detail(job_id: int) -> Optional[Dict[str, Any]]:
    """
    查询单个职位详情。

    Args:
        job_id: 职位 ID
    """
    return java_client.get_job(job_id)


@tool
def list_resume_versions(user_id: int) -> List[Dict[str, Any]]:
    """
    查询用户的所有简历版本。

    Args:
        user_id: 用户 ID
    """
    return java_client.list_resumes(user_id)


@tool
def get_resume_detail(resume_id: int) -> Optional[Dict[str, Any]]:
    """
    查询单份简历内容。

    Args:
        resume_id: 简历 ID
    """
    return java_client.get_resume(resume_id)


@tool
def list_applications(user_id: int, status: str = None) -> List[Dict[str, Any]]:
    """
    查询投递记录，可按状态筛选（applied/viewed/written/first/second/hr/offer/rejected/no_response/abandoned）。

    Args:
        user_id: 用户 ID
        status: 可选的投递状态筛选
    """
    return java_client.list_applications(user_id, status=status)


@tool
def create_application_record(user_id: int, company: str, position: str,
                              resume_id: int = None, channel: str = None,
                              job_type: str = None, match_score: int = None,
                              notes: str = None) -> Dict[str, Any]:
    """
    创建一条投递记录（写操作）。用户说"今天投了XX公司"时自动调用。

    Args:
        user_id: 用户 ID
        company: 公司名称
        position: 职位名称
        resume_id: 使用的简历版本 ID
        channel: 投递渠道（BOSS直聘/官网/内推等）
        job_type: 岗位类型
        match_score: 匹配度评分
        notes: 备注
    """
    return java_client.create_application(
        user_id=user_id,
        company=company,
        position=position,
        resume_id=resume_id,
        channel=channel,
        job_type=job_type,
        match_score=match_score,
        notes=notes,
    )


@tool
def advance_application_status(app_id: int) -> Dict[str, Any]:
    """
    推进投递状态（前进一步，写操作）。

    Args:
        app_id: 投递记录 ID
    """
    return java_client.advance_application(app_id)


@tool
def get_funnel_analysis(user_id: int) -> Dict[str, Any]:
    """
    查询投递漏斗统计数据。

    Args:
        user_id: 用户 ID
    """
    return java_client.get_funnel_stats(user_id)


# LangChain 工具列表（供 Agent 绑定使用）
AGENT_TOOLS = [
    search_jobs,
    get_job_detail,
    list_resume_versions,
    get_resume_detail,
    list_applications,
    create_application_record,
    advance_application_status,
    get_funnel_analysis,
]

# 兼容旧代码：名称 → 函数的注册表
TOOL_REGISTRY = {
    "search_jobs": search_jobs,
    "get_job_detail": get_job_detail,
    "list_resume_versions": list_resume_versions,
    "get_resume_detail": get_resume_detail,
    "list_applications": list_applications,
    "create_application_record": create_application_record,
    "advance_application_status": advance_application_status,
    "get_funnel_analysis": get_funnel_analysis,
}
