from apps.project.models import Design
from ninja import Field, Schema, ModelSchema
from typing import List, Union
from pydantic import AliasChoices

# 删除schema
class DeleteSchema(Schema):
    ids: List[int]

# 查询设计需求
class DesignFilterSchema(Schema):
    project_id: int = Field(None, alias='projectId')
    round_id: str = Field(None, alias='round')
    dut_id: str = Field(None, alias='dut')
    ident: str = Field(None, alias='ident')
    demandType: str = Field(None, alias='demandType')
    name: str = Field(None, alias='name')
    # 新增字段 - chapter
    chapter: str = Field(None, alias='chapter')

class DesignModelOutSchema(ModelSchema):
    class Config:
        model = Design
        model_exclude = ['project', 'round', 'dut', 'remark', 'sort']

# 处理树状结构的schema
class DesignTreeReturnSchema(Schema):
    title: str = Field(..., alias='title')
    key: str = Field(..., alias='key')
    level: str = Field(..., alias='level')

class DesignTreeInputSchema(Schema):
    # 注意这里有alias
    project_id: int = Field(None, alias='projectId')
    key: str = Field(None, alias='key')
    level: str = Field(None, alias='level')

# 增加设计需求/更新设计需求
class DesignCreateOutSchema(ModelSchema):
    level: Union[str, int]

    class Meta:
        model = Design
        exclude = ['remark', 'sort', 'project', 'round', 'dut']

# 新增接口schema
class DesignCreateInputSchema(Schema):
    project_id: int = Field(..., validation_alias=AliasChoices('project_id', 'projectId'),
                            serialization_alias='projectId')
    round_key: str = Field(..., alias="round")
    dut_key: str = Field(..., alias="dut")
    ident: str = Field("", alias="ident")
    name: str = Field(None, alias="name")
    demandType: str = Field(None, alias="demandType")
    description: str = Field("", alias="description")
    chapter: str = Field(None, alias='chapter')
    # 接口独有的4个字段
    source: str = Field('', alias='source')
    to: str = Field('', alias='to')
    type: str = Field('', alias='type')
    protocal: str = Field('', alias='protocal')

class SingleDesignSchema(Schema):
    ident: str = Field(None, alias="ident")
    name: str = Field(None, alias="title")
    demandType: str = Field(None, alias="demandType")
    description: str = Field(None, alias="content")
    chapter: str = Field(None, alias='chapter')

# 批量新增design的Schema
class MultiDesignCreateInputSchema(Schema):
    project_id: int = Field(..., alias="projectId")
    dut_key: str = Field(..., alias="key")
    data: List[SingleDesignSchema]
