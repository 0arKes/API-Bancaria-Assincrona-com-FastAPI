from http import HTTPStatus


def test_create_user(client):
    response = client.post(
        '/user/',
        json={
            'email': 'alice@example.com',
            'password': 'secret',
            'cpf': 1234567890,
        },
    )
    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'id': 1,
        'email': 'alice@example.com',
    }


def test_post_user_exist(client, user_test):
    response = client.post(
        '/user/', json={'email': user_test.email, 'password': '123', 'cpf': 5}
    )

    assert response.status_code == HTTPStatus.CONFLICT


def test_read_user(client, user_test):
    response = client.get('/user/')
    assert response.json() == {
        'users': [
            {'email': 'teste@test.com', 'id': 1},
        ]
    }


def test_update_user(client, user_test, token):
    response = client.put(
        '/user/1',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'password': '12356',
        },
    )
    assert response.status_code == HTTPStatus.OK


def test_invalid_id_update_user(client, user_test, token):
    response = client.put(
        f'/user/{user_test.id + 1}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'bob',
            'email': 'bob@example.com',
            'password': 'mynewpassword',
        },
    )
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Not enough permissions'}


def test_delete_user(client, user_test, token):
    response = client.delete(
        '/user/1', headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'msg': 'user deleted'}


def test_invalid_id_delete_user(client, user_test, token):
    response = client.delete(
        f'/user/{user_test.id + 1}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
