from ninja_schema import ModelSchema
from apps.dict.models import Dict, DictItem
from apps.project.models import Contact
from ninja import Field, Schema
from typing import List

# class DictItemOut(ModelSchema):
#     class Config:
#         model = DictItem
#         include = ('id', 'title', 'key', 'sort', 'status',)

class DictOut(ModelSchema):
    class Config:
        model = Dict
        include = ('id', 'code', 'name', 'remark', 'status', 'update_datetime')

class DictItemOut(ModelSchema):
    class Config:
        model = DictItem
        include = ('id', 'update_datetime', 'sort', 'title', 'key', 'status', 'remark', 'show_title')

class DictIndexInput(Schema):
    name: str = Field(None, alias='name')
    remark: str = Field(None, alias='remark')
    code: str = Field(None, alias='code')
    status: str = Field(None, alias='status')
    update_datetime_start: str = Field(None, alias='update_datetime[0]')
    update_datetime_end: str = Field(None, alias='update_datetime[1]')

class ChangeStautsSchemaInput(Schema):
    id: int = Field(None, alias='id')
    status: str = Field(None, alias='status')

class DictItemInput(Schema):
    dict_id: int = Field(None, alias='id')
    title: str = Field(None, alias='title')
    key: str = Field(None, alias='key')
    status: str = Field(None, alias='status')
    show_title: str = Field(None, alias='show_title')
    update_datetime_start: str = Field(None, alias='update_datetime[0]')
    update_datetime_end: str = Field(None, alias='update_datetime[1]')

class DictItemChangeSrotInput(Schema):
    id: int = Field(None, alias='id')
    numberName: str = Field(None, alias='numberName')
    numberValue: int = Field(None, alias='numberValue')

class DictItemCreateInputSchema(Schema):
    dict_id: int = Field(None, alias='id')
    remark: str = Field(None, alias='remark')
    sort: int = Field(None, alias='sort')
    status: str = Field(None, alias='status')
    title: str = Field(None, alias='title')
    show_title: str = Field(None, alias='show_title')

class DictItemUpdateInputSchema(Schema):
    remark: str = Field(None, alias='remark')
    sort: int = Field(None, alias='sort')
    status: str = Field(None, alias='status')
    title: str = Field(None, alias='title')
    show_title: str = Field(None, alias='show_title')

# 删除schema
class DeleteSchema(Schema):
    ids: List[int]

#############公司信息处理##############
class ContactOut(ModelSchema):
    class Config:
        model = Contact
        include = ('id', 'entrust_person', 'name', 'key', 'update_datetime')

class ContactListInputSchema(Schema):
    key: str = Field(None, alias='key')
    name: str = Field(None, alias='name')
    entrust_person: str = Field(None, alias='entrust_person')
