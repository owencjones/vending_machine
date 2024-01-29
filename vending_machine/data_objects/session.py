from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from vending_machine.database import Base


class UserSession(Base):
    __tablename__ = "user_sessions"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"))
    expiry_time: Mapped[DateTime] = mapped_column(DateTime)
    deposited_amount: Mapped[int] = mapped_column(Integer)

    user = relationship("User", back_populates="users")
