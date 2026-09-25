"""Pydantic 模型：所有 Agent 输出的结构化数据定义。"""

from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field, model_validator


# ============ 简历解析 ============

class EducationItem(BaseModel):
    # school/major/degree 全部给默认值：LLM 抽取教育经历时经常漏掉 degree
    # （简历里只写了专业和起止时间），一旦是必填，Pydantic 会抛 ValidationError
    # 把整条简历解析链路打断，进而让 Agent 的 match 节点报「简历未解析完成」。
    school: str = Field(default="", description="学校名称")
    major: str = Field(default="", description="专业")
    degree: str = Field(default="", description="学历，如本科/硕士")
    period: str = Field(default="", description="就读时间段")


class ExperienceItem(BaseModel):
    company: str = Field(description="公司名称")
    position: str = Field(description="职位")
    period: str = Field(default="", description="工作时间段")
    description: str = Field(default="", description="工作内容描述")


class ProjectItem(BaseModel):
    name: str = Field(description="项目名称")
    role: str = Field(default="", description="担任角色")
    description: str = Field(default="", description="项目描述")
    tech_stack: List[str] = Field(default_factory=list, description="技术栈")


class ResumeParseResult(BaseModel):
    """简历结构化解析结果"""
    name: str = Field(default="", description="姓名")
    phone: str = Field(default="", description="电话")
    email: str = Field(default="", description="邮箱")
    education: List[EducationItem] = Field(default_factory=list)
    experience: List[ExperienceItem] = Field(default_factory=list)
    projects: List[ProjectItem] = Field(default_factory=list)
    skills: List[str] = Field(default_factory=list, description="技能列表")
    summary: str = Field(default="", description="个人简介")


# ============ JD 结构化 ============

class JDParseResult(BaseModel):
    """职位描述结构化结果"""
    company: str = Field(default="", description="公司名称")
    position: str = Field(default="", description="职位名称")
    hard_requirements: List[str] = Field(default_factory=list, description="硬性要求（必须满足）")
    nice_to_have: List[str] = Field(default_factory=list, description="加分项")
    implicit_requirements: List[str] = Field(default_factory=list, description="隐性要求（如'抗压能力强'暗示加班）")
    job_type: str = Field(default="", description="岗位类型，如Java后端/前端/AI应用")
    salary_range: str = Field(default="", description="薪资范围")


# ============ 匹配度评分 ============

class MatchedSkill(BaseModel):
    """已满足的一条要求。

    LLM 实际输出的键名并不稳定：提示词里写的是 skill，但 DeepSeek 经常
    返回 requirement（甚至 name / item）。早期版本用必填字段，直接抛
    ValidationError 打断整条链路；改成默认值后错误变成「静默空字符串」——
    前端拿到的 hard_met 全是 {"skill": "", "evidence": "..."}，看似成功
    实则没有内容。这里用 alias + 兜底解析，把常见写法都归一化到 skill。
    """

    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    skill: str = Field(default="", description="技能/要求名称")
    evidence: str = Field(default="", description="简历中的证据原文片段")

    @model_validator(mode="before")
    @classmethod
    def _normalize_keys(cls, data):
        """把 requirement / name / item / 纯字符串 统一成 skill。"""
        if isinstance(data, str):
            return {"skill": data, "evidence": ""}
        if isinstance(data, dict):
            data = dict(data)
            if not data.get("skill"):
                for key in ("requirement", "name", "item", "title", "key"):
                    value = data.get(key)
                    if isinstance(value, str) and value.strip():
                        data["skill"] = value.strip()
                        break
            if data.get("evidence") is None:
                data["evidence"] = ""
        return data


class MatchResult(BaseModel):
    """简历与 JD 匹配度分析结果"""
    score: int = Field(description="匹配度分数 0-100")
    hard_met: List[MatchedSkill] = Field(default_factory=list, description="已满足的硬性要求")
    hard_missing: List[str] = Field(default_factory=list, description="缺失的硬性要求")
    nice_met: List[MatchedSkill] = Field(default_factory=list, description="已满足的加分项")
    nice_missing: List[str] = Field(default_factory=list, description="未满足的加分项")
    summary: str = Field(default="", description="总体评价")
    suggestions: List[str] = Field(default_factory=list, description="改进建议")
