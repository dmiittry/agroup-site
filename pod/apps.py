from django.apps import AppConfig


class PodConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'pod'

    def ready(self):
        import pod.signals