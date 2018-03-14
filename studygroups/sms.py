from django.conf import settings

from twilio.rest import Client

def send_message(to, body):
    client = Client(
        settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN 
    )
    message = client.messages.create(
        body=body,
        to=to,
        from_=settings.TWILIO_NUMBER
    )
