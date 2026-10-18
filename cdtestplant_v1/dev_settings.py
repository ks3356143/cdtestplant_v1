from .settings import *

# ~~~~以下为开发环境对 settings.py 的覆盖（其余配置由 settings.py 统一维护）~~~~

# 调试模式【开发环境有变动】
DEBUG = True

# Mysql数据库【开发环境有变动】
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "HOST": DATABASE_HOST,
        "PORT": 3306,
        "USER": DATABASE_USER,
        "PASSWORD": DATABASE_PASSWORD,
        "NAME": DATABASE_NAME,
    }
}
