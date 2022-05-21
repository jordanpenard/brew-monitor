from http import HTTPStatus

from brewmonitor.admin._app import admin_bp
from brewmonitor.configuration import config
from brewmonitor.decorators import admin_required
from brewmonitor.storage import access
from brewmonitor.storage.tables import Project, User
from flask import request, url_for
from flask_mako import render_template
from werkzeug.exceptions import abort
from werkzeug.utils import redirect


@admin_bp.route('/projects')
@admin_required
def all_projects():
    with config().db_connection() as db_conn:
        users = User.get_all(db_conn)
        projects = Project.get_all(db_conn)
    return render_template('admin_projects.html.mako', projects=projects, users=users)


# Explicit method
@admin_bp.route('/project/<project_id>/delete', methods=['GET'])
@admin_required
def delete_project(project_id):
    project = access.get_project_data(project_id)
    if project is None:
        abort(HTTPStatus.NOT_FOUND)

    access.remove_project(project)
    return redirect(url_for('admin.all_projects'))


@admin_bp.route('/project/<project_id>/edit', methods=['POST'])
@admin_required
def edit_project(project_id):
    name: str = request.form['project_name']
    owner_id: int = int(request.form['project_owner_id'])

    project = access.get_project_data(project_id)
    if project is None:
        abort(HTTPStatus.NOT_FOUND)

    new_owner = access.get_user(owner_id)
    if new_owner is None:
        abort(HTTPStatus.BAD_REQUEST)  # unknown user

    access.edit_project(project, name=name, owner=new_owner)
    return redirect(url_for('admin.all_projects'))
