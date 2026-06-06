"""Generate practical error analysis from model prediction artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import pandas as pd

PREDICTIONS_PATH = Path("reports/baseline_predictions.csv")
BASELINE_METRICS_PATH = Path("reports/baseline_metrics.json")
ERROR_CSV_PATH = Path("reports/error_analysis.csv")
ERROR_REPORT_PATH = Path("reports/error_analysis.md")


def _select_model(
    predictions: pd.DataFrame,
    *,
    model_name: str | None,
    metrics_path: Path,
) -> pd.DataFrame:
    selected_name = model_name
    if selected_name is None and metrics_path.exists():
        payload = json.loads(metrics_path.read_text(encoding="utf-8"))
        selected_name = payload.get("best_model")
    if selected_name is None:
        selected_name = str(predictions["model_name"].iloc[0])

    selected = predictions.loc[
        predictions["model_name"] == selected_name
    ].copy()
    if selected.empty:
        raise ValueError(f"no predictions found for model: {selected_name}")
    return selected


def generate_error_analysis(
    predictions: pd.DataFrame,
    *,
    output_csv: Path = ERROR_CSV_PATH,
    report_path: Path = ERROR_REPORT_PATH,
) -> dict[str, Any]:
    required = {
        "text",
        "label",
        "predicted_label",
        "confidence",
        "text_length",
    }
    missing = required - set(predictions.columns)
    if missing:
        raise ValueError(f"missing required columns: {', '.join(sorted(missing))}")

    working = predictions.copy()
    working["is_error"] = working["label"] != working["predicted_label"]
    errors = working.loc[working["is_error"]].sort_values(
        "confidence",
        ascending=False,
    )
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    errors.drop(columns=["is_error"]).to_csv(output_csv, index=False)

    confused_pairs = (
        errors.groupby(["label", "predicted_label"])
        .size()
        .sort_values(ascending=False)
    )
    working["length_bucket"] = pd.cut(
        working["text_length"],
        bins=[-1, 25, 50, 100, 200, float("inf")],
        labels=["0-25", "26-50", "51-100", "101-200", "201+"],
    )
    length_errors = (
        working.groupby("length_bucket", observed=False)["is_error"]
        .agg(["sum", "count", "mean"])
        .reset_index()
    )

    lines = [
        "# Error Analysis",
        "",
        f"- Total predictions: {len(working):,}",
        f"- Misclassified: {len(errors):,}",
        f"- Error rate: {working['is_error'].mean():.1%}",
        "",
        "## Most confused label pairs",
        "",
        "| Actual | Predicted | Count |",
        "|---|---|---:|",
    ]
    if confused_pairs.empty:
        lines.append("| None | None | 0 |")
    else:
        lines.extend(
            f"| {actual} | {predicted} | {count} |"
            for (actual, predicted), count in confused_pairs.head(10).items()
        )

    lines.extend(
        [
            "",
            "## Error rate by text length",
            "",
            "| Characters | Errors | Reviews | Error rate |",
            "|---|---:|---:|---:|",
        ]
    )
    lines.extend(
        f"| {row.length_bucket} | {int(row.sum)} | {int(row.count)} | "
        f"{row.mean:.1%} |"
        for row in length_errors.itertuples(index=False)
    )

    lines.extend(["", "## Hard cases", ""])
    hard_cases = errors.sort_values("confidence", ascending=True).head(10)
    if hard_cases.empty:
        lines.append("No misclassified examples were found.")
    else:
        lines.extend(
            f"- `{row.label}` → `{row.predicted_label}` "
            f"({row.confidence:.1%}): {row.text}"
            for row in hard_cases.itertuples()
        )

    lines.extend(
        [
            "",
            "## Possible reasons",
            "",
            "- Thai slang and creative spelling create sparse or unseen tokens.",
            "- Mixed-sentiment reviews force one label onto multiple opinions.",
            "- Question and neutral messages can overlap when context is absent.",
            "- Sarcasm, omitted subjects, and external image context are not "
            "recoverable from text alone.",
            "- Short reviews provide little lexical evidence; very long reviews "
            "may contain conflicting sentiment.",
            "",
        ]
    )
    report_path.write_text("\n".join(lines), encoding="utf-8")
    return {
        "total_predictions": len(working),
        "misclassified": len(errors),
        "error_rate": float(working["is_error"].mean()),
        "confused_pairs": {
            f"{actual}->{predicted}": int(count)
            for (actual, predicted), count in confused_pairs.items()
        },
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Analyze sentiment model errors.")
    parser.add_argument("--predictions", type=Path, default=PREDICTIONS_PATH)
    parser.add_argument("--metrics", type=Path, default=BASELINE_METRICS_PATH)
    parser.add_argument("--model-name")
    parser.add_argument("--output-csv", type=Path, default=ERROR_CSV_PATH)
    parser.add_argument("--report", type=Path, default=ERROR_REPORT_PATH)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    predictions = pd.read_csv(args.predictions)
    selected = _select_model(
        predictions,
        model_name=args.model_name,
        metrics_path=args.metrics,
    )
    summary = generate_error_analysis(
        selected,
        output_csv=args.output_csv,
        report_path=args.report,
    )
    print(
        f"Saved {summary['misclassified']:,} errors "
        f"({summary['error_rate']:.1%})"
    )


if __name__ == "__main__":
    main()
