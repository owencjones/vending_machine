import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from vending_machine.database import Base, SessionLocal, get_db
from vending_machine.main import main

from datetime import datetime, timedelta
from vending_machine.models.product import Product
from vending_machine.models.session import UserSession


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
def test_session(test_client: TestClient):
    yield test_client.app.dependency_overrides[get_db]()


@pytest.fixture
def user_data() -> dict:
    return {
        "username": "testuser",
        "role": "BUYER",
        "password": "testpassword",
    }


@pytest.fixture
def test_products(test_session: SessionLocal) -> tuple[Product, Product]:
    # Create a user session
    user_session = UserSession(user_id=1, expiry_time=datetime.now() + timedelta(hours=1))
    test_session.add(user_session)
    test_session.commit()

    # Create some products
    product1 = Product(name="Product 1", price=10)
    product2 = Product(name="Product 2", price=20)
    test_session.add_all([product1, product2])
    test_session.commit()

    # Add products to the user session
    user_session.products.extend([product1, product2])
    test_session.commit()

    return product1, product2