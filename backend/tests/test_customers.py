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


def test_create_customer(client):
    response = client.post("/api/customers", json=customer_payload())

    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 1
    assert data["name"] == "Ivan Petrov"


def test_get_customers_list(client):
    client.post("/api/customers", json=customer_payload())

    response = client.get("/api/customers")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Ivan Petrov"


def test_get_customer_by_id(client):
    created = client.post("/api/customers", json=customer_payload()).json()

    response = client.get(f"/api/customers/{created['id']}")

    assert response.status_code == 200
    assert response.json()["name"] == "Ivan Petrov"


def test_delete_customer(client):
    created = client.post("/api/customers", json=customer_payload()).json()

    delete_response = client.delete(f"/api/customers/{created['id']}")
    get_response = client.get(f"/api/customers/{created['id']}")

    assert delete_response.status_code == 204
    assert get_response.status_code == 404
