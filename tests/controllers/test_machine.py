import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from vending_machine.main import main
from vending_machine.models.api_messages import ApiMessage
from vending_machine.models.product import Product
from vending_machine.models.user import UserWithoutPassword
from vending_machine.models.session import UserSession
from vending_machine.database import get_db
from vending_machine.models.session_product import SessionProduct
from datetime import datetime, timedelta


client = TestClient(main())


async def test_get_products():
    async with AsyncSession() as session:
        async with session.begin():
            # Create a user session
            user_session = UserSession(user_id=1, expiry_time=datetime.now() + timedelta(hours=1))
            session.add(user_session)
            session.commit()

            # Create some products
            product1 = Product(name="Product 1", price=10)
            product2 = Product(name="Product 2", price=20)
            session.add_all([product1, product2])
            session.commit()

            # Add products to the user session
            user_session.products.extend([product1, product2])
            session.commit()

            # Make a request to get the products
            response = await client.get("/machine/products", dependencies=[(UserWithoutPassword, {"id": 1})])
            assert response.status_code == 200
            assert response.json() == [product1.dict(), product2.dict()]


async def test_deposit():
    async with AsyncSession() as session:
        async with session.begin():
            # Create a user session
            user_session = UserSession(user_id=1, expiry_time=datetime.now() + timedelta(hours=1))
            session.add(user_session)
            session.commit()

            # Make a request to deposit
            response = await client.post(
                "/machine/deposit", json={"amount": 10}, dependencies=[(UserWithoutPassword, {"id": 1})]
            )
            assert response.status_code == 200
            assert response.json() == ApiMessage(message="Deposited successfully", success=True).dict()

            # Check the deposited amount in the user session
            assert user_session.deposited_amount == 10


async def test_buy_product():
    async with AsyncSession() as session:
        async with session.begin():
            # Create a user session
            user_session = UserSession(user_id=1, expiry_time=datetime.now() + timedelta(hours=1))
            session.add(user_session)
            session.commit()

            # Create a product
            product = Product(name="Product 1", price=10)
            session.add(product)
            session.commit()

            # Make a request to buy the product
            response = await client.get("/machine/buy/1/1", dependencies=[(UserWithoutPassword, {"id": 1})])
            assert response.status_code == 200
            assert response.json() == product.dict()

            # Check the deposited amount in the user session
            assert user_session.deposited_amount == 0

            # Check the products in the user session
            assert user_session.products == [product]


async def test_reset():
    async with AsyncSession() as session:
        async with session.begin():
            user_session = UserSession(user_id=1, expiry_time=datetime.now() + timedelta(hours=1))
            session.add(user_session)
            session.commit()

            # Create some session products
            session_product1 = SessionProduct(user_id=1, product_id=1)
            session_product2 = SessionProduct(user_id=1, product_id=2)
            session.add_all([session_product1, session_product2])
            session.commit()

            # Make a request to reset
            response = await client.get("/machine/reset", dependencies=[(UserWithoutPassword, {"id": 1})])
            assert response.status_code == 200
            assert response.json() == True

            # Check that the session products are deleted
            assert session.query(SessionProduct).filter(SessionProduct.user_id == 1).count() == 0


if __name__ == "__main__":

    pytest.main(["-x", __file__])