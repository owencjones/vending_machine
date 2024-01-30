from pydantic import BaseModel, Field


class ProductBase(BaseModel):
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

    class Config:
        from_attributes = True
