from datetime import datetime, timedelta, timezone
from typing import Annotated
from uuid import uuid4

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from vending_machine.config import settings
from vending_machine.data_objects.role import Role
from vending_machine.database import SessionLocal
from vending_machine.models.session import UserSession
from vending_machine.models.session_product import SessionProduct
from vending_machine.models.token import TokenData
from vending_machine.models.user import User, UserCreate, UserWithoutPassword
from vending_machine.data_objects.user import User as UserOrm

app = FastAPI()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def _verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def _get_user(db: SessionLocal, username: str):
    return app.db.query(User).filter(User.username == username).first()


def authenticate_user(
    db: SessionLocal, username: str, password: str
) -> UserWithoutPassword | bool:
    user = _get_user(db, username)
    if not user:
        return False
    if not _verify_password(password, user.hashed_password):
        return False
    return UserWithoutPassword(**user.dict())


def user_create(db: SessionLocal, user: UserCreate) -> UserWithoutPassword:
    user_creation_object = {
        **user.model_dump(),
        **{"hashed_password": get_password_hash(user.password), "id": str(uuid4())},
    }
    del user_creation_object["password"]
    new_user = UserOrm(**user_creation_object)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return UserWithoutPassword(**new_user.__dict__)


def create_access_token(
    db: SessionLocal, data: dict, expires_delta: timedelta | None = None
):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)

    most_recent_session = (
        db.query(UserSession)
        .filter(UserSession.user_id == data["sub"])
        .order_by(UserSession.expiry_time.desc())
        .last()
    )

    if most_recent_session and most_recent_session.expiry_time > datetime.now(
        timezone.utc
    ):
        raise HTTPException(
            status_code=400, detail="Cannot log into a user with an active session"
        )

    db.query(UserSession).filter(UserSession.user_id == data["sub"]).delete()
    db.query(SessionProduct).filter(SessionProduct.user_id == data["sub"]).delete()
    db.commit()

    db.add(
        UserSession(
            user_id=data["sub"],
            expiry_time=expire,
        )
    )

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm
    )

    return encoded_jwt


async def _get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.jwt_secret, algorithms=[settings.jwt_algorithm]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = _get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return UserWithoutPassword(**user.dict())


async def _get_current_active_user(
    current_user: Annotated[UserWithoutPassword, Depends(_get_current_user)]
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_buyer_user(
    current_user: Annotated[UserWithoutPassword, Depends(_get_current_user)]
):
    """
    Retrieves the buyer user from the current user.  Confirms is a buyer user.

    Raises:
        HTTPException: If the current user is not a buyer.
    """
    if current_user.role != Role.buyer:
        raise HTTPException(status_code=400, detail="User is not a buyer")
    return current_user


async def get_seller_user(
    current_user: Annotated[UserWithoutPassword, Depends(_get_current_user)]
):
    """
    Retrieves the seller user from the current user.  Confirms is a seller user.

    Raises:
        HTTPException: If the current user is not a seller.
    """
    if current_user.role != Role.seller:
        raise HTTPException(status_code=400, detail="User is not a seller")
    return current_user


async def get_buyer_or_seller_user(
    current_user: Annotated[UserWithoutPassword, Depends(_get_current_user)]
):
    """
    Retrieves the buyer or seller user from the current user.  Confirms is a buyer or seller user.

    Raises:
        HTTPException: If the current user role is not recognised.
    """

    if current_user.role != Role.buyer and current_user.role != Role.seller:
        raise HTTPException(status_code=400, detail="User is not a buyer or seller")

    return current_user
