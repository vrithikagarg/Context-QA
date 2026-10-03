from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm

from app.crud import user_crud
from app.api.deps import SessionDep
from app.core import security
from app.core.rate_limit import (
    client_ip,
    login_ip_limiter,
    login_user_limiter,
    raise_if_limited,
)
from app.core.config import settings
from app.models.user_model import Token


router = APIRouter()


@router.post("/login/access-token")
def login_access_token(
    request: Request,
    session: SessionDep,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    ip_key = f"ip:{client_ip(request)}"
    user_key = f"user:{form_data.username.strip().lower()}"
    raise_if_limited(login_ip_limiter, ip_key)
    raise_if_limited(login_user_limiter, user_key)

    user = user_crud.authenticate(
        session=session, email=form_data.username, password=form_data.password
    )
    if not user:
        login_ip_limiter.record(ip_key)
        login_user_limiter.record(user_key)
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    login_user_limiter.clear(user_key)
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return Token(
        access_token=security.create_access_token(
            user.id, expires_delta=access_token_expires
        )
    )
