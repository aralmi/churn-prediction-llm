from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import inspect, text

from app.database import Base, engine
from app.routers import customers, explanations, predictions

# Импорт моделей нужен, чтобы SQLAlchemy увидела все таблицы перед create_all.
from app import models  # noqa: F401


def sync_mvp_schema():
    """Добавляет новые колонки в существующие таблицы без Alembic."""
    inspector = inspect(engine)
    table_names = inspector.get_table_names()

    if "predictions" in table_names:
        columns = {column["name"] for column in inspector.get_columns("predictions")}
        if "risk_level" not in columns:
            with engine.begin() as connection:
                connection.execute(
                    text("ALTER TABLE predictions ADD COLUMN risk_level VARCHAR(20)")
                )


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    sync_mvp_schema()
    yield


app = FastAPI(
    title="Churn Prediction API",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def healthcheck():
    return {"status": "ok"}


app.include_router(customers.router)
app.include_router(predictions.router)
app.include_router(explanations.router)
