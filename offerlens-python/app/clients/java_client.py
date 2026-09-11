"""Java 后端 REST 客户端封装：Python Agent 通过 HTTP 调用 Java，不直连数据库。"""

import httpx
from typing import Optional, List, Dict, Any
from app.config import settings


class JavaClient:
    def __init__(self, base_url: str = None):
        self.base_url = base_url or settings.JAVA_BACKEND_URL
        self.client = httpx.Client(timeout=10.0)

    def _get(self, path: str, params: dict = None) -> Dict[str, Any]:
        resp = self.client.get(f"{self.base_url}{path}", params=params)
        resp.raise_for_status()
        return resp.json()

    def _post(self, path: str, json: dict = None) -> Dict[str, Any]:
        resp = self.client.post(f"{self.base_url}{path}", json=json)
        resp.raise_for_status()
        return resp.json()

    def _put(self, path: str, json: dict = None) -> Dict[str, Any]:
        resp = self.client.put(f"{self.base_url}{path}", json=json)
        resp.raise_for_status()
        return resp.json()

    # ============ 职位相关 ============

    def list_jobs(self, user_id: int) -> List[Dict[str, Any]]:
        """查询用户收藏的所有职位"""
        result = self._get("/api/jobs", params={"userId": user_id})
        return result.get("data", [])

    def get_job(self, job_id: int) -> Optional[Dict[str, Any]]:
        """查询单个职位详情"""
        result = self._get(f"/api/jobs/{job_id}")
        return result.get("data")

    # ============ 简历相关 ============

    def list_resumes(self, user_id: int) -> List[Dict[str, Any]]:
        """查询用户的所有简历版本"""
        result = self._get("/api/resumes", params={"userId": user_id})
        return result.get("data", [])

    def get_resume(self, resume_id: int) -> Optional[Dict[str, Any]]:
        """查询单份简历"""
        result = self._get(f"/api/resumes/{resume_id}")
        return result.get("data")

    # ============ 投递相关 ============

    def list_applications(self, user_id: int, status: str = None) -> List[Dict[str, Any]]:
        """查询投递记录，可按状态筛选"""
        params = {"userId": user_id}
        if status:
            params["status"] = status
        result = self._get("/api/applications", params=params)
        return result.get("data", [])

    def get_application(self, app_id: int) -> Optional[Dict[str, Any]]:
        """查询单条投递记录"""
        result = self._get(f"/api/applications/{app_id}")
        return result.get("data")

    def create_application(self, user_id: int, company: str, position: str,
                           resume_id: int = None, jd_id: int = None,
                           channel: str = None, job_type: str = None,
                           match_score: int = None, notes: str = None) -> Dict[str, Any]:
        """创建一条投递记录（写操作）"""
        payload = {
            "userId": user_id,
            "company": company,
            "position": position,
        }
        if resume_id:
            payload["resumeId"] = resume_id
        if jd_id:
            payload["jdId"] = jd_id
        if channel:
            payload["channel"] = channel
        if job_type:
            payload["jobType"] = job_type
        if match_score is not None:
            payload["matchScore"] = match_score
        if notes:
            payload["notes"] = notes
        result = self._post("/api/applications", json=payload)
        return result.get("data")

    def advance_application(self, app_id: int) -> Dict[str, Any]:
        """推进投递状态（前进一步，写操作）"""
        result = self._post(f"/api/applications/{app_id}/advance")
        return result.get("data")

    def transition_application(self, app_id: int, target_status: str) -> Dict[str, Any]:
        """流转到指定状态（含终态，写操作）"""
        result = self._post(f"/api/applications/{app_id}/transition", json={"status": target_status})
        return result.get("data")

    def update_application_notes(self, app_id: int, notes: str) -> bool:
        """更新投递备注（写操作）"""
        result = self._put(f"/api/applications/{app_id}/notes", json={"notes": notes})
        return result.get("code") == 200

    # ============ 统计相关 ============

    def get_funnel_stats(self, user_id: int) -> Dict[str, Any]:
        """查询投递漏斗统计"""
        result = self._get("/api/stats/funnel", params={"userId": user_id})
        return result.get("data")


java_client = JavaClient()
