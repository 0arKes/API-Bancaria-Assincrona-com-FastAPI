from datetime import datetime, timedelta
from http import HTTPStatus
from zoneinfo import ZoneInfo

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jwt import DecodeError, decode, encode
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backendapi.database import create_session
from backendapi.models.user_models import User
from backendapi.settings import Settings

pwd = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/token')


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(tz=ZoneInfo('UTC')) + timedelta(
        minutes=Settings().ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({'exp': expire})
    encoded_jwt = encode(
        to_encode, Settings().SECRET_KEY, algorithm=Settings().ALGORITHM
    )
    return encoded_jwt


def get_password_hash(password: str):
    return pwd.hash(password)


def verify_password_hash(plain_password: str, hashed_password: str):
    return pwd.verify(plain_password, hashed_password)


async def get_current_user(
    session: AsyncSession = Depends(create_session),
    token: str = Depends(oauth2_scheme),
):

    credentials_exception = HTTPException(
        status_code=HTTPStatus.UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )

    try:
        payload = decode(
            token, Settings().SECRET_KEY, algorithms=[Settings().ALGORITHM]
        )
        subject_email = payload.get('sub')

        if not subject_email:
            raise credentials_exception

    except DecodeError:
        raise credentials_exception

    user_from_db = await session.scalar(
        select(User).where(User.email == subject_email)
    )

    if not user_from_db:
        raise credentials_exception

    return user_from_db
