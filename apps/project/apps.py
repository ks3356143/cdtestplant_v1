from django.apps import AppConfig

class ProjectConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.project'

    def ready(self) -> None:
        from apps.project.signals import set_request_locals, clear_request_locals
        from django.core.signals import request_finished, request_started
        request_started.connect(set_request_locals)
        request_finished.connect(clear_request_locals)
