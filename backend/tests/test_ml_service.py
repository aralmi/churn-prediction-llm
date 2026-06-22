from types import SimpleNamespace

from app.services import ml_service


class StubModel:
    def predict_proba(self, _features):
        return [[0.35, 0.65]]


def test_predict_customer_churn_uses_threshold_from_metrics(tmp_path, monkeypatch):
    metrics_path = tmp_path / "metrics.json"
    metrics_path.write_text('{"best_threshold": 0.7}', encoding="utf-8")

    monkeypatch.setattr(ml_service, "METRICS_PATH", metrics_path)
    monkeypatch.setattr(ml_service, "load_model", lambda: StubModel())

    customer = SimpleNamespace(
        tenure=12,
        contract_type="Month-to-month",
        monthly_charges=79.99,
        total_charges=959.88,
        internet_service="Fiber optic",
        tech_support="No",
        payment_method="Electronic check",
    )

    result = ml_service.predict_customer_churn(customer)

    assert result["churn_probability"] == 0.65
    assert result["predicted_label"] is False
    assert result["risk_level"] == "medium"
