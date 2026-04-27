import pytest
from sqlalchemy import select

from backendapi.models.user_models import User


@pytest.mark.asyncio
async def test_create_user(session):
    new_user = User(email='test@test.com', password='123456', cpf=1)
    session.add(new_user)
    await session.commit()

    get_user = await session.scalar(select(User).where(User.cpf == 1))

    assert get_user.email == 'test@test.com'
