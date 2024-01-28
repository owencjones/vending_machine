from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from vending_machine.authentication import (
    authenticate_user,
    create_access_token,
    get_buyer_or_seller_user,
)
from vending_machine.config import settings
from vending_machine.logging import get_logger
from vending_machine.models.token import Token
from vending_machine.models.user import User, UserWithoutPassword

routes = APIRouter()
logger = get_logger(__name__)


@routes.post("/auth/whoami", response_model=UserWithoutPassword, tags=["auth"])
async def whoami(user: User = Depends(get_buyer_or_seller_user)):
    """
    Returns the user information without the password.

    Parameters:
    - user (User): The user object.

    Returns:
    - UserWithoutPassword: The user information without the password.
    """
    return UserWithoutPassword(user)


@routes.post("/auth/token", response_model=Token, tags=["auth"])
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> Token:
    """
    Authenticates a user and generates an access token.

    Args:
        form_data (OAuth2PasswordRequestForm): The form data containing the username and password.

    Returns:
        Token: The generated access token.

    Raises:
        HTTPException: If the user fails to authenticate.
    """
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        logger.info(f"User {form_data.username} failed to authenticate")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(seconds=settings.jwt_timeout)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    logger.info(f"User {form_data.username} authenticated successfully")
    return Token(access_token=access_token, token_type="bearer")
