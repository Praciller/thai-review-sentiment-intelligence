import json
import sys
from types import SimpleNamespace

import pytest

from src.data.dataset_paths import ensure_not_diagnostic_challenge
from src.evaluation.robustness_challenge import (
    ALLOWED_SLICES,
    CHALLENGE_DATASET_PATH,
    REQUIRED_FIELDS,
    evaluate_predictor,
    generate_report,
    load_challenge_dataset,
)
from src.models.predict import DemoPredictor
from src.models.train_baseline import (
    PROCESSED_DATA_PATH,
    build_parser,
)
from src.models.train_baseline import (
    main as baseline_main,
)
from src.models.train_transformer import PROCESSED_DATA_PATH as TRANSFORMER_INPUT
from src.models.train_transformer import main as transformer_main


def test_manual_challenge_fixture_has_reviewable_schema_and_contract():
    examples = load_challenge_dataset()

    assert len(examples) >= 20
    assert len({example.id for example in examples}) == len(examples)
    assert {example.expected_label for example in examples} == {
        "positive",
        "negative",
        "neutral",
        "question",
    }
    assert {example.slice for example in examples} == set(ALLOWED_SLICES)
    assert all(
        set(example.as_dict()) == REQUIRED_FIELDS
        and example.text.strip()
        and example.rationale.strip()
        for example in examples
    )


def test_challenge_fixture_rejects_duplicate_ids(tmp_path):
    valid = {
        "id": "one",
        "text": "ดี",
        "expected_label": "positive",
        "slice": "negation",
        "rationale": "Explicitly positive wording.",
    }
    invalid_path = tmp_path / "invalid.json"
    invalid_path.write_text(
        json.dumps([valid, {**valid, "slice": "unknown"}], ensure_ascii=False),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="duplicate id"):
        load_challenge_dataset(invalid_path)


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("expected_label", "unsupported", "unsupported label"),
        ("slice", "unknown", "unsupported slice"),
    ],
)
def test_challenge_fixture_rejects_unknown_contract_values(
    tmp_path,
    field,
    value,
    message,
):
    row = {
        "id": "one",
        "text": "ดี",
        "expected_label": "positive",
        "slice": "negation",
        "rationale": "Explicitly positive wording.",
    }
    row[field] = value
    invalid_path = tmp_path / f"invalid-{field}.json"
    invalid_path.write_text(
        json.dumps([row], ensure_ascii=False),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match=message):
        load_challenge_dataset(invalid_path)


def test_challenge_dataset_is_not_a_training_input():
    assert CHALLENGE_DATASET_PATH != PROCESSED_DATA_PATH
    assert CHALLENGE_DATASET_PATH != TRANSFORMER_INPUT
    assert build_parser().parse_args([]).input == PROCESSED_DATA_PATH
    with pytest.raises(ValueError, match="cannot be used for training"):
        ensure_not_diagnostic_challenge(CHALLENGE_DATASET_PATH)
    ensure_not_diagnostic_challenge(PROCESSED_DATA_PATH)


def test_training_entrypoints_reject_the_diagnostic_fixture(monkeypatch):
    for entrypoint, program in (
        (baseline_main, "train_baseline"),
        (transformer_main, "train_transformer"),
    ):
        monkeypatch.setattr(
            sys,
            "argv",
            [program, "--input", str(CHALLENGE_DATASET_PATH)],
        )
        with pytest.raises(ValueError, match="cannot be used for training"):
            entrypoint()


def test_evaluation_is_deterministic_and_reports_metrics_by_slice():
    examples = load_challenge_dataset()

    first = evaluate_predictor(DemoPredictor(), examples, review_threshold=0.55)
    second = evaluate_predictor(DemoPredictor(), examples, review_threshold=0.55)

    assert first == second
    assert first.metrics["labels"] == [
        "positive",
        "negative",
        "neutral",
        "question",
    ]
    assert sum(sum(row) for row in first.metrics["confusion_matrix"]) == len(examples)
    assert set(first.per_slice) == set(ALLOWED_SLICES)
    assert sum(first.per_slice[name]["count"] for name in first.per_slice) == len(
        examples
    )


class LowScorePredictor:
    model_name = "test-low-score"
    model_version = "test-v1"

    def predict(self, texts):
        return [
            SimpleNamespace(
                text=text,
                predicted_label="neutral",
                model_score=0.2,
                class_scores={
                    "positive": 0.2,
                    "negative": 0.2,
                    "neutral": 0.2,
                    "question": 0.2,
                },
                score_type="test_score",
                model_name=self.model_name,
                model_version=self.model_version,
                topic="other",
            )
            for text in texts
        ]


def test_low_confidence_predictions_route_to_human_review():
    example = load_challenge_dataset()[0]
    evaluation = evaluate_predictor(
        LowScorePredictor(), [example], review_threshold=0.55
    )

    assert evaluation.low_confidence_count == 1
    assert evaluation.rows[0].routing.route == "human_review"
    assert evaluation.rows[0].routing.requires_human_review is True
    assert {
        "low_model_score",
        "low_confidence",
    } & set(evaluation.rows[0].routing.reason_codes)


def test_report_generation_separates_demo_from_optional_baseline(tmp_path):
    output = tmp_path / "robustness_challenge.md"

    report = generate_report(
        report_path=output,
        baseline_model_path=None,
        include_demo=True,
    )

    assert output.read_text(encoding="utf-8") == report
    assert "# Thai Sentiment Robustness Challenge" in report
    assert "## Selected production baseline" in report
    assert "baseline was not evaluated" in report
    assert "## Deterministic demo predictor" in report
    assert "## Confusion matrices" in report
    assert "## Representative failure examples" in report
