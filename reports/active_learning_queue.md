# Synthetic Active-Learning Review Queue

This deterministic queue uses only repository sample data; it does not persist private reviews.

| Rank | Label | Confidence | Priority | Reason codes | Synthetic review |
|---:|---|---:|---:|---|---|
| 1 | negative | 0.366 | 8.345 | low_confidence, negative_sentiment, possible_mixed_sentiment, contains_waiting_time_issue, contains_delivery_issue, multiple_aspects | พนักงานพูดดีแต่ส่งช้าเกินหนึ่งชั่วโมง |
| 2 | negative | 0.366 | 7.345 | low_confidence, negative_sentiment, possible_mixed_sentiment, contains_waiting_time_issue | ดีมากเลย รอนานแค่สองชั่วโมงเอง |
| 3 | negative | 0.610 | 5.897 | low_confidence, negative_sentiment, possible_mixed_sentiment, contains_waiting_time_issue, contains_price_issue, multiple_aspects | อาหารอร่อยแต่รอนานและราคาแพง |
| 4 | neutral | 0.250 | 4.500 | low_confidence | ได้รับสินค้าแล้ว บรรจุภัณฑ์ปกติ |
| 5 | question | 0.870 | 3.500 | question_intent, contains_delivery_issue, rare_class_candidate | ร้านเปิดกี่โมง ส่งวันอาทิตย์ไหม? |
| 6 | negative | 0.810 | 3.000 | negative_sentiment, contains_waiting_time_issue, contains_delivery_issue, multiple_aspects | ส่งช้ามาก สินค้าเสียหาย บริการไม่ดี |
| 7 | positive | 0.810 | 3.000 | possible_mixed_sentiment, contains_waiting_time_issue, contains_delivery_issue, multiple_aspects | ส่งช้าไปนิดแต่อาหารอร่อยมาก บริการดี ชอบเลย |
| 8 | positive | 0.870 | 1.000 | multiple_aspects | อาหารอร่อยมาก บริการดี ประทับใจ |
