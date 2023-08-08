# ================================================= #
# *************** mysql数据库 配置  *************** #
# ================================================= #
# 数据库地址
DATABASE_HOST = "127.0.0.1"
# 数据库端口
DATABASE_PORT = 3306
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
CELERY_TASK_RESULT_EXPIRES = 60 * 60 * 24 # 任务过期时间
CELERY_REUSLT_SERIALIZER = "json" # celery结果序列化,接受mime类型，任务序列化形式
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
DJANGO_CELERY_BEAT_TZ_AWARE = False # 不知道
CELERY_WORKER_CONCURRENCY = 5 # 并发数量
CELERY_MAX_TASKS_PER_CHILD = 10 # 每worker最多执行5个任务自动销毁

# ================================================= #
# ******************  其他 配置  ****************** #
# ================================================= #
# DEBUG = True  # 线上环境请设置为False
DEBUG = False  # 线上环境请设置为False
ALLOWED_HOSTS = ["*"]
LOGIN_NO_CAPTCHA_AUTH = True  # 登录接口 /api/token/ 是否需要验证码认证，用于测试，正式环境建议取消
ENABLE_LOGIN_ANALYSIS_LOG = True  # 启动登录详细概略获取(通过调用api获取ip详细地址)
