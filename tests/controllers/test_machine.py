import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from vending_machine.main import main
from vending_machine.models.product import Product
from vending_machine.models.user import UserWithoutPassword
from vending_machine.models.session import UserSession
from vending_machine.models.session_product import SessionProduct
from datetime import datetime, timedelta
from vending_machine.database import SessionLocal

from tests.fixtures import *  # noqa

from typing import Tuple



def test_get_products(test_client: TestClient, test_products: Tuple[Product, Product]) -> None:
    product1, product2 = test_products

    # Make a request to get the products
    response = test_client.get("/machine/products", dependencies=[(UserWithoutPassword, {"id": 1})])
    assert response.status_code == 200
    assert response.json() == [product1.model_dump(), product2.model_dump()]


def test_deposit(test_client: TestClient) -> None:
    ...


async def test_buy_product(test_client: TestClient) -> None:
    ...


async def test_reset(test_client: TestClient, test_session: SessionLocal, test_products: Tuple[Product, Product]) -> None:
    assert len(test_session.query(UserSession).first().products) == 2

    response = test_client.post("/machine/reset", dependencies=[(UserWithoutPassword, {"id": 1})])

    assert response.status_code == 200

    assert len(test_session.query(UserSession).first().products) == 0


if __name__ == "__main__":

    pytest.main(["-x", __file__])