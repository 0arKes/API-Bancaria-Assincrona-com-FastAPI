from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from backendapi.database import create_session
from backendapi.models.user_models import User
from backendapi.schemas.token_schemas import Token
from backendapi.security import (
    creat_access_token,
    verify_password_hash,
)

GetSession = Annotated[Session, Depends(create_session)]
OAuth2Form = Annotated[OAuth2PasswordRequestForm, Depends()]

router = APIRouter(prefix='/token', tags=['Token'])


@router.post('/', response_model=Token)
def get_access_token(
    session: GetSession,
    form_data: OAuth2Form,
):
    user_from_db = session.scalar(
        select(User).where(User.email == form_data.username)
    )
    if not user_from_db:
        raise HTTPException(
            HTTPStatus.NOT_FOUND, detail='Incorrect email or password'
        )

    if not verify_password_hash(form_data.password, user_from_db.password):
        raise HTTPException(
            HTTPStatus.NOT_FOUND, detail='Incorrect email or password'
        )

    access_token = creat_access_token(data={'sub': user_from_db.email})

    return {'access_token': access_token, 'token_type': 'bearer'}
