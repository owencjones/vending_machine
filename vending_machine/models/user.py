from typing import Optional

from pydantic import BaseModel

from vending_machine.data_objects.role import Role


class UserBase(BaseModel):
    username: str
    role: Role


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    role: Optional[Role] = None
    deposit: Optional[int] = None


class User(UserBase):
    id: int
    hashed_password: str
    deposit: int = 0

    class Config:
        from_attributes = True


class UserWithoutPassword(User):
    class Config:
        from_attributes = True
        exclude = ["hashed_password"]
