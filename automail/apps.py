from django.apps import AppConfig


class AutomailConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'automail'

    def ready(self) -> None:
        from . import signals
        return super().ready()