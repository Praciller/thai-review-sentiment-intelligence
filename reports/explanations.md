# Explanation Evidence

These explanations are approximate model/debug aids, not causal explanations.

## synthetic-positive

- Mode: `keyword_demo`
- Evidence terms: ดี, อร่อย, ประทับใจ
- Topic terms: บริการ
- Reason codes: none

## synthetic-neutral

- Mode: `keyword_demo`
- Evidence terms: none
- Topic terms: none
- Reason codes: low_confidence

## synthetic-negative

- Mode: `keyword_demo`
- Evidence terms: ช้า, เสีย, ไม่ดี
- Topic terms: ส่ง
- Reason codes: negative_sentiment, contains_waiting_time_issue, contains_delivery_issue

## synthetic-mixed

- Mode: `keyword_demo`
- Evidence terms: อร่อย, แพง, รอนาน
- Topic terms: แพง, ราคา
- Reason codes: low_confidence, negative_sentiment, possible_mixed_sentiment, contains_waiting_time_issue, contains_price_issue

## synthetic-complaint

- Mode: `keyword_demo`
- Evidence terms: ดี, ช้า
- Topic terms: ส่ง
- Reason codes: low_confidence, negative_sentiment, possible_mixed_sentiment, contains_waiting_time_issue, contains_delivery_issue

## synthetic-positive-complaint

- Mode: `keyword_demo`
- Evidence terms: ดี, อร่อย, ชอบ, ช้า
- Topic terms: ส่ง
- Reason codes: possible_mixed_sentiment, contains_waiting_time_issue, contains_delivery_issue

## synthetic-slang

- Mode: `keyword_demo`
- Evidence terms: ดี, ชอบ, คุ้ม
- Topic terms: คุ้ม
- Reason codes: contains_price_issue

## synthetic-code-switch

- Mode: `keyword_demo`
- Evidence terms: ดี, ชอบ
- Topic terms: none
- Reason codes: contains_delivery_issue

## synthetic-ambiguous

- Mode: `keyword_demo`
- Evidence terms: ดี, รอนาน
- Topic terms: รอนาน
- Reason codes: low_confidence, negative_sentiment, possible_mixed_sentiment, contains_waiting_time_issue

## synthetic-question

- Mode: `keyword_demo`
- Evidence terms: ไหม, กี่, ?
- Topic terms: ส่ง
- Reason codes: question_intent, contains_delivery_issue
