from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Customer, LLMExplanation, Prediction
from app.schemas import LLMExplanationResponse
from app.services import llm_service

router = APIRouter(tags=["explanations"])


@router.post(
    "/api/explanations/{prediction_id}",
    response_model=LLMExplanationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_explanation(prediction_id: int, db: Session = Depends(get_db)):
    """Генерирует и сохраняет LLM-объяснение для prediction."""
    prediction = db.get(Prediction, prediction_id)
    if prediction is None:
        raise HTTPException(status_code=404, detail="Prediction not found")

    customer = db.get(Customer, prediction.customer_id)
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")

    explanation_data = llm_service.generate_explanation(customer, prediction)
    explanation = LLMExplanation(
        customer_id=customer.id,
        prediction_id=prediction.id,
        **explanation_data,
    )
    db.add(explanation)
    db.commit()
    db.refresh(explanation)
    return explanation


@router.get(
    "/api/predictions/{prediction_id}/explanations",
    response_model=list[LLMExplanationResponse],
)
def get_prediction_explanations(prediction_id: int, db: Session = Depends(get_db)):
    """Возвращает все LLM-объяснения для prediction."""
    prediction = db.get(Prediction, prediction_id)
    if prediction is None:
        raise HTTPException(status_code=404, detail="Prediction not found")

    statement = (
        select(LLMExplanation)
        .where(LLMExplanation.prediction_id == prediction_id)
        .order_by(LLMExplanation.id)
    )
    return db.execute(statement).scalars().all()
