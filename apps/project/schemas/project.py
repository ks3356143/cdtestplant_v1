from ninja.errors import HttpError
from apps.project.models import Project
from ninja import Schema, ModelSchema
from pydantic import field_validator
from typing import List, Optional

window_file_str = ['\\', '/', ':', '*', '?', '"', '<', '>', "|"]

class ProjectRetrieveSchema(ModelSchema):
    class Meta:
        model = Project
        exclude = ['update_datetime', 'create_datetime', 'remark']

class ProjectFilterSchema(Schema):
    ident: Optional[str] = None
    name: Optional[str] = None
    duty_person: Optional[str] = None
    security_level: Optional[str] = None
    report_type: Optional[str] = None
    step: Optional[str] = None
    # 新增软件类型：新研/改造
    soft_type: Optional[str] = None
    # 新增密级
    secret: Optional[str] = None

class ProjectCreateInput(ModelSchema):
    ident: str

    class Meta:
        model = Project
        exclude = ['remark', 'update_datetime', 'create_datetime', 'sort', 'id']

    @field_validator('ident')
    @staticmethod
    def check_ident_window(val):
        if any(window_str in val for window_str in window_file_str):
            raise HttpError(400, message='标识包含window文件名不允许的特殊字符')
        return val

class DeleteSchema(Schema):
    ids: List[int]
