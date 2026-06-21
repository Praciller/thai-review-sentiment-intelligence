from pathlib import Path
import socket

import pytest

from scripts.generate_local_sentiment_report import build_report, load_fixtures
from src.models.predict import DemoPredictor


FIXTURES = Path("data/sample/synthetic_reviews.json")


def test_synthetic_review_report_is_deterministic_and_offline(monkeypatch):
    fixtures = load_fixtures(FIXTURES)

    def deny_network(*args, **kwargs):
        raise AssertionError("network access is forbidden in local review")

    monkeypatch.setattr(socket, "socket", deny_network)

    first = build_report(fixtures)
    second = build_report(fixtures)

    assert first == second
    assert all(row["expected_label"] == row["prediction"].predicted_label for row in first)
    assert {row["category"] for row in first} >= {
        "positive",
        "neutral",
        "negative",
        "mixed sentiment",
        "complaint with detail",
        "positive with complaint detail",
        "slang and informal Thai",
        "Thai-English mixed",
        "ambiguous or sarcastic",
    }
    assert all(row["normalized_text"] and row["tokens"] for row in first)


def test_demo_predictor_handles_very_short_thai_input():
    result = DemoPredictor().predict(["ดี"])[0]

    assert result.predicted_label == "positive"
    assert result.text == "ดี"


def test_local_review_rejects_missing_or_empty_fixture_files(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_fixtures(tmp_path / "missing.json")

    empty = tmp_path / "empty.json"
    empty.write_text("[]", encoding="utf-8")
    with pytest.raises(ValueError, match="at least one fixture"):
        load_fixtures(empty)
