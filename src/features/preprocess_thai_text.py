"""Reusable Thai text preprocessing for sparse baseline models."""

from __future__ import annotations

import re
from collections.abc import Collection

from pythainlp.corpus.common import thai_stopwords
from pythainlp.tokenize import word_tokenize
from pythainlp.util import normalize

URL_PATTERN = re.compile(r"(?:https?://|www\.)\S+", re.IGNORECASE)
WHITESPACE_PATTERN = re.compile(r"\s+")
REPEATED_THAI_CHARACTER_PATTERN = re.compile(r"([ก-๛])\1{2,}")

LABEL_ALIASES = {
    "pos": "positive",
    "positive": "positive",
    "neg": "negative",
    "negative": "negative",
    "neu": "neutral",
    "neutral": "neutral",
    "q": "question",
    "question": "question",
}

TOPIC_KEYWORDS = {
    "price": ("แพง", "ราคา", "คุ้ม"),
    "delivery": ("ส่ง", "เดลิเวอรี่", "ไรเดอร์"),
    "waiting_time": ("ช้า", "รอนาน", "คิว"),
    "service": ("พนักงาน", "บริการ"),
    "taste": ("อร่อย", "รสชาติ", "หวาน", "เค็ม"),
    "cleanliness": ("สะอาด", "สกปรก"),
    "product_quality": ("คุณภาพ", "ชำรุด", "เสียหาย", "ใช้งาน"),
}


def clean_text(text: str) -> str:
    """Lightly normalize Thai text while preserving sentiment-bearing content."""
    if not isinstance(text, str):
        raise TypeError("text must be a string")

    cleaned = normalize(text)
    cleaned = URL_PATTERN.sub(" ", cleaned)
    cleaned = REPEATED_THAI_CHARACTER_PATTERN.sub(r"\1\1", cleaned)
    return WHITESPACE_PATTERN.sub(" ", cleaned).strip()


def tokenize_thai_text(
    text: str,
    *,
    remove_stopwords: bool = False,
    stopwords: Collection[str] | None = None,
) -> list[str]:
    """Tokenize cleaned Thai text with PyThaiNLP's dictionary-based tokenizer."""
    cleaned = clean_text(text)
    if not cleaned:
        return []

    tokens = [
        token.strip()
        for token in word_tokenize(cleaned, engine="newmm", keep_whitespace=False)
        if token.strip()
    ]
    if not remove_stopwords:
        return tokens

    excluded = set(stopwords) if stopwords is not None else set(thai_stopwords())
    return [token for token in tokens if token not in excluded]


def preprocess_for_baseline(text: str, *, remove_stopwords: bool = False) -> str:
    """Return space-delimited tokens suitable for TF-IDF."""
    return " ".join(
        tokenize_thai_text(text, remove_stopwords=remove_stopwords)
    )


def normalize_label(label: str) -> str:
    """Map Wisesight aliases to stable API labels."""
    normalized = str(label).strip().lower()
    try:
        return LABEL_ALIASES[normalized]
    except KeyError as exc:
        raise ValueError(f"unsupported label: {label}") from exc


def detect_topic(text: str) -> str:
    """Return the first matching topic from the documented rule taxonomy."""
    cleaned = clean_text(text)
    for topic, keywords in TOPIC_KEYWORDS.items():
        if any(keyword in cleaned for keyword in keywords):
            return topic
    return "other"
