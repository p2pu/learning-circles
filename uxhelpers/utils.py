from django import http
from django.core.serializers.json import DjangoJSONEncoder

import json

def json_response(request, objects):
    data = json.dumps(objects, cls=DjangoJSONEncoder)
    if 'callback' in request.REQUEST:
        data = u'{0}({1});'.format(request.REQUEST['callback'], data)
        return http.HttpResponse(data, 'text/javascript')
    return http.HttpResponse(data, 'application/json')
