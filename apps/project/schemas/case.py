from pydantic import AliasChoices
from apps.project.models import Case, CaseStep
from ninja import Field, Schema, ModelSchema
from typing import List, Union, Optional
from datetime import date
# 关联问题单
from apps.project.schemas.problem import ProblemModelOutSchema

# 删除schema
class DeleteSchema(Schema):
    ids: List[int]

# 测试步骤输出schema
class CaseStepSchema(ModelSchema):
    class Config:
        model = CaseStep
        model_fields = ["operation", 'expect', 'result', 'passed', 'case', 'id']

# 测试用例的步骤输出schema，输出isPassed和isExe转换后的
class CaseStepWithTransitionSchema(ModelSchema):
    class Meta:
        model = CaseStep
        fields = ["operation", 'expect', 'result', 'passed', 'case', 'id']

# 输出case：不关联问题单和步骤
class CaseModelOutSchemaWithoutProblem(ModelSchema):
    testStep: List[CaseStepWithTransitionSchema]
    testType: str  # 用例额外字段，用于测试类型FT的标识给前端

    class Config:
        model = Case
        model_exclude = ['project', 'round', 'dut', 'design', 'test', 'remark', 'sort']

# 输出case：关联问题单
class CaseModelOutSchema(ModelSchema):
    testStep: List[CaseStepSchema]
    testType: str  # 用例额外字段，用于测试类型FT的标识给前端
    # 新增：关联的问题单
    problem: Optional[ProblemModelOutSchema] = None

    class Config:
        model = Case
        model_exclude = ['project', 'round', 'dut', 'design', 'test', 'remark', 'sort']

# 查询测试项
class CaseFilterSchema(Schema):
    id: int = Field(None, alias='id')
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
    # 3月13日新增字段，让case作为树状尾部节点
    isLeaf: bool = Field(True, alias='isLeaf')
    # 2024年6月6日新增：用于树图显示
    isRelatedProblem: bool = Field(False, alias='isRelatedProblem')
    isNotPassed: bool = Field(False, alias='isNotPassed')

class CaseTreeInputSchema(Schema):
    # 注意这里有alias
    project_id: int = Field(None, alias='projectId')
    key: str = Field(None, alias='key')
    level: str = Field(None, alias='level')

# 增加测试用例
class CaseCreateOutSchema(ModelSchema):
    level: Union[str, int]

    class Config:
        model = Case
        model_exclude = ['remark', 'sort', 'project', 'round', 'dut', 'design']

# 新增接口schema
class CaseInputSchema(Schema):
    operation: str = Field(None, alias="operation")
    expect: str = Field(None, alias="expect")
    result: str = Field(None, alias="result")
    passed: str = Field('3', alias="passed")

class CaseCreateInputSchema(Schema):
    project_id: int = Field(..., validation_alias=AliasChoices('project_id', 'projectId'),
                            serialization_alias='projectId')
    round_key: str = Field(None, alias="round")
    dut_key: str = Field(None, alias="dut")
    design_key: str = Field(None, alias="designDemand")
    test_key: str = Field(None, alias="testDemand")
    # 其他字段
    ident: str = Field('', alias='ident')
    name: str = Field('', alias='name')
    designPerson: str = Field('', alias='designPerson')
    testPerson: str = Field('', alias='testPerson')
    monitorPerson: str = Field('', alias='monitorPerson')
    summarize: str = Field('', alias='summarize')
    initialization: str = Field('', alias='initialization')
    premise: str = Field('', alias='premise')
    testStep: List[CaseInputSchema]
    # 新增执行时间字段
    exe_time: date = Field(None, alias='exe_time')
    # 新增时序图字段
    timing_diagram: str = Field("", alias="timing_diagram")

# 由demand创建case的输入Schema
class DemandNodeSchema(Schema):
    project_id: int
    level: int = Field(3, gt=0)
    isLeaf: bool = False
    key: str = Field(None, alias='nodekey')
    title: str = Field(None)
