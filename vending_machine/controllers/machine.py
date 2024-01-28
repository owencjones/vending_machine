from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from vending_machine.authentication import get_buyer_or_seller_user, get_buyer_user
from vending_machine.database import get_db
from vending_machine.logging import get_logger
from vending_machine.models.api_messages import ApiResponse
from vending_machine.models.product import Product
from vending_machine.models.session_product import SessionProduct
from vending_machine.models.user import UserWithoutPassword

logger = get_logger(__name__)

routes = APIRouter()


@routes.get("/machine/products", response_model=list[Product], tags=["machine"])
async def get_products(
    current_user: UserWithoutPassword = Depends(get_buyer_user),
    db: AsyncSession = Depends(get_db),
) -> list[Product]: ...


@routes.post("/machine/deposit", response_model=int, tags=["machine"])
async def deposit(
    amount: int,
    current_user: UserWithoutPassword = Depends(get_buyer_or_seller_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse: ...


@routes.get("/machine/buy/{product_id}", response_model=Product, tags=["machine"])
async def buy_product(
    product_id: str,
    current_user: UserWithoutPassword = Depends(get_buyer_user),
    db: AsyncSession = Depends(get_db),
) -> Product: ...


@routes.get("/machine/reset", response_model=bool, tags=["machine"])
async def reset(
    current_user: UserWithoutPassword = Depends(get_buyer_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse:
    try:
        await db.query(SessionProduct).filter(
            SessionProduct.user_id == current_user.id
        ).delete()
        await db.commit()
        return True
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail="Internal server error")
