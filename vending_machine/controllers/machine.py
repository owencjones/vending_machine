from fastapi import APIRouter, Depends, HTTPException
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from vending_machine.authentication import get_buyer_or_seller_user, get_seller_user
from vending_machine.database import get_db
from vending_machine.models.user import UserWithoutPassword
from vending_machine.models.product import Product
from vending_machine.models.session_product import SessionProduct

routes = APIRouter()


@routes.post("/machine/deposit", response_model=int)
async def deposit(
    amount: int,
    current_user: UserWithoutPassword = Depends(get_buyer_or_seller_user),
    db: AsyncSession = Depends(get_db),
) -> int:
    ...


@routes.get("/machine/buy/{product_id}", response_model=Product)
async def buy_product(
    product_id: str,
    current_user: UserWithoutPassword = Depends(get_buyer_or_seller_user),
    db: AsyncSession = Depends(get_db),
) -> Product:
    ...


@routes.get("/machine/reset", response_model=bool)
async def reset(
    current_user: UserWithoutPassword = Depends(get_seller_user),
    db: AsyncSession = Depends(get_db),
) -> bool:
    try:
        await db.query(SessionProduct).filter(SessionProduct.user_id == current_user.id).delete()
        await db.commit()
        return True
    except Exception as e:
        routes.app.logger.error(e)
        raise HTTPException(status_code=500, detail="Internal server error")
