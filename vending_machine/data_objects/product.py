from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from vending_machine.database import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[str] = mapped_column(Integer, primary_key=True)
    amount_available: Mapped[int] = mapped_column(Integer)
    cost: Mapped[int] = mapped_column(Integer)
    product_name: Mapped[str] = mapped_column(String)
    seller_id: Mapped[str] = mapped_column(Integer, ForeignKey("users.id"))

    seller = relationship("User", back_populates="products")
