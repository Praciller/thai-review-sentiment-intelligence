# Thai Review Sentiment Intelligence - Project Requirements

## 1. Project Summary

### Repository Name

`thai-review-sentiment-intelligence`

### Project Type

End-to-end Data Science / NLP / Machine Learning portfolio project.

### Main Goal

Build a Thai customer review sentiment intelligence platform that can classify Thai text reviews into sentiment labels and present useful business insights through an API and React dashboard.

This project is designed to demonstrate practical skills for Data Scientist, Machine Learning Engineer, NLP Engineer, and Data & AI Developer roles.

---

## 2. Recommended Scope

This project should not be only a notebook project. It should include:

- Data loading
- Data validation
- Exploratory data analysis
- Thai text preprocessing
- Baseline machine learning models
- PyTorch Transformer fine-tuning
- Model evaluation
- Error analysis
- FastAPI inference API
- React dashboard
- Documentation
- Reproducible local setup

---

## 3. Data Source

### Primary Dataset

Use the Wisesight Sentiment Corpus from PyThaiNLP.

### Access Method

Install PyThaiNLP:

```bash
pip install pythainlp
```

Load dataset:

```python
from pythainlp.corpus import wisesight_sentiment

texts = wisesight_sentiment.get_texts()
labels = wisesight_sentiment.get_labels()
```

### Dataset Requirements

The project must inspect the actual dataset after loading and produce a data validation report.

Expected columns after processing:

```txt
text
label
cleaned_text
text_length
```

Expected label types may include:

```txt
positive
negative
neutral
question
```

The project must not assume labels blindly. It must print and save the actual label distribution.

### External Data

External datasets are optional. The project must be able to run using only Wisesight Sentiment Corpus.

If external data is added later, it should follow this CSV format:

```csv
id,text,label
1,"อาหารอร่อยมาก บริการดี",positive
2,"รอนานมาก พนักงานไม่สนใจ",negative
```

---

## 4. Tech Stack

### Required

```txt
Python 3.10+
pandas
numpy
scikit-learn
PyThaiNLP
PyTorch
Hugging Face Transformers
FastAPI
Uvicorn
React
Vite
Tailwind CSS
joblib
matplotlib
```

### Recommended Optional

These are worth using in this free portfolio project:

```txt
Docker
MLflow local tracking
Hugging Face Spaces for optional demo deployment
```

### Not Recommended for First Version

These are useful but should not be required in version 1:

```txt
SHAP
LIME
Full cloud deployment
Paid GPU
Database
Authentication
Complex MLOps pipeline
Kubernetes
```

### Optional Decision

For this project, use optional tools like this:

| Tool | Use? | Reason |
|---|---|---|
| React + Vite | Yes | Lightweight frontend, simpler than Next.js |
| Docker | Yes | Good for reproducibility and portfolio |
| MLflow | Yes, local only | Good for experiment tracking without paid services |
| Hugging Face Spaces | Optional | Useful for free demo if model size/resources allow |
| SHAP | No for v1 | Adds complexity and may not work smoothly with Transformer text models |
| LIME | Optional later | Easier than SHAP for text, but not required |
| Database | No for v1 | CSV and in-memory inference are enough |
| PostgreSQL | No for v1 | This is an ML/NLP project, not a data warehouse project |
| Airflow/Prefect | No | Too heavy for this project |
| TensorFlow | No for v1 | Use PyTorch first to keep the project focused |
| Streamlit | No | You want a real React frontend |
| Paid cloud GPU | No | Keep project free-tier friendly |

---

## 5. Functional Requirements

## 5.1 Data Loading

The system must load Wisesight Sentiment Corpus from PyThaiNLP.

### Acceptance Criteria

- Dataset can be loaded with one command.
- Raw text and labels are converted into a pandas DataFrame.
- The raw dataset is saved to:

```txt
data/raw/wisesight_raw.csv
```

- The processed dataset is saved to:

```txt
data/processed/wisesight_processed.csv
```

---

## 5.2 Data Validation

