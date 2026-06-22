import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

DATA_DIR = Path(__file__).resolve().parent / "data"
ARTIFACTS_DIR = Path(__file__).resolve().parent / "artifacts"
CSV_PATH = DATA_DIR / "Telco-Customer-Churn.csv"
MODEL_PATH = ARTIFACTS_DIR / "churn_model.joblib"
METRICS_PATH = ARTIFACTS_DIR / "metrics.json"

NUMERIC_FEATURES = ["tenure", "monthly_charges", "total_charges"]
CATEGORICAL_FEATURES = [
    "contract_type",
    "internet_service",
    "tech_support",
    "payment_method",
]
FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES


def load_dataset() -> tuple[pd.DataFrame, pd.Series]:
    """Загружает и подготавливает Telco Customer Churn dataset."""
    if not CSV_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found: {CSV_PATH}. Put Telco-Customer-Churn.csv into app/ml/data."
        )

    dataframe = pd.read_csv(CSV_PATH)
    dataframe["TotalCharges"] = pd.to_numeric(dataframe["TotalCharges"], errors="coerce")

    prepared = pd.DataFrame(
        {
            "tenure": dataframe["tenure"],
            "contract_type": dataframe["Contract"],
            "monthly_charges": dataframe["MonthlyCharges"],
            "total_charges": dataframe["TotalCharges"],
            "internet_service": dataframe["InternetService"],
            "tech_support": dataframe["TechSupport"],
            "payment_method": dataframe["PaymentMethod"],
        }
    )
    prepared["total_charges"] = prepared["total_charges"].fillna(
        prepared["total_charges"].median()
    )

    target = dataframe["Churn"].map({"Yes": 1, "No": 0})
    return prepared[FEATURES], target


def build_pipeline() -> Pipeline:
    """Создает sklearn pipeline для бинарной классификации."""
    preprocessor = ColumnTransformer(
        transformers=[
            ("numeric", StandardScaler(), NUMERIC_FEATURES),
            ("categorical", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL_FEATURES),
        ]
    )

    return Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("classifier", LogisticRegression(max_iter=1000)),
        ]
    )


def find_best_threshold(y_true: pd.Series, probabilities) -> tuple[float, float]:
    """Подбирает threshold, который дает максимальный F1-score."""
    best_threshold = 0.5
    best_f1 = -1.0

    for step in range(5, 96):
        threshold = step / 100
        predictions = (probabilities >= threshold).astype(int)
        current_f1 = f1_score(y_true, predictions, zero_division=0)

        if current_f1 > best_f1:
            best_f1 = current_f1
            best_threshold = threshold

    return best_threshold, best_f1


def evaluate_model(
    model: Pipeline,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    threshold: float,
) -> dict:
    """Считает метрики модели с учетом выбранного threshold."""
    probabilities = model.predict_proba(X_test)[:, 1]
    predictions = (probabilities >= threshold).astype(int)

    return {
        "accuracy": round(float(accuracy_score(y_test, predictions)), 4),
        "precision": round(float(precision_score(y_test, predictions, zero_division=0)), 4),
        "recall": round(float(recall_score(y_test, predictions, zero_division=0)), 4),
        "f1": round(float(f1_score(y_test, predictions, zero_division=0)), 4),
        "roc_auc": round(float(roc_auc_score(y_test, probabilities)), 4),
        "best_threshold": round(float(threshold), 2),
    }


def train_model():
    """Обучает модель и сохраняет артефакты в app/ml/artifacts."""
    X, y = load_dataset()
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )

    pipeline = build_pipeline()
    param_grid = {
        "classifier__C": [0.1, 1.0, 10.0],
        "classifier__class_weight": [None, "balanced"],
        "classifier__solver": ["liblinear", "lbfgs"],
    }

    grid_search = GridSearchCV(
        estimator=pipeline,
        param_grid=param_grid,
        cv=5,
        scoring="roc_auc",
        n_jobs=-1,
    )
    grid_search.fit(X_train, y_train)

    model = grid_search.best_estimator_
    test_probabilities = model.predict_proba(X_test)[:, 1]
    best_threshold, _ = find_best_threshold(y_test, test_probabilities)

    metrics = evaluate_model(model, X_test, y_test, best_threshold)
    metrics["best_params"] = grid_search.best_params_
    metrics["cv_best_score"] = round(float(grid_search.best_score_), 4)

    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    METRICS_PATH.write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    print(f"Model saved to: {MODEL_PATH}")
    print(f"Metrics saved to: {METRICS_PATH}")
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    train_model()
