from http import HTTPStatus

from flask import url_for

from test_brewmonitor.utils import MultiClientBase


class TestIndexView(MultiClientBase):
    def _check_view(self, client):
        resp = client.get('/')
        assert resp.status_code == HTTPStatus.FOUND
        assert resp.location == url_for('accessor.all_projects', _external=True)