The system must validate the dataset before training.

### Validation Checks

- Text column must not be null.
- Label column must not be null.
- Empty text rows must be removed.
- Duplicate rows must be detected.
- Label distribution must be calculated.
- Text length statistics must be calculated.
- Number of samples per class must be reported.

### Output

```txt
reports/data_validation_report.md
```

### Acceptance Criteria

- Running the validation script creates a readable markdown report.
- The report includes dataset size, missing values, duplicates, and label distribution.

---

## 5.3 Exploratory Data Analysis

The project must include EDA.

### Required EDA

- Total number of reviews
- Number of labels
- Label distribution
- Text length distribution
- Average text length per label
- Example reviews per label
- Top frequent Thai words
- Class imbalance analysis

### Output

```txt
notebooks/01_eda.ipynb
reports/eda_summary.md
reports/figures/label_distribution.png
reports/figures/text_length_distribution.png
```

### Acceptance Criteria

- EDA notebook can be run from top to bottom.
- EDA summary is written in plain English.
- At least two figures are saved in `reports/figures`.

---

## 5.4 Thai Text Preprocessing

The system must support Thai text preprocessing for baseline ML models.

### Required Preprocessing

- Normalize text
- Remove URLs
- Remove extra whitespace
- Remove or normalize repeated characters where appropriate
- Tokenize Thai text using PyThaiNLP
- Optionally remove Thai stopwords
- Keep raw text for Transformer model

### Important Rule

Use different preprocessing strategies for different models:

```txt
Baseline ML:
cleaned text + tokenization + TF-IDF

Transformer:
raw or lightly cleaned text
```

### Acceptance Criteria

- Preprocessing functions are reusable.
- Unit tests cover common text cleaning cases.
- The project keeps both `text` and `cleaned_text`.

---

## 5.5 Baseline Machine Learning Models

The project must train at least two baseline models.

### Required Baseline Models

```txt
TF-IDF + Logistic Regression
TF-IDF + Linear SVM
```

### Training Requirements

- Use stratified train/validation/test split.
- Set random seed.
- Train both baseline models.
- Compare performance.
- Save the best baseline model.

### Output

```txt
models/baseline_model.joblib
reports/baseline_metrics.json
reports/baseline_classification_report.md
```

### Acceptance Criteria

- Baseline training can be run from CLI.
- Metrics are saved to JSON.
- Classification report is saved to markdown.
- Best model is saved with joblib.

---

## 5.6 PyTorch Transformer Model

The project must fine-tune a Thai Transformer model using PyTorch.

### Recommended Model

```txt
airesearch/wangchanberta-base-att-spm-uncased
```

### Required Components

- Hugging Face tokenizer
- PyTorch Dataset
- DataLoader or Hugging Face Trainer
- Train/validation/test split
- Training loop or Trainer API
- Evaluation on test set
- Model checkpoint saving
- Configurable epochs and batch size

### Output

```txt
models/wangchanberta_sentiment/
reports/transformer_metrics.json
reports/transformer_classification_report.md
```

### Acceptance Criteria

- Transformer training script can run from CLI.
- Model checkpoint is saved locally.
- Test metrics are saved.
- README explains hardware requirements.
- If training is too slow on CPU, the project must still include a smaller debug mode.

### Debug Mode Requirement

The training script must support a small debug run:

```bash
python -m src.models.train_transformer --debug
```

Debug mode should use a small sample and 1 epoch to verify that the pipeline works.

---

## 5.7 Model Evaluation

The project must evaluate all models using the same test set.

### Required Metrics

```txt
accuracy
precision
recall
macro_f1
weighted_f1
confusion_matrix
```

### Required Reports

```txt
reports/model_comparison.md
reports/confusion_matrix.png
```

### README Model Comparison Table

The README must include a table like this:

