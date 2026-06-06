from pathlib import Path

import pandas as pd

from src.data.eda import generate_eda_artifacts
from src.data.load_wisesight import load_wisesight_dataframe, save_raw_dataset
from src.data.validate_data import validate_dataset


def fake_corpus_fetcher():
    return (
        [
            "อาหารอร่อยมาก",
            "บริการช้ามาก",
            "เปิดกี่โมง",
            "ข่าวทั่วไป",
        ],
        ["pos", "neg", "q", "neu"],
        "test-fixture",
    )


def test_load_wisesight_dataframe_normalizes_labels_and_saves_raw_csv(tmp_path):
    frame, source = load_wisesight_dataframe(fetcher=fake_corpus_fetcher)
    output_path = tmp_path / "raw" / "wisesight_raw.csv"

    save_raw_dataset(frame, output_path)

    assert source == "test-fixture"
    assert frame.to_dict("records") == [
        {"text": "อาหารอร่อยมาก", "label": "positive"},
        {"text": "บริการช้ามาก", "label": "negative"},
        {"text": "เปิดกี่โมง", "label": "question"},
        {"text": "ข่าวทั่วไป", "label": "neutral"},
    ]
    assert pd.read_csv(output_path).shape == (4, 2)


def test_validate_dataset_removes_invalid_rows_and_reports_duplicates(tmp_path):
    frame = pd.DataFrame(
        {
            "text": [
                "อาหารอร่อยมาก",
                "อาหารอร่อยมาก",
                "   ",
                None,
                "บริการช้ามาก",
                "เปิดกี่โมง",
            ],
            "label": ["positive", "positive", "neutral", "negative", None, "q"],
        }
    )
    processed_path = tmp_path / "processed.csv"
    report_path = tmp_path / "validation.md"

    processed, summary = validate_dataset(
        frame,
        processed_path=processed_path,
        report_path=report_path,
    )

    assert list(processed.columns) == [
        "text",
        "label",
        "cleaned_text",
        "text_length",
    ]
    assert processed[["text", "label"]].to_dict("records") == [
        {"text": "อาหารอร่อยมาก", "label": "positive"},
        {"text": "เปิดกี่โมง", "label": "question"},
    ]
    assert summary["input_rows"] == 6
    assert summary["missing_text"] == 1
    assert summary["missing_label"] == 1
    assert summary["empty_text"] == 1
    assert summary["duplicate_rows"] == 1
    assert Path(processed_path).exists()
    report = report_path.read_text(encoding="utf-8")
    assert "# Data Validation Report" in report
    assert "Label distribution" in report
    assert "Text length statistics" in report


def test_generate_eda_artifacts_writes_summary_and_required_figures(tmp_path):
    frame = pd.DataFrame(
        {
            "text": [
                "อาหารอร่อยมาก",
                "บริการดี",
                "รอนานเกินไป",
                "เปิดกี่โมง",
                "ข้อมูลทั่วไป",
                "ราคาแพง",
                "สะอาดมาก",
                "ส่งช้า",
            ],
            "label": [
                "positive",
                "positive",
                "negative",
                "question",
                "neutral",
                "negative",
                "positive",
                "negative",
            ],
            "cleaned_text": [
                "อาหาร อร่อย มาก",
                "บริการ ดี",
                "รอ นาน เกิน ไป",
                "เปิด กี่ โมง",
                "ข้อมูล ทั่วไป",
                "ราคา แพง",
                "สะอาด มาก",
                "ส่ง ช้า",
            ],
            "text_length": [15, 9, 12, 10, 12, 8, 9, 7],
        }
    )
    report_path = tmp_path / "eda_summary.md"
    figures_dir = tmp_path / "figures"

    summary = generate_eda_artifacts(
        frame,
        report_path=report_path,
        figures_dir=figures_dir,
        examples_per_label=1,
    )

    assert summary["total_reviews"] == 8
    assert summary["label_count"] == 4
    assert report_path.exists()
    assert (figures_dir / "label_distribution.png").exists()
    assert (figures_dir / "text_length_distribution.png").exists()
    report = report_path.read_text(encoding="utf-8")
    assert "Class imbalance" in report
    assert "Frequent Thai tokens" in report
