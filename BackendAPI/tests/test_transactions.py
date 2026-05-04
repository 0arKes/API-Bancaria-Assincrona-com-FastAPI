from http import HTTPStatus

import pytest


@pytest.mark.asyncio
async def test_create_transaction_deposit(client, token, bank_account):
    response = client.post(
        '/transaction/',
        json={
            'account_id': bank_account['account_id'],
            'type_transaction': 'deposit',
            'amount': 50,
        },
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.CREATED


@pytest.mark.asyncio
async def test_create_transaction_withdrawal(client, token, bank_account):
    response = client.post(
        '/transaction/',
        json={
            'account_id': bank_account['account_id'],
            'type_transaction': 'withdrawal',
            'amount': 50,
        },
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.CREATED


@pytest.mark.asyncio
async def test_withdrawal_insufficient_balance(client, token, bank_account):
    response = client.post(
        '/transaction/',
        json={
            'account_id': bank_account['account_id'],
            'type_transaction': 'withdrawal',
            'amount': 9999,
        },
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST


@pytest.mark.asyncio
async def test_transaction_account_not_found(client, token):
    response = client.post(
        '/transaction/',
        json={
            'account_id': 999,
            'type_transaction': 'deposit',
            'amount': 50,
        },
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
def test_read_transactions(client, token, bank_account, transaction):

    response = client.get(
        '/transaction/?offset=0&limit=10',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK

