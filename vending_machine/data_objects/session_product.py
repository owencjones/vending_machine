from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from vending_machine.database import Base


class SessionProduct(Base):
    __tablename__ = "session_products"

    id: Mapped[str] = mapped_column(Integer, primary_key=True)

    product_id: Mapped[str] = mapped_column(String, ForeignKey("products.id"))
    session_id: Mapped[str] = mapped_column(String, ForeignKey("user_sessions.id"))

    session = relationship("UserSession", back_populates="user_sessions")
    product = relationship("Product", back_populates="products")
