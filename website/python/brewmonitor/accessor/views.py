# noinspection PyUnresolvedReferences
import brewmonitor.accessor.project_views  # noqa
# noinspection PyUnresolvedReferences
import brewmonitor.accessor.sensor_views  # noqa
from brewmonitor.accessor._app import accessor_bp
from flask import url_for
from werkzeug.utils import redirect


@accessor_bp.route('/', methods=['GET'])
def index():
    return redirect(url_for('accessor.all_projects'))
