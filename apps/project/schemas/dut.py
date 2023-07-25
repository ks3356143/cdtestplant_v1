from apps.project.models import Dut
from ninja import Field, Schema, ModelSchema

class DutModelOutSchema(ModelSchema):
    class Config:
        model = Dut
        model_exclude = ['project', 'round', 'remark', 'sort']

class DutFilterSchema(Schema):
    ident: str = Field(None, alias='ident')
    type: str = Field(None, alias='type')
    name: str = Field(None, alias='name')

# 树状目录schema
class DutTreeInputSchema(Schema):
    # 注意这里有alias
    project_id: int = Field(None, alias='projectId')
    key: str = Field(None, alias='key')
    level: str = Field(None, alias='level')

class DutTreeReturnSchema(Schema):
    title: str = Field(..., alias='title')
    key: str = Field(..., alias='key')
    level: str = Field(..., alias='level')
