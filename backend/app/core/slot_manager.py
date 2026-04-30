from typing import ClassVar, Optional
from pydantic import BaseModel


class DialogueSlots(BaseModel):
    gender: Optional[str] = None
    marital_status: Optional[str] = None
    has_children: Optional[bool] = None
    children_count: Optional[int] = None
    children_age: Optional[str] = None
    living_arrangement: Optional[str] = None
    income_status: Optional[str] = None
    employment_status: Optional[str] = None
    property_type: Optional[str] = None
    property_detail: Optional[str] = None
    violence_involved: Optional[bool] = None
    violence_type: Optional[str] = None
    fault_party: Optional[str] = None
    dispute_type: Optional[str] = None
    existing_court_orders: Optional[str] = None
    goal: Optional[str] = None

    REQUIRED_FIELDS_BY_DISPUTE: ClassVar[dict[str, list[str]]] = {
        "离婚-抚养权": ["gender", "marital_status", "has_children", "children_age", "living_arrangement", "income_status"],
        "离婚-财产分割": ["gender", "marital_status", "property_type", "property_detail"],
        "家庭暴力": ["gender", "violence_type", "living_arrangement"],
        "继承纠纷": ["gender", "marital_status"],
        "离婚-综合": ["gender", "marital_status", "has_children", "property_type"],
        "彩礼纠纷": ["gender", "marital_status"],
    }

    FIELD_LABELS: ClassVar[dict[str, str]] = {
        "gender": "您的性别",
        "marital_status": "婚姻状态",
        "has_children": "是否有子女",
        "children_age": "子女年龄",
        "living_arrangement": "目前居住安排",
        "income_status": "收入状况",
        "employment_status": "就业状况",
        "property_type": "财产类型",
        "property_detail": "财产详情",
        "violence_type": "暴力类型",
        "existing_court_orders": "是否有法院判决或协议",
    }

    FIELD_OPTIONS: ClassVar[dict[str, list[str]]] = {
        "gender": ["男性", "女性", "其他"],
        "marital_status": ["已婚", "未婚", "分居中", "正在离婚", "已离婚"],
        "has_children": ["有子女", "无子女"],
        "living_arrangement": ["与配偶同住", "分居独住", "与亲友同住", "其他"],
        "income_status": ["有稳定收入", "收入不稳定", "无收入", "不愿透露"],
        "employment_status": ["全职工作", "兼职工作", "自由职业", "失业", "退休"],
        "violence_type": ["身体暴力", "精神暴力/言语虐待", "经济控制", "多种形式"],
        "existing_court_orders": ["有法院判决/调解书", "有私下协议", "没有任何协议或判决"],
    }

    def to_context_string(self) -> str:
        parts = []
        if self.gender:
            parts.append(f"性别: {self.gender}")
        if self.marital_status:
            parts.append(f"婚姻状态: {self.marital_status}")
        if self.has_children is not None:
            parts.append(f"是否有子女: {'是' if self.has_children else '否'}")
        if self.children_count is not None:
            parts.append(f"子女数量: {self.children_count}")
        if self.children_age:
            parts.append(f"子女年龄: {self.children_age}")
        if self.living_arrangement:
            parts.append(f"居住安排: {self.living_arrangement}")
        if self.income_status:
            parts.append(f"收入状况: {self.income_status}")
        if self.employment_status:
            parts.append(f"就业状况: {self.employment_status}")
        if self.property_type:
            parts.append(f"财产类型: {self.property_type}")
        if self.property_detail:
            parts.append(f"财产详情: {self.property_detail}")
        if self.violence_involved is not None:
            parts.append(f"是否涉及家暴: {'是' if self.violence_involved else '否'}")
        if self.violence_type:
            parts.append(f"暴力类型: {self.violence_type}")
        if self.fault_party:
            parts.append(f"过错方: {self.fault_party}")
        if self.dispute_type:
            parts.append(f"争议类型: {self.dispute_type}")
        if self.existing_court_orders:
            parts.append(f"已有法院命令/协议: {self.existing_court_orders}")
        if self.goal:
            parts.append(f"用户目标: {self.goal}")
        return "\n".join(parts) if parts else "暂无已知信息"

    def update_from_dict(self, data: dict) -> "DialogueSlots":
        for key, value in data.items():
            if hasattr(self, key) and value is not None:
                setattr(self, key, value)
        return self

    def is_info_complete(self) -> bool:
        if not self.dispute_type:
            return False
        return len(self.get_missing_fields()) == 0

    def get_missing_fields(self) -> list[str]:
        if not self.dispute_type:
            return []
        required = self.REQUIRED_FIELDS_BY_DISPUTE.get(self.dispute_type, [])
        missing = []
        for field in required:
            val = getattr(self, field, None)
            if val is None:
                missing.append(field)
        return missing

    def get_missing_field_label(self, field: str) -> str:
        return self.FIELD_LABELS.get(field, field)

    def get_missing_field_options(self, field: str) -> list[str] | None:
        return self.FIELD_OPTIONS.get(field)


SLOT_EXTRACTION_PROMPT = """Based on the user's message and conversation history, extract the following information if mentioned.
Only extract explicitly stated facts, do not infer.

Fields:
- gender: 用户性别 (如: 男性, 女性, 其他)
- marital_status: 婚姻状态 (如: 已婚, 未婚, 分居中, 正在离婚, 已离婚)
- has_children: 是否有子女 (true/false)
- children_count: 子女数量 (数字)
- children_age: 子女年龄 (如: "3岁和5岁")
- living_arrangement: 居住安排 (如: 与配偶同住, 分居独住, 与亲友同住)
- income_status: 收入状况 (如: 有稳定收入, 收入不稳定, 无收入)
- employment_status: 就业状况 (如: 全职工作, 兼职工作, 自由职业, 失业)
- property_type: 财产类型 (如: 房产, 车辆, 存款, 股权)
- property_detail: 财产详情 (如: "婚前购买,婚后共同还贷")
- violence_involved: 是否涉及家暴 (true/false)
- violence_type: 暴力类型 (如: 身体暴力, 精神暴力, 经济控制, 多种形式)
- fault_party: 过错方 (如: 对方出轨, 对方家暴)
- dispute_type: 争议类型 (如: 离婚-财产分割, 离婚-抚养权, 离婚-综合, 家庭暴力, 继承纠纷, 彩礼纠纷)
- existing_court_orders: 已有法院命令或协议 (如: 有法院判决/调解书, 有私下协议, 没有任何协议或判决)
- goal: 用户目标 (如: 想离婚, 要抚养权, 分割房产)

Return a JSON object with only the fields that can be extracted. If nothing can be extracted, return {{}}.

Conversation history: {history}
User latest input: {user_input}
Current known slots: {current_slots}
"""
