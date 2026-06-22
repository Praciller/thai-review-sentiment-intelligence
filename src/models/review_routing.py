"""Deterministic operational routing for sentiment predictions."""

from __future__ import annotations

import re
from dataclasses import dataclass


POSITIVE_TERMS = ("ดี", "อร่อย", "ชอบ", "เยี่ยม", "คุ้ม", "ประทับใจ")
NEGATIVE_TERMS = ("แย่", "ช้า", "แพง", "เสีย", "สกปรก", "รอนาน", "ไม่ดี")
QUESTION_TERMS = ("ไหม", "หรือ", "กี่", "เมื่อไหร่", "?", "หรือเปล่า")


@dataclass(frozen=True)
class RoutingDecision:
    route: str
    requires_human_review: bool
    priority: str
    reason_codes: tuple[str, ...]
    confidence_threshold: float


def route_prediction(
    text: str,
    predicted_label: str,
    confidence: float,
    *,
    confidence_threshold: float = 0.7,
) -> RoutingDecision:
    """Route one prediction while keeping the reason trail explicit."""
    reasons: list[str] = []
    question = predicted_label == "question" or _contains(text, QUESTION_TERMS)
    mixed = _contains(text, POSITIVE_TERMS) and _contains(text, NEGATIVE_TERMS)

    if confidence < confidence_threshold:
        reasons.append("low_confidence")
    if predicted_label == "negative":
        reasons.append("negative_sentiment")
    if question:
        reasons.append("question_intent")
    if mixed:
        reasons.append("possible_mixed_sentiment")
    if len(text.strip()) < 8:
        reasons.append("short_text")
    if _contains(text, ("ช้า", "รอนาน", "คิว")):
        reasons.append("contains_waiting_time_issue")
    if _contains(text, ("ส่ง", "เดลิเวอรี่", "ไรเดอร์", "delivery")):
        reasons.append("contains_delivery_issue")
    if _contains(text, ("แพง", "ราคา", "คุ้ม")):
        reasons.append("contains_price_issue")

    if question:
        route, priority = "support_workflow", "high"
    elif mixed or confidence < confidence_threshold:
        priority = "high" if predicted_label == "negative" else "normal"
        route = "human_review"
    elif predicted_label == "negative":
        route, priority = "escalation_queue", "high"
    else:
        route, priority = "auto_label", "normal"

    return RoutingDecision(
        route=route,
        requires_human_review=route != "auto_label",
        priority=priority,
        reason_codes=tuple(dict.fromkeys(reasons)),
        confidence_threshold=confidence_threshold,
    )


def _contains(text: str, terms: tuple[str, ...]) -> bool:
    return bool(match_terms(text, terms))


def match_terms(text: str, terms: tuple[str, ...]) -> tuple[str, ...]:
    """Match keywords without treating common Thai negation as positive evidence."""
    lowered = text.lower()
    return tuple(
        term
        for term in terms
        if (
            re.search(rf"(?<!ไม่){re.escape(term.lower())}", lowered)
            if term in POSITIVE_TERMS
            else term.lower() in lowered
        )
    )
