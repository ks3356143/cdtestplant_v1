from typing import List,Optional
from ninja_extra import api_controller, ControllerBase, route
from ninja import Schema, Field, Query, ModelSchema
from ninja.errors import HttpError
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

    def validate_unique_update_fragName(self, id: int):
        frag_filters = Fragment.objects.filter(name=self.name)
        if len(frag_filters) > 1:
            raise HttpError(400, "文档片段名称重复")
        elif len(frag_filters) == 1:
            if frag_filters[0].id == id:
                return
            else:
                raise HttpError(400, "文档片段名称重复")
        else:
            return

# 删除schema
class FragmentDeleteSchema(Schema):
    ids: List[int]

# 全局静态变量
PIC_URL_PREFIX = "/uploads/"

# Controller
@api_controller("/system/userField", tags=['文档片段'], auth=JWTAuth(), permissions=[IsAuthenticated])
class UserFiledController(ControllerBase):
    @route.get("/getFragment", response=List[FragmentOutSchema], url_name='fragment-list')
    @paginate(MyPagination)
    def get_fragement(self, condition: Query[FragementListSchema]):
        fragment_qs = Fragment.objects.filter(project_id=condition.project_id)
        res_qs = model_retrieve(condition, fragment_qs, ['project_id', 'is_main'])
        res_qs = res_qs.filter(project_id=condition.project_id)
        return res_qs

    @route.post("/add", url_name='fragment-add', response=FragmentOutSchema)
    def add_fragement(self, data: FragmentAddSchema):
        return createWithOutRequestParam(data, Fragment)

    @route.delete("/delete", url_name="fragment-delete")
    def delete_fragment(self, data: FragmentDeleteSchema):
        try:
            multi_delete(data.ids, Fragment)
        except Exception:
            raise HttpError(500, "删除失败")

    @route.put("/update/{int:id}", url_name='fragment-update')
    def update_fragment(self, id: int, data: FragmentUpdateSchema):
        update_obj = updateWithoutRequestParam(id, data, Fragment)
        if update_obj:
            return '更新成功'
        raise HttpError(500, "设置替换磁盘文件渲染失败")
