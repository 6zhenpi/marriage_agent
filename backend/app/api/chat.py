import json
from typing import Optional
from fastapi import APIRouter
from pydantic import BaseModel

from app.core.intent_guard import intent_guard, IntentResult
from app.core.emergency import detect_emergency, prepend_emergency_info
from app.core.heuristic import is_stuck, generate_heuristic_options
from app.core.slot_manager import DialogueSlots, SLOT_EXTRACTION_PROMPT
from app.llm.client import get_llm_response
from app.llm.prompts import (
    SYSTEM_PROMPT_COLLECT,
    SYSTEM_PROMPT_FINAL,
    SLOT_EXTRACTION_SYSTEM_PROMPT,
    INQUIRY_PROMPT,
)
from app.core.rag_retriever import search_all, format_rag_context

router = APIRouter()

conversations: dict[str, dict] = {}


class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"
    feedback: Optional[str] = None


class ChatResponse(BaseModel):
    reply: str
    options: Optional[list[str]] = None
    is_emergency: bool = False
    session_id: str


class OptionRequest(BaseModel):
    option: str
    session_id: str = "default"


def _get_or_create_session(session_id: str) -> dict:
    if session_id not in conversations:
        conversations[session_id] = {
            "history": [],
            "slots": DialogueSlots(),
        }
    return conversations[session_id]


def _search_similar_cases(query: str, dispute_type: str | None = None) -> list[dict]:
    rag_results = search_all(query, dispute_type=dispute_type)
    return rag_results


def _format_rag_context(rag_results: dict[str, list[dict]]) -> str:
    return format_rag_context(rag_results)


async def _extract_slots(
    user_input: str, history: list[dict], current_slots: DialogueSlots
) -> DialogueSlots:
    history_text = "\n".join(
        f"{'用户' if m['role'] == 'user' else '助手'}: {m['content']}"
        for m in history[-6:]
    )
    prompt = SLOT_EXTRACTION_PROMPT.format(
        history=history_text,
        user_input=user_input,
        current_slots=current_slots.model_dump_json(),
    )
    try:
        response = await get_llm_response(
            messages=[
                {"role": "system", "content": SLOT_EXTRACTION_SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.1,
            max_tokens=300,
        )
        extracted = json.loads(response)
        if isinstance(extracted, dict):
            current_slots.update_from_dict(extracted)
    except (json.JSONDecodeError, Exception):
        pass
    return current_slots


async def _generate_inquiry(
    user_input: str,
    slots: DialogueSlots,
    missing_fields: list[str],
) -> tuple[str, list[str] | None]:
    missing_labels = [slots.get_missing_field_label(f) for f in missing_fields[:3]]
    missing_options_map = {
        slots.get_missing_field_label(f): slots.get_missing_field_options(f)
        for f in missing_fields[:3]
    }

    all_options: list[str] = []
    for label, opts in missing_options_map.items():
        if opts:
            all_options.extend(opts[:3])

    if len(missing_fields) <= 2 and all_options:
        inquiry_text = (
            f"为了给您更准确的建议，我还需要了解：{'、'.join(missing_labels)}。"
            f"请选择最符合您情况的选项，或者直接告诉我："
        )
        all_options.append("以上都不是，我来说明")
        return inquiry_text, all_options[:5]

    prompt = INQUIRY_PROMPT.format(
        known_info=slots.to_context_string(),
        missing_info="、".join(missing_labels),
        user_input=user_input,
    )
    try:
        response = await get_llm_response(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=200,
        )
        result = json.loads(response)
        inquiry_text = result.get("inquiry", f"为了给您更准确的建议，我还需要了解：{'、'.join(missing_labels)}")
        options = result.get("options", [])
        if not options or not isinstance(options, list):
            return inquiry_text, None
        if options[-1] not in ("以上都不是，我来说明", "以上都不是,我来说明"):
            options.append("以上都不是，我来说明")
        return inquiry_text, options[:5]
    except (json.JSONDecodeError, AttributeError):
        inquiry_text = (
            f"为了给您更准确的建议，我还需要了解：{'、'.join(missing_labels)}。"
            f"请告诉我相关情况："
        )
        return inquiry_text, None


async def _collect_phase_reply(
    user_input: str,
    history: list[dict],
    slots: DialogueSlots,
    missing_fields: list[str],
    is_emergency: bool,
) -> ChatResponse:
    inquiry_text, options = await _generate_inquiry(
        user_input, slots, missing_fields
    )

    if is_emergency:
        gender = slots.gender or "未知"
        inquiry_text = prepend_emergency_info(inquiry_text, gender)

    history.append({"role": "user", "content": user_input})
    history.append({"role": "assistant", "content": inquiry_text})

    if len(history) > 14:
        history[:] = history[-14:]

    return ChatResponse(
        reply=inquiry_text,
        options=options,
        is_emergency=is_emergency,
        session_id="",
    )


async def _final_phase_reply(
    user_input: str,
    history: list[dict],
    slots: DialogueSlots,
    is_emergency: bool,
    session_id: str,
) -> ChatResponse:
    rag_results = _search_similar_cases(user_input, slots.dispute_type)
    rag_context = _format_rag_context(rag_results)

    slot_context = f"\n\n当前已知用户信息：\n{slots.to_context_string()}"

    messages = [{"role": "system", "content": SYSTEM_PROMPT_FINAL + rag_context + slot_context}]
    for msg in history[-8:]:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": user_input})

    reply = await get_llm_response(messages=messages)

    if is_emergency:
        gender = slots.gender or "未知"
        reply = prepend_emergency_info(reply, gender)

    if "以上内容仅供参考" not in reply:
        reply += "\n\n⚠️ **免责声明**：以上内容仅供参考，不构成法律意见。如需正式法律帮助，请咨询专业律师或拨打12348法律援助热线。"

    history.append({"role": "user", "content": user_input})
    history.append({"role": "assistant", "content": reply})

    if len(history) > 14:
        history[:] = history[-14:]

    options = None
    if is_stuck(user_input, None):
        options = await generate_heuristic_options(
            user_input, history, slots.to_context_string()
        )

    return ChatResponse(
        reply=reply,
        options=options,
        is_emergency=is_emergency,
        session_id=session_id,
    )


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    session = _get_or_create_session(request.session_id)
    history = session["history"]
    slots = session["slots"]

    intent_result, fixed_reply = intent_guard.check(request.message)

    if fixed_reply is not None and intent_result != IntentResult.ALLOWED_FAMILY_LAW:
        is_emergency = detect_emergency(request.message)
        reply = fixed_reply
        if is_emergency:
            gender = slots.gender or "未知"
            reply = prepend_emergency_info(reply, gender)

        history.append({"role": "user", "content": request.message})
        history.append({"role": "assistant", "content": reply})

        if len(history) > 14:
            history[:] = history[-14:]

        return ChatResponse(
            reply=reply,
            is_emergency=is_emergency,
            session_id=request.session_id,
        )

    slots = await _extract_slots(request.message, history, slots)
    session["slots"] = slots

    is_emergency = detect_emergency(request.message)
    if is_emergency:
        slots.violence_involved = True

    if not slots.is_info_complete():
        missing_fields = slots.get_missing_fields()
        result = await _collect_phase_reply(
            request.message, history, slots, missing_fields, is_emergency
        )
        result.session_id = request.session_id
        return result

    result = await _final_phase_reply(
        request.message, history, slots, is_emergency, request.session_id
    )
    return result


@router.post("/option", response_model=ChatResponse)
async def select_option(request: OptionRequest):
    return await chat(
        ChatRequest(message=request.option, session_id=request.session_id)
    )
