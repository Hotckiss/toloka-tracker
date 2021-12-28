from pydantic import BaseModel
import datetime

class User(BaseModel):
    login: str
    password: str
    tg_chat_id: int


class UserResponse(BaseModel):
    id: int
    login: str
    tg_chat_id: int
    created_at: datetime.datetime
