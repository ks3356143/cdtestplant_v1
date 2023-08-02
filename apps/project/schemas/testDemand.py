from apps.project.models import TestDemand, TestDemandContent
from ninja import Field, Schema, ModelSchema
from typing import List

# 删除schema
class DeleteSchema(Schema):
    ids: List[int]

# 测试项-输出schema
class TestContentSchema(ModelSchema):
    class Config:
        model = TestDemandContent
        model_fields = ["testXuQiu", "testYuQi"]

class TestDemandModelOutSchema(ModelSchema):
    testContent: List[TestContentSchema]

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
    testType: str = Field(None, alias='testType')
    name: str = Field(None, alias='name')
    priority: str = Field(None, alias="priority")

# 处理树状结构的schema
class TestDemandTreeReturnSchema(Schema):
    title: str = Field(..., alias='title')
    key: str = Field(..., alias='key')
    level: str = Field(..., alias='level')

class TestDemandTreeInputSchema(Schema):
    # 注意这里有alias
    project_id: int = Field(None, alias='projectId')
    key: str = Field(None, alias='key')
    level: str = Field(None, alias='level')

# 增加测试项
class TestDemandCreateOutSchema(ModelSchema):
    class Config:
        model = TestDemand
        model_exclude = ['remark', 'sort', 'project', 'round', 'dut', 'design']

# 新增接口schema
class TestContentInputSchema(Schema):
    testXuQiu: str = Field(None, alias="testXuQiu")
    testYuQi: str = Field(None, alias="testYuQi")

class TestDemandCreateInputSchema(Schema):
    project_id: int = Field(..., alias="projectId")
    round_key: str = Field(..., alias="round")
    dut_key: str = Field(..., alias="dut")
    design_key: str = Field(..., alias="designDemand")
    # 其他字段
    ident: str = Field(None, alias="ident")
    name: str = Field(None, alias="name")
    adequacy: str = Field(None, alias="adequacy")
    premise: str = Field(None, alias="premise")
    priority: str = Field(None, alias="priority")
    termination: str = Field(None, alias="termination")
    testContent: List[TestContentInputSchema]
    testMethod: str = Field(None, alias="testMethod")
    testType: str = Field(None, alias="testType")
