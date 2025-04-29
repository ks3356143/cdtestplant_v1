"""该文件主要是小工具，简化接口处理函数写的代码太多"""
from ninja import Schema
from django.db.models import QuerySet

def conditionNoneToBlank(condition: Schema):
    """将BaseModel/Schema对象中None变为空字符串"""
    for attr, value in condition.__dict__.items():
        if getattr(condition, attr) is None:
            setattr(condition, attr, '')

def model_retrieve(condition: Schema, qs: QuerySet, exclude_field) -> QuerySet:
    """该函数合并上面功能，传入qs以及排除字段，全部添加__icontains进行查询"""
    conditionNoneToBlank(condition)
    search_obj = {}
    for k, v in condition.dict(exclude_none=True).items():
        if k not in exclude_field:
            search_obj["".join([k, "__icontains"])] = v
    return qs.filter(**search_obj)
