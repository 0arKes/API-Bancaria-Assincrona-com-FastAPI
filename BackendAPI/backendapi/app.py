from http import HTTPStatus

from fastapi import Depends, FastAPI, HTTPException
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

app = FastAPI(title='API Sitema Bancário')


@app.get('/')
def read_root():
    return {'msg': 'teste'}


@app.post(
    '/user/', status_code=HTTPStatus.CREATED, response_model=UserSchemaPublic
)
def create_user(user: UserSchema, session: Session = Depends(create_session)):
    user_from_db = session.scalar(
        select(User).where((User.email == user.email) | (User.cpf == user.cpf))
    )
    if user_from_db:
        raise HTTPException(
            HTTPStatus.CONFLICT, detail='email or cpf already exists'
        )

    user_data = User(
        email=user.email,
        password=user.password,
        cpf=user.cpf,
    )
    session.add(user_data)
    session.commit()
    session.refresh(user_data)
    return user_data


@app.get('/user/', status_code=HTTPStatus.OK, response_model=UserList)
def read_user(
    skip: int = 0, limit: int = 10, session: Session = Depends(create_session)
):
    users = session.scalars(select(User).offset(skip).limit(limit)).all()
    return {'users': users}


@app.put(
    '/user/{user_id}',
    status_code=HTTPStatus.OK,
    response_model=UserSchemaPublic,
)
def update_user(
    user_id: int, user: UserUpdate, session: Session = Depends(create_session)
):

    user_from_db = session.scalar(select(User).where(User.id == user_id))

    if not user_from_db:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='user not found'
        )

    user_from_db.password = user.password
    session.commit()
    session.refresh(user_from_db)
    return user_from_db


@app.delete('/user/{user_id}', status_code=HTTPStatus.OK)
def delete_user(user_id: int, session: Session = Depends(create_session)):
    user_from_db = session.scalar(select(User).where(User.id == user_id))
    if not user_from_db:
        raise HTTPException(HTTPStatus.NOT_FOUND, detail='User not found')

    session.delete(user_from_db)
    session.commit()

    return {'msg': 'user deleted'}
