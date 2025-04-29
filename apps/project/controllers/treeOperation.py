from ninja_extra import api_controller, ControllerBase, route
from ninja_jwt.authentication import JWTAuth
from ninja_extra.permissions import IsAuthenticated
from django.db import transaction
from django.shortcuts import get_object_or_404
# 导入schema
from apps.project.schemas.treeOperation import CopySchema
# 导入模型
from apps.project.models import Project
# 导入本app工具
from apps.project.tools.keyTools import TreeKey
# 导入项目工具
from utils.chen_response import ChenResponse

@api_controller("/treeOperation", auth=JWTAuth(), permissions=[IsAuthenticated], tags=['树的操作'])
class TreeController(ControllerBase):
    @route.post("/copy", url_name="tree-copy")
    @transaction.atomic
    def tree_copy(self, data: CopySchema):
        """新建下一个轮次，并复制选中的节点"""
        project_obj = get_object_or_404(Project, id=data.pid)
        round_count = project_obj.pField.count()
        tree_keys = data.data
        # 逻辑是：如果大节点有值，则复制整个大节点而不关心其子节点
        key_tree = TreeKey(tree_keys)
        key_tree.copy_tree(round_count, project_obj)
        return ChenResponse(code=200, status=200, message='生成轮次成功')
