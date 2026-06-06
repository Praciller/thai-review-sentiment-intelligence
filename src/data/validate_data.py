"""Validate and preprocess the raw Wisesight dataset."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import pandas as pd

from src.features.preprocess_thai_text import (
    normalize_label,
    preprocess_for_baseline,
)

RAW_DATA_PATH = Path("data/raw/wisesight_raw.csv")
PROCESSED_DATA_PATH = Path("data/processed/wisesight_processed.csv")
VALIDATION_REPORT_PATH = Path("reports/data_validation_report.md")


def _markdown_table(series: pd.Series) -> str:
    lines = ["| Value | Count |", "|---|---:|"]
    lines.extend(f"| {index} | {int(value)} |" for index, value in series.items())
    return "\n".join(lines)


def _build_validation_report(
    summary: dict[str, Any],
    label_distribution: pd.Series,
    length_stats: pd.Series,
) -> str:
    return "\n".join(
        [
            "# Data Validation Report",
            "",
            "## Dataset size",
            "",
            f"- Input rows: {summary['input_rows']:,}",
            f"- Valid rows before duplicate removal: "
            f"{summary['valid_rows_before_duplicates']:,}",
            f"- Processed rows: {summary['processed_rows']:,}",
            "",
            "## Missing and invalid values",
            "",
            f"- Missing text: {summary['missing_text']:,}",
            f"- Missing label: {summary['missing_label']:,}",
            f"- Empty text: {summary['empty_text']:,}",
            f"- Duplicate rows: {summary['duplicate_rows']:,}",
            "",
            "## Label distribution",
            "",
            _markdown_table(label_distribution),
            "",
            "## Text length statistics",
            "",
            _markdown_table(length_stats.round(2)),
            "",
            "Text length is measured in Unicode characters after trimming.",
            "",
        ]
    )


def validate_dataset(
    frame: pd.DataFrame,
    *,
    processed_path: Path = PROCESSED_DATA_PATH,
    report_path: Path = VALIDATION_REPORT_PATH,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    required_columns = {"text", "label"}
    missing_columns = required_columns - set(frame.columns)
    if missing_columns:
        raise ValueError(
            f"missing required columns: {', '.join(sorted(missing_columns))}"
        )

    working = frame.loc[:, ["text", "label"]].copy()
    missing_text = int(working["text"].isna().sum())
    missing_label = int(working["label"].isna().sum())
    non_null_text = working["text"].dropna().astype(str).str.strip()
    empty_text = int(non_null_text.eq("").sum())

    valid_mask = (
        working["text"].notna()
        & working["label"].notna()
        & working["text"].astype(str).str.strip().ne("")
    )
    valid = working.loc[valid_mask].copy()
    valid["text"] = valid["text"].astype(str).str.strip()
    valid["label"] = valid["label"].map(normalize_label)

    duplicate_rows = int(valid.duplicated(subset=["text", "label"]).sum())
    valid_rows_before_duplicates = len(valid)
    processed = valid.drop_duplicates(subset=["text", "label"]).reset_index(
        drop=True
    )
    processed["cleaned_text"] = processed["text"].map(
        preprocess_for_baseline
    )
    processed["text_length"] = processed["text"].str.len()

    label_distribution = processed["label"].value_counts().sort_index()
    length_stats = processed["text_length"].describe()
    summary: dict[str, Any] = {
        "input_rows": len(working),
        "valid_rows_before_duplicates": valid_rows_before_duplicates,
        "processed_rows": len(processed),
        "missing_text": missing_text,
        "missing_label": missing_label,
        "empty_text": empty_text,
        "duplicate_rows": duplicate_rows,
        "label_distribution": label_distribution.to_dict(),
        "text_length_statistics": length_stats.to_dict(),
    }

    processed_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    processed.to_csv(processed_path, index=False)
    report_path.write_text(
        _build_validation_report(summary, label_distribution, length_stats),
        encoding="utf-8",
    )
    return processed, summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate and preprocess Wisesight data."
    )
    parser.add_argument("--input", type=Path, default=RAW_DATA_PATH)
    parser.add_argument("--output", type=Path, default=PROCESSED_DATA_PATH)
    parser.add_argument(
        "--report",
        type=Path,
        default=VALIDATION_REPORT_PATH,
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    frame = pd.read_csv(args.input)
    processed, summary = validate_dataset(
        frame,
        processed_path=args.output,
        report_path=args.report,
    )
    print(f"Saved {len(processed):,} processed rows to {args.output}")
    print(pd.Series(summary["label_distribution"]).sort_index().to_string())


if __name__ == "__main__":
    main()
