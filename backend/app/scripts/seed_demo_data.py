from pathlib import Path

import pandas as pd
from sqlalchemy import delete, text

from app.database import SessionLocal
from app.models import CSVUpload, Customer, LLMExplanation, Prediction

CSV_PATH = Path(__file__).resolve().parents[1] / "ml" / "data" / "Telco-Customer-Churn.csv"
DEMO_NAMES = [
    "Алексей Смирнов",
    "Мария Иванова",
    "Дмитрий Кузнецов",
    "Елена Попова",
    "Иван Соколов",
    "Ольга Морозова",
    "Сергей Волков",
    "Наталья Лебедева",
    "Андрей Новиков",
    "Татьяна Федорова",
    "Максим Михайлов",
    "Анна Павлова",
    "Павел Семенов",
    "Светлана Голубева",
    "Никита Виноградов",
    "Юлия Богданова",
    "Артем Воробьев",
    "Ксения Белова",
    "Роман Захаров",
    "Виктория Ковалева",
]


def load_demo_customers() -> list[Customer]:
    """Готовит первые 20 клиентов из Telco CSV для демо-режима."""
    if not CSV_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found: {CSV_PATH}. Put Telco-Customer-Churn.csv into app/ml/data."
        )

    dataframe = pd.read_csv(CSV_PATH).head(20).copy()
    dataframe["TotalCharges"] = pd.to_numeric(dataframe["TotalCharges"], errors="coerce")
    dataframe["TotalCharges"] = dataframe["TotalCharges"].fillna(
        dataframe["TotalCharges"].median()
    )

    customers: list[Customer] = []
    for index, row in enumerate(dataframe.itertuples(index=False), start=1):
        customers.append(
            Customer(
                name=DEMO_NAMES[index - 1],
                tenure=int(row.tenure),
                contract_type=str(row.Contract),
                monthly_charges=float(row.MonthlyCharges),
                total_charges=float(row.TotalCharges),
                internet_service=str(row.InternetService),
                tech_support=str(row.TechSupport),
                payment_method=str(row.PaymentMethod),
            )
        )

    return customers


def reset_demo_tables(db) -> None:
    """Очищает таблицы и при PostgreSQL сбрасывает счетчики ID."""
    dialect_name = db.bind.dialect.name if db.bind is not None else ""

    if dialect_name == "postgresql":
        db.execute(
            text(
                "TRUNCATE TABLE llm_explanations, predictions, csv_uploads, customers "
                "RESTART IDENTITY CASCADE"
            )
        )
        db.commit()
        return

    db.execute(delete(LLMExplanation))
    db.execute(delete(Prediction))
    db.execute(delete(CSVUpload))
    db.execute(delete(Customer))
    db.commit()


def seed_demo_data():
    """Очищает тестовые данные и создает 20 демо-клиентов."""

    customers = load_demo_customers()

    with SessionLocal() as db:
        reset_demo_tables(db)
        db.add_all(customers)
        db.commit()

    print(f"Готово: создано {len(customers)} демо-клиентов.")


if __name__ == "__main__":
    seed_demo_data()
