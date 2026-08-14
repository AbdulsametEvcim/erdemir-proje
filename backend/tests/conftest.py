import os

os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["LOGIN_USERNAME"] = "testuser"
os.environ["LOGIN_PASSWORD"] = "testpass"
os.environ["AUTH_TOKEN"] = "test-token"

import pytest
from fastapi.testclient import TestClient

from app.database import Base, engine
from app.main import app


@pytest.fixture(autouse=True)
def reset_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def auth_headers():
    return {"Authorization": "Bearer test-token"}
