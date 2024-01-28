from sqlalchemy import Column, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship

from vending_machine.database import Base


class UserSession(Base):
    __tablename__ = "user_sessions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    expiry_time = Column(DateTime)
    deposited_amount = Column(Integer)

    user = relationship("User", back_populates="users")
