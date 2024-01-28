from datetime import datetime

from pydantic import BaseModel

from vending_machine.models.user import User
from vending_machine.models.product import Product


class UserSession(BaseModel):
    id: int
    user_id: int
    expiry_time: datetime
    deposited_amount: int
    
    user: User
    products: list[Product]

    class Config:
        orm_mode = True
