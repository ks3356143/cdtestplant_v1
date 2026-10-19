from typing import List,Optional
from ninja_extra import api_controller, ControllerBase, route
from ninja import Schema, Field, Query, ModelSchema
from ninja.errors import HttpError
import logging
from ninja_jwt.authentication import JWTAuth
from ninja_extra.permissions import IsAuthenticated
from pydantic import model_validator
# 小工具函数
from utils.smallTools.interfaceTools import model_retrieve
from ninja.pagination import paginate
from utils.chen_pagination import MyPagination
from utils.chen_crud import updateWithoutRequestParam, multi_delete, createWithOutRequestParam
# ORM模型
from apps.dict.models import Fragment
from apps.project.tools.access_control import check_project_access_by_id, accessible_project_ids
from ninja_extra.exceptions import PermissionDenied
from django.db.models import Q

logger = logging.getLogger(__name__)

# Schemas
## 查询fragment的输入
class FragementListSchema(Schema):
    name: Optional[str] = None  # 片段名称
    is_main: Optional[bool] = None  # 是否替换磁盘的片段
    project_id: int = Field(None, alias='projectId')

## 查询结果
class FragmentOutSchema(ModelSchema):
    class Meta:
        model = Fragment
        fields = ['id', 'name', 'project', 'is_main', 'content']

## 新增
class FragmentAddSchema(Schema):
    name: str  # 必填
    is_main: bool = False  # 后端直接设置为False
    project_id: int = Field(None, alias='projectId')
    content: str = ""

    # username判重
    @model_validator(mode='after')
    def unique_name(self):
        if Fragment.objects.filter(name=self.name, project_id=self.project_id).exists():
            raise HttpError(400, "文档片段名称重复")
        return self

## 更新文档片段
class FragmentUpdateSchema(Schema):
    name: Optional[str] = None
    is_main: Optional[bool] = None
    project_id: int = Field(None, alias='projectId')
    content: str = Field(None, alias='content')

# 删除schema
class FragmentDeleteSchema(Schema):
    ids: List[int]

# Controller
@api_controller("/system/userField", tags=['文档片段'], auth=JWTAuth(), permissions=[IsAuthenticated])
class UserFiledController(ControllerBase):
    def _check_project(self, project_id, user):
        """文档片段按项目隔离：全局片段（project_id 为空）仅系统管理员可操作"""
        if project_id in (None, '', 0):
            if getattr(user, 'role', None) != 'admin':
                raise PermissionDenied('全局文档片段仅系统管理员可操作')
            return
        check_project_access_by_id(project_id, user)

    @route.get("/getFragment", response=List[FragmentOutSchema], url_name='fragment-list')
    @paginate(MyPagination)
    def get_fragement(self, condition: Query[FragementListSchema]):
        user = self.context.request.user
        fragment_qs = Fragment.objects.all()
        if condition.project_id is not None:
            # 显式指定项目时校验项目访问权
            self._check_project(condition.project_id, user)
            fragment_qs = fragment_qs.filter(project_id=condition.project_id)
        elif getattr(user, 'role', None) != 'admin':
            # 未指定项目：只返回全局片段 + 当前用户可访问项目的片段
            fragment_qs = fragment_qs.filter(
                Q(project_id__isnull=True) | Q(project_id__in=accessible_project_ids(user)))
        res_qs = model_retrieve(condition, fragment_qs, ['project_id', 'is_main'])
        return res_qs

    @route.post("/add", url_name='fragment-add', response=FragmentOutSchema)
    def add_fragement(self, data: FragmentAddSchema):
        self._check_project(data.project_id, self.context.request.user)
        return createWithOutRequestParam(data, Fragment)

    @route.delete("/delete", url_name="fragment-delete")
    def delete_fragment(self, data: FragmentDeleteSchema):
        user = self.context.request.user
        # 逐个校验待删除片段所属项目，防止跨项目删除
        objs = list(Fragment.objects.filter(id__in=data.ids))
        missing = [i for i in data.ids if i not in {o.id for o in objs}]
        if missing:
            raise HttpError(404, f"文档片段不存在或已被删除：{missing}")
        for obj in objs:
            self._check_project(obj.project_id, user)
        try:
            multi_delete([obj.id for obj in objs], Fragment)
        except Exception as e:
            # 保留原始异常信息，便于排查删除失败原因
            logger.exception("删除文档片段失败：ids=%s", data.ids)
            raise HttpError(500, "删除失败") from e

    @route.put("/update/{int:id}", url_name='fragment-update')
    def update_fragment(self, id: int, data: FragmentUpdateSchema):
        user = self.context.request.user
        obj = Fragment.objects.filter(id=id).first()
        if obj is None:
            raise HttpError(404, "文档片段不存在")
        # 既不能改别的项目的片段，也不能把片段挪到自己无权访问的项目
        self._check_project(obj.project_id, user)
        if data.project_id is not None and data.project_id != obj.project_id:
            self._check_project(data.project_id, user)
        update_obj = updateWithoutRequestParam(id, data, Fragment)
        if update_obj:
            return '更新成功'
        raise HttpError(500, "设置替换磁盘文件渲染失败")
