from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    tenure: Mapped[int] = mapped_column(Integer, nullable=False)
    contract_type: Mapped[str] = mapped_column(String(100), nullable=False)
    monthly_charges: Mapped[float] = mapped_column(Float, nullable=False)
    total_charges: Mapped[float] = mapped_column(Float, nullable=False)
    internet_service: Mapped[str] = mapped_column(String(100), nullable=False)
    tech_support: Mapped[str] = mapped_column(String(100), nullable=False)
    payment_method: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    predictions: Mapped[list["Prediction"]] = relationship(
        back_populates="customer",
        cascade="all, delete-orphan",
    )
    llm_explanations: Mapped[list["LLMExplanation"]] = relationship(
        back_populates="customer",
        cascade="all, delete-orphan",
    )


class Prediction(Base):
    __tablename__ = "predictions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"), nullable=False)
    churn_probability: Mapped[float | None] = mapped_column(Float, nullable=True)
    predicted_label: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    risk_level: Mapped[str | None] = mapped_column(String(20), nullable=True)
    model_version: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    customer: Mapped["Customer"] = relationship(back_populates="predictions")
    llm_explanations: Mapped[list["LLMExplanation"]] = relationship(
        back_populates="prediction",
        cascade="all, delete-orphan",
    )


class LLMExplanation(Base):
    __tablename__ = "llm_explanations"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"), nullable=False)
    prediction_id: Mapped[int | None] = mapped_column(
        ForeignKey("predictions.id"),
        nullable=True,
    )
    explanation_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    recommendations: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    customer: Mapped["Customer"] = relationship(back_populates="llm_explanations")
    prediction: Mapped["Prediction"] = relationship(back_populates="llm_explanations")


class CSVUpload(Base):
    __tablename__ = "csv_uploads"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="uploaded")
    rows_total: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    rows_processed: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
