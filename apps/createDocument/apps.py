from django.apps import AppConfig

class CreatedocumentConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.createDocument'

    # 在app准备好时候执行的代码，以后放async、signal等
    def ready(self):
        pass
