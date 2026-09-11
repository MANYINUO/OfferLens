"""Agent 工具层：每个工具函数无状态、单一职责，全部通过 JavaClient 调用后端。"""

from typing import List, Dict, Any, Optional
from app.clients.java_client import java_client


def search_jobs(user_id: int, keyword: str = None) -> List[Dict[str, Any]]:
    """
    工具1：查询用户收藏的职位列表
    可选关键词过滤（在公司名或职位名中搜索）
    """
    jobs = java_client.list_jobs(user_id)
    if keyword:
        keyword_lower = keyword.lower()
        jobs = [
            j for j in jobs
            if keyword_lower in (j.get("company", "") + j.get("position", "")).lower()
        ]
    return jobs


def get_job_detail(job_id: int) -> Optional[Dict[str, Any]]:
    """工具2：查询单个职位详情"""
    return java_client.get_job(job_id)


def list_resume_versions(user_id: int) -> List[Dict[str, Any]]:
    """工具3：查询用户的所有简历版本"""
    return java_client.list_resumes(user_id)


def get_resume_detail(resume_id: int) -> Optional[Dict[str, Any]]:
    """工具4：查询单份简历内容"""
    return java_client.get_resume(resume_id)


def list_applications(user_id: int, status: str = None) -> List[Dict[str, Any]]:
    """
    工具5：查询投递记录
    可按状态筛选（applied/viewed/written/first/second/hr/offer/rejected/no_response/abandoned）
    """
    return java_client.list_applications(user_id, status=status)


def create_application_record(user_id: int, company: str, position: str,
                              resume_id: int = None, channel: str = None,
                              job_type: str = None, match_score: int = None,
                              notes: str = None) -> Dict[str, Any]:
    """
    工具6：创建一条投递记录（写操作）
    这是 Agent 唯一的写操作入口，用户说"今天投了XX公司"时自动调用
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


def advance_application_status(app_id: int) -> Dict[str, Any]:
    """工具7：推进投递状态（前进一步，写操作）"""
    return java_client.advance_application(app_id)


def get_funnel_analysis(user_id: int) -> Dict[str, Any]:
    """工具8：查询投递漏斗统计数据"""
    return java_client.get_funnel_stats(user_id)


# 工具注册表：名称 → 函数，方便 LangGraph 或对话接口统一调度
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
