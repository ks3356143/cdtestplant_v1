from pathlib import Path

# 目录根目录
LOG_DIR = Path.cwd() / 'logs'
if not LOG_DIR.exists():
    LOG_DIR.mkdir(parents=True)

# 生成文档文件
LOG_GENERATE_FILE = LOG_DIR / 'generates_logs'

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {"require_debug_false": {"()": "django.utils.log.RequireDebugFalse"}},
    "formatters": {
        # 详细
        "verbose": {
            "format": "%(levelname)s %(asctime)s %(module)s "
                      "%(process)d %(thread)d %(message)s"
        },
        # 简单
        'simple': {
            'format': '[%(levelname)s][%(asctime)s][%(filename)s:%(lineno)d]%(message)s'
        },
    },
    # 两种分发器
    "handlers": {  # 定义了三种分发器
        'root_log_file': {
            'level': "WARNING",
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOG_DIR / 'root_log',
            'maxBytes': 1024 * 1024 * 10,
            'backupCount': 10,
            'formatter': 'simple',
            'encoding': 'utf-8',
        },
        'generate_log_file': {
            'level': "INFO",
            # 滚动生成日志，切割
            'class': 'logging.handlers.RotatingFileHandler',
            # 日志文件名
            'filename': LOG_GENERATE_FILE,
            # 单个日志文件最大为20M
            'maxBytes': 1024 * 1024 * 20,
            # 日志备份文件最大数量30个
            'backupCount': 30,
            # 简单格式
            'formatter': 'simple',
            # 放置中文乱码
            'encoding': 'utf-8',
        },
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {"level": "WARNING", "handlers": ["console", 'root_log_file']},  # Django-root日志默认级别为WARNING
    "loggers": {
        "generate_document_logger": {
            "level": "DEBUG",
            "handlers": ["console", "generate_log_file"],
            "propagate": True,
        },
    },
}
