"""Generate reproducible exploratory analysis artifacts."""

from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path
from typing import Any

import matplotlib
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt

PROCESSED_DATA_PATH = Path("data/processed/wisesight_processed.csv")
EDA_REPORT_PATH = Path("reports/eda_summary.md")
FIGURES_DIR = Path("reports/figures")

LABEL_COLORS = {
    "positive": "#2E7D32",
    "negative": "#C0392B",
    "neutral": "#607086",
    "question": "#355C8A",
}


def _save_label_distribution(frame: pd.DataFrame, path: Path) -> None:
    counts = frame["label"].value_counts().sort_index()
    colors = [LABEL_COLORS.get(label, "#607086") for label in counts.index]
    figure, axis = plt.subplots(figsize=(8, 5))
    counts.plot(kind="bar", ax=axis, color=colors)
    axis.set_title("Wisesight sentiment label distribution")
    axis.set_xlabel("Label")
    axis.set_ylabel("Reviews")
    axis.tick_params(axis="x", rotation=0)
    figure.tight_layout()
    figure.savefig(path, dpi=160)
    plt.close(figure)


def _save_text_length_distribution(frame: pd.DataFrame, path: Path) -> None:
    figure, axis = plt.subplots(figsize=(8, 5))
    axis.hist(frame["text_length"], bins=30, color="#0F2D52", alpha=0.85)
    axis.set_title("Thai review text length distribution")
    axis.set_xlabel("Unicode characters")
    axis.set_ylabel("Reviews")
    figure.tight_layout()
    figure.savefig(path, dpi=160)
    plt.close(figure)


def _top_tokens(frame: pd.DataFrame, limit: int = 20) -> list[tuple[str, int]]:
    counter: Counter[str] = Counter()
    for cleaned_text in frame["cleaned_text"].fillna("").astype(str):
        counter.update(
            token for token in cleaned_text.split() if len(token) > 1
        )
    return counter.most_common(limit)


def _examples_section(
    frame: pd.DataFrame,
    examples_per_label: int,
) -> list[str]:
    lines: list[str] = []
    for label in sorted(frame["label"].unique()):
        lines.extend([f"### {label}", ""])
        examples = frame.loc[frame["label"] == label, "text"].head(
            examples_per_label
        )
        lines.extend(f"- {text}" for text in examples)
        lines.append("")
    return lines


def generate_eda_artifacts(
    frame: pd.DataFrame,
    *,
    report_path: Path = EDA_REPORT_PATH,
    figures_dir: Path = FIGURES_DIR,
    examples_per_label: int = 3,
) -> dict[str, Any]:
    required = {"text", "label", "cleaned_text", "text_length"}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"missing required columns: {', '.join(sorted(missing))}")

    figures_dir.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    _save_label_distribution(
        frame,
        figures_dir / "label_distribution.png",
    )
    _save_text_length_distribution(
        frame,
        figures_dir / "text_length_distribution.png",
    )

    counts = frame["label"].value_counts().sort_values(ascending=False)
    averages = frame.groupby("label")["text_length"].mean().sort_index()
    imbalance_ratio = float(counts.max() / counts.min()) if counts.min() else 0.0
    top_tokens = _top_tokens(frame)

    lines = [
        "# Exploratory Data Analysis Summary",
        "",
        f"- Total reviews: {len(frame):,}",
        f"- Number of labels: {frame['label'].nunique()}",
        "",
        "## Label distribution",
        "",
        "| Label | Reviews | Share |",
        "|---|---:|---:|",
    ]
    lines.extend(
        f"| {label} | {count:,} | {count / len(frame):.1%} |"
        for label, count in counts.items()
    )
    lines.extend(
        [
            "",
            "## Average text length per label",
            "",
            "| Label | Average characters |",
            "|---|---:|",
        ]
    )
    lines.extend(
        f"| {label} | {average:.1f} |"
        for label, average in averages.items()
    )
    lines.extend(
        [
            "",
            "## Class imbalance",
            "",
            f"The largest class is {imbalance_ratio:.2f} times the smallest "
            "class. Macro F1 is therefore a required model-selection metric.",
            "",
            "## Frequent Thai tokens",
            "",
            "| Token | Count |",
            "|---|---:|",
        ]
    )
    lines.extend(f"| {token} | {count} |" for token, count in top_tokens)
    lines.extend(["", "## Example reviews per label", ""])
    lines.extend(_examples_section(frame, examples_per_label))
    lines.extend(
        [
            "## Figures",
            "",
            "- `reports/figures/label_distribution.png`",
            "- `reports/figures/text_length_distribution.png`",
            "",
        ]
    )
    report_path.write_text("\n".join(lines), encoding="utf-8")

    return {
        "total_reviews": len(frame),
        "label_count": int(frame["label"].nunique()),
        "label_distribution": counts.to_dict(),
        "average_text_length": averages.to_dict(),
        "class_imbalance_ratio": imbalance_ratio,
        "top_tokens": top_tokens,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate Wisesight EDA artifacts.")
    parser.add_argument("--input", type=Path, default=PROCESSED_DATA_PATH)
    parser.add_argument("--report", type=Path, default=EDA_REPORT_PATH)
    parser.add_argument("--figures-dir", type=Path, default=FIGURES_DIR)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    frame = pd.read_csv(args.input)
    summary = generate_eda_artifacts(
        frame,
        report_path=args.report,
        figures_dir=args.figures_dir,
    )
    print(
        f"Generated EDA for {summary['total_reviews']:,} reviews "
        f"across {summary['label_count']} labels"
    )


if __name__ == "__main__":
    main()
