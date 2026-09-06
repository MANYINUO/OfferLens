"""JD 结构化服务：把职位描述文本拆解成硬性要求/加分项/隐性要求。"""

from app.models import JDParseResult
from app.llm_client import llm_client


SYSTEM_PROMPT = """你是一个专业的职位分析助手。请从给定的职位描述（JD）中提取结构化信息。
要求：
1. hard_requirements：明确写了"必须"、"要求"、"精通"、"熟练"的条件
2. nice_to_have：写了"优先"、"加分"、"了解"的条件
3. implicit_requirements：字面上没说但暗示的要求，比如：
   - "抗压能力强" → 可能需要加班
   - "有创业精神" → 可能一人多岗
   - "能接受出差" → 频繁出差
   - "年轻化团队" → 可能加班文化
4. job_type：判断岗位大类（Java后端/前端/测试/运维/AI应用/产品/运营等）
5. 只提取文本中存在的信息，不要编造
6. 输出严格的 JSON 格式"""


def parse_jd(text: str) -> JDParseResult:
    """把 JD 文本结构化"""
    user_prompt = f"请解析以下职位描述，输出 JSON：\n\n{text}"
    data = llm_client.chat_json(SYSTEM_PROMPT, user_prompt)
    return JDParseResult(**data)
