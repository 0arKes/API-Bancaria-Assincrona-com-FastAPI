from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

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

GetSession = Annotated[AsyncSession, Depends(create_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]

router = APIRouter(prefix='/user', tags=['Users'])


@router.post(
    '/', status_code=HTTPStatus.CREATED, response_model=UserSchemaPublic
)
async def create_user(user: UserSchema, session: GetSession):
    user_from_db = await session.scalar(
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
    await session.commit()
    await session.refresh(user_data)
    return user_data


@router.get('/', status_code=HTTPStatus.OK, response_model=UserList)
async def read_user(
    session: GetSession, filter_page: Annotated[FilterPage, Query()]
):
    query = await session.scalars(
        select(User).offset(filter_page.offset).limit(filter_page.limit)
    )
    users = query.all()
    return {'users': users}


@router.put(
    '/{user_id}',
    status_code=HTTPStatus.OK,
    response_model=UserSchemaPublic,
)
async def update_user(
    user_id: int,
    user: UserUpdate,
    session: GetSession,
    current_user: CurrentUser,
):

    if current_user.id != user_id:
        raise HTTPException(
            HTTPStatus.FORBIDDEN, detail='Not enough permissions'
        )

    current_user.password = get_password_hash(user.password)
    await session.commit()
    await session.refresh(current_user)
    return current_user


@router.delete('/{user_id}', status_code=HTTPStatus.OK)
async def delete_user(
    user_id: int,
    session: GetSession,
    current_user: CurrentUser,
):

    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail='Not enough permissions'
        )

    await session.delete(current_user)
    await session.commit()

    return {'msg': 'user deleted'}
