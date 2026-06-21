# Model Methodology

## Preprocessing

`clean_text` applies PyThaiNLP Unicode normalization, removes URLs, collapses
whitespace, and caps repeated Thai characters. `newmm` tokenization produces
space-delimited tokens. TF-IDF consumes those tokens with `str.split` so Thai
combining marks are not split again.

## Sentiment Methods

The zero-cost review uses a deterministic keyword baseline with four labels:
positive, negative, neutral, and question. Negative evidence wins a positive tie;
question markers are routed separately. Its score is a normalized rule score,
not a calibrated probability.

The evaluated ML baseline uses word unigram/bigram TF-IDF with class-balanced
Logistic Regression. A calibrated Linear SVM is compared on the same seed-42
stratified split. Logistic Regression was selected by macro F1: 0.5731 on the
documented Wisesight test split. See `reports/baseline_classification_report.md`
and `reports/model_comparison.md`; these figures do not establish performance on
new business data.

## Aspect Extraction

`detect_topic` selects the first matching keyword group for price, delivery,
waiting time, service, taste, cleanliness, or product quality. The local report
lists matched aspect terms so the explanation is inspectable.

## Evaluation and Limitations

The local report checks deterministic behavior on synthetic fixtures covering
positive, neutral, negative, mixed, detailed complaint, informal, Thai-English,
ambiguous, and question text. This is regression evidence, not an accuracy
benchmark. The public-corpus model report uses accuracy, macro precision/recall,
macro F1, weighted F1, and a confusion matrix.

Thai negation, sarcasm, creative spelling, new slang, code-switching, and mixed
sentiment remain difficult. One label and one rule-based aspect cannot represent
all meanings in a review. Human review is required for real decisions.
