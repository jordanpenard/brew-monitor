# noinspection PyUnresolvedReferences
import brewmonitor.admin.project_views  # noqa
# noinspection PyUnresolvedReferences
import brewmonitor.admin.sensor_views  # noqa
# noinspection PyUnresolvedReferences
import brewmonitor.admin.user_views  # noqa
from brewmonitor.admin._app import admin_bp
from flask import redirect, url_for


@admin_bp.route('/', methods=['GET'])
def index():
    return redirect(url_for('home.index'))
