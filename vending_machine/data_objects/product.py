from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from vending_machine.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    amount_available = Column(Integer)
    cost = Column(Integer)
    product_name = Column(String)
    seller_id = Column(Integer, ForeignKey("users.id"))

    seller = relationship("User", back_populates="products")
