import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
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


@pytest_asyncio.fixture
async def session():

    engine = create_async_engine(
        'sqlite+aiosqlite:///:memory:',
        connect_args={'check_same_thread': False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.create_all)

    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.drop_all)


@pytest_asyncio.fixture
async def user_test(session):
    password = 'test'
    fake_user = User(
        email='teste@test.com',
        password=get_password_hash(password),
        cpf=1234567890,
    )
    session.add(fake_user)
    await session.commit()
    await session.refresh(fake_user)

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
    return response.json()['access_token']
