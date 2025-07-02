from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from django import http
from django.conf import settings

from .tasks import send_contact_form_inquiry

import requests

# Serializers define the API representation.
class ContactSerializer(serializers.Serializer):
    email = serializers.EmailField()
    name =  serializers.CharField(max_length=255)
    content = serializers.CharField()
    source = serializers.CharField(max_length=255)
    organization = serializers.CharField(max_length=255, required=False)
    organization = serializers.CharField(max_length=255, required=False)
    g_recaptcha_response = serializers.CharField(max_length=2048, required=False)

    def create(self, validated_data):
        return validated_data


class ContactAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):
        serializer = ContactSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        # call async task to send email

        recaptcha_response = serializer.data.get('g_recaptcha_response')
        print(recaptcha_response)
        data = {
            'secret': settings.RECAPTCHA_SECRET_KEY,
            'response': recaptcha_response
        }
        r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
        captcha_result = r.json()
        if not captcha_result.get('success'):
            # TODO track metric somewhere?
            print(captcha_result)
            return Response({"status": "error", "errors": '1011010010010010111'})

        send_contact_form_inquiry.delay(**serializer.data)

        if request.GET.get('next') and not request.headers.get('Content-Type') == 'application/json':
            # TODO should this be validated?
            return http.HttpResponseRedirect(request.GET.get('next'))

        data = {"status": "sent"}
        return Response(data)
