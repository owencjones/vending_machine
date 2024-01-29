from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from vending_machine.data_objects.role import Role
from vending_machine.models import BasePydantic

class UserBase(BaseModel):
    username: str
    role: Role  # Add role field with type Role

    class Config:
        use_enum_values = True  # Use enum values for validation


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    role: Optional[Role] = None
    deposit: Optional[int] = None


class UserNew(UserBase):
    password: str

    class Config:
        from_attributes = True


class User(UserBase, BasePydantic):
    id: UUID

    hashed_password: str
    deposit: int = 0

    @property
    def password(self) -> None:
        # When someone does set a password, we want to ignore it
        return None

    class Config:
        from_attributes = True


class UserWithoutPassword(UserBase):
    id: str
    deposit: int | None = 0

    @property
    def hashed_password(self) -> None:
        # When someone does set a hashed password, we want to ignore it
        return None

    @property
    def password(self) -> None:
        # When someone does set a password, we want to ignore it
        return None

    class Config:
        from_attributes = True
