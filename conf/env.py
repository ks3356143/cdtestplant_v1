"""全部是生产环境配置"""
import ldap
from django_auth_ldap.config import LDAPSearch
import environ
from pathlib import Path

# ***************读取LDAP的.env文件配置*************** #
env_file = '.env'
env = environ.Env()
env.read_env(env_file=Path(__file__).resolve().parent.parent / env_file)

# ================================================= #
# *************** mysql数据库 配置  *************** #
# ================================================= #
# 数据库地址
DATABASE_HOST = "127.0.0.1"
# 数据库端口
DATABASE_PORT = 3307  # 生成环境配置
# 数据库用户名
DATABASE_USER = "root"
# 数据库密码
DATABASE_PASSWORD = "root"
# 数据库名
DATABASE_NAME = "chengdu_test_plant_v1"

# ================================================= #
# ******************** celery配置  **************** #
# ================================================= #
CELERY_BROKER_URL = "redis://127.0.0.1:6379/0"
CELERY_RESULT_BACKEND = "redis://127.0.0.1:6379/1"
CELERY_ENABLE_UTC = False
CELERY_TIME_ZONE = "Asia/Shanghai"
CELERY_TASK_RESULT_EXPIRES = 60 * 60 * 24  # 任务过期时间
CELERY_REUSLT_SERIALIZER = "json"  # celery结果序列化,接受mime类型，任务序列化形式
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
DJANGO_CELERY_BEAT_TZ_AWARE = False
CELERY_WORKER_CONCURRENCY = 5  # 并发数量
CELERY_MAX_TASKS_PER_CHILD = 10  # 每worker最多执行5个任务自动销毁

# ================================================= #
# ******************  其他 配置  ****************** #
# ================================================= #
ALLOWED_HOSTS = ["*"]  # 线上环境设置
LOGIN_NO_CAPTCHA_AUTH = True  # 登录接口 /api/token/ 是否需要验证码认证，用于测试，正式环境建议取消
ENABLE_LOGIN_ANALYSIS_LOG = True  # 启动登录详细概略获取(通过调用api获取ip详细地址)
# ================================================= #
# ***************  接口throttle配置  *************** #
# ================================================= #

# ================================================= #
# ***************  LDAP认证配置  *************** #
# ================================================= #
AUTHENTICATION_BACKENDS = [
    'django_auth_ldap.backend.LDAPBackend',
    'django.contrib.auth.backends.ModelBackend',
]
# ldap连接配置
AUTH_LDAP_SERVER_URI = env('AUTH_LDAP_SERVER_URI', default='ldap://dns.paisat.cn:389')
# 绑定的DN,注意大小写敏感Administrator，Users
AUTH_LDAP_BIND_DN = env('AUTH_LDAP_BIND_DN', default="CN=Administrator,CN=Users,DC=sstc,DC=ctu")
# 管理员密码-生产环境
AUTH_LDAP_BIND_PASSWORD = env('AUTH_LDAP_BIND_PASSWORD', default="WXWX2019!!!!!!")
AUTH_LDAP_USER_SEARCH = LDAPSearch(
    env('BASE_DN', default='OU=all,DC=sstc,DC=ctu'),
    ldap.SCOPE_SUBTREE, env('FILTER_STR', default='(sAMAccountName=%(user)s)')
)
# 如果ldap服务器是Windows的AD，需要配置上如下选项
AUTH_LDAP_CONNECTION_OPTIONS = {
    ldap.OPT_DEBUG_LEVEL: 1,
    ldap.OPT_REFERRALS: 0,
}
# 每次LDAP认证后进行数据库更新，不包含密码
AUTH_LDAP_ALWAYS_UPDATE_USER = True
# 看看下面是否需要password字段
AUTH_LDAP_USER_ATTR_MAP = {
    "username": "sAMAccountName",
    "name": "name",
    "email": "mail",
}
# ================================================= #
# ***************  ...........配置  *************** #
# ================================================= #
