"""Shared deterministic stratified split manifest."""

from __future__ import annotations

import pandas as pd
from sklearn.model_selection import train_test_split


def create_stratified_split(
    frame: pd.DataFrame,
    *,
    seed: int,
    validation_size: float = 0.15,
    test_size: float = 0.15,
) -> pd.DataFrame:
    if "label" not in frame:
        raise ValueError("frame must contain a label column")
    if validation_size <= 0 or test_size <= 0:
        raise ValueError("validation_size and test_size must be positive")
    if validation_size + test_size >= 1:
        raise ValueError("validation_size + test_size must be less than 1")

    labels = frame["label"].reset_index(drop=True)
    row_ids = pd.Series(range(len(frame)), name="row_id")
    holdout_size = validation_size + test_size
    train_ids, holdout_ids = train_test_split(
        row_ids,
        test_size=holdout_size,
        random_state=seed,
        stratify=labels,
    )
    relative_test_size = test_size / holdout_size
    validation_ids, test_ids = train_test_split(
        holdout_ids,
        test_size=relative_test_size,
        random_state=seed,
        stratify=labels.iloc[holdout_ids.to_numpy()],
    )

    split_by_id = {
        **{int(row_id): "train" for row_id in train_ids},
        **{int(row_id): "validation" for row_id in validation_ids},
        **{int(row_id): "test" for row_id in test_ids},
    }
    return pd.DataFrame(
        {
            "row_id": row_ids,
            "split": row_ids.map(split_by_id),
        }
    )


def apply_split_manifest(
    frame: pd.DataFrame,
    manifest: pd.DataFrame,
) -> pd.DataFrame:
    expected_ids = set(range(len(frame)))
    manifest_ids = set(manifest["row_id"].astype(int))
    if manifest_ids != expected_ids:
        raise ValueError("split manifest row ids do not match dataset")

    working = frame.reset_index(drop=True).copy()
    working.insert(0, "row_id", range(len(working)))
    return working.merge(
        manifest.loc[:, ["row_id", "split"]],
        on="row_id",
        validate="one_to_one",
    )
