from flask import Blueprint

accessor_bp = Blueprint(
    'accessor',
    __name__,
    template_folder='../../../templates/accessor/',
    url_prefix='/accessor'
)