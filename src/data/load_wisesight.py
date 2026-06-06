"""Load the Wisesight Sentiment Corpus into a stable tabular contract."""

from __future__ import annotations

import argparse
import importlib
import json
from collections.abc import Callable, Sequence
from pathlib import Path
from urllib.request import Request, urlopen

import pandas as pd

from src.features.preprocess_thai_text import normalize_label

CorpusFetcher = Callable[[], tuple[Sequence[str], Sequence[str], str]]

RAW_DATA_PATH = Path("data/raw/wisesight_raw.csv")
SOURCE_METADATA_PATH = Path("data/raw/wisesight_source.json")
OFFICIAL_REPOSITORY_BASE = (
    "https://raw.githubusercontent.com/PyThaiNLP/"
    "wisesight-sentiment/c1d063649abc3a6870b5fd1aae26cd1c64bdde7b"
)
REPOSITORY_LABEL_FILES = {
    "pos": "pos.txt",
    "neg": "neg.txt",
    "neu": "neu.txt",
    "q": "q.txt",
}


def _load_from_historical_accessor() -> tuple[list[str], list[str], str] | None:
    try:
        module = importlib.import_module(
            "pythainlp.corpus.wisesight_sentiment"
        )
    except ModuleNotFoundError:
        return None

    get_texts = getattr(module, "get_texts", None)
    get_labels = getattr(module, "get_labels", None)
    if not callable(get_texts) or not callable(get_labels):
        return None

    return (
        list(get_texts()),
        list(get_labels()),
        "pythainlp.corpus.wisesight_sentiment",
    )


def _download_text_lines(url: str) -> list[str]:
    request = Request(url, headers={"User-Agent": "thai-review-intelligence/0.1"})
    with urlopen(request, timeout=60) as response:
        body = response.read().decode("utf-8-sig")
    return [line.strip() for line in body.splitlines() if line.strip()]


def _load_from_official_repository() -> tuple[list[str], list[str], str]:
    texts: list[str] = []
    labels: list[str] = []
    for label, filename in REPOSITORY_LABEL_FILES.items():
        label_texts = _download_text_lines(
            f"{OFFICIAL_REPOSITORY_BASE}/{filename}"
        )
        texts.extend(label_texts)
        labels.extend([label] * len(label_texts))
    return texts, labels, "github.com/PyThaiNLP/wisesight-sentiment"


def fetch_wisesight_corpus() -> tuple[list[str], list[str], str]:
    historical_result = _load_from_historical_accessor()
    if historical_result is not None:
        return historical_result
    return _load_from_official_repository()


def load_wisesight_dataframe(
    *,
    fetcher: CorpusFetcher | None = None,
) -> tuple[pd.DataFrame, str]:
    resolved_fetcher = fetcher or fetch_wisesight_corpus
    texts, labels, source = resolved_fetcher()

    if len(texts) != len(labels):
        raise ValueError(
            f"corpus text/label length mismatch: {len(texts)} != {len(labels)}"
        )
    if not texts:
        raise ValueError("corpus is empty")

    frame = pd.DataFrame(
        {
            "text": [str(text) for text in texts],
            "label": [normalize_label(label) for label in labels],
        }
    )
    return frame, source


def save_raw_dataset(frame: pd.DataFrame, output_path: Path = RAW_DATA_PATH) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    frame.loc[:, ["text", "label"]].to_csv(output_path, index=False)


def save_source_metadata(
    *,
    source: str,
    row_count: int,
    output_path: Path = SOURCE_METADATA_PATH,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(
            {"source": source, "row_count": row_count},
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Load the Wisesight Sentiment Corpus."
    )
    parser.add_argument("--output", type=Path, default=RAW_DATA_PATH)
    parser.add_argument(
        "--metadata-output",
        type=Path,
        default=SOURCE_METADATA_PATH,
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    frame, source = load_wisesight_dataframe()
    save_raw_dataset(frame, args.output)
    save_source_metadata(
        source=source,
        row_count=len(frame),
        output_path=args.metadata_output,
    )
    print(f"Saved {len(frame):,} rows from {source} to {args.output}")
    print(frame["label"].value_counts().sort_index().to_string())


if __name__ == "__main__":
    main()
