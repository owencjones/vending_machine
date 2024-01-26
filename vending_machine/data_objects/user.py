from sqlalchemy import Boolean, Column, Enum, Integer, String

from vending_machine.database import Base

from .role import Role


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    deposit = Column(Integer)
    role = Column(Enum(Role))
    hashed_password = Column(String)
    disabled = Column(Boolean, default=False)
