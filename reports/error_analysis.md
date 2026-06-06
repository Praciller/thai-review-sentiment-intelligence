# Error Analysis

- Total predictions: 4,012
- Misclassified: 1,386
- Error rate: 34.5%

## Most confused label pairs

| Actual | Predicted | Count |
|---|---|---:|
| neutral | positive | 348 |
| neutral | negative | 346 |
| positive | neutral | 225 |
| negative | neutral | 153 |
| neutral | question | 118 |
| positive | negative | 73 |
| negative | positive | 57 |
| question | neutral | 24 |
| negative | question | 16 |
| positive | question | 15 |

## Error rate by text length

| Characters | Errors | Reviews | Error rate |
|---|---:|---:|---:|
| 0-25 | 596 | 1441 | 41.4% |
| 26-50 | 329 | 877 | 37.5% |
| 51-100 | 223 | 727 | 30.7% |
| 101-200 | 126 | 509 | 24.8% |
| 201+ | 112 | 458 | 24.5% |

## Hard cases

- `neutral` → `positive` (28.9%): ขอจองน้ำซุปต้มยำ
- `positive` → `negative` (29.0%): หน้าใครกันน้า..ที่นุ่มเด้งแบบเจลลี่?!? ก็หน้าซิสนี่แหละค่ะ เพราะอะไรหรอคะ ก็เพราะ การ์นิเย่ ซากุระ ไวท์ อควา เจลลี่ เอสเซนส์ ที่บันดาลให้หน้านุ่ม เด้ง ฉ่ำน้ำ อมชมพู ดุจกลีบดอกซากุระ ไม่เชื่อลองดิ ลองเลย แล้วจะรู้ว่าแก้มนุ่มเด้งกว่าเจลลี่เนี่ยมันเรื่องจริง!
- `neutral` → `positive` (29.6%): นิสสัน นี่น่าห่วงนะครับ
- `negative` → `positive` (30.0%): ใช้นาวารา มา 4 ปี ไมวิ่ง 110000 นิดๆ เทอร์เบอร์พังแล้วเมื่อวานนี้ ทำไมเทอร์โบนาวารามันกากจังครับ
- `negative` → `neutral` (30.3%): ถ้าเรามีบุหร่ไฟฟ้า...เราต้องพกใบกำกับภาษีก้วยใช่ไหมค่ะ
- `negative` → `neutral` (30.7%): ที่เปิดให้จองไว้ป่านนี้ยังไม่ได้ และยังเก็บค่าส่งด้วย แล้วทำไมซื้อที่ยังร้านมีส่วนลดอีก หมายความว่าไงค่ะ
- `neutral` → `negative` (30.8%): ใกล้สิ้นปีตำรวจเขาจะขยันหน่อยครับทำยอด
- `neutral` → `question` (31.1%): นาวาร่า7.9
- `neutral` → `negative` (31.1%): พรบ.คู่ชีวิตไทยนี่ถึงไหนแล้วคะ ไต้หวันไปไกลแล้วนะ............ 🤔
- `neutral` → `positive` (31.1%): หัวหน้ามาเฟีย สันต์ ปิดร้านเช้าสักวันไหม

## Possible reasons

- Thai slang and creative spelling create sparse or unseen tokens.
- Mixed-sentiment reviews force one label onto multiple opinions.
- Question and neutral messages can overlap when context is absent.
- Sarcasm, omitted subjects, and external image context are not recoverable from text alone.
- Short reviews provide little lexical evidence; very long reviews may contain conflicting sentiment.
