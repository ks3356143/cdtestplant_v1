from ninja_schema import Schema
from django.shortcuts import get_object_or_404

# 这个函数参数1：request、参数2：schema或schema.dict()、参数3：ORM模型
def create(request, data, model):
    if not isinstance(data, dict):
        data = data.dict()
    query_set = model.objects.create(**data)
    return query_set

# 更新便捷函数，特别注意参数0为request后面有用，参数1：id，参数2：schema，参数3：ORM模型
def update(request, id, data, model):
    dict_data = data.dict()
    instance = get_object_or_404(model, id=id)
    for attr, value in dict_data.items():
        setattr(instance, attr, value)
    instance.save()
    return instance

# 多个id删除便捷函数，参数1:ids数组，参数2：ORM模型
def multi_delete(ids,model):
    for item in ids:
        instance = get_object_or_404(model, pk=item)
        instance.delete()
    pass
