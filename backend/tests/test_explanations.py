from app.routers import explanations as explanations_router
from app.routers import predictions as predictions_router
from app.services import llm_service


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


def test_create_and_get_prediction_explanations(client, monkeypatch):
    created_customer = client.post("/api/customers", json=customer_payload()).json()

    def mock_predict_customer_churn(_customer):
        return {
            "churn_probability": 0.82,
            "predicted_label": True,
            "risk_level": "high",
            "model_version": "mock_model_v1",
        }

    def mock_generate_explanation(_customer, _prediction):
        return {
            "explanation_text": (
                "Краткое объяснение:\n"
                "У клиента высокий риск оттока.\n\n"
                "Основные факторы:\n"
                "1. Помесячный договор.\n"
                "2. Высокая вероятность оттока.\n"
                "3. Отсутствие техподдержки."
            ),
            "recommendations": "1. Предложить скидку.\n2. Подключить техподдержку.",
        }

    monkeypatch.setattr(
        predictions_router.ml_service,
        "predict_customer_churn",
        mock_predict_customer_churn,
    )
    monkeypatch.setattr(
        explanations_router.llm_service,
        "generate_explanation",
        mock_generate_explanation,
    )

    prediction = client.post(f"/api/predictions/{created_customer['id']}").json()
    create_response = client.post(f"/api/explanations/{prediction['id']}")
    list_response = client.get(f"/api/predictions/{prediction['id']}/explanations")

    assert create_response.status_code == 201
    created_explanation = create_response.json()
    assert created_explanation["prediction_id"] == prediction["id"]
    assert "Краткое объяснение:" in created_explanation["explanation_text"]
    assert "Основные факторы:" in created_explanation["explanation_text"]

    assert list_response.status_code == 200
    explanation_list = list_response.json()
    assert len(explanation_list) == 1
    assert "Предложить скидку" in explanation_list[0]["recommendations"]


def test_llm_service_fallback_without_ollama(monkeypatch):
    class StubCustomer:
        name = "Ivan Petrov"
        tenure = 12
        contract_type = "Month-to-month"
        monthly_charges = 79.99
        total_charges = 959.88
        internet_service = "Fiber optic"
        tech_support = "No"
        payment_method = "Electronic check"

    class StubPrediction:
        churn_probability = 0.76
        risk_level = "high"
        predicted_label = True
        model_version = "mock_model_v1"

    def mock_raise_http_error(self, *_args, **_kwargs):
        raise llm_service.httpx.ConnectError("Ollama is offline")

    monkeypatch.setattr(llm_service.httpx.Client, "post", mock_raise_http_error)

    result = llm_service.generate_explanation(StubCustomer(), StubPrediction())

    assert "Краткое объяснение:" in result["explanation_text"]
    assert "Основные факторы:" in result["explanation_text"]
    assert "1." in result["recommendations"]
    assert "churn" not in result["explanation_text"].lower()
    assert "customer" not in result["explanation_text"].lower()


def test_parse_llm_text_postprocesses_english_terms():
    raw_text = """
Краткое объяснение:
У клиента relatively low risk churn, но customer experience может ухудшаться.

Основные факторы:
1. Month-to-month contract
2. Fiber optic
3. Electronic check

Рекомендации:
1. Improve customer experience
2. Reduce churn risk
""".strip()

    result = llm_service.parse_llm_text(raw_text)

    assert "Краткое объяснение:" in result["explanation_text"]
    assert "Основные факторы:" in result["explanation_text"]
    assert "относительно низкая" in result["explanation_text"].lower()
    assert "отток клиентов" in result["explanation_text"].lower()
    assert "клиент" in result["explanation_text"].lower()
