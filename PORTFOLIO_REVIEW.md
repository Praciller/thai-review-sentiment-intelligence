# Portfolio Review

## What Was Implemented

- Real Wisesight loading, source recording, validation, preprocessing, and EDA.
- Two production-style scikit-learn baselines with one shared test split.
- WangchanBERTa Trainer with configurable full training and verified debug mode.
- Common metrics, confusion matrix, model comparison, and error analysis.
- Model registry and FastAPI single/batch inference.
- Responsive React/Vite/Tailwind product with CSV workflow and dashboard.
- Tests, Docker, local MLflow option, architecture docs, and reproducible commands.

## Fast Reviewer Walkthrough

1. Read the model comparison and why macro F1 selects Logistic Regression.
2. Run `docker compose up --build`.
3. Open <http://localhost:5173>, analyze the default mixed-sentiment review, then
   open the batch page.
4. Click **ใช้ข้อมูลตัวอย่าง**, run the batch, and filter the result table.
5. Review `reports/error_analysis.md` and the limitations below.

## Verified Gates

Verified locally on June 6, 2026:

- 31 backend tests passed.
- 5 frontend tests, ESLint, TypeScript, and Vite production build passed.
- Docker API and frontend images built; Compose health and prediction passed.
- Single prediction median latency was 16.32 ms across 10 local requests.
- A 100-review batch completed in 22.97 ms.
- Desktop prediction, batch, and mobile browser workflows were captured in
  `docs/screenshots/`.

## Data Science Skills Demonstrated

- Dataset inspection instead of assuming labels or row counts.
- Missing/empty/duplicate validation and class-imbalance analysis.
- Deterministic stratified experimental design.
- Selection by macro F1 instead of accuracy alone.
- Confusion-matrix and text-length error analysis.
- Honest separation between debug smoke tests and benchmark results.

## ML and NLP Skills Demonstrated

- Thai normalization and PyThaiNLP tokenization.
- Different preprocessing contracts for sparse and Transformer models.
- TF-IDF, Logistic Regression, Linear SVM, and calibrated probabilities.
- PyTorch/Hugging Face Trainer, checkpoints, dynamic padding, and label mapping.
- Inference abstraction that supports baseline and Transformer backends.
- Explicitly rule-based topic classification with no false ML claim.

## What Is Still Missing

- Full WangchanBERTa benchmark training on the complete split.
- Hyperparameter search and repeated-seed confidence intervals.
- Human-reviewed qualitative error labels.
- Production authentication, storage, monitoring, and deployed public URL.

These are stated gaps, not hidden placeholders.

## Resume Presentation

**Project bullet:**

> Built an end-to-end Thai customer-review intelligence platform using PyThaiNLP,
> scikit-learn, PyTorch/Transformers, FastAPI, and React; validated 26.7K Wisesight
> reviews, trained comparable TF-IDF baselines on a shared stratified test set,
> and delivered single/batch inference with operational sentiment dashboards.

**Discussion points:**

1. Explain why macro F1 selected Logistic Regression despite lower accuracy.
2. Show how the shared split prevents misleading model comparisons.
3. Demonstrate model loading once at API startup.
4. Use the one-click sample batch or upload `data/sample/sample_reviews.csv`,
   then filter negative results.
5. Be explicit that topic detection is rule-based and Transformer full training is
   the next modeling milestone.
