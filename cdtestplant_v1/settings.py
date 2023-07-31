from pathlib import Path
from conf.env import *
import datetime

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-gng$@ebwaxy7bsc86r5pc&$(h8a8+to0v1rbzc9+vkopuv6j-g'

INSTALLED_APPS = [
    'simpleui',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # 第三方包
    'ninja_extra',
    'ninja_jwt',
    'tinymce',
    # apps
    'apps.user',
    'apps.dict',
    'apps.project'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'cdtestplant_v1.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates']
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'cdtestplant_v1.wsgi.application'
# Mysql数据库
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "HOST": DATABASE_HOST,
        "PORT": DATABASE_PORT,
        "USER": DATABASE_USER,
        "PASSWORD": DATABASE_PASSWORD,
        "NAME": DATABASE_NAME,
    }
}

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_TZ = True
# 静态文件目录
STATIC_URL = 'static/'
# 默认ORM主键pk
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
# token 有效时间 时 分 秒（暂未使用）
TOKEN_LIFETIME = 12 * 60 * 60
# User表去找我们自定义的
AUTH_USER_MODEL = 'user.Users'
USERNAME_FIELD = 'username'
ALL_MODELS_OBJECTS = []  # 所有app models 对象

# JWT配置
NINJA_JWT = {
    # token类型，其他方案：SlidingToken
    "AUTH_TOKEN_CLASSES": ("ninja_jwt.tokens.AccessToken",),
    # token失效时间
    "ACCESS_TOKEN_LIFETIME": datetime.timedelta(hours=1),
    "REFRESH_TOKEN_LIFETIME": datetime.timedelta(days=1),
}
# Extra配置
NINJA_EXTRA={

}