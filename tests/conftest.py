import pytest
from starlette.testclient import TestClient

from main import app


@pytest.fixture(scope="module")
def client() -> TestClient:
    client = TestClient(app)
    yield client
