"""Shared pytest fixtures: isolated in-memory DB + TestClient."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import Base, get_db
from app.main import app


@pytest.fixture()
def client():
    """Fresh in-memory SQLite DB per test, wired through the app dependency."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,  # single shared connection — memory DB survives threads
    )
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
    engine.dispose()


@pytest.fixture()
def student(client):
    """One existing student; returns its response body."""
    resp = client.post(
        "/students",
        json={
            "name": "Aziz Karimov",
            "phone": "+998901234567",
            "group_name": "A-101",
            "monthly_amount": 400000,
        },
    )
    assert resp.status_code == 201
    return resp.json()
