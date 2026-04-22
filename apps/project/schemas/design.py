from typing import Optional
from apps.project.models import Design, JKDesignInfo
from ninja import Field, Schema, ModelSchema
from typing import List, Union
from pydantic import AliasChoices
# 上级dut-schema
from apps.project.schemas.dut import DutModelOutSchema

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

# 2025年改为2个输出，因为下级需要上级，原始不再嵌套上级
class DesignModelOutSchemaOrigin(ModelSchema):
    class Meta:
        model = Design
        exclude = ['project', 'round', 'dut', 'remark', 'sort']

class DesignModelOutSchema(ModelSchema):
    # 新增字段 - 上级的dut对象
    dut: Optional[DutModelOutSchema] = None
    is_bidirectional: bool = Field(False, alias='is_bidirectional')
    forward_source: str = Field("")
    forward_destination: str = Field("")
    forward_description: str = Field("")
    reverse_source: str = Field("")
    reverse_destination: str = Field("")
    reverse_description: str = Field("")

    class Meta:
        model = Design
        exclude = ['project', 'round', 'dut', 'remark', 'sort']

    # ---------- 解析器方法 ----------
    @staticmethod
    def resolve_is_bidirectional(obj: Design) -> bool:
        return obj.is_bidirectional

    @staticmethod
    def resolve_forward_source(obj: Design) -> str:
        """从 JKDesignInfo 正向记录中获取 source"""
        info = obj.jkField.filter(direction=JKDesignInfo.Direction.FORWARD).first()
        return info.source if info else ""

    @staticmethod
    def resolve_forward_destination(obj: Design) -> str:
        info = obj.jkField.filter(direction=JKDesignInfo.Direction.FORWARD).first()
        return info.destination if info else ""

    @staticmethod
    def resolve_forward_description(obj: Design) -> str:
        info = obj.jkField.filter(direction=JKDesignInfo.Direction.FORWARD).first()
        return info.description if info else ""

    @staticmethod
    def resolve_reverse_source(obj: Design) -> str:
        info = obj.jkField.filter(direction=JKDesignInfo.Direction.REVERSE).first()
        return info.source if info else ""

    @staticmethod
    def resolve_reverse_destination(obj: Design) -> str:
        info = obj.jkField.filter(direction=JKDesignInfo.Direction.REVERSE).first()
        return info.destination if info else ""

    @staticmethod
    def resolve_reverse_description(obj: Design) -> str:
        info = obj.jkField.filter(direction=JKDesignInfo.Direction.REVERSE).first()
        return info.description if info else ""

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
    # 接口类型包含
    type: str = Field('', alias='type')
    is_bidirectional: bool = Field(False, alias='is_bidirectional')
    forward_source: str = Field("")
    forward_destination: str = Field("")
    forward_description: str = Field("")
    reverse_source: str = Field("")
    reverse_destination: str = Field("")
    reverse_description: str = Field("")

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

# 批量替换design的接口Schema
class ReplaceDesignContentSchema(Schema):
    project_id: int
    round_key: str
    originText: str
    replaceText: str
    selectRows: List[int]
    selectColumn: List[str]
