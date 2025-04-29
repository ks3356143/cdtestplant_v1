from typing import Optional
from ninja import Schema, ModelSchema
from pydantic import Field
from apps.project.models import Round

# 输出树状信息的schema
class TreeReturnRound(Schema):
    title: str = Field(..., alias='title')
    key: str = Field(..., alias='key')
    level: str = Field(..., alias='level')

class RoundInfoOutSchema(ModelSchema):
    class Meta:
        model = Round
        exclude = ('remark',)

class EditSchemaIn(Schema):
    beginTime: str
    best_condition_tem: Optional[str] = None
    best_condition_voltage: Optional[str] = None
    create_datetime: str
    endTime: str
    grade: str = '3'
    id: int
    ident: str
    key: str
    level: str
    low_condition_tem: Optional[str] = None
    low_condition_voltage: Optional[str] = None
    name: str
    project: int
    title: str
    update_datetime: str
    typical_condition_tem: Optional[str] = None
    typical_condition_voltage: Optional[str] = None
    # 新增
    location: str

class DeleteSchema(Schema):
    title: str
    key: str
    level: str

class CreateRoundOutSchema(ModelSchema):
    class Meta:
        model = Round
        exclude = ['remark']

class CreateRoundInputSchema(ModelSchema):
    class Meta:
        model = Round
        fields = ['beginTime', 'best_condition_tem', 'best_condition_voltage', 'endTime', 'grade', 'ident',
                  'low_condition_tem', 'low_condition_voltage', 'name',
                  'typical_condition_tem', 'typical_condition_voltage', 'key', 'location']
        fields_optional = ['best_condition_tem', 'best_condition_voltage',
                           'low_condition_tem', 'low_condition_voltage', 'typical_condition_tem',
                           'typical_condition_voltage' 'grade']
