from vending_machine.models.product import Product as ORMProduct
from typing import Literal
from pydantic import Field
from vending_machine.models import BasePydantic


class ProductBase(BasePydantic):
    amountAvailable: int
    cost: int = Field(..., multiple_of=5)
    productName: str
    sellerId: int


class ProductCreate(ProductBase):
    class Config:
        from_attributes = True
        exclude = ["sellerId"]


class Product(ProductBase):
    id: int

    is_orm: Literal[True] = True
    @property
    def orm_model(self) -> ORMProduct:
        return ORMProduct(
            id=self.id,
            amountAvailable=self.amountAvailable,
            cost=self.cost,
            productName=self.productName,
            sellerId=self.sellerId,
        )

    class Config:
        from_attributes = True
