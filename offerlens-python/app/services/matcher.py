"""匹配度评分服务：对比简历和 JD，给出分数+缺口分析+证据链。"""

from app.models import MatchResult, ResumeParseResult, JDParseResult
from app.llm_client import llm_client


SYSTEM_PROMPT = """你是一个专业的求职匹配分析师。请对比简历和职位描述，给出匹配度分析。
要求：
1. score：0-100 的整数，客观评分，不要虚高
2. hard_met：已满足的硬性要求，每条必须带 evidence（简历原文片段，必须能在简历中找到）
3. hard_missing：缺失的硬性要求
4. nice_met / nice_missing：加分项同理
5. summary：一句话总体评价
6. suggestions：具体的改进建议（2-4条）
7. 关键红线：evidence 必须是简历原文中真实存在的片段，绝对不能编造
8. 输出严格的 JSON 格式"""


def match_resume_jd(resume: ResumeParseResult, jd: JDParseResult) -> MatchResult:
    """对比简历和 JD，给出匹配度分析"""
    resume_text = _resume_to_text(resume)
    jd_text = _jd_to_text(jd)

    user_prompt = f"""请对比以下简历和职位描述，输出匹配度分析 JSON：

=== 简历 ===
{resume_text}

=== 职位描述 ===
{jd_text}
"""
    data = llm_client.chat_json(SYSTEM_PROMPT, user_prompt)
    return MatchResult(**data)


def _resume_to_text(resume: ResumeParseResult) -> str:
    """把结构化简历转成文本，方便 LLM 处理"""
    lines = []
    if resume.name:
        lines.append(f"姓名：{resume.name}")
    if resume.phone:
        lines.append(f"电话：{resume.phone}")
    if resume.email:
        lines.append(f"邮箱：{resume.email}")
    if resume.summary:
        lines.append(f"简介：{resume.summary}")
    if resume.skills:
        lines.append(f"技能：{', '.join(resume.skills)}")
    if resume.education:
        lines.append("\n教育经历：")
        for edu in resume.education:
            lines.append(f"- {edu.school} {edu.major} {edu.degree} {edu.period}")
    if resume.experience:
        lines.append("\n工作经历：")
        for exp in resume.experience:
            lines.append(f"- {exp.company} {exp.position} {exp.period}")
            if exp.description:
                lines.append(f"  {exp.description}")
    if resume.projects:
        lines.append("\n项目经历：")
        for proj in resume.projects:
            lines.append(f"- {proj.name}（{proj.role}）")
            if proj.tech_stack:
                lines.append(f"  技术栈：{', '.join(proj.tech_stack)}")
            if proj.description:
                lines.append(f"  {proj.description}")
    return "\n".join(lines)


def _jd_to_text(jd: JDParseResult) -> str:
    """把结构化 JD 转成文本"""
    lines = []
    if jd.company:
        lines.append(f"公司：{jd.company}")
    if jd.position:
        lines.append(f"职位：{jd.position}")
    if jd.job_type:
        lines.append(f"岗位类型：{jd.job_type}")
    if jd.salary_range:
        lines.append(f"薪资：{jd.salary_range}")
    if jd.hard_requirements:
        lines.append("\n硬性要求：")
        for req in jd.hard_requirements:
            lines.append(f"- {req}")
    if jd.nice_to_have:
        lines.append("\n加分项：")
        for req in jd.nice_to_have:
            lines.append(f"- {req}")
    if jd.implicit_requirements:
        lines.append("\n隐性要求：")
        for req in jd.implicit_requirements:
            lines.append(f"- {req}")
    return "\n".join(lines)
