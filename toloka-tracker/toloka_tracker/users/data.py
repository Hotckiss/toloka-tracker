from sqlalchemy import Column, String, Integer, DateTime
import datetime
from dependencies import Base


class UsersDatabase(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    login = Column(String, unique=True)
    password = Column(String)
    tg_chat_id = Column(Integer)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
