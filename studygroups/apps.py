from django.apps import AppConfig

class StudyGroupConfig(AppConfig):
    name = 'studygroups'

    def ready(self):
        # importing model classes
        import signals
