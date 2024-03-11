# 导入所有本目录控制器，为了自动导入
from apps.createDocument.controllers.dg import GenerateControllerDG
from apps.createDocument.controllers.sm import GenerateControllerSM

# 给外部导入
__all__ = ['GenerateControllerDG', 'GenerateControllerSM']