from src.evaluation.model_governance import build_governance_summary


def test_governance_selects_macro_f1_and_reports_each_class():
    summary = build_governance_summary()

    assert summary.selected_production_model == "logistic_regression"
    assert summary.selection_metric == "macro_f1"
    assert set(summary.per_class_metrics) == {"positive", "negative", "neutral", "question"}
    assert summary.human_review_threshold == 0.7
    assert "WangchanBERTa debug mode is not a benchmark" in summary.wangchanberta_status
    assert summary.low_confidence_review_count >= 0
