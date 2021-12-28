from fastapi import Depends, APIRouter, Request
from dependency_injector.wiring import inject, Provide
from dependencies import Container, Service
from toloka_tracker.auth.service import get_current_user
from toloka_tracker.users.data import UsersDatabase
from toloka_tracker.users.models import User, UserResponse
from toloka_tracker.users.service import get_user_by_id
from toloka_tracker.util.security import AuthService

users_router = APIRouter()


@users_router.get("/users/profile", response_model=UserResponse)
@inject
async def get_authenticated_user(request: Request, current_user=Depends(get_current_user),
                 db: Service = Depends(Provide[Container.db])):
    return get_user_by_id(user_id=current_user.id, db=next(db.get_db()))


@users_router.get("/users/{user_id}", response_model=UserResponse)
@inject
async def get_user(request: Request, user_id: int, db: Service = Depends(Provide[Container.db])):
    return get_user_by_id(user_id=user_id, db=next(db.get_db()))


@users_router.post("/users/create")
@inject
def create_user(user: User, db: Service = Depends(Provide[Container.db])):
    db = next(db.get_db())
    db_user = UsersDatabase(login=user.login, password=AuthService().hashed_password(user.password), tg_chat_id=user.tg_chat_id)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
