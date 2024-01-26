from fastapi import APIRouter, Depends, HTTPException
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from vending_machine.authentication import get_buyer_or_seller_user
from vending_machine.database import get_db
from vending_machine.models.user import (
    User,
    UserCreate,
    UserUpdate,
    UserWithoutPassword,
)

routes = APIRouter()


# Create a user
@routes.post("/users/create", response_model=UserWithoutPassword)
async def create_user(
    user: UserCreate,
    db: AsyncSession = Depends(get_db),
) -> UserWithoutPassword:
    try:
        new_user = User(**user.model_dump())

        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        return UserWithoutPassword(new_user)

    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.errors())
    except Exception as e:
        if routes.app.debug:
            raise HTTPException(status_code=500, detail=str(e))
        else:
            raise HTTPException(status_code=500, detail="Internal server error")


# Retrieve all users
@routes.get("/users", response_model=list[UserWithoutPassword])
async def get_users(
    current_user: UserWithoutPassword = Depends(get_buyer_or_seller_user),
    db: AsyncSession = Depends(get_db),
) -> list[UserWithoutPassword]:
    try:
        assert isinstance(
            current_user, UserWithoutPassword
        ), "User was not authorised"  # Probably unnecessary defensive coding

        users = await db.query(User).all()

        return [UserWithoutPassword(user) for user in users]
    except AssertionError as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    except Exception as e:
        if routes.app.debug:
            raise HTTPException(status_code=500, detail=str(e))
        else:
            raise HTTPException(status_code=500, detail="Internal server error")


# Retrieve a user by id or username
@routes.get("/users/{user_id_or_password}", response_model=UserWithoutPassword)
async def get_user(
    user_id_or_password: str,
    current_user: UserWithoutPassword = Depends(get_buyer_or_seller_user),
    db: AsyncSession = Depends(get_db),
) -> UserWithoutPassword:
    try:
        assert isinstance(
            current_user, UserWithoutPassword
        ), "User was not authorised"  # Probably unnecessary defensive coding

        if user_id_or_password.isdigit():
            user: User = db.query(User).filter(User.id == user_id_or_password).first()
        else:
            user: User = (
                db.query(User).filter(User.username == user_id_or_password).first()
            )

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

    except AssertionError as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return UserWithoutPassword(user)


# Update a user by id or username
@routes.put("/users/{user_id_or_password}", response_model=UserWithoutPassword)
async def update_user(
    user_id_or_password: str,
    user: UserUpdate,
    current_user: UserWithoutPassword = Depends(get_buyer_or_seller_user),
    db: AsyncSession = Depends(get_db),
) -> UserWithoutPassword:
    try:
        assert isinstance(
            current_user, UserWithoutPassword
        ), "User was not authorised"  # Probably unnecessary defensive coding

        if user_id_or_password.isdigit():
            user: User = db.query(User).filter(User.id == user_id_or_password).first()
        else:
            user: User = (
                db.query(User).filter(User.username == user_id_or_password).first()
            )

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        user.update(**user.model_dump())

        await db.commit()
        await db.refresh(user)

    except AssertionError as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return UserWithoutPassword(user)


# Delete a user by id or username
async def delete_user(
    user_id_or_password: str,
    current_user: UserWithoutPassword = Depends(get_buyer_or_seller_user),
    db: AsyncSession = Depends(get_db),
) -> UserWithoutPassword:
    try:
        assert isinstance(
            current_user, UserWithoutPassword
        ), "User was not authorised"  # Probably unnecessary defensive coding

        if user_id_or_password.isdigit():
            user: User = db.query(User).filter(User.id == user_id_or_password).first()
        else:
            user: User = (
                db.query(User).filter(User.username == user_id_or_password).first()
            )

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        await db.delete(user)
        await db.commit()

    except AssertionError as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return UserWithoutPassword(user)
