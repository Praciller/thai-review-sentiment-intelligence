# Thai Sentiment Robustness Challenge

This is a small, manually authored, synthetic diagnostic fixture. It is not a new benchmark and must not be used as training, hyperparameter tuning, or model-selection data.

## Methodology

- Frozen examples: 27
- Slices: negation, code_switching, conversational_slang, emoji_punctuation, question_like, mixed_sentiment, length_contrast, spelling_variation, defensible_sarcasm
- Provenance: manually authored synthetic Thai text; no scraped customer reviews and no private data.
- The selected production baseline is evaluated as currently built; no retraining, challenge-set tuning, or threshold selection is performed.
- Overall macro F1 uses all four contract labels. Per-slice macro F1 uses only labels present in that slice.

## Selected production baseline

- Model: `logistic_regression`
- Model version: `logistic_regression-c1d063649abc-seed42`
- Routing threshold: `0.55`

| Accuracy | Macro F1 |
|---:|---:|
| 0.6296 | 0.4867 |

## Deterministic demo predictor

- Model: `demo-rule-based`
- Model version: `demo-rules-v1`
- This result is separate demo evidence and is not a production baseline result.

| Accuracy | Macro F1 |
|---:|---:|
| 0.7037 | 0.7254 |

## Per-slice results

Per-slice figures are descriptive diagnostics on a tiny, intentionally non-representative fixture.

| Slice | N | Baseline accuracy | Baseline macro F1 | Demo accuracy | Demo macro F1 |
|---|---:|---:|---:|---:|---:|
| negation | 3 | 0.3333 | 0.1667 | 0.0000 | 0.0000 |
| code_switching | 3 | 1.0000 | 1.0000 | 0.6667 | 0.8333 |
| conversational_slang | 3 | 0.6667 | 0.5556 | 0.6667 | 0.5556 |
| emoji_punctuation | 3 | 0.6667 | 0.5556 | 0.6667 | 0.5556 |
| question_like | 3 | 0.3333 | 0.5000 | 1.0000 | 1.0000 |
| mixed_sentiment | 3 | 0.6667 | 0.8000 | 1.0000 | 1.0000 |
| length_contrast | 4 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| spelling_variation | 3 | 0.6667 | 0.5556 | 1.0000 | 1.0000 |
| defensible_sarcasm | 2 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |

## Confusion matrices

### logistic_regression

Rows are expected labels; columns are predicted labels.

| Expected \ Predicted | positive | negative | neutral | question |
|---|---:|---:|---:|---:|
| positive | 6 | 1 | 0 | 0 |
| negative | 3 | 10 | 0 | 0 |
| neutral | 1 | 3 | 0 | 0 |
| question | 0 | 0 | 2 | 1 |

### demo-rule-based

Rows are expected labels; columns are predicted labels.

| Expected \ Predicted | positive | negative | neutral | question |
|---|---:|---:|---:|---:|
| positive | 6 | 1 | 0 | 0 |
| negative | 3 | 8 | 2 | 0 |
| neutral | 1 | 1 | 2 | 0 |
| question | 0 | 0 | 0 | 3 |

## Low-confidence and review-routing behavior

### logistic_regression

- Review threshold: `0.55` (model score, not a calibrated probability)
- Low-confidence rows: 10/27 (37.0%)
- Routes: `auto_label`=8, `escalation_queue`=8, `human_review`=8, `support_workflow`=3

Rows routed away from `auto_label` are review/support evidence, not automatic business decisions.

