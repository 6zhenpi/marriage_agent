import json
from app.llm.client import get_llm_response

STUCK_KEYWORDS = [
    "不懂", "不明白", "不理解", "不清楚", "不知道怎么说",
    "不知道怎么描述", "说不清楚", "不知道从何说起",
    "迷糊", "混乱", "搞不懂", "看不懂",
    "没看懂", "不理解", "啥意思", "什么意思",
    "怎么办", "不知道怎么办", "毫无头绪",
]

HEURISTIC_PROMPT = """用户在描述问题时遇到了困难。根据对话历史，生成2-3个专业、易懂的选项帮助用户继续。

规则：
- 严格基于已知事实
- 如果用户不理解术语，提供解释选项和行动选项
- 如果情况不明确，将模糊描述映射到最可能的2-3个婚姻法律场景
- 每个选项不超过20个字
- 始终添加最后一个"以上都不是，我来说明"选项
- 严格输出JSON格式: {{"options": ["选项A", "选项B", "选项C"]}}

对话历史: {history}
用户最新输入: {user_input}
已知信息: {entities}"""


def is_stuck(user_input: str, feedback: str | None = None) -> bool:
    if feedback == "not_helpful":
        return True
    lower = user_input.strip().lower()
    return any(kw in lower for kw in STUCK_KEYWORDS)


async def generate_heuristic_options(
    user_input: str,
    history: list[dict],
    entities: str,
) -> list[str]:
    history_text = "\n".join(
        f"{'用户' if m['role'] == 'user' else '助手'}: {m['content']}"
        for m in history[-6:]
    )

    prompt = HEURISTIC_PROMPT.format(
        history=history_text,
        user_input=user_input,
        entities=entities,
    )

    response = await get_llm_response(
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5,
        max_tokens=200,
    )

    try:
        result = json.loads(response)
        options = result.get("options", [])
        if not options or not isinstance(options, list):
            return ["我想咨询离婚问题", "我想咨询财产分割", "以上都不是，我来说明"]
        if options[-1] not in ("以上都不是，我来说明", "以上都不是,我来说明"):
            options.append("以上都不是，我来说明")
        return options[:4]
    except (json.JSONDecodeError, AttributeError):
        return ["我想咨询离婚问题", "我想咨询财产分割", "以上都不是，我来说明"]
