from http import HTTPStatus

import pytest
from brewmonitor.storage.tables import User
from flask import url_for
from test_brewmonitor.conftest import config_from_client, find_user


pages = (
    ('GET', 'admin.all_users', {}),
    ('GET', 'admin.delete_user', dict(user_id=42)),  # id does not matter
    ('POST', 'admin.add_user', {}),
)


@pytest.mark.parametrize('method, url_str, kw', pages)
def test_public_views_redirect(public_client, url_str, kw, method):
    target = url_for(url_str, **kw)
    resp = public_client.open(target, method=method)
    assert resp.status_code == HTTPStatus.FOUND
    # redirects to home.index that redirects to accessor.all_projects
    assert resp.location == url_for('home.index', _external=True, next=target)


@pytest.mark.parametrize('method, url_str, kw', pages)
def test_non_admin_views_redirect(user_client, url_str, kw, method):
    target = url_for(url_str, **kw)
    resp = user_client.open(target, method=method)
    assert resp.status_code == HTTPStatus.FOUND
    # redirects to home.index that redirects to accessor.all_projects
    assert resp.location == url_for('home.index', _external=True, next=target)


class TestAdminViews:
    """A logged-in user that is an admin"""

    def test_all_users_views(self, admin_client):
        resp = admin_client.get(url_for('admin.all_users'))
        assert resp.status_code == HTTPStatus.OK

    @pytest.mark.parametrize('is_admin', (True, False))
    def test_add_user(self, admin_client, new_user_data, is_admin):
        if is_admin:
            # checkbox only added to request if ticked
            new_user_data['is_admin'] = 1
        resp = admin_client.post(
            url_for('admin.add_user'),
            data=new_user_data,
        )
        assert resp.status_code == HTTPStatus.FOUND
        assert resp.location == url_for('admin.all_users', _external=True)

        bm_config = config_from_client(admin_client.application)
        with bm_config.db_connection() as conn:
            user = find_user(conn, new_user_data['username'])
            assert user, 'User should have been created'
            assert user.is_admin is is_admin

    # TODO(tr) add test when trying to delete user that does not exist

    @pytest.mark.parametrize('is_admin', (True, False))
    def test_delete_user(self, admin_client, new_user_data, is_admin):
        bm_config = config_from_client(admin_client.application)
        with bm_config.db_connection() as conn:
            new_user = User.create(conn, is_admin=is_admin, **new_user_data)

        resp = admin_client.get(url_for('admin.delete_user', user_id=new_user.id))
        assert resp.status_code == HTTPStatus.FOUND
        assert resp.location == url_for('admin.all_users', _external=True)

        bm_config = config_from_client(admin_client.application)
        with bm_config.db_connection() as conn:
            user = User.find(conn, new_user.id)
            assert user is None, 'User should have been deleted'
