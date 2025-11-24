def test_create_source(client):
    response = client.post("/sources", json={
        "name": "telegram_bot",
        "description": "Test Telegram bot"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "telegram_bot"
    assert data["description"] == "Test Telegram bot"


def test_set_operator_weights(client):
    op1 = client.post("/operators", json={
        "name": "Operator 1",
        "is_active": True,
        "max_load": 10
    })
    op2 = client.post("/operators", json={
        "name": "Operator 2",
        "is_active": True,
        "max_load": 5
    })

    source = client.post("/sources", json={
        "name": "test_source",
        "description": "Test"
    })
    source_id = source.json()["id"]

    response = client.post(f"/sources/{source_id}/weights", json={
        "weights": [
            {"operator_id": op1.json()["id"], "weight": 3.0},
            {"operator_id": op2.json()["id"], "weight": 2.0}
        ]
    })
    assert response.status_code == 200
    assert response.json()["message"] == "Weights updated successfully"


def test_set_weights_for_nonexistent_source(client):
    op = client.post("/operators", json={
        "name": "Operator 1",
        "is_active": True,
        "max_load": 10
    })

    response = client.post("/sources/999/weights", json={
        "weights": [
            {"operator_id": op.json()["id"], "weight": 1.0}
        ]
    })
    assert response.status_code == 404
