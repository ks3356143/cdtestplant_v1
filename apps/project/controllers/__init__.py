# 导入所有控制器
from .project import ProjectController
from .round import RoundController
from .dut import DutController
from .design import DesignController
from .testDemand import TestDemandController
from .case import CaseController
from .problem import ProblemController

# 将导入的控制器以列表方式放入下面数组
__all__ = ['ProjectController', 'RoundController', 'DutController', 'DesignController', 'TestDemandController',
           'CaseController', 'ProblemController']
