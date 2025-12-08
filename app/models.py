from database import Base
from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
)


class Memo(Base):
    __tablename__ = "memo"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(100), nullable=True)
    content = Column(String(1000), nullable=True)


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True)
    email = Column(String(100))
    hashed_password = Column(String(512))
