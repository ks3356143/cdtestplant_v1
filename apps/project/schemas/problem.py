from pydantic import AliasChoices

from apps.project.models import Problem
from ninja import Field, Schema, ModelSchema
from typing import List, Optional

# 删除schema
class DeleteSchema(Schema):
    ids: List[int]

# 问题单-输出schema
class ProblemModelOutSchema(ModelSchema):
    related: Optional[bool] = Field(False)  # 给前端反应是否为关联的问题单
    hang: bool = Field(False)  # 给前端反应是否是悬挂状态（即没有关联case）

    class Meta:
        model = Problem
        exclude = ['case', 'remark', 'sort']

# 查询问题单
class ProblemFilterSchema(Schema):
    project_id: int = Field(None, alias='projectId')
    round_id: str = Field(None, alias='round')
    dut_id: str = Field(None, alias='dut')
    design_id: str = Field(None, alias='designDemand')
    test_id: str = Field(None, alias='testDemand')
    case_id: str = Field(None, alias='case')
    key: str = Field(None, alias='key')
    # 其他字段
    ident: str = Field(None, alias='ident')
    name: str = Field(None, alias='name')
    status: str = Field(None, alias='status')
    type: str = Field(None, alias='type')
    grade: str = Field(None, alias='grade')
    operation: str = Field(None, alias='operation')
    postPerson: str = Field(None, alias='postPerson')

class ProblemFilterWithHangSchema(ProblemFilterSchema):
    # 搜索增加hang字段
    hang: str = Field('3', alias='hang')

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
    class Meta:
        model = Problem
        exclude = ['remark', 'sort', 'case']

# 更新，新增schema
class ProblemCreateInputSchema(Schema):
    project_id: int = Field(..., validation_alias=AliasChoices('project_id', 'projectId'))
    round_key: str = Field(None, alias="round")
    dut_key: str = Field(None, alias="dut")
    design_key: str = Field(None, alias="designDemand")
    test_key: str = Field(None, alias="testDemand")
    case_key: str = Field(None, alias="case")
    # 其他字段
    ident: str = Field(None, alias='ident')
    name: str = Field(None, alias='name')
    grade: str = Field(None, alias='grade')
    operation: str = Field("", alias='operation')  # !重要：由于保存到数据库为null，则查询空字符串无法查询出来
    result: str = Field("", alias='result')  # 问题影响
    status: str = Field(None, alias='status')
    type: str = Field(None, alias='type')
    postPerson: str = Field(None, alias='postPerson')
    postDate: str = Field(None, alias='postDate')
    designerPerson: str = Field("", alias='designerPerson')
    designDate: str = Field(None, alias='designDate')
    verifyPerson: str = Field("", alias='verifyPerson')
    verifyDate: str = Field(None, alias='verifyDate')
    closeMethod: List[str]
    # 2024年3月27日新增-处理方式字段
    solve: Optional[str] = ""
    # 2024年5月13日新增
    analysis: str = Field("", alias='analysis')
    effect_scope: str = Field("", alias='effect_scope')
    verify_result: str = Field("", alias='verify_result')

# 不带round_key、dut_key、design_key、test_key、case_key的更新Schema
class ProblemUpdateInputSchema(Schema):
    project_id: int = Field(..., alias="projectId")
    # 其他字段
    ident: str = Field(None, alias='ident')
    name: str = Field(None, alias='name')
    grade: str = Field(None, alias='grade')
    operation: str = Field(None, alias='operation')
    result: str = Field(None, alias='result')
    status: str = Field(None, alias='status')
    type: str = Field(None, alias='type')
    postPerson: str = Field(None, alias='postPerson')
    postDate: str = Field(None, alias='postDate')
    designerPerson: str = Field(None, alias='designerPerson')
    designDate: str = Field(None, alias='designDate')
    verifyPerson: str = Field(None, alias='verifyPerson')
    verifyDate: str = Field(None, alias='verifyDate')
    closeMethod: List[str]
    # 5月13日新增字段
    analysis: str = Field(None, alias='analysis')
    effect_scope: str = Field(None, alias='effect_scope')
    verify_result: str = Field(None, alias='verify_result')
    # 更新字段
    solve: Optional[str] = None

class ProblemSingleInputSchema(Schema):
    project_id: int = Field(..., alias="projectId")
    round_id: str = Field(..., alias="round")
    dut_id: str = Field(..., alias="dut")
    design_id: str = Field(..., alias="designDemand")
    test_id: str = Field(..., alias="testDemand")
    case_id: str = Field(..., alias="case")
    problem_id: str = Field(..., alias="problem")
