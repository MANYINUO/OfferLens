"""漏斗归因服务：从投递数据里找出规律，这是项目的灵魂。

归因维度：
1. 按岗位类型：哪类岗回复率最高
2. 按渠道：哪个渠道效果好
3. 按简历版本：哪版简历转化率高
4. 按时间段：找出集体沉默的批次
5. 按匹配度：高匹配是否真的回复率高
"""

from collections import defaultdict
from typing import List, Dict, Any
from app.clients.java_client import java_client
from app.llm_client import llm_client


# 回复的定义：状态进入 viewed 及以上（即 HR 看了简历）
REPLIED_STATES = {"viewed", "written", "first", "second", "hr", "offer"}
# 终态
TERMINAL_STATES = {"offer", "rejected", "no_response", "abandoned"}


def _is_replied(app: Dict[str, Any]) -> bool:
    """判断这条投递是否收到了回复（HR 查看了简历）"""
    return app.get("status") in REPLIED_STATES


def _is_offer(app: Dict[str, Any]) -> bool:
    """判断是否拿到了 offer"""
    return app.get("status") == "offer"


def analyze_by_job_type(applications: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """按岗位类型统计：投递数、回复数、回复率、offer数"""
    groups = defaultdict(list)
    for app in applications:
        job_type = app.get("job_type") or "未分类"
        groups[job_type].append(app)

    result = []
    for job_type, apps in groups.items():
        total = len(apps)
        replied = sum(1 for a in apps if _is_replied(a))
        offers = sum(1 for a in apps if _is_offer(a))
        result.append({
            "job_type": job_type,
            "total": total,
            "replied": replied,
            "reply_rate": round(replied / total * 100, 1) if total > 0 else 0,
            "offers": offers,
            "offer_rate": round(offers / total * 100, 1) if total > 0 else 0,
        })
    # 按回复率降序
    result.sort(key=lambda x: x["reply_rate"], reverse=True)
    return result


def analyze_by_channel(applications: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """按投递渠道统计"""
    groups = defaultdict(list)
    for app in applications:
        channel = app.get("channel") or "未标注"
        groups[channel].append(app)

    result = []
    for channel, apps in groups.items():
        total = len(apps)
        replied = sum(1 for a in apps if _is_replied(a))
        result.append({
            "channel": channel,
            "total": total,
            "replied": replied,
            "reply_rate": round(replied / total * 100, 1) if total > 0 else 0,
        })
    result.sort(key=lambda x: x["reply_rate"], reverse=True)
    return result


def analyze_by_resume_version(applications: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """按简历版本统计：哪版简历效果好"""
    groups = defaultdict(list)
    for app in applications:
        resume_id = app.get("resume_id")
        key = f"简历版本#{resume_id}" if resume_id else "未关联简历"
        groups[key].append(app)

    result = []
    for version, apps in groups.items():
        total = len(apps)
        replied = sum(1 for a in apps if _is_replied(a))
        offers = sum(1 for a in apps if _is_offer(a))
        result.append({
            "resume_version": version,
            "total": total,
            "replied": replied,
            "reply_rate": round(replied / total * 100, 1) if total > 0 else 0,
            "offers": offers,
        })
    result.sort(key=lambda x: x["reply_rate"], reverse=True)
    return result


def analyze_by_time_period(applications: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """按投递月份统计：找出集体沉默的批次"""
    groups = defaultdict(list)
    for app in applications:
        applied_at = app.get("applied_at")
        if applied_at:
            # 取年月，格式 "2026-08"
            month = applied_at[:7] if len(applied_at) >= 7 else applied_at
        else:
            month = "未知时间"
        groups[month].append(app)

    result = []
    for month, apps in sorted(groups.items()):
        total = len(apps)
        replied = sum(1 for a in apps if _is_replied(a))
        no_response = sum(1 for a in apps if a.get("status") == "no_response")
        result.append({
            "month": month,
            "total": total,
            "replied": replied,
            "reply_rate": round(replied / total * 100, 1) if total > 0 else 0,
            "no_response": no_response,
        })
    return result


def analyze_by_match_score(applications: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """按匹配度分数段统计：高匹配是否真的回复率高"""
    # 分数段：0-30, 30-50, 50-70, 70-85, 85-100
    ranges = [(0, 30, "0-30"), (30, 50, "30-50"), (50, 70, "50-70"),
              (70, 85, "70-85"), (85, 101, "85-100")]
    result = []
    for low, high, label in ranges:
        apps = [a for a in applications
                if a.get("match_score") is not None and low <= a["match_score"] < high]
        total = len(apps)
        replied = sum(1 for a in apps if _is_replied(a))
        result.append({
            "score_range": label,
            "total": total,
            "replied": replied,
            "reply_rate": round(replied / total * 100, 1) if total > 0 else 0,
        })
    return result


def generate_attribution_conclusion(stats: Dict[str, Any]) -> str:
    """用 LLM 把统计数据总结成归因结论（这是灵魂）"""
    prompt = f"""请基于以下投递数据统计，生成一段投递决策归因分析（300字以内）。

=== 整体情况 ===
总投递数：{stats['total']}
总回复数：{stats['replied']}
整体回复率：{stats['overall_reply_rate']}%
offer数：{stats['offers']}

=== 按岗位类型（回复率从高到低）===
{_format_list(stats['by_job_type'], ['job_type', 'total', 'reply_rate', 'offers'])}

=== 按渠道 ===
{_format_list(stats['by_channel'], ['channel', 'total', 'reply_rate'])}

=== 按简历版本 ===
{_format_list(stats['by_resume_version'], ['resume_version', 'total', 'reply_rate'])}

=== 按月份 ===
{_format_list(stats['by_time_period'], ['month', 'total', 'reply_rate', 'no_response'])}

=== 按匹配度 ===
{_format_list(stats['by_match_score'], ['score_range', 'total', 'reply_rate'])}

请分析：
1. 哪类岗位回复率最高？占投递量多少？是否应该加大投入？
2. 哪类岗位回复率最低但占比最大？是不是投错了方向？
3. 哪个渠道效果最好/最差？
4. 哪版简历效果好？是否应该统一用那版？
5. 有没有集体沉默的时间段？可能是什么原因？
6. 匹配度高的岗位回复率真的高吗？如果不是，说明什么？

要求：
- 用数据说话，每个结论都要有数字支撑
- 给出具体的行动建议（下一步该投什么、用哪版简历、走哪个渠道）
- 语气直接，不要客套话
- 输出纯文本，不要 JSON
"""
    conclusion = llm_client.chat(
        "你是一个资深求职策略分析师，擅长从投递数据中找出规律并给出 actionable 的建议。",
        prompt,
        temperature=0.4,
    )
    return conclusion


def _format_list(items: List[Dict[str, Any]], fields: List[str]) -> str:
    """把统计列表格式化成可读文本"""
    if not items:
        return "（无数据）"
    lines = []
    for item in items:
        parts = [f"{f}={item.get(f, '-')}" for f in fields]
        lines.append("  " + ", ".join(parts))
    return "\n".join(lines)


def run_full_analysis(user_id: int) -> Dict[str, Any]:
    """运行完整的漏斗归因分析"""
    # 1. 拉取所有投递记录
    applications = java_client.list_applications(user_id)

    if not applications:
        return {
            "total": 0,
            "message": "暂无投递记录，先去投几份简历吧",
        }

    # 2. 各维度统计
    by_job_type = analyze_by_job_type(applications)
    by_channel = analyze_by_channel(applications)
    by_resume_version = analyze_by_resume_version(applications)
    by_time_period = analyze_by_time_period(applications)
    by_match_score = analyze_by_match_score(applications)

    total = len(applications)
    replied = sum(1 for a in applications if _is_replied(a))
    offers = sum(1 for a in applications if _is_offer(a))

    stats = {
        "total": total,
        "replied": replied,
        "offers": offers,
        "overall_reply_rate": round(replied / total * 100, 1) if total > 0 else 0,
        "by_job_type": by_job_type,
        "by_channel": by_channel,
        "by_resume_version": by_resume_version,
        "by_time_period": by_time_period,
        "by_match_score": by_match_score,
    }

    # 3. LLM 生成归因结论
    conclusion = generate_attribution_conclusion(stats)
    stats["conclusion"] = conclusion

    return stats
