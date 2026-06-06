import pandas as pd

from src.evaluation.metrics import compute_classification_metrics
from src.evaluation.error_analysis import generate_error_analysis
from src.models.train_baseline import (
    build_baseline_models,
    train_baseline_candidates,
)
from src.models.train_transformer import _debug_sample
from src.models.splitting import create_stratified_split
from src.utils.constants import SENTIMENT_LABELS


def make_balanced_frame(rows_per_label: int = 12) -> pd.DataFrame:
    rows = []
    for label in SENTIMENT_LABELS:
        for index in range(rows_per_label):
            rows.append(
                {
                    "text": f"{label} review {index}",
                    "label": label,
                    "cleaned_text": f"{label} review {index}",
                    "text_length": 10 + index,
                }
            )
    return pd.DataFrame(rows)


def test_create_stratified_split_is_deterministic_and_disjoint():
    frame = make_balanced_frame()

    first = create_stratified_split(frame, seed=42)
    second = create_stratified_split(frame, seed=42)

    assert first.equals(second)
    assert set(first["split"]) == {"train", "validation", "test"}
    assert first["row_id"].is_unique
    assert len(first) == len(frame)
    distribution = (
        first.join(frame["label"])
        .groupby(["split", "label"])
        .size()
        .unstack(fill_value=0)
    )
    assert (distribution > 0).all().all()


def test_create_stratified_split_changes_when_seed_changes():
    frame = make_balanced_frame()

    first = create_stratified_split(frame, seed=42)
    second = create_stratified_split(frame, seed=7)

    assert not first["split"].equals(second["split"])


def test_compute_classification_metrics_returns_required_schema():
    y_true = [
        "positive",
        "positive",
        "negative",
        "negative",
        "neutral",
        "neutral",
        "question",
        "question",
    ]
    y_pred = [
        "positive",
        "neutral",
        "negative",
        "negative",
        "neutral",
        "question",
        "question",
        "question",
    ]

    metrics = compute_classification_metrics(y_true, y_pred)

    assert set(metrics) == {
        "accuracy",
        "precision",
        "recall",
        "macro_f1",
        "weighted_f1",
        "confusion_matrix",
        "labels",
    }
    assert metrics["accuracy"] == 0.75
    assert len(metrics["confusion_matrix"]) == 4
    assert metrics["labels"] == list(SENTIMENT_LABELS)


def test_train_baseline_candidates_trains_both_required_models():
    frame = make_balanced_frame(rows_per_label=16)
    manifest = create_stratified_split(frame, seed=42)
    prepared = frame.copy()
    prepared["cleaned_text"] = (
        prepared["label"] + " " + prepared.index.astype(str)
    )
    prepared.loc[0, "cleaned_text"] = None

    results = train_baseline_candidates(prepared, manifest, seed=42)

    assert set(results) == {"logistic_regression", "linear_svm"}
    for result in results.values():
        assert result.metrics["labels"] == list(SENTIMENT_LABELS)
        assert len(result.predictions) == int(
            (manifest["split"] == "test").sum()
        )
        probability_columns = [
            f"probability_{label}" for label in SENTIMENT_LABELS
        ]
        assert result.predictions[probability_columns].sum(axis=1).round(6).eq(
            1.0
        ).all()


def test_baseline_vectorizer_preserves_presegmented_thai_tokens():
    pipeline = build_baseline_models(seed=42)["logistic_regression"]
    vectorizer = pipeline.named_steps["tfidf"]
    text = "ส่ง เร็ว แพ็ก ของ เรียบร้อย"

    vectorizer.fit([text])

    assert set(vectorizer.get_feature_names_out()) >= {
        "ส่ง",
        "เร็ว",
        "แพ็ก",
        "เรียบร้อย",
        "ส่ง เร็ว",
    }


def test_generate_error_analysis_saves_misclassified_rows_and_markdown(tmp_path):
    predictions = pd.DataFrame(
        {
            "text": ["ดีมาก", "แย่มาก", "เปิดกี่โมง", "ข้อมูลทั่วไป"],
            "label": ["positive", "negative", "question", "neutral"],
            "predicted_label": [
                "positive",
                "neutral",
                "neutral",
                "positive",
            ],
            "confidence": [0.91, 0.61, 0.55, 0.52],
            "text_length": [6, 7, 10, 12],
            "model_name": ["linear_svm"] * 4,
        }
    )
    csv_path = tmp_path / "errors.csv"
    report_path = tmp_path / "errors.md"

    summary = generate_error_analysis(
        predictions,
        output_csv=csv_path,
        report_path=report_path,
    )

    assert summary["total_predictions"] == 4
    assert summary["misclassified"] == 3
    errors = pd.read_csv(csv_path)
    assert len(errors) == 3
    report = report_path.read_text(encoding="utf-8")
    assert "Most confused label pairs" in report
    assert "Error rate by text length" in report
    assert "Possible reasons" in report


def test_transformer_debug_sample_preserves_split_and_label_columns():
    frame = make_balanced_frame(rows_per_label=12)
    manifest = create_stratified_split(frame, seed=42)
    prepared = frame.copy()
    prepared.insert(0, "row_id", range(len(prepared)))
    prepared = prepared.merge(manifest, on="row_id", validate="one_to_one")

    sampled = _debug_sample(prepared, seed=42)

    assert {"split", "label", "text"}.issubset(sampled.columns)
    assert (
        sampled.groupby(["split", "label"]).size().le(8).all()
    )
