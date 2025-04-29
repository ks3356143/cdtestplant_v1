import logging
from conf.logConfig import LOG_GENERATE_FILE

generate_logger = logging.getLogger("generate_document_logger")

class GenerateLogger(object):
    instance = None

    # 单例模式
    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = object.__new__(cls)
            return cls.instance
        else:
            return cls.instance

    def __init__(self, model: str = '通用文档'):
        self.logger = generate_logger
        # 模块属性
        self.model = model

    def write_warning_log(self, fragment: str, message: str):
        """警告日志记录，暂时简单点：model和message"""
        whole_message = f"[{self.model}模块][{fragment}]片段:{message}"
        self.logger.warning(whole_message)

    @staticmethod
    def delete_one_logs():
        """删除生成文档logger的日志记录"""
        with open(LOG_GENERATE_FILE, 'w') as f:
            f.truncate()
