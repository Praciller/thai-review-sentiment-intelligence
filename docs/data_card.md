# Data Card

## Sources and Classification

| Data | Classification | Source and license |
|---|---|---|
| `data/sample/synthetic_reviews.json` | Synthetic | Manually authored for this repository; project MIT license |
| `data/sample/sample_reviews.csv` | Synthetic | Manually authored dashboard examples; project MIT license |
| Wisesight evaluation artifacts | Public | [PyThaiNLP Wisesight Sentiment](https://github.com/PyThaiNLP/wisesight-sentiment), CC0 1.0; accessed 2026-06-06 |

The default review uses only synthetic files. Downloaded raw and processed
Wisesight CSV files are ignored and are not required for offline review.

## Fields

Synthetic JSON rows contain `id`, `category`, `text`, and `expected_label`.
The dashboard CSV contains synthetic `id` and `text` fields. Public evaluation
reports contain labels, predictions, confidence data, and redacted text excerpts.

## Privacy and Safety

No real customer data is required. Do not add names, emails, phone numbers,
addresses, order identifiers, private exports, scraped private content, database
dumps, or credentials. Existing public-corpus report excerpts have email- and
phone-like sequences redacted. Notebooks are committed without outputs.

## Intended Use and Limitations

The data demonstrates Thai preprocessing, sentiment evaluation, aspect rules,
API behavior, and portfolio review. It is not representative of a specific
business population. Synthetic agreement is not model accuracy, and Wisesight
labels may not match a business taxonomy. Human review is required.
