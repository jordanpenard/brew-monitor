from http import HTTPStatus
from typing import Optional, Iterable, Tuple, List, Any

import attr
from flask import Response
from flask_csv import send_csv

from brewmonitor import json
from brewmonitor.storage.tables import Datapoint


def json_response(
    content: Any,
    status: int = HTTPStatus.OK,
    headers: Optional[Iterable[Tuple[str, str]]] = None,
) -> Response:

    if headers is None:
        headers = []
    response = Response(json.dumps(content), status)
    response.headers['Content-Type'] = 'application/json'
    for hd in headers:
        response.headers[hd[0]] = hd[1]
    return response


def make_csv(data: List[attr.s], filename: str) -> Response:

    headers = set()
    entries = []
    for d in data:
        headers.update(attr.fields_dict(d.__class__).keys())
        # This will not work too well for objects that include other attr.s objects.
        entries.append(attr.asdict(d))

    return send_csv(entries, filename, headers)


def export_data(filename: str, _format: str, data: List[Datapoint]) -> Response:

    if _format == 'json':
        output = [attr.asdict(d) for d in data]
        return json_response(output, headers=(
            ('Content-Disposition', f'attachment; filename={filename}'),
        ))
    elif _format == 'csv':
        return make_csv(data, filename)

    return Response('Invalid format', HTTPStatus.BAD_REQUEST)
