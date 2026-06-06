# Data Source

## Wisesight Sentiment Corpus

The project uses the Wisesight Sentiment Corpus maintained by PyThaiNLP:

- Repository: <https://github.com/PyThaiNLP/wisesight-sentiment>
- License and attribution: follow the upstream repository.
- Labels observed on June 6, 2026: `positive`, `negative`, `neutral`, `question`.

PyThaiNLP 5.3.4 no longer exposes the historical
`pythainlp.corpus.wisesight_sentiment.get_texts/get_labels` accessor shown in the
original requirements. The loader attempts that API first for compatibility, then
downloads the equivalent official PyThaiNLP repository files.

## Observed Snapshot

| Label | Raw rows |
|---|---:|
| negative | 6,824 |
| neutral | 14,572 |
| positive | 4,778 |
| question | 575 |
| **Total** | **26,749** |

Validation removed three duplicate rows, producing 26,746 processed reviews.
Source and row count are stored in `data/raw/wisesight_source.json` when the loader
runs.

## Commands

```powershell
python -m src.data.load_wisesight
python -m src.data.validate_data
python -m src.data.eda
```

Raw and processed CSV files are intentionally ignored by Git. Recreate them using
the commands above.
