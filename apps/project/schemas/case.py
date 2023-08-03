from apps.project.models import Case, CaseStep
from ninja import Field, Schema, ModelSchema
from typing import List

# 删除schema
class DeleteSchema(Schema):
    ids: List[int]

# 测试项-输出schema
class CaseStepSchema(ModelSchema):
    class Config:
        model = CaseStep
        model_fields = ["operation", 'expect', 'result', 'passed', 'status', 'case', 'id']

class CaseModelOutSchema(ModelSchema):
    testStep: List[CaseStepSchema]

    class Config:
        model = Case
        model_exclude = ['project', 'round', 'dut', 'design', 'test', 'remark', 'sort']

# 查询测试项
class CaseFilterSchema(Schema):
    project_id: int = Field(None, alias='projectId')
    round_id: str = Field(None, alias='round')
    dut_id: str = Field(None, alias='dut')
    design_id: str = Field(None, alias='designDemand')
    test_id: str = Field(None, alias='testDemand')
    # 其他字段
    ident: str = Field(None, alias='ident')
    name: str = Field(None, alias='name')
    designPerson: str = Field(None, alias='designPerson')
    testPerson: str = Field(None, alias='testPerson')
    monitorPerson: str = Field(None, alias='monitorPerson')
    summarize: str = Field(None, alias='summarize')

# 处理树状结构的schema
class CaseTreeReturnSchema(Schema):
    title: str = Field(..., alias='title')
    key: str = Field(..., alias='key')
    level: str = Field(..., alias='level')

class CaseTreeInputSchema(Schema):
    # 注意这里有alias
    project_id: int = Field(None, alias='projectId')
    key: str = Field(None, alias='key')
    level: str = Field(None, alias='level')

# 增加测试用例
class CaseCreateOutSchema(ModelSchema):
    class Config:
        model = Case
        model_exclude = ['remark', 'sort', 'project', 'round', 'dut', 'design']

# 新增接口schema
class CaseInputSchema(Schema):
    operation: str = Field(None, alias="operation")
    expect: str = Field(None, alias="expect")
    result: str = Field(None, alias="result")
    passed: str = Field(None, alias="passed")
    status: str = Field(None, alias="status")

class CaseCreateInputSchema(Schema):
    project_id: int = Field(..., alias="projectId")
    round_key: str = Field(..., alias="round")
    dut_key: str = Field(..., alias="dut")
    design_key: str = Field(..., alias="designDemand")
    test_key: str = Field(..., alias="testDemand")
    # 其他字段
    ident: str = Field(None, alias='ident')
    name: str = Field(None, alias='name')
    designPerson: str = Field(None, alias='designPerson')
    testPerson: str = Field(None, alias='testPerson')
    monitorPerson: str = Field(None, alias='monitorPerson')
    summarize: str = Field(None, alias='summarize')
    initialization: str = Field(None, alias='initialization')
    premise: str = Field(None, alias='premise')
    testStep: List[CaseInputSchema]
