# 导入下面的控制器
from apps.system.controllers.log import LogController
from apps.system.controllers.policy import SecurityPolicyController
from apps.system.controllers.secrecy import ConfidentialityController
# 暴露控制器变量
__all__ = ['LogController', 'SecurityPolicyController', 'ConfidentialityController']
