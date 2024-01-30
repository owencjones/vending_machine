import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from vending_machine.database import Base
from vending_machine.main import main, get_db


@pytest.fixture
def test_client() -> TestClient:
    app = main(testing=True)

    SQLALCHEMY_DATABASE_URL = "sqlite://"  # in-memory database for testing

    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    Base.metadata.create_all(bind=engine)

    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    client = TestClient(app)

    return client


@pytest.fixture
def user_data() -> dict:
    return {
        "username": "testuser",
        "role": "BUYER",
        "password": "testpassword",
    }