| ID | Expected | Predicted | Route | Reason codes |
|---|---|---|---|---|
| TRS-NEG-01 | negative | negative | `escalation_queue` | negative_sentiment |
| TRS-NEG-02 | neutral | negative | `escalation_queue` | negative_sentiment |
| TRS-NEG-03 | positive | negative | `escalation_queue` | negative_sentiment, contains_waiting_time_issue, contains_delivery_issue |
| TRS-CODE-02 | negative | negative | `human_review` | low_model_score, negative_sentiment, contains_waiting_time_issue |
| TRS-CODE-03 | negative | negative | `escalation_queue` | negative_sentiment |
| TRS-SLANG-02 | negative | negative | `escalation_queue` | negative_sentiment |
| TRS-SLANG-03 | neutral | negative | `escalation_queue` | negative_sentiment |
| TRS-EMOJI-02 | negative | negative | `human_review` | low_model_score, negative_sentiment |
| TRS-EMOJI-03 | neutral | positive | `human_review` | low_model_score |
| TRS-QUESTION-01 | question | question | `support_workflow` | low_model_score, question_intent |
| TRS-QUESTION-02 | question | neutral | `support_workflow` | low_model_score, question_intent, contains_delivery_issue |
| TRS-QUESTION-03 | question | neutral | `support_workflow` | question_intent |
| … | | | | 7 more routed rows |

### demo-rule-based

- Review threshold: `0.55` (model score, not a calibrated probability)
- Low-confidence rows: 21/27 (77.8%)
- Routes: `auto_label`=3, `escalation_queue`=1, `human_review`=20, `support_workflow`=3

Rows routed away from `auto_label` are review/support evidence, not automatic business decisions.

| ID | Expected | Predicted | Route | Reason codes |
|---|---|---|---|---|
| TRS-NEG-01 | negative | positive | `human_review` | low_model_score |
| TRS-NEG-02 | neutral | negative | `human_review` | low_model_score, negative_sentiment |
| TRS-NEG-03 | positive | negative | `human_review` | low_model_score, negative_sentiment, contains_waiting_time_issue, contains_delivery_issue |
| TRS-CODE-02 | negative | negative | `escalation_queue` | negative_sentiment, contains_waiting_time_issue |
| TRS-CODE-03 | negative | neutral | `human_review` | low_model_score |
| TRS-SLANG-02 | negative | neutral | `human_review` | low_model_score |
| TRS-SLANG-03 | neutral | neutral | `human_review` | low_model_score |
| TRS-EMOJI-01 | positive | positive | `human_review` | low_model_score |
| TRS-EMOJI-02 | negative | negative | `human_review` | low_model_score, negative_sentiment |
| TRS-EMOJI-03 | neutral | positive | `human_review` | low_model_score |
| TRS-QUESTION-01 | question | question | `support_workflow` | low_model_score, question_intent |
| TRS-QUESTION-02 | question | question | `support_workflow` | question_intent, contains_delivery_issue |
| … | | | | 12 more routed rows |

## Representative failure examples

### logistic_regression

Misclassified rows: **10 of 27**.

The table shows the first 12 failures in frozen fixture order; the count above does not hide failures outside the table.

