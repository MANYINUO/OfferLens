"""LangGraph 工作流定义：5 节点线性流程。"""

from langgraph.graph import StateGraph, END

from app.agent.state import AgentState
from app.agent.nodes import (
    parse_resume_node,
    parse_jd_node,
    match_node,
    gap_analysis_node,
    suggestion_node,
    interview_questions_node,
)


def build_graph():
    """构建并编译工作流"""
    workflow = StateGraph(AgentState)

    # 添加节点
    workflow.add_node("parse_resume", parse_resume_node)
    workflow.add_node("parse_jd", parse_jd_node)
    workflow.add_node("match", match_node)
    workflow.add_node("gap_analysis", gap_analysis_node)
    workflow.add_node("suggestion", suggestion_node)
    workflow.add_node("interview_questions", interview_questions_node)

    # 设置入口
    workflow.set_entry_point("parse_resume")

    # 线性连接：简历解析 → JD解析 → 匹配 → 缺口分析 → 建议 → 面试题 → 结束
    workflow.add_edge("parse_resume", "parse_jd")
    workflow.add_edge("parse_jd", "match")
    workflow.add_edge("match", "gap_analysis")
    workflow.add_edge("gap_analysis", "suggestion")
    workflow.add_edge("suggestion", "interview_questions")
    workflow.add_edge("interview_questions", END)

    # 编译
    return workflow.compile()


# 全局单例
agent_graph = build_graph()
