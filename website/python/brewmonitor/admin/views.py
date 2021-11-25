from flask import url_for, redirect

# noinspection PyUnresolvedReferences
import brewmonitor.admin.project_views
# noinspection PyUnresolvedReferences
import brewmonitor.admin.sensor_views
# noinspection PyUnresolvedReferences
import brewmonitor.admin.user_views

from brewmonitor.admin._app import admin_bp


@admin_bp.route('/', methods=['GET'])
def index():
    return redirect(url_for('home.index'))
