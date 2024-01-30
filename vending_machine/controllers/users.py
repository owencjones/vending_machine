from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from vending_machine.authentication import get_buyer_or_seller_user, get_password_hash, user_create
from vending_machine.config import settings
from vending_machine.database import get_db
from vending_machine.logging import get_logger
from vending_machine.models.user import (
    User,
    UserCreate,
    UserUpdate,
    UserWithoutPassword,
)

routes = APIRouter()
logger = get_logger(__name__)


# Create a user
@routes.post("/users/create", response_model=UserWithoutPassword, tags=["users"])
async def create_user(
    user: UserCreate,
    db: AsyncSession = Depends(get_db),
) -> UserWithoutPassword:
    """
    Create a new user.

    Args:
        user (UserCreate): The user data to create.
        db (AsyncSession, optional): The database session. Defaults to Depends(get_db).

    Returns:
        UserWithoutPassword: The created user without the password.

    Raises:
        HTTPException: If there is a validation error or an internal server error occurs.
    """

    try:
        new_user = user_create(db, user)
        del user.password  # No longer need this in memory

        return new_user

    except ValidationError as e:
        logger.info(e)
        raise HTTPException(status_code=400, detail=e.errors())
    except Exception as e:
        logger.error(e)
        if settings.debug:
            raise HTTPException(status_code=500, detail=str(e))
        else:
            raise HTTPException(status_code=500, detail="Internal server error")


# Retrieve all users
@routes.get("/users", response_model=list[UserWithoutPassword], tags=["users"])
async def get_users(
    current_user: UserWithoutPassword = Depends(get_buyer_or_seller_user),
    db: AsyncSession = Depends(get_db),
) -> list[UserWithoutPassword]:
    """
    Retrieve a list of users.

    Args:
        current_user (UserWithoutPassword): The current authenticated user.
        db (AsyncSession): The database session.

    Returns:
        list[UserWithoutPassword]: A list of users without their password.

    Raises:
        HTTPException: If the user is not authorized or if there is an internal server error.
    """

    try:
        assert isinstance(current_user, UserWithoutPassword), "User was not authorised"

        users = await db.query(User).all()

        return [UserWithoutPassword(user) for user in users]
    except AssertionError as e:
        logger.info(e)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    except Exception as e:
        logger.error(e)
        if settings.debug:
            raise HTTPException(status_code=500, detail=str(e))
        else:
            raise HTTPException(status_code=500, detail="Internal server error")


# Retrieve a user by id or username
@routes.get(
    "/users/{user_id_or_password}", response_model=UserWithoutPassword, tags=["users"]
)
async def get_user(
    user_id_or_password: str,
    current_user: UserWithoutPassword = Depends(get_buyer_or_seller_user),
    db: AsyncSession = Depends(get_db),
) -> UserWithoutPassword:
    """
    Retrieve a user by their ID or username.

    Args:
        user_id_or_password (str): The ID or username of the user to retrieve.
        current_user (UserWithoutPassword, optional): The current authenticated user. Defaults to Depends(get_buyer_or_seller_user).
        db (AsyncSession, optional): The database session. Defaults to Depends(get_db).

    Returns:
        UserWithoutPassword: The retrieved user.

    Raises:
        HTTPException: If the user is not found or if there is an internal server error.
    """

    try:
        assert isinstance(current_user, UserWithoutPassword), "User was not authorised"

        if user_id_or_password.isdigit():
            user: User = db.query(User).filter(User.id == user_id_or_password).first()
        else:
            user: User = (
                db.query(User).filter(User.username == user_id_or_password).first()
            )

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

    except AssertionError as e:
        logger.info(e)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    except HTTPException as e:
        logger.info(e)
        raise e
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=str(e))

    return UserWithoutPassword(user)


# Update a user by id or username
@routes.put(
    "/users/{user_id_or_password}", response_model=UserWithoutPassword, tags=["users"]
)
async def update_user(
    user_id_or_password: str,
    user: UserUpdate,
    current_user: UserWithoutPassword = Depends(get_buyer_or_seller_user),
    db: AsyncSession = Depends(get_db),
) -> UserWithoutPassword:
    """
    Update a user's information in the database.

    Args:
        user_id_or_password (str): The user's ID or password.
        user (UserUpdate): The updated user information.
        current_user (UserWithoutPassword, optional): The current authenticated user. Defaults to Depends(get_buyer_or_seller_user).
        db (AsyncSession, optional): The database session. Defaults to Depends(get_db).

    Returns:
        UserWithoutPassword: The updated user information without the password.

    Raises:
        HTTPException: If the user is not authorized, the user is not found, or there is an internal server error.
    """

    try:
        assert isinstance(current_user, UserWithoutPassword), "User was not authorised"

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
        logger.info(e)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    except HTTPException as e:
        logger.info(e)
        raise e
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=str(e))

    return UserWithoutPassword(user)


# Delete a user by id or username
@routes.delete(
    "/users/{user_id_or_password}", response_model=UserWithoutPassword, tags=["users"]
)
async def delete_user(
    user_id_or_password: str,
    current_user: UserWithoutPassword = Depends(get_buyer_or_seller_user),
    db: AsyncSession = Depends(get_db),
) -> UserWithoutPassword:
    try:
        assert isinstance(current_user, UserWithoutPassword), "User was not authorised"

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
        logger.info(e)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    except HTTPException as e:
        logger.info(e)
        raise e
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=str(e))

    return UserWithoutPassword(user)
