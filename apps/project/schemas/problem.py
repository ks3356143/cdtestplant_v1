import json
from apps.project.models import Problem
from ninja import Field, Schema, ModelSchema
from typing import List

# 删除schema
class DeleteSchema(Schema):
    ids: List[int]

# 测试项-输出schema
class ProblemModelOutSchema(ModelSchema):
    class Config:
        model = Problem
        model_exclude = ['project', 'round', 'dut', 'design', 'test', 'case', 'remark', 'sort']

# 查询测试项
class ProblemFilterSchema(Schema):
    project_id: int = Field(None, alias='projectId')
    round_id: str = Field(None, alias='round')
    dut_id: str = Field(None, alias='dut')
    design_id: str = Field(None, alias='designDemand')
    test_id: str = Field(None, alias='testDemand')
    case_id: str = Field(None, alias='case')
    # 其他字段
    ident: str = Field(None, alias='ident')
    name: str = Field(None, alias='name')
    status: str = Field(None, alias='status')
    type: str = Field(None, alias='type')
    grade: str = Field(None, alias='grade')
    operation: str = Field(None, alias='operation')
    postPerson: str = Field(None, alias='postPerson')

# 处理树状结构的schema
class ProblemTreeReturnSchema(Schema):
    title: str = Field(..., alias='title')
    key: str = Field(..., alias='key')
    level: str = Field(..., alias='level')
    isLeaf: bool = Field(..., alias='isLeaf')

class ProblemTreeInputSchema(Schema):
    # 注意这里有alias
    project_id: int = Field(None, alias='projectId')
    key: str = Field(None, alias='key')
    level: str = Field(None, alias='level')
    isLeaf: bool = Field(None, alias='isLeaf')

# 增加问题单
class ProblemCreateOutSchema(ModelSchema):
    class Config:
        model = Problem
        model_exclude = ['remark', 'sort', 'project', 'round', 'dut', 'design', 'case']

class ProblemCreateInputSchema(Schema):
    project_id: int = Field(..., alias="projectId")
    round_key: str = Field(..., alias="round")
    dut_key: str = Field(..., alias="dut")
    design_key: str = Field(..., alias="designDemand")
    test_key: str = Field(..., alias="testDemand")
    case_key: str = Field(..., alias="case")
    # 其他字段
    ident: str = Field(None, alias='ident')
    name: str = Field(None, alias='name')
    rules: str = Field(None, alias='rules')
    expect: str = Field(None, alias='expect')
    grade: str = Field(None, alias='grade')
    operation: str = Field(None, alias='operation')
    result: str = Field(None, alias='result')
    status: str = Field(None, alias='status')
    suggest: str = Field(None, alias='suggest')
    type: str = Field(None, alias='type')
    postPerson: str = Field(None, alias='postPerson')
    postDate: str = Field(None, alias='postDate')
    designerPerson: str = Field(None, alias='designerPerson')
    designDate: str = Field(None, alias='designDate')
    revokePerson: str = Field(None, alias='revokePerson')
    revokeDate: str = Field(None, alias='revokeDate')
    verifyPerson: str = Field(None, alias='verifyPerson')
    verifyDate: str = Field(None, alias='verifyDate')
    closeMethod: List[str]

class ProblemSingleInputSchema(Schema):
    project_id:int = Field(...,alias="projectId")
    round_id:str = Field(...,alias="round")
    dut_id: str = Field(..., alias="dut")
    design_id: str = Field(..., alias="designDemand")
    test_id: str = Field(..., alias="testDemand")
    case_id: str = Field(..., alias="case")
    problem_id: str = Field(..., alias="problem")

