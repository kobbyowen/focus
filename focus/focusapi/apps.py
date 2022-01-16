from django.apps import AppConfig


class FocusapiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'focusapi'

    def ready(self):
        import focus.signals
