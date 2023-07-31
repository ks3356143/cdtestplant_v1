from apps.project.models import Design
from ninja import Field, Schema, ModelSchema
from typing import List

# 删除schema
class DeleteSchema(Schema):
    ids: List[int]

# 查询设计需求
class DesignFilterSchema(Schema):
    project_id: int = Field(None, alias='projectId')
    round_id: str = Field(None, alias='round')
    dut_id: str = Field(None, alias='dut')
    # 其他字段
    ident: str = Field(None, alias='ident')
    demandType: str = Field(None, alias='demandType')
    name: str = Field(None, alias='name')

class DesignModelOutSchema(ModelSchema):
    class Config:
        model = Design
        model_exclude = ['project', 'round', 'dut', 'remark', 'sort']
