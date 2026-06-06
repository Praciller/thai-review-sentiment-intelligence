# Frontend

## Stack

- React 19
- Vite 8
- Tailwind CSS 4
- Recharts 3
- PapaParse
- Lucide icons

## Routes

- `/`: single-review prediction and compact analytics.
- `/batch`: CSV validation, one-click sample data, preview, batch inference, and
  sentiment filter.
- `/dashboard`: distribution, confidence, issues, and negative-review queue.

## Design

The interface follows `PRODUCT.md`, `DESIGN.md`, and
`docs/design/dashboard-concept.png`.

- Warm paper light theme for daytime analyst use.
- Ink blue actions, tamarind active state, semantic sentiment colors.
- Open bands and dividers instead of nested cards.
- Thai-first typography using Sarabun with local fallbacks.
- Visible focus, text labels in addition to color, reduced-motion support.

## CSV Contract

The file must:

- Use `.csv`.
- Be 2 MB or smaller.
- Include a `text` column.
- Include no more than 100 non-empty review rows.
- Optionally include an `id` column.

Sample: `data/sample/sample_reviews.csv`.

Reviewers can also click **ใช้ข้อมูลตัวอย่าง** to exercise the same eight-review
fixture without opening a file picker.
