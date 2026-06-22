# Churn Prediction Backend MVP

Простой backend для этапов 1-4 проекта `Churn Prediction с LLM-объяснением риска`.

## Что уже реализовано

- FastAPI backend
- Подключение к PostgreSQL через `DATABASE_URL`
- 4 таблицы: `customers`, `predictions`, `llm_explanations`, `csv_uploads`
- CRUD API для клиентов
- ML-модель на `scikit-learn` для churn prediction
- API для сохранения предсказаний по клиенту
- LLM-объяснения через локальную Ollama
- Swagger по адресу `/docs`
- CORS для будущего React frontend
- Базовые pytest-тесты

## 1. Создание базы PostgreSQL

Убедитесь, что PostgreSQL запущен, затем создайте базу данных:

```sql
CREATE DATABASE churn_db;
```

Например, через `psql`:

```bash
psql -U postgres
```

После входа выполните команду:

```sql
CREATE DATABASE churn_db;
```

## 2. Создание и активация виртуального окружения

Перейдите в папку backend:

```bash
cd backend
```

Создайте виртуальное окружение:

```bash
python3 -m venv .venv
```

Активируйте его:

```bash
source .venv/bin/activate
```

## 3. Установка зависимостей

```bash
pip install -r requirements.txt
```

## 4. Настройка .env

Скопируйте пример:

```bash
cp .env.example .env
```

Откройте `.env` и при необходимости измените строку подключения:

```env
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/churn_db
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b
```

## 5. Запуск backend

```bash
uvicorn app.main:app --reload
```

Backend будет доступен по адресу:

```text
http://127.0.0.1:8000
```

## 6. Swagger

Откройте документацию FastAPI:

```text
http://127.0.0.1:8000/docs
```

## 7. Запуск тестов

Из папки `backend` выполните:

```bash
pytest
```

## 8. Подготовка CSV для обучения

Положите датасет Telco Customer Churn в файл:

```text
backend/app/ml/data/Telco-Customer-Churn.csv
```

Ожидаются колонки:

- `tenure`
- `Contract`
- `MonthlyCharges`
- `TotalCharges`
- `InternetService`
- `TechSupport`
- `PaymentMethod`
- `Churn`

## 9. Обучение модели

Из папки `backend` выполните:

```bash
python -m app.ml.train_model
```

После обучения будут созданы файлы:

```text
backend/app/ml/artifacts/churn_model.joblib
backend/app/ml/artifacts/metrics.json
```

Скрипт обучения теперь:

- подбирает гиперпараметры через `GridSearchCV`
- ищет лучший `threshold` для классификации
- сохраняет его в `metrics.json`

`prediction` API использует этот сохраненный `threshold`, а не фиксированное значение `0.5`.

## 10. Проверка prediction через Swagger

1. Запустите backend: `uvicorn app.main:app --reload`
2. Откройте `http://127.0.0.1:8000/docs`
3. Создайте клиента через `POST /api/customers`
4. Выполните `POST /api/predictions/{customer_id}`
5. Посмотрите историю через `GET /api/customers/{customer_id}/predictions`

Если модель еще не обучена, API вернет понятную ошибку с просьбой сначала запустить `python -m app.ml.train_model`.

## API

- `GET /api/health`
- `GET /api/customers`
- `POST /api/customers`
- `GET /api/customers/{customer_id}`
- `PUT /api/customers/{customer_id}`
- `DELETE /api/customers/{customer_id}`
- `POST /api/predictions/{customer_id}`
- `GET /api/customers/{customer_id}/predictions`
- `POST /api/explanations/{prediction_id}`
- `GET /api/predictions/{prediction_id}/explanations`

## 11. Frontend setup

Frontend lives in:

```text
frontend/
```

Install dependencies:

```bash
cd frontend
npm install
```

## 12. Frontend запуск

Важно: backend должен быть запущен отдельно на:

```text
http://127.0.0.1:8000
```

После этого из папки `frontend` выполните:

```bash
npm run dev
```

Vite dev server будет доступен по адресу:

```text
http://127.0.0.1:5173
```

## 13. Какие страницы проверить в браузере

- `http://127.0.0.1:5173/` — HomePage
- `http://127.0.0.1:5173/customers` — CustomersPage
- `http://127.0.0.1:5173/predict` — PredictPage
- `http://127.0.0.1:5173/analytics` — AnalyticsPage
- `http://127.0.0.1:5173/customers/{id}` — CustomerDetailsPage

Проверьте сценарии:

1. Создание клиента через форму на странице `Customers`
2. Обновление таблицы после создания клиента
3. Переход в карточку клиента
4. Запуск prediction из карточки клиента
5. Запуск prediction из страницы `Predict`
6. Обновление истории predictions
7. Загрузку аналитики на странице `Analytics`

## 14. Установка Ollama

Установите Ollama с официального сайта:

```text
https://ollama.com/download
```

После установки убедитесь, что сервис Ollama запущен локально.

## 15. Загрузка модели llama3.2:3b

Скачайте модель командой:

```bash
ollama pull llama3.2:3b
```

## 16. Как проверить, что Ollama работает

Проверьте список доступных моделей:

```bash
curl http://localhost:11434/api/tags
```

Если Ollama работает корректно, вы увидите JSON-ответ со списком моделей.

## 17. Как использовать LLM-объяснения

1. Запустите backend и frontend
2. Создайте клиента
3. Создайте prediction через Swagger или интерфейс
4. Откройте карточку клиента
5. Нажмите кнопку `Сгенерировать объяснение по клиенту` в отдельном LLM-блоке
6. Объяснение будет построено по последнему прогнозу клиента
7. После генерации на странице появится текст объяснения и рекомендации

Если Ollama временно выключена или недоступна, backend автоматически вернет шаблонное fallback-объяснение на русском языке.

## 18. Seed demo data

Для очистки старых тестовых данных и загрузки 20 демо-клиентов из CSV выполните:

```bash
python -m app.scripts.seed_demo_data
```

Скрипт:

- очищает таблицы `llm_explanations`, `predictions`, `csv_uploads`, `customers`
- берет первые 20 клиентов из `backend/app/ml/data/Telco-Customer-Churn.csv`
- создает 20 клиентов в формате `Клиент 1 ... Клиент 20`
- не создает predictions автоматически
- не создает explanations автоматически
