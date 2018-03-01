from django.apps import AppConfig

class CustomRegistrationConfig(AppConfig):
    name = 'custom_registration'

    def ready(self):
        # importing model classes
        import custom_registration.signals
