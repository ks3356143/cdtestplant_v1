from django.shortcuts import get_object_or_404

# 1.1)这个函数参数1：request、参数2：schema或schema.dict()、参数3：ORM模型
def create(request, data, model):
    if not isinstance(data, dict):
        data = data.dict()
    query_set = model.objects.create(**data)
    return query_set

# 1.2)新增快捷函数，直接填入data
def createWithOutRequestParam(data, model):
    if not isinstance(data, dict):
        data = data.dict()
    query_set = model.objects.create(**data)
    return query_set

# 2.1)更新便捷函数，特别注意参数0为request后面有用，参数1：id，参数2：schema，参数3：ORM模型
def update(request, id, data, model):
    dict_data = data.dict()
    instance = get_object_or_404(model, id=id)
    for attr, value in dict_data.items():
        setattr(instance, attr, value)
    instance.save()
    return instance

# 2.2)更新便捷函数-无request参数 -> data参数为schema对象
def updateWithoutRequestParam(id, data, model):
    dict_data = data.model_dump(exclude_none=True)
    instance = get_object_or_404(model, id=id)
    for attr, value in dict_data.items():
        if attr != 'id':  # 不对id更新
            setattr(instance, attr, value)
    instance.save()
    return instance

# 多个id删除便捷函数，参数1:ids数组，参数2：ORM模型
def multi_delete(ids, model):
    for item in ids:
        # 删除多对多关系 - project
        instance = get_object_or_404(model, pk=item)
        instance.delete()
    pass

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
