from http import HTTPStatus

from flask import request, url_for
from flask_mako import render_template
from werkzeug.exceptions import abort
from werkzeug.utils import redirect

from brewmonitor.admin._app import admin_bp
from brewmonitor.decorators import admin_required
from brewmonitor.storage import access


@admin_bp.route('/users')
@admin_required
def all_users():
    users = access.get_users()
    return render_template('admin_users.html.mako', users=users)


@admin_bp.route('/users/add', methods=['POST'])
@admin_required
def add_user():
    username = request.form['username']
    password = request.form['password']
    is_admin = bool(request.form['is_admin'])

    access.insert_user(username, password, is_admin)
    return redirect(url_for('admin.all_users'))


@admin_bp.route('/user/<user_id>/delete', methods=['GET'])
@admin_required
def delete_user(user_id):
    user = access.get_user(user_id)
    if user is None:
        abort(HTTPStatus.NOT_FOUND)

    access.remove_user(user)
    return redirect(url_for('admin.all_users'))
