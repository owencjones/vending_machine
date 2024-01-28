import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from vending_machine.main import main
from vending_machine.database import get_db
from vending_machine.models.user import UserCreate, UserWithoutPassword


@pytest.fixture(scope="module")
def test_client():
    with TestClient(main()) as client:
        yield client


@pytest.fixture(scope="module")
async def test_db():
    async with AsyncSession() as session:
        yield session


def test_create_user(test_client, test_db):
    user_data = {"username": "testuser", "password": "testpassword", "email": "testuser@example.com"}
    response = test_client.post("/users/create", json=user_data)
    assert response.status_code == 200
    user = response.json()
    assert isinstance(user, UserWithoutPassword)
    assert user.username == user_data["username"]
    assert user.email == user_data["email"]


def test_get_users(test_client, test_db):
    response = test_client.get("/users")
    assert response.status_code == 200
    users = response.json()
    assert isinstance(users, list)
    for user in users:
        assert isinstance(user, UserWithoutPassword)


def test_get_user(test_client, test_db):
    response = test_client.get("/users/1")
    assert response.status_code == 200
    user = response.json()
    assert isinstance(user, UserWithoutPassword)
    assert user.id == 1


def test_update_user(test_client, test_db):
    user_data = {"username": "updateduser", "email": "updateduser@example.com"}
    response = test_client.put("/users/1", json=user_data)
    assert response.status_code == 200
    user = response.json()
    assert isinstance(user, UserWithoutPassword)
    assert user.username == user_data["username"]
    assert user.email == user_data["email"]


def test_delete_user(test_client, test_db):
    response = test_client.delete("/users/1")
    assert response.status_code == 200
    user = response.json()
    assert isinstance(user, UserWithoutPassword)
    assert user.id == 1


if __name__ == "__main__":
    pytest.main(["-s", "-v", __file__])