```md
| Model | Accuracy | Macro F1 | Weighted F1 | Notes |
|---|---:|---:|---:|---|
| TF-IDF + Logistic Regression | TBD | TBD | TBD | Baseline |
| TF-IDF + Linear SVM | TBD | TBD | TBD | Strong baseline |
| WangchanBERTa Fine-tuned | TBD | TBD | TBD | PyTorch Transformer |
```

### Acceptance Criteria

- All model metrics are stored.
- Confusion matrix is generated.
- Model comparison table is updated manually or generated into markdown.

---

## 5.8 Error Analysis

The project must include error analysis.

### Required Analysis

- Misclassified examples
- Most confused label pairs
- Error rate by text length
- Examples of hard cases
- Possible reasons for errors

### Output

```txt
reports/error_analysis.csv
reports/error_analysis.md
```

### Acceptance Criteria

- Misclassified examples are saved to CSV.
- Error analysis markdown includes practical observations.
- README includes a short summary of model limitations.

---

## 5.9 Prediction API

Build a FastAPI backend for model inference.

### Required Endpoints

#### Health Check

```http
GET /health
```

Response:

```json
{
  "status": "ok"
}
```

#### Single Prediction

```http
POST /predict
```

Request:

```json
{
  "text": "ร้านนี้อาหารอร่อยมาก บริการดี"
}
```

Response:

```json
{
  "text": "ร้านนี้อาหารอร่อยมาก บริการดี",
  "predicted_label": "positive",
  "confidence": 0.94,
  "probabilities": {
    "positive": 0.94,
    "neutral": 0.04,
    "negative": 0.01,
    "question": 0.01
  },
  "model_name": "wangchanberta"
}
```

#### Batch Prediction

```http
POST /predict-batch
```

Request:

```json
{
  "texts": [
    "อร่อยมาก",
    "รอนานเกินไป",
    "ร้านเปิดกี่โมง"
  ]
}
```

Response:

```json
{
  "results": [
    {
      "text": "อร่อยมาก",
      "predicted_label": "positive",
      "confidence": 0.91
    },
    {
      "text": "รอนานเกินไป",
      "predicted_label": "negative",
      "confidence": 0.88
    },
    {
      "text": "ร้านเปิดกี่โมง",
      "predicted_label": "question",
      "confidence": 0.85
    }
  ]
}
```

### API Requirements

- Load model once at startup.
- Validate input text.
- Reject empty text.
- Limit max text length.
- Return useful error messages.
- Include CORS configuration for React frontend.

### Acceptance Criteria

- API runs locally with Uvicorn.
- `/health` works.
- `/predict` works.
- `/predict-batch` works.
- API documentation is available through FastAPI Swagger UI.

---

## 5.10 React Frontend

Use React with Vite instead of Next.js.

### Required Pages

#### Home / Prediction Page

Features:

- Text input for Thai review
- Predict button
- Predicted sentiment label
- Confidence score
- Probability breakdown
- Example review buttons

#### Batch Analysis Page

Features:

- CSV upload
- Preview uploaded reviews
- Run batch prediction
- Display prediction result table
- Filter by predicted sentiment

#### Dashboard Page

Features:

- Sentiment distribution chart
- Review count by label
- Average confidence
- Top negative reviews
- Business insight summary section

### Required Components

```txt
ReviewInput
PredictionResult
ProbabilityBar
CsvUploader
SentimentChart
ReviewTable
InsightSummary
LoadingState
ErrorMessage
```

### Frontend Tech

```txt
React
Vite
Tailwind CSS
Recharts
Axios or Fetch API
```

### Acceptance Criteria

- React frontend can call FastAPI backend.
- User can predict a single review.
- User can upload a CSV for batch prediction.
- Dashboard shows sentiment distribution.
- UI is responsive enough for desktop and mobile.
- README includes screenshots.

---

## 5.11 Optional Topic Classification

Topic classification is optional and should be treated as an experimental feature.

### Suggested Topics

```txt
taste
price
service
delivery
cleanliness
waiting_time
product_quality
other
```

### Recommended Implementation for Version 1

Use rule-based topic detection, not a trained model.

Example rules:

