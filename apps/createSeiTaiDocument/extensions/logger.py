import logging
from conf.logConfig import LOG_GENERATE_FILE

generate_logger = logging.getLogger("generate_document_logger")

class GenerateLogger(object):
    # 注意：各模块以不同 model 名构造该对象（如「测评大纲」「回归测试说明」）。
    # 原单例实现下，后构造的模块会覆盖 self.model，导致所有模块日志都打错标签；
    # 因此这里不做单例——每个实例各自持有自己的 model。
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
