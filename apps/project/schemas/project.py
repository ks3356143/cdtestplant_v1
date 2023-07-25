from apps.project.models import Project
from ninja import Field, Schema, ModelSchema
from typing import List

class ProjectRetrieveSchema(ModelSchema):
    class Config:
        model = Project
        model_exclude = ['update_datetime', 'create_datetime', 'remark']

class ProjectFilterSchema(Schema):
    ident: str = Field(None, alias='ident')
    name: str = Field(None, alias='name')
    duty_person: str = Field(None, alias='duty_person')
    security_level: str = Field(None, alias='security_level')
    report_type: str = Field(None, alias="report_type")
    step: str = Field(None, alias="step")

class ProjectCreateInput(ModelSchema):
    class Config:
        model = Project
        model_exclude = ['remark', 'update_datetime', 'create_datetime', 'sort', 'id']

class DeleteSchema(Schema):
    ids: List[int]
