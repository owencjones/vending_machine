import pytest
from vending_machine.models.user import UserWithoutPassword

from tests.fixtures import *  # noqa





@pytest.mark.parametrize("role", ["BUYER", "SELLER"])
def test_create_user_types(role, test_client, user_data):
    """
    Tests that we can create a user with a role of either BUYER or SELLER

    Runs two tests, parameterised
    """
    user_data["role"] = role

    response = test_client.post("/users/create", json=user_data)

    assert response.status_code == 200
    user = response.json()

    assert user["username"] == user_data["username"]
    assert user["role"] == user_data["role"]
    assert "password" not in user
    assert "hashed_password" not in user
    assert user.deposit is None


def test_cannot_create_user_with_invalid_role(test_client, user_data):
    user_data["role"] = "THIS IS NOT A VALID ROLE"

    response = test_client.post("/users/create", json=user_data)

    assert response.status_code != 200 and (400 <= response.status_code < 500)
    user = response.json()

    assert "errors" in user


def test_cannot_create_user_with_deposited_amount(test_client, user_data):
    user_data["deposit"] = 100

    response = test_client.post("/users/create", json=user_data)

    assert response.status_code != 200 and (400 <= response.status_code < 500)
    user = response.json()

    assert "errors" in user


def test_cannot_create_user_with_clashing_username(test_client, user_data):
    response = test_client.post("/users/create", json=user_data)

    assert response.status_code == 200

    response = test_client.post("/users/create", json=user_data)

    assert response.status_code != 200 and (400 <= response.status_code < 500)
    user = response.json()

    assert "errors" in user


def test_get_users(test_client):
    response = test_client.get("/users")
    assert response.status_code == 200
    users = response.json()
    assert isinstance(users, list)
    for user in users:
        assert isinstance(user, UserWithoutPassword)


def test_get_user(test_client):
    response = test_client.get("/users/1")
    assert response.status_code == 200
    user = response.json()
    assert isinstance(user, UserWithoutPassword)
    assert user.id == 1


def test_cannot_retrieve_non_existent_user(test_client):
    response = test_client.get("/users/100")
    assert response.status_code == 404
    user = response.json()
    assert user == {"detail": "User not found"}


@pytest.mark.parametrize("updateable_field, updateable", [
    ("id", False),
    ("username", False),
    ("role", True),
    ("deposit", True),
    ("hashed_password", False),
])
def test_update_user_can_update_only_certain_parameters(updateable_field:str , updateable:bool, test_client) -> None:
    ...


def test_cannot_update_non_existent_user(test_client):
    ...


def test_delete_user(test_client):
    response = test_client.delete("/users/1")
    assert response.status_code == 200
    user = response.json()
    assert isinstance(user, UserWithoutPassword)
    assert user.id == 1

def test_cannot_delete_non_existent_user(test_client):
    ...


if __name__ == "__main__":
    pytest.main(["-s", "-v", __file__])
