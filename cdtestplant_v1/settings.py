from pathlib import Path
import os
import datetime
# 导入其他配置：env、ninja_extra、ldap、log
from conf.env import *
from conf.ninja_extra_settings import *
from django_auth_ldap.config import LDAPSearch
from conf.logConfig import LOGGING

BASE_DIR = Path(__file__).resolve().parent.parent

# 生产环境应在 .env 中配置随机生成的 DJANGO_SECRET_KEY；缺省值仅保证本地开发可用
SECRET_KEY = env('DJANGO_SECRET_KEY', default='django-insecure-gng$@ebwaxy7bsc86r5pc&$(h8a8+to0v1rbzc9+vkopuv6j-g')

# 用户敏感字段（电话/邮箱）落库加密密钥（GB/T 28452-2012 7.1.8 用户数据保密性保护）
# 未配置时由 SECRET_KEY 派生；生产环境应在 .env 中显式配置并使用独立固定值。
# 注意：本值一旦变更，历史密文将无法解密，务必先备份再更换。
FIELD_ENCRYPTION_KEY = env('FIELD_ENCRYPTION_KEY', default='')

INSTALLED_APPS = [
    # 'simpleui',
    # 'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    # 'django.contrib.sessions',
    # 'django.contrib.messages',
    'django.contrib.staticfiles',  # TODO:生成环境记得删除，这是为了swagger文档调试用的
    # 第三方包
    'ninja',
    'ninja_extra',
    'ninja_jwt',
    'tinymce',
    # apps
    'apps.user',
    'apps.dict',
    'apps.system',
    'apps.project',
    'apps.createDocument',
    'apps.createSeiTaiDocument',
]

# auth中间件未打开
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # 'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    # 'django.contrib.auth.middleware.AuthenticationMiddleware',
    # 'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 新加入日志记录的中间件
    'utils.log_util.middleware.ApiLoggingMiddleware'
]

# 设置跨域
SECURE_CROSS_ORIGIN_OPENER_POLICY = 'None'

ROOT_URLCONF = 'cdtestplant_v1.urls'

# 模版不需要，生成环境删除 TODO:生成环境记得删除，这是为了swagger文档调试用的
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                # 'django.template.context_processors.debug',
                # 'django.template.context_processors.request',
                # 'django.contrib.auth.context_processors.auth',
                # 'django.contrib.messages.context_processors.messages',
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

# 调试模式
DEBUG = False

# 生产启动校验：关键安全配置缺失时拒绝启动，避免带可预测密钥/未加密配置上线
if not DEBUG:
    from django.core.exceptions import ImproperlyConfigured
    if SECRET_KEY.startswith('django-insecure-'):
        raise ImproperlyConfigured('生产环境必须在 .env 中配置随机的 DJANGO_SECRET_KEY')
    if not FIELD_ENCRYPTION_KEY:
        raise ImproperlyConfigured('生产环境必须在 .env 中配置 FIELD_ENCRYPTION_KEY（变更会导致历史密文无法解密）')

# 配置缓存
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",  # 这里直接使用redis别名作为host ip地址
        # 剩余信息保护（7.1.8 c/f）：缓存键默认 5 分钟过期，避免临时/敏感数据长期驻留
        "TIMEOUT": 300,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            # Windows 绿色版 Redis 5.0.14 仅支持 RESP2；redis-py 8.x 需显式固定，否则 HELLO 命令报错
            "CONNECTION_POOL_KWARGS": {"protocol": 2},
            # "PASSWORD": "yourpassword",  # 换成你自己密码
        },
    }
}

# 密码验证Django处理，rest不需要
# AUTH_PASSWORD_VALIDATORS = [
#     {
#         'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
#     },
#     {
#         'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
#     },
#     {
#         'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
#     },
#     {
#         'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
#     },
# ]

LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_TZ = False  # False时数据库保存本地时间
# 默认ORM主键pk
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
# token 有效时间 时 分 秒（暂未使用）
TOKEN_LIFETIME = 12 * 60 * 60
# User表去找我们自定义的
AUTH_USER_MODEL = 'user.Users'
USERNAME_FIELD = 'username'

# JWT配置
NINJA_JWT = {
    # token类型，其他方案：SlidingToken
    "AUTH_TOKEN_CLASSES": ("ninja_jwt.tokens.AccessToken",),
    # token失效时间，14小时失效
    "ACCESS_TOKEN_LIFETIME": datetime.timedelta(hours=14),
    "REFRESH_TOKEN_LIFETIME": datetime.timedelta(days=1),
}
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=["*"])  # 见 conf/env.py 说明，生产环境应收敛
# 受信反向代理：只有来自这些地址的请求才采信 X-Forwarded-For（默认本机 nginx）
TRUSTED_PROXIES = env.list('TRUSTED_PROXIES', default=['127.0.0.1', '::1'])

# 静态文件目录 - manage.py collectstatic
# -> 会将所有app静态文件移动到STATIC_ROOT目录下面
STATIC_URL = '/static/'
# 静态与媒体目录统一放在项目根下（原为 BASE_DIR/../../，在 Linux 上会落到根分区 /uploads，部署时不可写）
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# 配置MEDIA_ROOT和MEDIA_URL
MEDIA_URL = "/uploads/"
MEDIA_ROOT = os.path.join(BASE_DIR, 'uploads')

# 接口日志记录
API_LOG_ENABLE = True
API_LOG_METHODS = ['POST', 'GET', 'DELETE', 'PUT']
API_MODEL_MAP = {}  # 暂时不使用，使用信号记录模型操作
# 接口日志黑名单：字典的操作日志、所有联系人的操作、所有缩略语的操作、判断轮次是否有源代码被测件、不记录自己
API_OPERATION_EXCLUDE_START = [
    '/api/system/dataDict',
    '/api/system/contact/index',
    '/api/system/abbreviation/index',
    '/api/project/dut/soExist',
    '/api/system/log/',
    '/api/system/dict/'
]

# 配置单次请求最大字节数（base64图片和上传需求文档适用）
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880 * 10
