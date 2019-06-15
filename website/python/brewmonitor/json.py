import datetime
import json


class AdditionalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime.datetime, datetime.date)):
            return obj.isoformat()
        return super(AdditionalEncoder, self).default(obj)


def dumps(data, **kwargs):
    return json.dumps(data, cls=AdditionalEncoder, **kwargs)