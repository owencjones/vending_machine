from typing import Literal
from vending_machine.models.session_product import SessionProduct as ORMSessionProduct
from vending_machine.models import BasePydantic


class SessionProduct(BasePydantic):
    id: int
    session_id: int
    product_id: int

    is_orm: Literal[True] = True
    @property
    def orm_model(self) -> ORMSessionProduct:
        return ORMSessionProduct(
            id=self.id,
            session_id=self.session_id,
            product_id=self.product_id,
        )

    class Config:
        from_attributes = True
