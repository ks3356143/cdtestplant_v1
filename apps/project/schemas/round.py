from ninja_schema import Schema,ModelSchema
from pydantic import Field
from apps.project.models import Round

# 输出树状信息的schema
class TreeReturnRound(Schema):
    title: str = Field(..., alias='title')
    key: str = Field(..., alias='key')
    level: str = Field(..., alias='level')

class RoundInfoOutSchema(ModelSchema):
    class Config:
        model = Round
        exclude = ('remark',)

class EditSchemaIn(Schema):
    beginTime: str
    best_condition_tem: str
    best_condition_voltage: str
    create_datetime: str
    endTime: str
    grade: str
    id: int
    ident: str
    key: str
    level: str
    low_condition_tem: str
    low_condition_voltage: str
    name: str
    package: str
    project: int
    speedGrade: str
    title: str
    update_datetime: str
    typical_condition_tem: str
    typical_condition_voltage: str

class DeleteSchema(Schema):
    title:str
    key:str
    level:str

class CreateRoundOutSchema(ModelSchema):
    class Config:
        model = Round
        exclude = ('remark',)

class CreateRoundInputSchema(ModelSchema):
    class Config:
        model = Round
        include = ('beginTime', 'best_condition_tem', 'best_condition_voltage', 'endTime', 'grade', 'ident',
                        'low_condition_tem', 'low_condition_voltage', 'name', 'package', 'speedGrade',
                        'typical_condition_tem', 'typical_condition_voltage','key',)