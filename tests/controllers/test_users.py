import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from vending_machine.main import main
from vending_machine.models.user import UserWithoutPassword


@pytest.fixture(scope="module")
def test_client():
    with TestClient(main()) as client:
        yield client


@pytest.fixture(scope="module")
async def test_db():
    async with AsyncSession() as session:
        yield session

@pytest.mark.parametrize("role", ["BUYER", "SELLER"])
def test_create_user_types(role, test_client):
    user_data = {
        "username": "testuser",
        "role": role,
        "password": "testpassword",
    }
    
    response = test_client.post("/users/create", json=user_data)
    
    assert response.status_code == 200
    user = response.json()

    assert user['username'] == user_data["username"]
    assert user['role'] == user_data["role"]
    assert "password" not in user
    assert "hashed_password" not in user
    assert user.deposit is None


def test_create_seller_user(test_client, test_db):
    user_data = {
        "username": "testuser",
        "role": "SELLER",
        "password": "testpassword",
    }
    
    response = test_client.post("/users/create", json=user_data)
    
    assert response.status_code == 200
    user = response.json()
    
    assert isinstance(user, UserWithoutPassword)
    assert user.username == user_data["username"]
    assert user.role == user_data["role"]
    assert "password" not in user.dict()
    assert "hashed_password" not in user.dict()
    assert user.deposit == 0


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