```txt
"แพง", "ราคา", "คุ้ม" → price
"ช้า", "รอนาน", "คิว" → waiting_time
"พนักงาน", "บริการ" → service
"อร่อย", "รสชาติ", "หวาน", "เค็ม" → taste
"สะอาด", "สกปรก" → cleanliness
"ส่ง", "เดลิเวอรี่", "ไรเดอร์" → delivery
```

### Acceptance Criteria

- Topic classification must be clearly marked as rule-based.
- It must not be presented as a trained ML model unless labeled data is available.
- It may be added to API response as:

```json
{
  "topic": "service",
  "topic_method": "rule_based"
}
```

---

## 6. Non-Functional Requirements

## 6.1 Cost Requirement

The project must be free-tier friendly.

### Requirements

- Must run locally without paid services.
- Must not require paid GPU.
- Must not require paid database.
- Must not require paid cloud hosting.
- Deployment is optional.

### Recommended Free Deployment Options

```txt
Frontend:
Vercel free tier or Netlify free tier

Backend/API:
Hugging Face Spaces or Render free tier

Model demo:
Hugging Face Spaces
```

If deployment becomes difficult because of memory or model size, local demo is acceptable as long as README includes screenshots and clear instructions.

---

## 6.2 Performance Requirement

### API

- Single prediction should respond within 2 seconds after model is loaded on a reasonable local machine.
- Batch prediction should support at least 100 reviews per request.
- Model must not reload on every request.

### Frontend

- UI should show loading states.
- UI should show clear error messages if API is unavailable.
- Batch results should render without freezing for at least 100 rows.

---

## 6.3 Reproducibility Requirement

The project must include:

```txt
requirements.txt
.env.example
README.md
random seed configuration
clear setup instructions
sample input CSV
```

Training scripts must support reproducible runs with a seed value.

Example:

```bash
python -m src.models.train_baseline --seed 42
python -m src.models.train_transformer --seed 42
```

---

## 6.4 Maintainability Requirement

The codebase must be modular.

### Required Backend Structure

```txt
src/
├── data/
├── features/
├── models/
├── evaluation/
├── api/
└── utils/
```

### Required Frontend Structure

```txt
frontend/
├── src/
│   ├── components/
│   ├── pages/
│   ├── services/
│   ├── types/
│   └── utils/
```

### Requirements

- Avoid putting all logic in notebooks.
- Training code must be available as Python scripts.
- API code must not contain training logic.
- Frontend API calls must be separated into service files.

---

## 6.5 Security Requirement

The API must:

- Reject empty input.
- Limit maximum text length.
- Avoid logging full user input in production mode.
- Avoid exposing environment variables.
- Enable CORS only for configured frontend origins.

The frontend must:

- Validate file type before CSV upload.
- Show warning for large files.
- Avoid storing sensitive data permanently.

---

## 6.6 Documentation Requirement

The project must include:

```txt
README.md
docs/architecture.md
docs/data_source.md
docs/modeling_approach.md
docs/api.md
docs/frontend.md
docs/error_analysis.md
```

README must be recruiter-friendly and include:

```txt
Project overview
Problem statement
Dataset
Tech stack
Architecture
How to run
Model results
API examples
Frontend screenshots
Business impact
Limitations
Future improvements
```

---

## 6.7 Testing Requirement

The project must include basic tests.

### Required Tests

```txt
tests/test_preprocess.py
tests/test_api.py
```

### Test Cases

- Text cleaning works.
- Empty text is rejected.
- API health endpoint returns ok.
- Predict endpoint returns expected response structure.
- Batch endpoint handles multiple texts.

---

## 7. Recommended Repository Structure

