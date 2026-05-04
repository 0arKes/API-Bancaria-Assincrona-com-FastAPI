from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backendapi.database import create_session
from backendapi.models.models import BankAccount, Transaction, User
from backendapi.schemas.bank_account import (
    AccountExtract,
    AccountPublic,
    CreateAccount,
)
from backendapi.security import (
    get_current_user,
)

router = APIRouter(prefix='/bank', tags=['bank'])


GetSession = Annotated[AsyncSession, Depends(create_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post('/', status_code=HTTPStatus.CREATED, response_model=AccountPublic)
async def create_bank_account(
    account: CreateAccount,
    user: CurrentUser,
    session: GetSession,
):
    if account.balance < 0:
        raise HTTPException(
            HTTPStatus.BAD_REQUEST, detail='Initial balance cannot be negative'
        )

    db_account = BankAccount(
        owner_id=user.id,
        balance=account.balance,
    )
    session.add(db_account)
    await session.commit()
    await session.refresh(db_account)

    return db_account


@router.get(
    '/{account_id}/', response_model=AccountExtract, status_code=HTTPStatus.OK
)
async def get_account_extract(
    account_id: int, session: GetSession, user: CurrentUser
):

    account = await session.get(BankAccount, account_id)

    if not account:
        raise HTTPException(HTTPStatus.NOT_FOUND, detail='Account not found')

    if account.owner_id != user.id:
        raise HTTPException(HTTPStatus.FORBIDDEN, 'Not allowed')

    result = await session.scalars(
        select(Transaction)
        .where(Transaction.account_id == account_id)
        .order_by(Transaction.created_at.desc())
    )

    transactions = result.all()

    return {'balance': account.balance, 'transactions': transactions}
