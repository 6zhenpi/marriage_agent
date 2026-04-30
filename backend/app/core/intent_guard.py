from enum import Enum
from typing import Optional


class IntentResult(Enum):
    WHITELIST_GREETING = "whitelist_greeting"
    WHITELIST_IDENTITY = "whitelist_identity"
    WHITELIST_CAPABILITY = "whitelist_capability"
    WHITELIST_THANKS = "whitelist_thanks"
    ALLOWED_FAMILY_LAW = "allowed_family_law"
    REJECT_NON_LEGAL = "reject_non_legal"
    REJECT_OUTSIDE_DOMAIN = "reject_outside_domain"
    REJECT_BLACKLIST = "reject_blacklist"


GREETING_PATTERNS = [
    "你好", "您好", "hi", "hello", "嗨", "早上好", "下午好", "晚上好",
    "早上好", "下午好", "晚上好", "早", "在吗", "在不在",
]

IDENTITY_PATTERNS = [
    "你是谁", "你叫什么", "你是什么", "who are you", "介绍一下你自己",
    "你是哪个", "你叫啥",
]

CAPABILITY_PATTERNS = [
    "你能做什么", "你会什么", "你有什么功能", "你可以做什么",
    "你能帮我什么", "你有什么用", "what can you do",
]

THANKS_PATTERNS = [
    "谢谢", "感谢", "多谢", "thanks", "thank you", "谢了", "辛苦了",
]

FAMILY_LAW_KEYWORDS = [
    "结婚", "离婚", "婚姻", "彩礼", "嫁妆", "婚约", "同居", "事实婚姻",
    "夫妻", "配偶", "丈夫", "妻子", "老公", "老婆",
    "财产", "共同财产", "个人财产", "婚前财产", "婚后财产", "房产", "分割",
    "抚养", "抚养权", "抚养费", "子女", "孩子", "监护", "探望", "探视",
    "家暴", "家庭暴力", "暴力", "殴打", "虐待", "人身保护令",
    "继承", "遗嘱", "遗产", "法定继承", "遗赠", "赠与",
    "收养", "领养",
    "婚内", "出轨", "重婚", "同居", "忠诚协议",
    "离婚协议", "诉讼离婚", "协议离婚", "调解",
    "赡养", "扶养",
    "婚姻法", "民法典", "婚姻家庭编", "继承编",
    "离婚冷静期", "过错方", "损害赔偿",
]

NON_LEGAL_KEYWORDS = [
    "做饭", "菜谱", "美食", "旅游", "天气", "电影", "音乐", "游戏",
    "笑话", "聊天", "闲聊", "星座", "算命", "占卜",
    "减肥", "健身", "养生", "化妆", "穿搭",
]

OUTSIDE_DOMAIN_KEYWORDS = [
    "劳动", "工伤", "劳动合同", "工资", "社保",
    "刑事", "犯罪", "盗窃", "诈骗", "故意伤害",
    "交通", "交通事故", "肇事",
    "合同", "买卖合同", "租赁合同",
    "公司", "股东", "股权", "破产",
    "行政", "行政诉讼",
    "知识产权", "专利", "商标", "著作权",
    "税务", "税收",
    "移民", "签证",
]

BLACKLIST_KEYWORDS = [
    "转移财产", "隐匿财产", "假离婚", "虚假离婚", "逃避债务",
    "伪造证据", "伪造签名", "冒名",
    "如何隐藏", "如何转移", "如何逃避",
]


class IntentGuard:
    def check(self, user_input: str) -> tuple[IntentResult, Optional[str]]:
        text = user_input.strip().lower()

        if self._match_patterns(text, IDENTITY_PATTERNS):
            return IntentResult.WHITELIST_IDENTITY, (
                "我是婚姻家庭法律知识助手，专注于为您提供婚姻、家庭、继承等方面的法律知识科普。"
                "本工具不构成法律意见，如需正式法律帮助请咨询专业律师。"
            )

        if self._match_patterns(text, CAPABILITY_PATTERNS):
            return IntentResult.WHITELIST_CAPABILITY, (
                "我可以为您：\n"
                "1. 解释婚姻家庭相关法律条文\n"
                "2. 分析类似案例供参考\n"
                "3. 梳理法律程序和步骤\n"
                "4. 指导证据收集方向\n"
                "5. 提供诉讼费用估算和抚养费参考\n\n"
                "请注意：以上内容均为法律知识科普，不构成法律意见。"
            )

        if self._match_patterns(text, GREETING_PATTERNS):
            return IntentResult.WHITELIST_GREETING, (
                "您好！我是婚姻家庭法律知识助手，可以为您解答婚姻、离婚、财产分割、"
                "子女抚养、家庭暴力、继承等方面的法律问题。请问有什么可以帮您？"
            )

        if self._match_patterns(text, THANKS_PATTERNS):
            return IntentResult.WHITELIST_THANKS, (
                "不客气！如果还有其他婚姻家庭法律问题，随时可以问我。"
                "以上内容仅供参考，不构成法律意见。"
            )

        if self._match_keywords(text, BLACKLIST_KEYWORDS):
            return IntentResult.REJECT_BLACKLIST, (
                "抱歉，我无法提供可能违反法律或公序良俗的行为指导。"
                "如果您有合法的法律问题，我很乐意为您解答。"
            )

        if self._match_keywords(text, OUTSIDE_DOMAIN_KEYWORDS):
            return IntentResult.REJECT_OUTSIDE_DOMAIN, (
                "这超出了我的专业范围。我是婚姻家庭法律助手，"
                "主要解答婚姻、离婚、财产分割、子女抚养、家庭暴力、继承等问题。"
                "如需其他领域法律帮助，请拨打12348法律援助热线或咨询专业律师。"
            )

        if self._match_keywords(text, FAMILY_LAW_KEYWORDS):
            return IntentResult.ALLOWED_FAMILY_LAW, None

        if self._match_keywords(text, NON_LEGAL_KEYWORDS):
            return IntentResult.REJECT_NON_LEGAL, (
                "我是婚姻家庭法律知识助手，只能回答与法律相关的问题。"
                "如有婚姻家庭法律方面的疑问，欢迎随时提问。"
            )

        return IntentResult.ALLOWED_FAMILY_LAW, None

    def _match_patterns(self, text: str, patterns: list[str]) -> bool:
        return any(p in text for p in patterns)

    def _match_keywords(self, text: str, keywords: list[str]) -> bool:
        return any(kw in text for kw in keywords)


intent_guard = IntentGuard()
