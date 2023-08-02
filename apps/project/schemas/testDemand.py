from apps.project.models import TestDemand, TestDemandContent
from ninja import Field, Schema, ModelSchema
from typing import List

# 删除schema
class DeleteSchema(Schema):
    ids: List[int]

# 测试项-输出schema
class TestDemandModelOutSchema(ModelSchema):
    class Config:
        model = TestDemand
        model_exclude = ['project', 'round', 'dut', 'design', 'remark', 'sort']

# 查询测试项
class TestDemandFilterSchema(Schema):
    project_id: int = Field(None, alias='projectId')
    round_id: str = Field(None, alias='round')
    dut_id: str = Field(None, alias='dut')
    design_id: str = Field(None, alias='designDemand')
    # 其他字段
    ident: str = Field(None, alias='ident')
    testType: str = Field(None, alias='demandType')
    name: str = Field(None, alias='name')
    priority: str = Field(None, alias="priority")
