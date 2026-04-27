import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from backendapi.app import app
from backendapi.database import create_session
from backendapi.models.user_models import User, table_registry
from backendapi.security import get_password_hash


@pytest.fixture
def client(session):
    def get_session_override():
        return session

    with TestClient(app) as client:
        app.dependency_overrides[create_session] = get_session_override
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
def session():

    engine = create_engine(
        'sqlite:///:memory:',
        connect_args={'check_same_thread': False},
        poolclass=StaticPool,
    )

    table_registry.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

    table_registry.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
def user_test(session):
    password = 'test'
    fake_user = User(
        email='teste@test.com',
        password=get_password_hash(password),
        cpf=1234567890,
    )
    session.add(fake_user)
    session.commit()
    session.refresh(fake_user)

    fake_user.clean_password = password
    return fake_user


@pytest.fixture
def token(client, user_test):
    response = client.post(
        '/token/',
        data={
            'username': user_test.email,
            'password': user_test.clean_password,
        },
    )
    print('============= flag=============')
    print(response.status_code)
    return response.json()['access_token']
