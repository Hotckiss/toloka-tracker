from dependency_injector.wiring import inject, Provide
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from dependencies import Container, Service
from toloka_tracker.users.service import get_user_by_login
from toloka_tracker.util.security import AuthService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


@inject
async def get_current_user(db: Service = Depends(Provide[Container.db]), token: str = Depends(oauth2_scheme)):
    auth = AuthService()
    user_data = auth.decode_token(token)
    if user_data.get("iss") is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unable to determine user login",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = get_user_by_login(next(db.get_db()), user_data.get("iss"))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unable to extract user: either it was deleted or token is invalid",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
