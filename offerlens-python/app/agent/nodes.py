"""LangGraph 5 节点定义：每个节点接收状态，返回状态的更新。"""

from typing import Dict, Any

from app.agent.state import AgentState
from app.services.resume_parser import parse_resume_text
from app.services.jd_parser import parse_jd
from app.services.matcher import match_resume_jd
from app.llm_client import llm_client


def parse_resume_node(state: AgentState) -> Dict[str, Any]:
    """节点1：简历结构化解析"""
    try:
        resume = parse_resume_text(state["resume_text"])
        return {"resume_structured": resume}
    except Exception as e:
        return {"error": f"简历解析失败: {str(e)}"}


def parse_jd_node(state: AgentState) -> Dict[str, Any]:
    """节点2：JD 结构化解析"""
    try:
        jd = parse_jd(state["jd_text"])
        return {"jd_structured": jd}
    except Exception as e:
        return {"error": f"JD解析失败: {str(e)}"}


def match_node(state: AgentState) -> Dict[str, Any]:
    """节点3：匹配度评分"""
    try:
        resume = state.get("resume_structured")
        jd = state.get("jd_structured")
        if not resume or not jd:
            return {"error": "简历或JD未解析完成"}
        match = match_resume_jd(resume, jd)
        return {"match_result": match}
    except Exception as e:
        return {"error": f"匹配度评分失败: {str(e)}"}


def gap_analysis_node(state: AgentState) -> Dict[str, Any]:
    """节点4：缺口分析（基于匹配结果，LLM 生成深度分析）"""
    try:
        match = state.get("match_result")
        if not match:
            return {"error": "匹配结果不存在"}

        prompt = f"""请基于以下匹配度分析，生成一段深度缺口分析（200字以内）：
- 匹配分数：{match.score}/100
- 已满足硬性要求：{[m.skill for m in match.hard_met]}
- 缺失硬性要求：{match.hard_missing}
- 已满足加分项：{[m.skill for m in match.nice_met]}
- 未满足加分项：{match.nice_missing}

请分析：
1. 最关键的缺口是什么
2. 这些缺口对求职成功率的影响
3. 短期能补什么、短期补不了什么
"""
        analysis = llm_client.chat(
            "你是一个专业的求职顾问，擅长分析简历与岗位的差距。",
            prompt,
            temperature=0.4,
        )
        return {"gap_analysis": analysis}
    except Exception as e:
        return {"error": f"缺口分析失败: {str(e)}"}


def suggestion_node(state: AgentState) -> Dict[str, Any]:
    """节点5：定制建议（基于缺口分析，生成具体行动建议）"""
    try:
        gap = state.get("gap_analysis", "")
        match = state.get("match_result")
        if not match:
            return {"error": "匹配结果不存在"}

        prompt = f"""基于以下缺口分析，给出3-5条具体的、可执行的改进建议：

缺口分析：
{gap}

当前匹配分数：{match.score}/100
缺失硬性要求：{match.hard_missing}
总体评价：{match.summary}

要求：
1. 每条建议要具体、可执行（不要说"提升能力"这种空话）
2. 区分"简历优化"和"技能补充"两类
3. 优先建议能在1-2周内见效的动作
4. 输出 JSON 格式：{{"suggestions": ["建议1", "建议2", ...]}}
"""
        data = llm_client.chat_json(
            "你是一个资深求职顾问，擅长给出具体可执行的建议。",
            prompt,
            temperature=0.5,
        )
        suggestions = data.get("suggestions", [])
        return {"suggestions": suggestions}
    except Exception as e:
        return {"error": f"建议生成失败: {str(e)}"}


def interview_questions_node(state: AgentState) -> Dict[str, Any]:
    """节点6：面试题生成（基于JD和简历，生成三层深度面试题）"""
    try:
        jd = state.get("jd_structured")
        resume = state.get("resume_structured")
        if not jd or not resume:
            return {"error": "JD或简历未解析完成"}

        # 提取简历中的项目经历
        projects_text = ""
        if resume.projects:
            for p in resume.projects:
                projects_text += f"- {p.name}（{p.role}）：{p.description}\n"

        prompt = f"""基于以下职位要求和候选人简历，生成8道面试题，分三层深度：

职位：{jd.company} - {jd.position}
硬性要求：{jd.hard_requirements}
加分项：{jd.nice_to_have}

候选人项目经历：
{projects_text}

候选人技能：{resume.skills}

要求：
1. 第一层（基础题，3道）：考察基础知识是否扎实
2. 第二层（项目题，3道）：针对候选人项目经历深挖
3. 第三层（场景题，2道）：考察解决问题的思路和深度
4. 每道题后面附上"考察点"说明
5. 输出 JSON 格式：{{"questions": ["题1（考察点：xxx）", "题2（考察点：xxx）", ...]}}
"""
        data = llm_client.chat_json(
            "你是一个资深面试官，擅长针对岗位和候选人背景出有深度的面试题。",
            prompt,
            temperature=0.6,
        )
        questions = data.get("questions", [])
        return {"interview_questions": questions}
    except Exception as e:
        return {"error": f"面试题生成失败: {str(e)}"}
