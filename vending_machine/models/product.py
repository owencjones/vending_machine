from pydantic import BaseModel, Field, root_validator


class ProductBase(BaseModel):
    amountAvailable: int = Field(..., ge=0)
    cost: int = Field(..., multiple_of=5)
    productName: str = Field(..., min_length=1, max_length=50)


class ProductCreate(ProductBase):
    @root_validator
    def validate_amount_available(cls, values):
        if "sellerId" in values:
            # We don't want to allow the user to set the sellerId - it's set from their session
            raise ValueError("Cannot create product with sellerId")

    class Config:
        from_attributes = True
        exclude = ["sellerId"]


class Product(ProductBase):
    id: str
    sellerId: str

    class Config:
        from_attributes = True
