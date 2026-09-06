"""Pydantic 模型：所有 Agent 输出的结构化数据定义。"""

from typing import List, Optional
from pydantic import BaseModel, Field


# ============ 简历解析 ============

class EducationItem(BaseModel):
    school: str = Field(description="学校名称")
    major: str = Field(description="专业")
    degree: str = Field(description="学历，如本科/硕士")
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
    skill: str = Field(description="技能/要求名称")
    evidence: str = Field(description="简历中的证据原文片段")


class MatchResult(BaseModel):
    """简历与 JD 匹配度分析结果"""
    score: int = Field(description="匹配度分数 0-100")
    hard_met: List[MatchedSkill] = Field(default_factory=list, description="已满足的硬性要求")
    hard_missing: List[str] = Field(default_factory=list, description="缺失的硬性要求")
    nice_met: List[MatchedSkill] = Field(default_factory=list, description="已满足的加分项")
    nice_missing: List[str] = Field(default_factory=list, description="未满足的加分项")
    summary: str = Field(default="", description="总体评价")
    suggestions: List[str] = Field(default_factory=list, description="改进建议")
