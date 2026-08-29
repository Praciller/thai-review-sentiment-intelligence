"""Named dataset paths and safeguards for training inputs."""

from __future__ import annotations

from pathlib import Path

DIAGNOSTIC_CHALLENGE_DATASET_PATH = Path(
    "data/challenges/thai_sentiment_robustness.json"
)


def ensure_not_diagnostic_challenge(path: Path) -> None:
    """Prevent the frozen diagnostic fixture from becoming training data."""
    if Path(path).resolve() == DIAGNOSTIC_CHALLENGE_DATASET_PATH.resolve():
        raise ValueError(
            "the diagnostic robustness challenge dataset cannot be used for training"
        )
