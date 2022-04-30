from http import HTTPStatus

from flask import url_for


def test_index_view(public_client):
    resp = public_client.get('/')
    assert resp.status_code == HTTPStatus.FOUND
    # redirects to home.index that redirects to accessor.all_projects
    assert resp.location == url_for('accessor.all_projects', _external=True)


def test_logged_in_index_view(admin_client):
    resp = admin_client.get('/')
    assert resp.status_code == HTTPStatus.FOUND
    # redirects to home.index that redirects to accessor.all_projects
    assert resp.location == url_for('accessor.all_projects', _external=True)
