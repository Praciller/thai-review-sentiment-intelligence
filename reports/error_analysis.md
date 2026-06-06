# Error Analysis

- Total predictions: 4,012
- Misclassified: 1,378
- Error rate: 34.3%

## Most confused label pairs

| Actual | Predicted | Count |
|---|---|---:|
| neutral | positive | 345 |
| neutral | negative | 325 |
| positive | neutral | 225 |
| negative | neutral | 151 |
| neutral | question | 120 |
| positive | negative | 92 |
| negative | positive | 59 |
| question | neutral | 24 |
| positive | question | 13 |
| negative | question | 11 |

## Error rate by text length

| Characters | Errors | Reviews | Error rate |
|---|---:|---:|---:|
| 0-25 | 609 | 1441 | 42.3% |
| 26-50 | 316 | 877 | 36.0% |
| 51-100 | 218 | 727 | 30.0% |
| 101-200 | 128 | 509 | 25.1% |
| 201+ | 107 | 458 | 23.4% |

## Hard cases

- `neutral` → `negative` (28.5%): อ้าวบาบิก้อน เราอายุเท่ากันหรือนี้
- `neutral` → `negative` (29.4%): เซรั่มน้ำนมเข้มข้น ตอบโจทย์ทุกปัญหาผิว 💯 #DrJiLL อัดแน่นด้วยสารสกัด #5EGF #เหมาะกับทุกสภาพผิว 😎✨จะผิวแบบไหนก็ใช้ได้ !! ✔ผิวผสม ✔ผิวแห้ง ✔ผิวมัน ✔ผิวแพ้ง่าย #DrJiLLG5Essence เซรั่มของคุณหมอ ขวดเดียว จบทุกปัญหาผิว 💫
- `negative` → `positive` (29.6%): ใช้นาวารา มา 4 ปี ไมวิ่ง 110000 นิดๆ เทอร์เบอร์พังแล้วเมื่อวานนี้ ทำไมเทอร์โบนาวารามันกากจังครับ
- `neutral` → `question` (30.0%): ลด 20%
- `neutral` → `positive` (30.0%): มีกี่ใบอ่ะ
- `neutral` → `positive` (30.8%): ขอจองน้ำซุปต้มยำ
- `positive` → `neutral` (31.4%): แบบนี้ปะละ หรือไรดี คิด
- `negative` → `question` (31.7%): คุ้มค่าเช่าชุดมั้ย
- `question` → `positive` (31.9%): วันนี้มีของรึยัง
- `neutral` → `positive` (32.1%): มิสซูกับนิสัน คือกลุ่ม RenaULT nissan ครับ

## Possible reasons

- Thai slang and creative spelling create sparse or unseen tokens.
- Mixed-sentiment reviews force one label onto multiple opinions.
- Question and neutral messages can overlap when context is absent.
- Sarcasm, omitted subjects, and external image context are not recoverable from text alone.
- Short reviews provide little lexical evidence; very long reviews may contain conflicting sentiment.
