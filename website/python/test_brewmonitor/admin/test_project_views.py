from http import HTTPStatus

import pytest
from brewmonitor.storage.tables import Project
from flask import url_for
from test_brewmonitor.conftest import config_from_client


pages = (
    ('GET', 'admin.all_projects', {}),
    ('GET', 'admin.delete_project', dict(project_id=42)),  # id does not matter
    ('POST', 'admin.edit_project', dict(project_id=42)),  # id does not matter
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

    def test_all_projects(self, admin_client):
        resp = admin_client.get(url_for('admin.all_projects'))
        assert resp.status_code == HTTPStatus.OK

    # TODO(tr) add test when deleting an unknown project

    def test_delete_project(self, admin_user, admin_client, other_project):
        resp = admin_client.get(url_for('admin.delete_project', project_id=other_project.id))
        assert resp.status_code == HTTPStatus.FOUND
        assert resp.location == url_for('admin.all_projects', _external=True)

        bm_config = config_from_client(admin_client.application)
        with bm_config.db_connection() as conn:
            assert Project.find(conn, other_project.id) is None, 'project should have been deleted'

    # TODO(tr) add test when editing an unknown project
    # TODO(tr) add test when changing owner in a project

    def test_edit_project(self, admin_user, admin_client, other_project):

        new_name = other_project.name + ' - frozen fermented'

        resp = admin_client.post(
            url_for('admin.edit_project', project_id=other_project.id),
            data={
                'project_name': new_name,
                'project_owner_id': admin_user.id,
            },
        )
        assert resp.status_code == HTTPStatus.FOUND
        assert resp.location == url_for('admin.all_projects', _external=True)

        bm_config = config_from_client(admin_client.application)
        with bm_config.db_connection() as conn:
            updated_project = Project.find(conn, other_project.id)
            assert updated_project.name == new_name
