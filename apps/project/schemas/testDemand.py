from apps.project.models import TestDemand, TestDemandContent, TestDemandContentStep
from ninja import Field, Schema, ModelSchema
from typing import List, Union, Optional
from pydantic import AliasChoices

# 删除schema
class DeleteSchema(Schema):
    ids: List[int]

# 测试项-输出schema -> 包含两层嵌套
class TestContentStepSchema(ModelSchema):
    class Meta:
        model = TestDemandContentStep
        fields = ['operation', 'expect']

class TestContentSchema(ModelSchema):
    subStep: List[TestContentStepSchema] = []  # 可能为空

    class Meta:
        model = TestDemandContent
        fields = ["subName"]

class TestDemandModelOutSchema(ModelSchema):
    testContent: List[TestContentSchema]

    class Meta:
        model = TestDemand
        exclude = ['project', 'round', 'dut', 'design', 'remark', 'sort']

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
    level: Union[str, int]

    class Config:
        model = TestDemand
        model_exclude = ['remark', 'sort', 'project', 'round', 'dut', 'design']

# 新增测试子项，单个子项的Schema
class TestContentInputSchema(Schema):
    subName: str = None
    subStep: Optional[List[TestContentStepSchema]] = []

# 新增/更新测试项Schema
class TestDemandCreateInputSchema(Schema):
    project_id: int = Field(..., validation_alias=AliasChoices("projectId", "project_id"),
                            serialization_alias="projectId")
    round_key: str = Field(..., alias="round")
    dut_key: str = Field(..., alias="dut")
    design_key: str = Field(..., alias="designDemand")
    # 其他字段
    ident: str = Field(None, alias="ident")
    name: str = Field(None, alias="name")
    adequacy: str = Field(None, alias="adequacy")
    priority: str = Field(None, alias="priority")
    testContent: List[TestContentInputSchema] = []
    testMethod: List[str] = []
    testType: str = Field(None, alias="testType")
    testDesciption: str = Field("", alias='testDesciption')

# 处理前端请求-设计需求关联测试需求（测试项）
class TestDemandRelatedSchema(Schema):
    data: List[int] = None
    project_id: int = Field(None, alias="project_id")
    round_key: str = Field(None, alias="roundNumber")
    dut_key: str = Field(None, alias="dutNumber")
    design_key: str = Field(None, alias="designDemandNumber")

# 处理前端请求-设计需求已关联测试需求（测试项）
class TestDemandExistRelatedSchema(Schema):
    project_id: int = Field(None, alias="project_id")
    round_key: str = Field(None, alias="roundNumber")
    dut_key: str = Field(None, alias="dutNumber")
    design_key: str = Field(None, alias="designDemandNumber")

# 根据design的id，testDemand数据，项目id，depth复制测试项到指定design
class DemandCopyToDesignSchema(Schema):
    project_id: int
    design_id: int
    demand_key: str
    depth: bool = False
