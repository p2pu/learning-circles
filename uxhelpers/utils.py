from django import http

import json

def json_response(request, objects):
    data = json.dumps(objects)
    if 'callback' in request.REQUEST:
        data = u'{0}({1});'.format(request.REQUEST['callback'], data)
        return http.HttpResponse(data, 'text/javascript')
    return http.HttpResponse(data, 'application/json')
