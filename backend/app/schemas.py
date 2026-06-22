from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

PYDANTIC_CONFIG = ConfigDict(from_attributes=True, protected_namespaces=())


class CustomerBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    tenure: int = Field(..., ge=0)
    contract_type: str = Field(..., min_length=1, max_length=100)
    monthly_charges: float = Field(..., ge=0)
    total_charges: float = Field(..., ge=0)
    internet_service: str = Field(..., min_length=1, max_length=100)
    tech_support: str = Field(..., min_length=1, max_length=100)
    payment_method: str = Field(..., min_length=1, max_length=100)


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(CustomerBase):
    pass


class CustomerResponse(CustomerBase):
    id: int
    created_at: datetime

    model_config = PYDANTIC_CONFIG


class PredictionResponse(BaseModel):
    id: int
    customer_id: int
    churn_probability: float | None
    predicted_label: bool | None
    risk_level: str | None
    model_version: str | None
    created_at: datetime

    model_config = PYDANTIC_CONFIG


class LLMExplanationResponse(BaseModel):
    id: int
    customer_id: int
    prediction_id: int | None
    explanation_text: str | None
    recommendations: str | None
    created_at: datetime

    model_config = PYDANTIC_CONFIG
