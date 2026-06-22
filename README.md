# Churn Prediction with ML + LLM Explanations

Fullstack MVP for customer churn prediction. The application stores customer data, runs an ML risk prediction, and generates a short human-readable explanation through a local Ollama model.

## What the project does

- manages a customer base through a FastAPI backend and PostgreSQL;
- predicts churn risk for a selected customer with a `scikit-learn` model;
- stores prediction history in the database;
- generates a Russian-language explanation for the latest prediction through Ollama;
- provides a React frontend with customer list, prediction page, analytics, and customer details page.

## Tech stack

- Backend: Python 3.12, FastAPI, SQLAlchemy, Pydantic
- Database: PostgreSQL
- ML: pandas, scikit-learn, joblib
- LLM: Ollama (`llama3.2:3b`)
- Frontend: React, TypeScript, Vite, React Router
- Tests: pytest

## Project structure

```text
backend/
  app/
    database.py
    main.py
    models.py
    schemas.py
    routers/
    services/
    ml/
    scripts/
  tests/
  requirements.txt
  .env.example

frontend/
  src/
    components/
    pages/
    api.ts
    config.ts
    types.ts
    utils.ts
  package.json
  .env.example
```

## Main features

### Backend

- `GET /api/health`
- Customer CRUD:
  - `GET /api/customers`
  - `POST /api/customers`
  - `GET /api/customers/{customer_id}`
  - `PUT /api/customers/{customer_id}`
  - `DELETE /api/customers/{customer_id}`
- Predictions:
  - `POST /api/predictions/{customer_id}`
  - `GET /api/customers/{customer_id}/predictions`
- LLM explanations:
  - `POST /api/explanations/{prediction_id}`
  - `GET /api/predictions/{prediction_id}/explanations`

### Frontend

- Home page with project overview
- Customers page with search and add-customer form
- Customer details page with prediction history and one LLM explanation block
- Prediction page with customer selection and prediction launch
- Analytics page with summary statistics
- Light/dark theme switch

## Database tables

- `customers` — main customer records
- `predictions` — ML prediction results for customers
- `llm_explanations` — LLM-generated explanations for predictions
- `csv_uploads` — reserved table for future CSV import workflow

## Local setup

### 1. Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Set your own PostgreSQL credentials inside `backend/.env`.

Run backend:

```bash
uvicorn app.main:app --reload
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

### 2. Frontend

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

Frontend:

```text
http://127.0.0.1:5173
```

## ML workflow

Dataset location:

```text
backend/app/ml/data/Telco-Customer-Churn.csv
```

Train the model:

```bash
cd backend
python -m app.ml.train_model
```

The training script:

- preprocesses numerical and categorical features;
- uses `OneHotEncoder` and `StandardScaler`;
- trains `LogisticRegression` inside a `Pipeline`;
- performs hyperparameter search with `GridSearchCV`;
- searches for the best classification threshold;
- saves generated artifacts locally.

## Demo data

To reset demo data and load 20 sample customers:

```bash
cd backend
python -m app.scripts.seed_demo_data
```

## Ollama setup

Install Ollama and pull the model:

```bash
ollama pull llama3.2:3b
```

Optional backend environment variables:

```env
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b
```

## Tests

Backend tests:

```bash
cd backend
pytest
```

Frontend production build:

```bash
cd frontend
npm run build
```

## Security before publishing

- real secrets are not committed;
- local `.env` files are ignored by Git;
- ML artifacts and local caches are ignored;
- `README` uses generic local examples instead of personal credentials or machine-specific paths.

## Notes

- This repository is prepared for local development.
- Backend and frontend are started separately.
- ML artifacts are generated locally after training and should not be committed.
