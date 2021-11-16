import time

from starlette.testclient import TestClient


def test_ping(client: TestClient):
    res = client.get("/api/core/ping")
    assert res.status_code == 200
    assert abs(res.json() - time.time() * 1000) < 1000


def test_ping_db(client: TestClient):
    res = client.get("/api/core/ping-db")
    assert res.status_code == 200
    assert abs(res.json() - time.time()*1000) < 1000


