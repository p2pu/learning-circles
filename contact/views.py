from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from django import http

from .tasks import send_contact_form_inquiry


# Serializers define the API representation.
class ContactSerializer(serializers.Serializer):
    email = serializers.EmailField()
    name =  serializers.CharField(max_length=255)
    content = serializers.CharField()
    source = serializers.CharField(max_length=255)
    organization = serializers.CharField(max_length=255, required=False)

    def create(self, validated_data):
        return validated_data


class ContactAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):
        serializer = ContactSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        # call async task to send email
        send_contact_form_inquiry.delay(**serializer.data)

        if request.GET.get('next') and not request.headers.get('Content-Type') == 'application/json':
            # TODO should this be validated?
            return http.HttpResponseRedirect(request.GET.get('next'))

        data = {"status": "sent"}
        return Response(data)
