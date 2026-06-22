import json
from pathlib import Path

import joblib
import pandas as pd

MODEL_PATH = Path(__file__).resolve().parents[1] / "ml" / "artifacts" / "churn_model.joblib"
METRICS_PATH = Path(__file__).resolve().parents[1] / "ml" / "artifacts" / "metrics.json"
MODEL_VERSION = "logistic_regression_v2"


class ModelNotTrainedError(Exception):
    """Выбрасывается, если ML-модель еще не была обучена."""


def load_model():
    """Загружает обученную модель из файловой системы."""
    if not MODEL_PATH.exists():
        raise ModelNotTrainedError(
            "Model file not found. Run python -m app.ml.train_model first."
        )
    return joblib.load(MODEL_PATH)


def load_threshold() -> float:
    """Загружает лучший threshold из metrics.json."""
    if not METRICS_PATH.exists():
        return 0.5

    metrics = json.loads(METRICS_PATH.read_text(encoding="utf-8"))
    return float(metrics.get("best_threshold", 0.5))


def get_risk_level(probability: float) -> str:
    """Преобразует вероятность оттока в категорию риска."""
    if probability < 0.35:
        return "low"
    if probability < 0.7:
        return "medium"
    return "high"


def predict_customer_churn(customer):
    """Строит предсказание по данным клиента из БД."""
    model = load_model()
    threshold = load_threshold()
    features = pd.DataFrame(
        [
            {
                "tenure": customer.tenure,
                "contract_type": customer.contract_type,
                "monthly_charges": customer.monthly_charges,
                "total_charges": customer.total_charges,
                "internet_service": customer.internet_service,
                "tech_support": customer.tech_support,
                "payment_method": customer.payment_method,
            }
        ]
    )

    churn_probability = float(model.predict_proba(features)[0][1])

    return {
        "churn_probability": churn_probability,
        "predicted_label": churn_probability >= threshold,
        "risk_level": get_risk_level(churn_probability),
        "model_version": MODEL_VERSION,
    }
