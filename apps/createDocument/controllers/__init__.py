# 导入所有本目录控制器，为了自动导入
from apps.createDocument.controllers.dg import GenerateControllerDG
from apps.createDocument.controllers.sm import GenerateControllerSM
from apps.createDocument.controllers.jl import GenerateControllerJL
from apps.createDocument.controllers.bg import GenerateControllerBG
from apps.createDocument.controllers.wtd import GenerateControllerWtd
from apps.createDocument.controllers.hsm import GenerateControllerHSM
from apps.createDocument.controllers.hjl import GenerateControllerHJL

# 给外部导入
__all__ = ['GenerateControllerDG', 'GenerateControllerSM', 'GenerateControllerJL', 'GenerateControllerBG',
           'GenerateControllerWtd', 'GenerateControllerHSM', 'GenerateControllerHJL']
