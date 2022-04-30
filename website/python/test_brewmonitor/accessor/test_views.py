from http import HTTPStatus

from flask import url_for


def test_index_view(public_client):
    resp = public_client.get('/')
    assert resp.status_code == HTTPStatus.FOUND
    assert resp.location == url_for('accessor.all_projects', _external=True)
