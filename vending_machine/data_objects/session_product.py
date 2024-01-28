from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

from vending_machine.database import Base


class SessionProduct(Base):
    __tablename__ = "session_products"

    id = Column(Integer, primary_key=True)

    product_id = Column(Integer, ForeignKey("products.id"))
    session_id = Column(Integer, ForeignKey("user_sessions.id"))

    session = relationship("UserSession", back_populates="user_sessions")
    product = relationship("Product", back_populates="products")
