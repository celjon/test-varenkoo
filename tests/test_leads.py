def test_get_leads(client):
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

    client.post("/contacts", json={
        "source_name": "telegram_bot",
        "phone": "+79991234567",
        "name": "Client 1",
        "message": "Message 1"
    })

    client.post("/contacts", json={
        "source_name": "telegram_bot",
        "phone": "+79991234568",
        "name": "Client 2",
        "message": "Message 2"
    })

    response = client.get("/leads")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


def test_get_statistics(client):
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

    client.post("/contacts", json={
        "source_name": "telegram_bot",
        "phone": "+79991234567",
        "message": "Test"
    })

    response = client.get("/leads/statistics")
    assert response.status_code == 200
    data = response.json()
    assert data["total_contacts"] == 1
    assert data["total_leads"] == 1
    assert data["contacts_with_operator"] == 1
    assert data["contacts_without_operator"] == 0