```txt
thai-review-sentiment-intelligence/
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
├── docker-compose.yml
├── data/
│   ├── raw/
│   ├── processed/
│   └── sample/
│       └── sample_reviews.csv
├── notebooks/
│   ├── 01_eda.ipynb
│   ├── 02_baseline_model.ipynb
│   └── 03_transformer_model.ipynb
├── src/
│   ├── data/
│   │   ├── load_wisesight.py
│   │   └── validate_data.py
│   ├── features/
│   │   └── preprocess_thai_text.py
│   ├── models/
│   │   ├── train_baseline.py
│   │   ├── train_transformer.py
│   │   ├── predict.py
│   │   └── model_registry.py
│   ├── evaluation/
│   │   ├── evaluate_model.py
│   │   └── error_analysis.py
│   ├── api/
│   │   └── main.py
│   └── utils/
│       └── config.py
├── frontend/
│   ├── package.json
│   ├── vite.config.ts
│   ├── index.html
│   └── src/
│       ├── main.tsx
│       ├── App.tsx
│       ├── components/
│       ├── pages/
│       ├── services/
│       ├── types/
│       └── utils/
├── reports/
│   ├── figures/
│   ├── baseline_metrics.json
│   ├── transformer_metrics.json
│   ├── model_comparison.md
│   ├── error_analysis.csv
│   └── error_analysis.md
├── models/
│   └── .gitkeep
├── docs/
│   ├── architecture.md
│   ├── data_source.md
│   ├── modeling_approach.md
│   ├── api.md
│   ├── frontend.md
│   └── error_analysis.md
└── tests/
    ├── test_preprocess.py
    └── test_api.py
```

---

## 8. CLI Commands

The project should support these commands.

### Install Backend

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

For Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Load Data

```bash
python -m src.data.load_wisesight
```

### Validate Data

```bash
python -m src.data.validate_data
```

### Train Baseline

```bash
python -m src.models.train_baseline --seed 42
```

### Train Transformer Debug Mode

```bash
python -m src.models.train_transformer --debug --seed 42
```

### Train Transformer Full Mode

```bash
python -m src.models.train_transformer --seed 42 --epochs 3 --batch-size 8
```

### Evaluate Model

```bash
python -m src.evaluation.evaluate_model
```

### Run API

```bash
uvicorn src.api.main:app --reload --port 8000
```

### Install Frontend

```bash
cd frontend
npm install
npm run dev
```

---

## 9. Docker Requirement

Docker is recommended but should not block local development.

### Required Docker Files

```txt
Dockerfile.api
frontend/Dockerfile
docker-compose.yml
```

### Docker Compose Services

```txt
api
frontend
```

### Docker Compose Acceptance Criteria

The following command should start the app:

```bash
docker compose up --build
```

The services should be available at:

```txt
Frontend: http://localhost:5173
API: http://localhost:8000
API Docs: http://localhost:8000/docs
```

---

## 10. MLflow Requirement

MLflow should be used locally only.

### Purpose

Use MLflow to track:

- Model name
- Parameters
- Metrics
- Training date
- Dataset version
- Artifact path

### Acceptance Criteria

- Baseline training logs to MLflow.
- Transformer training logs to MLflow if available.
- Project still works if MLflow is disabled.

### Example Command

```bash
mlflow ui
```

MLflow UI should be available at:

```txt
http://localhost:5000
```

---

## 11. README Requirements

The README must include these sections:

```txt
Project Overview
Problem Statement
Key Features
Dataset
Tech Stack
Architecture
Project Structure
Setup Instructions
How to Run Data Pipeline
How to Train Models
How to Run API
How to Run React Frontend
Model Results
Error Analysis
API Examples
Screenshots
Business Impact
Limitations
Future Improvements
```

---

## 12. Business Impact

The project should explain business value clearly.

Example:

```txt
This system helps businesses analyze Thai customer feedback at scale.
Instead of manually reading thousands of reviews, business owners can quickly
understand customer sentiment, detect negative issues, identify common complaint
patterns, and prioritize service improvement.
```

Example insights:

```txt
- Negative reviews often mention waiting time or poor service.
- Positive reviews often mention taste, quality, and friendly staff.
- Question-type reviews can be routed to customer support.
- Low-confidence predictions can be reviewed manually.
```

---

## 13. Model Limitations

The project must document limitations.

Possible limitations:

