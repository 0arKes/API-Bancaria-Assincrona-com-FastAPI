from http import HTTPStatus


def test_home(client):
    response = client.get('/')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'msg': 'teste'}
