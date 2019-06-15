# noinspection PyUnresolvedReferences
import brewmonitor.accessor.project_views
# noinspection PyUnresolvedReferences
import brewmonitor.accessor.sensor_views

from flask import url_for
from werkzeug.utils import redirect

from brewmonitor.accessor._app import accessor_bp


@accessor_bp.route('/', methods=['GET'])
def index():
    return redirect(url_for('accessor.all_projects'))