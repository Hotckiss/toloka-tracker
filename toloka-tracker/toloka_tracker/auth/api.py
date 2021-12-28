from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from dependency_injector.wiring import inject, Provide
from dependencies import Container, Service
from toloka_tracker.auth.models import Token
from toloka_tracker.users.service import get_user_by_login
from toloka_tracker.util.security import AuthService

auth_router = APIRouter()


@auth_router.post("/auth/token/", response_model=Token)
@inject
async def request_token(db: Service = Depends(Provide[Container.db]),
                        body: OAuth2PasswordRequestForm = Depends()):
    db = next(db.get_db())
    auth = AuthService()
    user = get_user_by_login(db, body.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect login",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not auth.check_password(body.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = auth.generate_token({"iss": user.login})
    return {"access_token": access_token, "token_type": "bearer"}