from django.views import View
from django import http

from uxhelpers.utils import json_response

import json
import logging

logger = logging.getLogger(__name__)

LEVELS = {
    'CRITICAL': 50,
    'ERROR': 40,
    'WARNING': 30,
    'INFO': 20,
    'DEBUG': 10,
    'NOTSET': 0
}


class LogPostView(View):
    def post(self, request):
        logger.error('received log event from frontend')
        try:
            json_data = json.loads(request.body)
            level = json_data['level']
            logger.log(LEVELS[level], json_data['message'])
        except (ValueError, KeyError):
            logger.warning('Malformed client log received')
        return json_response(request, {'status': 200})
