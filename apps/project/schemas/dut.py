from apps.project.models import Dut
from ninja import Field, Schema, ModelSchema
from typing import List

class DutModelOutSchema(ModelSchema):
    class Config:
        model = Dut
        model_exclude = ['project', 'round', 'remark', 'sort']

class DutFilterSchema(Schema):
    project_id: int = Field(None, alias='projectId')
    round_id: int = Field(None, alias='round')
    ident: str = Field(None, alias='ident')
    type: str = Field(None, alias='type')
    name: str = Field(None, alias='name')
    # 新增版本、单位
    version: str = Field(None, alias="version")
    release_union: str = Field(None, alias="release_union")

# 树状目录schema
class DutTreeInputSchema(Schema):
    # 注意这里有alias
    project_id: int = Field(None, alias='projectId')
    key: str = Field(None, alias='key')
    level: str = Field(None, alias='level')

class DutTreeReturnSchema(Schema):
    title: str = Field(..., alias='title')
    key: str = Field(..., alias='key')
    level: str = Field(..., alias='level')

# 新增接口schema
class DutCreateInputSchema(Schema):
    project_id: int = Field(..., alias="projectId")
    round_key: str = Field(..., alias="round")
    ident: str = Field(None, alias="ident")
    name: str = Field(None, alias="name")
    type: str = Field(None, alias="type")
    black_line: str = Field(None, alias="black_line")
    comment_line: str = Field(None, alias="comment_line")
    mix_line: str = Field(None, alias="mix_line")
    pure_code_line: str = Field(None, alias="pure_code_line")
    total_code_line: str = Field(None, alias="total_code_line")
    total_comment_line: str = Field(None, alias="total_comment_line")
    total_line: str = Field(None, alias="total_line")
    # 新增版本、单位、发布日期
    version: str = Field(None, alias="version")
    release_union: str = Field(None, alias="release_union")
    release_date: str = Field(None, alias="release_date")

class DutCreateOutSchema(ModelSchema):
    class Config:
        model = Dut
        model_exclude = ['remark', 'sort', 'project', 'round']

# 删除schema
class DeleteSchema(Schema):
    ids: List[int]
