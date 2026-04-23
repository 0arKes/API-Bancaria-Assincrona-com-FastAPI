from http import HTTPStatus


def test_home(client):
    response = client.get('/')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'msg': 'teste'}


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


def test_read_user(client, user_test):
    response = client.get('/user/')
    assert response.json() == {
        'users': [
            {'email': 'teste@test.com', 'id': 1},
        ]
    }


def test_update_user(client, user_test):
    response = client.put(
        '/user/1',
        json={
            'email': 'super@gmail.com',
            'password': '12356',
            'cpf': 123,
        },
    )
    assert response.status_code == HTTPStatus.OK


def test_delete_user(client, user_test):
    response = client.delete('/user/1')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"msg": "user deleted"}
