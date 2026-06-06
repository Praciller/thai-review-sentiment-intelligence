import pytest

from src.features.preprocess_thai_text import (
    clean_text,
    detect_topic,
    normalize_label,
    preprocess_for_baseline,
)


def test_clean_text_normalizes_url_whitespace_and_repeated_thai_characters():
    raw = "  ดีมากกกก   ดูเพิ่มที่ https://example.com/review  "

    assert clean_text(raw) == "ดีมากก ดูเพิ่มที่"


def test_clean_text_rejects_non_string_values():
    with pytest.raises(TypeError, match="text must be a string"):
        clean_text(None)  # type: ignore[arg-type]


def test_preprocess_for_baseline_returns_space_delimited_thai_tokens():
    processed = preprocess_for_baseline("อาหารอร่อยมาก บริการดี")

    assert "อาหาร" in processed
    assert "อร่อย" in processed
    assert "บริการ" in processed
    assert " " in processed


@pytest.mark.parametrize(
    ("raw_label", "expected"),
    [
        ("pos", "positive"),
        ("positive", "positive"),
        ("neg", "negative"),
        ("neu", "neutral"),
        ("q", "question"),
    ],
)
def test_normalize_label_maps_wisesight_aliases(raw_label, expected):
    assert normalize_label(raw_label) == expected


def test_normalize_label_rejects_unknown_values():
    with pytest.raises(ValueError, match="unsupported label"):
        normalize_label("mixed")


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("ราคาแพงไปหน่อยแต่คุณภาพดี", "price"),
        ("รอนานมาก คิวไม่ขยับ", "waiting_time"),
        ("พนักงานบริการดีมาก", "service"),
        ("อาหารอร่อย รสชาติดี", "taste"),
        ("โต๊ะสกปรก ไม่สะอาด", "cleanliness"),
        ("ไรเดอร์ส่งช้ามาก", "delivery"),
        ("สินค้าคุณภาพดี ใช้งานง่าย", "product_quality"),
        ("กลับมาซื้ออีกแน่นอน", "other"),
    ],
)
def test_detect_topic_uses_explicit_rule_based_taxonomy(text, expected):
    assert detect_topic(text) == expected