| ID | Expected | Predicted | Score | Route | Text | Ground-truth rationale |
|---|---|---|---:|---|---|---|
| TRS-NEG-02 | neutral | negative | 0.8598 | `escalation_queue` | ไม่ได้แย่ แต่ก็เฉยๆ ไม่มีอะไรพิเศษ | The negated negative phrase and explicit เฉยๆ indicate an unenthusiastic but neutral view. |
| TRS-NEG-03 | positive | negative | 0.6769 | `escalation_queue` | บริการไม่ได้ช้า ส่งตรงเวลามาก | Negation removes the potential complaint and the on-time delivery statement is positive. |
| TRS-SLANG-03 | neutral | negative | 0.6293 | `escalation_queue` | ก็โอเคอะ ไม่ได้ว้าว | The casual wording communicates acceptable but unremarkable sentiment. |
| TRS-EMOJI-03 | neutral | positive | 0.3868 | `human_review` | ได้รับของแล้ว... ก็ปกติดี 🙂 | The ellipsis and mild smile accompany a routine, explicitly normal outcome. |
| TRS-QUESTION-02 | question | neutral | 0.5401 | `support_workflow` | ส่งฟรีไหม??? | ไหม and repeated question marks make the request for information unambiguous. |
| TRS-QUESTION-03 | question | neutral | 0.5762 | `support_workflow` | มีไซซ์ใหญ่หรือเปล่า | หรือเปล่า marks a direct product-availability question without sentiment judgment. |
| TRS-MIXED-02 | negative | positive | 0.3862 | `human_review` | พนักงานบริการดี แต่ห้องน้ำสกปรก | A service compliment is paired with a concrete cleanliness complaint. |
| TRS-SPELL-03 | neutral | negative | 0.4769 | `human_review` | โอเคคค ไม่มีอะไรพิเศษ | The elongated spelling is informal, while the overall evaluation remains plainly unremarkable. |
| TRS-SARC-01 | negative | positive | 0.6084 | `auto_label` | ดีมาก รอแค่สามชั่วโมงเอง | The apparent praise is explicitly undercut by a three-hour wait; the negative label is defensible from the concrete complaint. |
| TRS-SARC-02 | negative | positive | 0.6035 | `auto_label` | ประทับใจสุดๆ ได้ของไม่ครบอีกแล้ว | The praise-like opener is contradicted by a missing-item complaint and อีกแล้ว, making the negative reading defensible. |

### demo-rule-based

Misclassified rows: **8 of 27**.

The table shows the first 12 failures in frozen fixture order; the count above does not hide failures outside the table.

| ID | Expected | Predicted | Score | Route | Text | Ground-truth rationale |
|---|---|---|---:|---|---|---|
| TRS-NEG-01 | negative | positive | 0.4754 | `human_review` | ไม่อร่อยเลย รสชาติจืดมาก | ไม่อร่อยเลย explicitly reverses the positive food-quality interpretation. |
| TRS-NEG-02 | neutral | negative | 0.4754 | `human_review` | ไม่ได้แย่ แต่ก็เฉยๆ ไม่มีอะไรพิเศษ | The negated negative phrase and explicit เฉยๆ indicate an unenthusiastic but neutral view. |
| TRS-NEG-03 | positive | negative | 0.4754 | `human_review` | บริการไม่ได้ช้า ส่งตรงเวลามาก | Negation removes the potential complaint and the on-time delivery statement is positive. |
| TRS-CODE-03 | negative | neutral | 0.2500 | `human_review` | สินค้าโอเคนะ แต่ support ไม่ตอบเลย | A mild positive acknowledgment is outweighed by the clear support failure. |
| TRS-SLANG-02 | negative | neutral | 0.2500 | `human_review` | ของพังจ้า ไม่ไหวละ | พัง and ไม่ไหวละ are common informal expressions of a clear failure. |
| TRS-EMOJI-03 | neutral | positive | 0.4754 | `human_review` | ได้รับของแล้ว... ก็ปกติดี 🙂 | The ellipsis and mild smile accompany a routine, explicitly normal outcome. |
| TRS-SARC-01 | negative | positive | 0.4754 | `human_review` | ดีมาก รอแค่สามชั่วโมงเอง | The apparent praise is explicitly undercut by a three-hour wait; the negative label is defensible from the concrete complaint. |
| TRS-SARC-02 | negative | positive | 0.4754 | `human_review` | ประทับใจสุดๆ ได้ของไม่ครบอีกแล้ว | The praise-like opener is contradicted by a missing-item complaint and อีกแล้ว, making the negative reading defensible. |

## Limitations

- The fixture is small, manually authored, and designed to expose specific linguistic slices; its scores are not population estimates.
- Ground truth for mixed and sarcasm-like text is judgment-based even where the rationale is deliberately conservative.
- Results can reflect vocabulary coverage and preprocessing behavior rather than broad Thai language competence.
- Routing uses the existing operational policy and model score; it is not a calibrated uncertainty estimate or a safety guarantee.
- Wisesight held-out evaluation remains the benchmark evidence for the selected model; this synthetic challenge is diagnostic evidence only.
