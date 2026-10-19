from django.db import transaction
from django.shortcuts import get_object_or_404

# 1.1)这个函数参数1：request、参数2：schema或schema.dict()、参数3：ORM模型
# 注意：request 参数仅为兼容旧调用签名，实际未使用，逻辑与 createWithOutRequestParam 完全一致
def create(request, data, model):
    return createWithOutRequestParam(data, model)

# 1.2)新增快捷函数，直接填入data
def createWithOutRequestParam(data, model):
    if not isinstance(data, dict):
        data = data.model_dump()
    query_set = model.objects.create(**data)
    return query_set

# 2)更新便捷函数-无request参数 -> data参数为schema对象
def updateWithoutRequestParam(id, data, model):
    dict_data = data.model_dump(exclude_none=True)
    instance = get_object_or_404(model, id=id)
    for attr, value in dict_data.items():
        if attr != 'id':  # 不对id更新
            setattr(instance, attr, value)
    instance.save()
    return instance

# 多个id删除便捷函数，参数1:ids数组，参数2：ORM模型
# 加事务：中途某个 id 不存在时整体回滚，避免部分删除的不一致状态
@transaction.atomic
def multi_delete(ids, model):
    ids = list(ids or [])
    if not ids:
        from ninja.errors import HttpError
        raise HttpError(400, '请选择要删除的数据')
    found = set(model.objects.filter(pk__in=ids).values_list('pk', flat=True))
    missing = [item for item in ids if item not in found]
    if missing:
        from ninja.errors import HttpError
        raise HttpError(404, f'数据不存在或已被删除：{missing}')
    # 一次性删除，避免逐个 id 查库 + 逐条删除
    model.objects.filter(pk__in=ids).delete()

# project删除，对应problem问题单多对多关系也要删除
def multi_delete_project(ids, model):
    idents = []
    for item in ids:
        instance = get_object_or_404(model, pk=item)
        # (注意：project所属problem全部删除，且关联关系删除)
        for problem in instance.projField.all():
            problem.case.clear()
        idents.append(instance.ident)
        instance.delete()
    return idents

# testDemand多个id删除便捷函数，参数1:ids数组，参数2：ORM模型
def multi_delete_testDemand(ids, model):
    for item in ids:
        instance = get_object_or_404(model, pk=item)
        # （多对多删除）case下面的problem关联删除
        for case in instance.tcField.all():
            case.caseField.clear()
        instance.delete()
    pass

# dut的删除，需要多对多case-problem
def multi_delete_dut(ids, model):
    for item in ids:
        instance = get_object_or_404(model, pk=item)
        # （多对多删除）case下面的problem关联删除
        for case in instance.ducField.all():
            case.caseField.clear()
        instance.delete()
    pass

# design的多个id删除便捷函数，参数1:ids数组，参数2：ORM模型
def multi_delete_design(ids, model):
    for item in ids:
        instance = get_object_or_404(model, pk=item)
        # （多对多删除）case下面problem关联删除
        for case in instance.dcField.all():
            case.caseField.clear()
        instance.delete()
    pass

# 由于case有多对多关系，所以单独提出来删除
def multi_delete_case(ids, model):
    for item in ids:
        instance = get_object_or_404(model, pk=item)
        instance.caseField.clear()
        instance.delete()
    pass
