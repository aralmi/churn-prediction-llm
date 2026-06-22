from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Customer, Prediction
from app.schemas import PredictionResponse
from app.services import ml_service

router = APIRouter(tags=["predictions"])


@router.post(
    "/api/predictions/{customer_id}",
    response_model=PredictionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_prediction(customer_id: int, db: Session = Depends(get_db)):
    """Строит и сохраняет ML-предсказание для клиента."""
    customer = db.get(Customer, customer_id)
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")

    try:
        prediction_data = ml_service.predict_customer_churn(customer)
    except ml_service.ModelNotTrainedError as error:
        raise HTTPException(
            status_code=400,
            detail="Model not found. Run python -m app.ml.train_model first.",
        ) from error

    prediction = Prediction(customer_id=customer.id, **prediction_data)
    db.add(prediction)
    db.commit()
    db.refresh(prediction)
    return prediction


@router.get(
    "/api/customers/{customer_id}/predictions",
    response_model=list[PredictionResponse],
)
def get_customer_predictions(customer_id: int, db: Session = Depends(get_db)):
    """Возвращает все сохраненные предсказания клиента."""
    customer = db.get(Customer, customer_id)
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")

    statement = (
        select(Prediction)
        .where(Prediction.customer_id == customer_id)
        .order_by(Prediction.id)
    )
    return db.execute(statement).scalars().all()
