from datetime import datetime
from typing import Literal

from vending_machine.models import BasePydantic
from vending_machine.models.product import Product
from vending_machine.models.session import UserSession as ORMUserSession
from vending_machine.models.user import User


class UserSession(BasePydantic):
    id: int
    user_id: int
    expiry_time: datetime
    deposited_amount: int

    user: User
    products: list[Product]

    is_orm: Literal[True] = True

    @property
    def orm_model(self) -> ORMUserSession:
        return ORMUserSession(
            id=self.id,
            user_id=self.user_id,
            expiry_time=self.expiry_time,
            deposited_amount=self.deposited_amount,
        )

    class Config:
        from_attributes = True
