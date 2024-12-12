from django.apps import AppConfig


class DebateConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'debate'

    def ready(self):
        import debate.signals
