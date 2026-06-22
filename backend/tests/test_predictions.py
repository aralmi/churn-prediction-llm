from app.routers import predictions as predictions_router


def customer_payload():
    return {
        "name": "Ivan Petrov",
        "tenure": 12,
        "contract_type": "Month-to-month",
        "monthly_charges": 79.99,
        "total_charges": 959.88,
        "internet_service": "Fiber optic",
        "tech_support": "No",
        "payment_method": "Electronic check",
    }


def test_create_prediction_with_mock_ml_service(client, monkeypatch):
    created_customer = client.post("/api/customers", json=customer_payload()).json()

    def mock_predict_customer_churn(_customer):
        return {
            "churn_probability": 0.82,
            "predicted_label": True,
            "risk_level": "high",
            "model_version": "mock_model_v1",
        }

    monkeypatch.setattr(
        predictions_router.ml_service,
        "predict_customer_churn",
        mock_predict_customer_churn,
    )

    response = client.post(f"/api/predictions/{created_customer['id']}")

    assert response.status_code == 201
    data = response.json()
    assert data["customer_id"] == created_customer["id"]
    assert data["risk_level"] == "high"
    assert data["model_version"] == "mock_model_v1"


def test_get_customer_predictions(client, monkeypatch):
    created_customer = client.post("/api/customers", json=customer_payload()).json()

    def mock_predict_customer_churn(_customer):
        return {
            "churn_probability": 0.41,
            "predicted_label": False,
            "risk_level": "medium",
            "model_version": "mock_model_v1",
        }

    monkeypatch.setattr(
        predictions_router.ml_service,
        "predict_customer_churn",
        mock_predict_customer_churn,
    )

    client.post(f"/api/predictions/{created_customer['id']}")
    client.post(f"/api/predictions/{created_customer['id']}")

    response = client.get(f"/api/customers/{created_customer['id']}/predictions")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["customer_id"] == created_customer["id"]
    assert data[0]["risk_level"] == "medium"
