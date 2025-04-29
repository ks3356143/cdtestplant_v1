# 导入所有控制器
from apps.project.controllers.project import ProjectController
from apps.project.controllers.round import RoundController
from apps.project.controllers.dut import DutController
from apps.project.controllers.design import DesignController
from apps.project.controllers.testDemand import TestDemandController
from apps.project.controllers.case import CaseController
from apps.project.controllers.problem import ProblemController
from apps.project.controllers.treeOperation import TreeController

# 将导入的控制器以列表方式放入下面数组
__all__ = ['ProjectController', 'RoundController', 'DutController', 'DesignController', 'TestDemandController',
           'CaseController', 'ProblemController', 'TreeController']
