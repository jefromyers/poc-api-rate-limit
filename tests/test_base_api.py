import pytest
from app import app
from fastapi.testclient import TestClient

# 🔥🧪 smoke tests!


@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client


@pytest.fixture
def game_id(client):
    resp = client.post("/start")
    assert resp.status_code == 200
    assert "id" in resp.json()
    return resp.json()["id"]


def test_start_game(client):
    resp = client.post("/start")
    assert resp.status_code == 200
    assert "id" in resp.json()


def test_get_game_item(client, game_id):
    resp = client.get(f"/{game_id}/item/")
    assert resp.status_code == 200
    assert "id" in resp.json()
    assert "game_id" in resp.json()
    assert "answer" in resp.json()


def test_get_game_solution(client, game_id):
    resp = client.get(f"/{game_id}/solution/")
    assert resp.status_code == 200
    assert "id" in resp.json()
    assert "rate_limit" in resp.json()
    assert "attempts" in resp.json()


def test_answer(client, game_id):
    resp = client.get(f"/{game_id}/solution/")
    rate_limit = resp.json()["rate_limit"]
    resp = client.get(f"/{game_id}/guess/{rate_limit}")
    assert resp.status_code == 200
    assert resp.json()["correct"]


# close enough!
def test_rate_limiter(client, game_id):
    resp = client.get(f"/{game_id}/solution/")
    rate_limit = resp.json()["rate_limit"]

    for _ in range(rate_limit):
        resp = client.get(f"/{game_id}/item/")
        assert resp.status_code == 200

    resp = client.get(f"/{game_id}/item/")
    assert resp.status_code == 429
