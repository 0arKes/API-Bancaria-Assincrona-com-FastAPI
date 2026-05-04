from http import HTTPStatus

import pytest


@pytest.mark.asyncio
async def test_create_account(client, token):
    response = client.post(
        '/bank/',
        json={'balance': 100},
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.CREATED


@pytest.mark.asyncio
async def test_create_with_negative_balance(client, token):
    response = client.post(
        '/bank/',
        json={'balance': -100},
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST


@pytest.mark.asyncio
async def test_get_account_extract(client, token, bank_account, transaction):
    response = client.get(
        f'/bank/{bank_account["account_id"]}/',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK


@pytest.mark.asyncio
async def test_get_account_not_found(client, token):
    response = client.get(
        '/bank/999/',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
