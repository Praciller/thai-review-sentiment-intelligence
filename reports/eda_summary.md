# Exploratory Data Analysis Summary

- Total reviews: 26,746
- Number of labels: 4

## Label distribution

| Label | Reviews | Share |
|---|---:|---:|
| neutral | 14,569 | 54.5% |
| negative | 6,824 | 25.5% |
| positive | 4,778 | 17.9% |
| question | 575 | 2.1% |

## Average text length per label

| Label | Average characters |
|---|---:|
| negative | 86.9 |
| neutral | 103.3 |
| positive | 58.1 |
| question | 47.2 |

## Class imbalance

The largest class is 25.34 times the smallest class. Macro F1 is therefore a required model-selection metric.

## Frequent Thai tokens

| Token | Count |
|---|---:|
| ไม่ | 9456 |
| ที่ | 7053 |
| ไป | 5921 |
| ได้ | 5560 |
| มี | 5479 |
| มา | 5035 |
| จะ | 4370 |
| เลย | 4210 |
| ก็ | 4075 |
| แล้ว | 3609 |
| ให้ | 3600 |
| ใน | 3464 |
| ครับ | 3396 |
| และ | 3373 |
| ของ | 3161 |
| กิน | 3145 |
| ค่ะ | 3117 |
| เป็น | 3044 |
| แต่ | 2972 |
| ว่า | 2896 |

## Example reviews per label

### negative

- ☹️
- 😔
- 😞

### neutral

- 🍾
- 🐷
- 🤓

### positive

- :3
- ☺️
- 🤤

### question

- เท่าไหร่
- 4Gหรือ2G?
- แพร่มีก่อ

## Figures

- `reports/figures/label_distribution.png`
- `reports/figures/text_length_distribution.png`