```txt
- Sentiment labels may not cover all real-world review types.
- Sarcasm and slang can be difficult.
- Mixed sentiment reviews may confuse the model.
- Topic classification is rule-based unless labeled topic data is added.
- Transformer model may require GPU for faster training.
```

---

## 14. Future Improvements

Recommended future improvements:

```txt
- Add LIME explanation for text predictions
- Add active learning workflow
- Add manual correction UI
- Add topic classification with labeled data
- Add model monitoring
- Add Hugging Face Spaces deployment
- Add OpenRouter/Gemini summary for batch review insights
- Integrate with smart-qr-kitchen-pos as Restaurant Review Intelligence
```

---

## 15. Definition of Done

The project is complete when:

- Dataset can be loaded from PyThaiNLP.
- Data validation report is generated.
- EDA notebook and summary are completed.
- Baseline models are trained and evaluated.
- PyTorch Transformer model can run in debug mode.
- Full Transformer training instructions are documented.
- Model comparison report exists.
- Error analysis exists.
- FastAPI backend works.
- React frontend works.
- Batch CSV upload works.
- Docker Compose works or local setup is clearly documented.
- README is complete and recruiter-friendly.
- Screenshots are added to README.
- Project runs without paid services.

---

# Codex Implementation Prompt

Use this prompt after cloning the empty GitHub repository.

```txt
You are working inside my GitHub repository named thai-review-sentiment-intelligence.

Goal:
Build an end-to-end Thai NLP Data Science portfolio project using PyThaiNLP, scikit-learn, PyTorch, Hugging Face Transformers, FastAPI, React with Vite, and Tailwind CSS.

Important:
- The project must be free-tier friendly.
- Use React + Vite instead of Next.js.
- Use Wisesight Sentiment Corpus from PyThaiNLP as the main dataset.
- Do not require paid cloud services.
- Do not commit large model files.
- Keep the project practical and recruiter-friendly.
- Build the project incrementally and keep the codebase clean.

Functional Requirements:
1. Create a clear project structure.
2. Add data loading from PyThaiNLP Wisesight Sentiment Corpus.
3. Add data validation and save a markdown validation report.
4. Add Thai text preprocessing utilities.
5. Add EDA notebook and EDA summary.
6. Add baseline training with TF-IDF + Logistic Regression and TF-IDF + Linear SVM.
7. Add PyTorch Transformer fine-tuning using airesearch/wangchanberta-base-att-spm-uncased.
8. Add debug mode for Transformer training.
9. Add model evaluation, model comparison, confusion matrix, and error analysis.
10. Add FastAPI backend with /health, /predict, and /predict-batch endpoints.
11. Add React + Vite frontend with single prediction, batch CSV upload, and dashboard pages.
12. Add Tailwind CSS styling.
13. Add Docker support if practical.
14. Add local MLflow tracking if practical but make it optional.
15. Add tests for preprocessing and API.
16. Add complete README and documentation files.

Non-Functional Requirements:
1. The project must run locally without paid services.
2. The API must load the model once at startup.
3. The API must validate input and reject empty text.
4. The frontend must show loading and error states.
5. The code must be modular and maintainable.
6. The README must explain setup, training, inference, frontend usage, and project value.
7. The project must include screenshots placeholders if real screenshots are not available yet.
8. The project must not include large model artifacts in GitHub.
9. The project must include .env.example and .gitignore.
10. The project must be suitable for a Data Scientist / ML Engineer portfolio.

Recommended Optional:
- Use Docker.
- Use MLflow locally.
- Add Hugging Face Spaces deployment instructions only if easy.
- Do not add SHAP in v1.
- Do not add TensorFlow in v1.
- Do not add PostgreSQL in v1.
- Do not add Airflow or Kubernetes.

After implementation:
Create a file named PORTFOLIO_REVIEW.md that explains:
- What was implemented
- What data science skills this project demonstrates
- What ML/NLP skills this project demonstrates
- What is still missing
- How to present this project in a resume
```
