from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from backendapi.database import create_session
from backendapi.models.user_models import User
from backendapi.schemas.user_schemas import (
    UserList,
    UserSchema,
    UserSchemaPublic,
    UserUpdate,
)
from backendapi.schemas.utility_schemas import FilterPage
from backendapi.security import (
    get_current_user,
    get_password_hash,
)

GetSession = Annotated[Session, Depends(create_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]

router = APIRouter(prefix='/user', tags=['Users'])


@router.post(
    '/', status_code=HTTPStatus.CREATED, response_model=UserSchemaPublic
)
def create_user(user: UserSchema, session: GetSession):
    user_from_db = session.scalar(
        select(User).where((User.email == user.email) | (User.cpf == user.cpf))
    )
    if user_from_db:
        raise HTTPException(
            HTTPStatus.CONFLICT, detail='email or cpf already exists'
        )

    user_data = User(
        email=user.email,
        password=get_password_hash(user.password),
        cpf=user.cpf,
    )
    session.add(user_data)
    session.commit()
    session.refresh(user_data)
    return user_data


@router.get('/', status_code=HTTPStatus.OK, response_model=UserList)
def read_user(
    session: GetSession, filter_page: Annotated[FilterPage, Query()]
):
    users = session.scalars(
        select(User).offset(filter_page.offset).limit(filter_page.limit)
    ).all()
    return {'users': users}


@router.put(
    '/{user_id}',
    status_code=HTTPStatus.OK,
    response_model=UserSchemaPublic,
)
def update_user(
    user_id: int,
    user: UserUpdate,
    session: GetSession,
    current_user: CurrentUser,
):

    if current_user.id != user_id:
        raise HTTPException(
            HTTPStatus.FORBIDDEN, detail='Not enough permissions'
        )

    if not current_user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='user not found'
        )

    current_user.password = get_password_hash(user.password)
    session.commit()
    session.refresh(current_user)
    return current_user


@router.delete('/{user_id}', status_code=HTTPStatus.OK)
def delete_user(
    user_id: int,
    session: GetSession,
    current_user: CurrentUser,
):

    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail='Not enough permissions'
        )

    if not current_user:
        raise HTTPException(HTTPStatus.NOT_FOUND, detail='User not found')

    session.delete(current_user)
    session.commit()

    return {'msg': 'user deleted'}
