def test_create_contact_with_distribution(client):
    op = client.post("/operators", json={
        "name": "Operator 1",
        "is_active": True,
        "max_load": 10
    })

    source = client.post("/sources", json={
        "name": "telegram_bot",
        "description": "Test"
    })
    source_id = source.json()["id"]

    client.post(f"/sources/{source_id}/weights", json={
        "weights": [
            {"operator_id": op.json()["id"], "weight": 1.0}
        ]
    })

    response = client.post("/contacts", json={
        "source_name": "telegram_bot",
        "phone": "+79991234567",
        "name": "Test Client",
        "message": "Test message"
    })

    assert response.status_code == 201
    data = response.json()
    assert data["operator_id"] == op.json()["id"]
    assert data["status"] == "new"


def test_create_contact_same_lead_twice(client):
    op = client.post("/operators", json={
        "name": "Operator 1",
        "is_active": True,
        "max_load": 10
    })

    source = client.post("/sources", json={
        "name": "telegram_bot",
        "description": "Test"
    })
    source_id = source.json()["id"]

    client.post(f"/sources/{source_id}/weights", json={
        "weights": [
            {"operator_id": op.json()["id"], "weight": 1.0}
        ]
    })

    contact1 = client.post("/contacts", json={
        "source_name": "telegram_bot",
        "phone": "+79991234567",
        "name": "Test Client",
        "message": "First message"
    })

    contact2 = client.post("/contacts", json={
        "source_name": "telegram_bot",
        "phone": "+79991234567",
        "message": "Second message"
    })

    assert contact1.json()["lead_id"] == contact2.json()["lead_id"]


def test_create_contact_without_available_operators(client):
    source = client.post("/sources", json={
        "name": "telegram_bot",
        "description": "Test"
    })

    response = client.post("/contacts", json={
        "source_name": "telegram_bot",
        "phone": "+79991234567",
        "message": "Test message"
    })

    assert response.status_code == 201
    data = response.json()
    assert data["operator_id"] is None


def test_create_contact_operator_at_max_load(client):
    op = client.post("/operators", json={
        "name": "Operator 1",
        "is_active": True,
        "max_load": 1
    })
    op_id = op.json()["id"]

    source = client.post("/sources", json={
        "name": "telegram_bot",
        "description": "Test"
    })
    source_id = source.json()["id"]

    client.post(f"/sources/{source_id}/weights", json={
        "weights": [
            {"operator_id": op_id, "weight": 1.0}
        ]
    })

    contact1 = client.post("/contacts", json={
        "source_name": "telegram_bot",
        "phone": "+79991234567",
        "message": "First"
    })
    assert contact1.json()["operator_id"] == op_id

    contact2 = client.post("/contacts", json={
        "source_name": "telegram_bot",
        "phone": "+79991234568",
        "message": "Second"
    })
    assert contact2.json()["operator_id"] is None


def test_create_contact_inactive_operator_not_assigned(client):
    op = client.post("/operators", json={
        "name": "Operator 1",
        "is_active": False,
        "max_load": 10
    })

    source = client.post("/sources", json={
        "name": "telegram_bot",
        "description": "Test"
    })
    source_id = source.json()["id"]

    client.post(f"/sources/{source_id}/weights", json={
        "weights": [
            {"operator_id": op.json()["id"], "weight": 1.0}
        ]
    })

    response = client.post("/contacts", json={
        "source_name": "telegram_bot",
        "phone": "+79991234567",
        "message": "Test"
    })

    assert response.status_code == 201
    assert response.json()["operator_id"] is None
