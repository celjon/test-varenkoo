def test_create_operator(client):
    response = client.post("/operators", json={
        "name": "Test Operator",
        "is_active": True,
        "max_load": 10
    })
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Operator"
    assert data["is_active"] is True
    assert data["max_load"] == 10
    assert data["current_load"] == 0


def test_get_operators(client):
    client.post("/operators", json={
        "name": "Operator 1",
        "is_active": True,
        "max_load": 5
    })
    client.post("/operators", json={
        "name": "Operator 2",
        "is_active": False,
        "max_load": 3
    })

    response = client.get("/operators")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["name"] == "Operator 1"
    assert data[1]["name"] == "Operator 2"


def test_update_operator(client):
    create_response = client.post("/operators", json={
        "name": "Test Operator",
        "is_active": True,
        "max_load": 10
    })
    operator_id = create_response.json()["id"]

    update_response = client.patch(f"/operators/{operator_id}", json={
        "is_active": False,
        "max_load": 15
    })
    assert update_response.status_code == 200
    data = update_response.json()
    assert data["is_active"] is False
    assert data["max_load"] == 15


def test_update_nonexistent_operator(client):
    response = client.patch("/operators/999", json={
        "is_active": False
    })
    assert response.status_code == 404
