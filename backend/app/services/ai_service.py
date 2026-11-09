from __future__ import annotations

import re
from typing import Any

import requests
from flask import current_app

from ..models.lost_case import LostCase
from ..models.match import CaseSightingMatch


def _normalize_description(text: str) -> str:
    normalized = re.sub(r"\s+", " ", text).strip()
    if normalized and normalized[-1] not in "。！？.!?":
        normalized += "。"
    return normalized


def _description_suggestions(text: str) -> list[str]:
    suggestions = [
        "补充宠物体型、毛色和明显特征，便于目击者快速辨认。",
        "写明最后出现的时间、地点及可能移动方向。",
        "上传正面和侧面的清晰近照，避免包含无关个人信息。",
    ]
    if any(word in text for word in ("项圈", "衣服", "吊牌", "铃铛")):
        suggestions[0] = "继续补充耳朵、尾巴或伤疤等不会轻易变化的特征。"
    return suggestions


def _remote_completion(system_prompt: str, user_prompt: str) -> str | None:
    base_url = str(current_app.config.get("AI_API_BASE_URL") or "").strip()
    api_key = str(current_app.config.get("AI_API_KEY") or "").strip()
    model = str(current_app.config.get("AI_MODEL") or "").strip()
    if not (base_url and api_key and model):
        return None

    timeout = float(current_app.config.get("AI_TIMEOUT_SECONDS", 8))
    response = requests.post(
        f"{base_url.rstrip('/')}/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": model,
            "temperature": 0.2,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        },
        timeout=timeout,
    )
    response.raise_for_status()
    payload: Any = response.json()
    if not isinstance(payload, dict):
        raise ValueError("AI response must be a JSON object")
    choices = payload.get("choices")
    if not isinstance(choices, list) or not choices:
        raise ValueError("AI response is missing choices")
    message = choices[0].get("message") if isinstance(choices[0], dict) else None
    content = message.get("content") if isinstance(message, dict) else None
    if not isinstance(content, str) or not content.strip():
        raise ValueError("AI response is missing message content")
    return content.strip()


def optimize_description(text: str) -> dict[str, Any]:
    local_text = _normalize_description(text)
    suggestions = _description_suggestions(local_text)
    if not current_app.config.get("AI_API_KEY"):
        return {"text": local_text, "suggestions": suggestions, "source": "local"}

    try:
        remote_text = _remote_completion(
            "你是宠物走失信息编辑助手。仅润色事实，不添加用户没有提供的信息。",
            f"请把下面描述整理成一段简洁、可核实的中文：\n{local_text}",
        )
        if remote_text is None:
            return {"text": local_text, "suggestions": suggestions, "source": "local"}
        return {"text": remote_text, "suggestions": suggestions, "source": "remote"}
    except (requests.RequestException, ValueError, TypeError, KeyError, IndexError):
        current_app.logger.warning("Optional AI description request failed; using local fallback")
        return {
            "text": local_text,
            "suggestions": suggestions,
            "source": "local_fallback",
        }


def _local_case_summary(lost_case: LostCase) -> str:
    match_count = CaseSightingMatch.query.filter_by(case_id=lost_case.case_id).count()
    high_match_count = CaseSightingMatch.query.filter(
        CaseSightingMatch.case_id == lost_case.case_id,
        CaseSightingMatch.total_score >= 75,
    ).count()
    return (
        f"宠物“{lost_case.pet.name}”在{lost_case.address}附近走失，"
        f"当前事件状态为 {lost_case.status}。系统已生成 {match_count} 条候选线索，"
        f"其中 {high_match_count} 条为高匹配线索。"
    )


def summarize_case(lost_case: LostCase) -> dict[str, str]:
    local_text = _local_case_summary(lost_case)
    if not current_app.config.get("AI_API_KEY"):
        return {"text": local_text, "source": "local"}

    try:
        remote_text = _remote_completion(
            "你是宠物协同搜寻助手。根据给定事实生成简短行动摘要，不推测未知信息。",
            local_text,
        )
        if remote_text is None:
            return {"text": local_text, "source": "local"}
        return {"text": remote_text, "source": "remote"}
    except (requests.RequestException, ValueError, TypeError, KeyError, IndexError):
        current_app.logger.warning("Optional AI summary request failed; using local fallback")
        return {"text": local_text, "source": "local_fallback"}
