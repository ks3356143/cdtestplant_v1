from ninja.errors import HttpError
from pyasn1_modules.rfc2315 import Data

from apps.project.models import Project, StuctSortData
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

# ~~~软件概述~~~
class DataSchema(Schema):
    type: Optional[str] = "text"
    fontnote: Optional[str] = ""
    content: str | list[list[str]]

## 输入
class SoftSummarySchema(Schema):
    id: int
    data: list[DataSchema]

# ~~~软件接口图~~~
## 复用DataSchema

# ~~~静态软件项、静态硬件项、动态软件项、动态硬件项~~~
class StaticDynamicData(Schema):
    id: int
    category: str
    table: list[list[str]]
    fontnote: Optional[str] = ""

# ~~~环境差异性分析~~~
class EnvAnalysisSchema(Schema):
    id: int
    table: list[list[str]]
    fontnote: Optional[str] = ""
    description: Optional[str] = ""