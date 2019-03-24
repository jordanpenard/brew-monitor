import json
from typing import Optional, Iterable, Tuple

import attr
from flask import Response
from flask_csv import send_csv


def json_response(content, status=200, headers=None):
    # type: (..., int, Optional[Iterable[Tuple[str, str]]]) -> Response
    if headers is None:
        headers = []
    response = Response(json.dumps(content), status)
    response.headers['Content-Type'] = 'application/json'
    for hd in headers:
        response.headers[hd[0]] = hd[1]
    return response


def make_csv(data, filename):
    # type: (List[attr.s], str) -> Response

    headers = set()
    entries = []
    for d in data:
        headers.update(attr.fields_dict(d.__class__).keys())
        # This will not work too well for objects that include other attr.s objects.
        entries.append(attr.asdict(d))

    return send_csv(entries, filename, headers)


def export_data(filename, format, data):
    # type: (str, str, List[access.DataPoints]) -> Response

    if format == 'json':
        output = json.dumps([attr.asdict(d) for d in data])
        return json_response(output, headers=(
            ('Content-Disposition', f'attachment; filename={filename}'),
        ))
    elif format == 'csv':
        return make_csv(data, filename)

    return Response('Invalid format', 400)