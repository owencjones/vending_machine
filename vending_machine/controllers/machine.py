from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from vending_machine.authentication import get_buyer_or_seller_user, get_buyer_user
from vending_machine.config import settings
from vending_machine.database import get_db
from vending_machine.logging import get_logger
from vending_machine.models.api_messages import ApiMessage
from vending_machine.models.product import Product
from vending_machine.models.session import UserSession
from vending_machine.models.session_product import SessionProduct
from vending_machine.models.user import UserWithoutPassword

logger = get_logger(__name__)

routes = APIRouter()


async def __get_user_session(
    current_user: UserWithoutPassword = Depends(get_buyer_user),
    db: AsyncSession = Depends(get_db),
) -> Optional[UserSession]:
    return (
        await db.query(UserSession)
        .filter(
            UserSession.user_id == current_user.id,
            UserSession.expiry_time > datetime.now(),
        )
        .last()
    )


@routes.get("/machine/products", response_model=list[Product], tags=["machine"])
async def get_products(
    current_user: UserWithoutPassword = Depends(get_buyer_user),
    db: AsyncSession = Depends(get_db),
) -> list[Product]:
    try:
        user_session = await __get_user_session(current_user, db)

        if not user_session:
            raise HTTPException(status_code=404, detail="Session not found")

        return user_session.products
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=500,
            detail="Internal server error" if not settings.debug else str(e),
        )


@routes.post("/machine/deposit", response_model=int, tags=["machine"])
async def deposit(
    amount: int,
    current_user: UserWithoutPassword = Depends(get_buyer_or_seller_user),
    db: AsyncSession = Depends(get_db),
) -> ApiMessage:
    try:
        assert amount > 0, "Amount must be greater than 0"
        assert amount in [
            5,
            10,
            20,
            50,
            100,
        ], "Amount must be one of the following coins: 5, 10, 20, 50, 100"

        user_session = await __get_user_session(current_user, db)
        if not user_session:
            raise HTTPException(status_code=404, detail="Session not found")

        user_session.deposited_amount += amount
        await db.commit()
        return ApiMessage(message="Deposited successfully", success=True)
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=500,
            detail="Internal server error" if not settings.debug else str(e),
        )


@routes.get(
    "/machine/buy/{product_id}/{amount}", response_model=Product, tags=["machine"]
)
async def buy_product(
    product_id: str,
    amount: int,
    current_user: UserWithoutPassword = Depends(get_buyer_user),
    db: AsyncSession = Depends(get_db),
) -> Product:
    try:
        assert amount > 0, "Amount must be greater than 0"

        user_session = await __get_user_session(current_user, db)
        if not user_session:
            raise HTTPException(status_code=404, detail="Session not found")

        product = await db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        if product.price > user_session.deposited_amount:
            raise HTTPException(status_code=400, detail="Insufficient funds")

        user_session.deposited_amount -= product.price * amount
        user_session.products.append(product * amount)

        await db.commit()
        return product
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=500,
            detail="Internal server error" if not settings.debug else str(e),
        )


@routes.get("/machine/reset", response_model=bool, tags=["machine"])
async def reset(
    current_user: UserWithoutPassword = Depends(get_buyer_user),
    db: AsyncSession = Depends(get_db),
) -> ApiMessage:
    try:
        await db.query(SessionProduct).filter(
            SessionProduct.user_id == current_user.id
        ).delete()
        await db.commit()
        return True
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail="Internal server error")
