from django.apps import AppConfig

class ProjectConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.project'

    def ready(self) -> None:
        from apps.project.signals import set_request_locals, clear_request_locals
        from django.core.signals import request_finished, request_started
        request_started.connect(set_request_locals)
        request_finished.connect(clear_request_locals)
        # 数据完整性标签信号（7.1.7）：受保护模型写后刷新标签、删后清理并留痕
        from apps.project.tools.integrity_signals import connect_signals
        connect_signals()
