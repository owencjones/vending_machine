from pydantic import BaseModel

class SessionProduct(BaseModel):
    id: int
    session_id: int
    product_id: int

    class Config:
        orm_mode = True