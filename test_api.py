import requests
import json

BASE_URL = "http://localhost:8000"


def test_full_workflow():
    print("Testing Mini-CRM API...")
    print("=" * 50)

    print("\n1. Creating operators...")
    operator1 = requests.post(f"{BASE_URL}/operators", json={
        "name": "Ivan Petrov",
        "is_active": True,
        "max_load": 10
    })
    print(f"Operator 1: {operator1.json()}")

    operator2 = requests.post(f"{BASE_URL}/operators", json={
        "name": "Maria Sidorova",
        "is_active": True,
        "max_load": 5
    })
    print(f"Operator 2: {operator2.json()}")

    print("\n2. Creating source...")
    source = requests.post(f"{BASE_URL}/sources", json={
        "name": "telegram_bot_1",
        "description": "Main Telegram bot"
    })
    print(f"Source: {source.json()}")
    source_id = source.json()["id"]

    print("\n3. Setting weights for source...")
    weights = requests.post(f"{BASE_URL}/sources/{source_id}/weights", json={
        "weights": [
            {"operator_id": 1, "weight": 3.0},
            {"operator_id": 2, "weight": 2.0}
        ]
    })
    print(f"Weights: {weights.json()}")

    print("\n4. Creating contacts...")
    for i in range(5):
        contact = requests.post(f"{BASE_URL}/contacts", json={
            "source_name": "telegram_bot_1",
            "phone": f"+7999123456{i}",
            "name": f"Client {i+1}",
            "message": f"Hello, this is message {i+1}"
        })
        print(f"Contact {i+1}: operator_id={contact.json()['operator_id']}")

    print("\n5. Getting all operators with load...")
    operators = requests.get(f"{BASE_URL}/operators")
    for op in operators.json():
        print(f"Operator {op['name']}: load {op['current_load']}/{op['max_load']}")

    print("\n6. Getting statistics...")
    stats = requests.get(f"{BASE_URL}/leads/statistics")
    print(json.dumps(stats.json(), indent=2))

    print("\n7. Getting all leads...")
    leads = requests.get(f"{BASE_URL}/leads")
    print(f"Total leads: {len(leads.json())}")

    print("\n" + "=" * 50)
    print("All tests completed successfully!")


if __name__ == "__main__":
    try:
        test_full_workflow()
    except requests.exceptions.ConnectionError:
        print("Error: Cannot connect to API. Make sure the server is running:")
        print("uvicorn app.main:app --reload")
    except Exception as e:
        print(f"Error: {e}")
