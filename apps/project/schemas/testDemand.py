from apps.project.models import TestDemand, TestDemandContent, TestDemandContentStep
from apps.project.schemas.design import DesignModelOutSchemaOrigin  # 注意导入的是不含上级的Schema
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
    subDescription: Optional[str] = ""
    subStep: List[TestContentStepSchema] = []  # 可能为空

    class Meta:
        model = TestDemandContent
        fields = ["subName"]

# 2025年修改为两个，一个含上级一个不含
class TestDemandModelOutSchemaOrigin(ModelSchema):
    testContent: List[TestContentSchema]  # 下级对象

    class Meta:
        model = TestDemand
        exclude = ['project', 'round', 'dut', 'design', 'remark', 'sort']

class TestDemandModelOutSchema(ModelSchema):
    testContent: List[TestContentSchema]  # 下级对象
    # 2025年5月9日新增上级字段design
    design: Optional[DesignModelOutSchemaOrigin] = None

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
    # 新增查询字段，给大表的查询
    testDesciption: str = Field(None, alias="testDesciption")
    testContent: str = Field(None, alias="testContent")

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

    class Meta:
        model = TestDemand
        exclude = ['remark', 'sort', 'project', 'round', 'dut', 'design']

# 新增测试子项，单个子项的Schema
class TestContentInputSchema(Schema):
    subName: str = None
    # 2025/12/15-对CPU增加测试子项描述
    subDescription: Optional[str] = ""  # 未提供时为空字符串
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

# 批量新增测试项Schema-2个Schema
class TestDemandOneInput(Schema):
    parent_key: str  # 直接给设计需求的key，前端去组装
    ident: str
    name: str
    priority: str = "1"
    adequacy: str
    testContent: str # 注意这个在接口里面分情况判断
    testMethod: List[str] = []
    testType: str
    testDesciption: Optional[str] = ""

class TestDemandMultiCreateInputSchema(Schema):
    project_id: int
    demands: List[TestDemandOneInput]

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

# 替换文本输入Schema
class ReplaceDemandContentSchema(Schema):
    project_id: int
    round_key: str
    originText: str
    replaceText: str
    selectRows: List[int]
    selectColumn: List[str]

# 优先级替换Schema
class PriorityReplaceSchema(Schema):
    selectRows: List[int] = None
    priority: str
