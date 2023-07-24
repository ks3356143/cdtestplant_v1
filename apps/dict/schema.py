from ninja_schema import ModelSchema
from apps.dict.models import Dict, DictItem

class DictItemOut(ModelSchema):
    class Config:
        model = DictItem
        include = ('id', 'title', 'key', 'sort', 'status',)
