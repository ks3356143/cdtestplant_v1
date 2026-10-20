from django.db import transaction

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
    ids = _ensure_all_exist(ids, model)
    # 一次性删除，避免逐个 id 查库 + 逐条删除
    model.objects.filter(pk__in=ids).delete()


def _ensure_all_exist(ids, model):
    """校验 id 全部存在，返回去重后的列表；不存在则抛 404"""
    from ninja.errors import HttpError
    ids = list(dict.fromkeys(ids or []))
    if not ids:
        raise HttpError(400, '请选择要删除的数据')
    found = set(model.objects.filter(pk__in=ids).values_list('pk', flat=True))
    missing = [item for item in ids if item not in found]
    if missing:
        raise HttpError(404, f'数据不存在或已被删除：{missing}')
    return ids


def _clear_problem_case_through(**filters):
    """批量清理 Problem-Case 多对多关系（等价于逐条 case.caseField.clear()）"""
    from apps.project.models import Problem
    Problem.case.through.objects.filter(**filters).delete()


# project删除，对应problem问题单多对多关系也要删除
@transaction.atomic
def multi_delete_project(ids, model):
    ids = _ensure_all_exist(ids, model)
    ident_map = dict(model.objects.filter(pk__in=ids).values_list('pk', 'ident'))
    # (注意：project所属problem全部删除，且关联关系先批量解除)
    _clear_problem_case_through(problem__project_id__in=ids)
    model.objects.filter(pk__in=ids).delete()
    return [ident_map[item] for item in ids]


# testDemand多个id删除便捷函数，参数1:ids数组，参数2：ORM模型
@transaction.atomic
def multi_delete_testDemand(ids, model):
    ids = _ensure_all_exist(ids, model)
    # （多对多删除）先批量解除用例与问题单的关联
    _clear_problem_case_through(case__test_id__in=ids)
    model.objects.filter(pk__in=ids).delete()


# dut的删除，需要多对多case-problem
@transaction.atomic
def multi_delete_dut(ids, model):
    ids = _ensure_all_exist(ids, model)
    _clear_problem_case_through(case__dut_id__in=ids)
    model.objects.filter(pk__in=ids).delete()


# design的多个id删除便捷函数，参数1:ids数组，参数2：ORM模型
@transaction.atomic
def multi_delete_design(ids, model):
    ids = _ensure_all_exist(ids, model)
    _clear_problem_case_through(case__design_id__in=ids)
    model.objects.filter(pk__in=ids).delete()


# 由于case有多对多关系，所以单独提出来删除
@transaction.atomic
def multi_delete_case(ids, model):
    ids = _ensure_all_exist(ids, model)
    _clear_problem_case_through(case_id__in=ids)
    model.objects.filter(pk__in=ids).delete()
