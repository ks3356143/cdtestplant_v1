from django.db.models import QuerySet

from apps.project.models import Design, TestDemand
from typing import Union

def DesignDrapAtoB(a: Design,
                   b: Design,
                   origin_qs: QuerySet[Design, Design],
                   pos: Union[-1 | 1]) -> str:
    """该函数传入拖拽design和释放到的design，然后更改排序，完成key的重新设置"""
    # 判断是移动到b前面还是后面
    list_qs = list(origin_qs)
    list_qs.remove(a)
    b_index = list_qs.index(b)
    if pos == -1:
        list_qs.insert(b_index, a)
    elif pos == 1:
        list_qs.insert(b_index + 1, a)
    # 重新完成排序后调整key
    prefix = "".join([a.dut.key, "-"])
    for index, obj in enumerate(list_qs):
        obj.key = "".join([prefix, str(index)])
        # 需要测试项调整key
        designConvertDemadnKey(obj)
        obj.save()
    return a.key

def designConvertDemadnKey(desgin_obj: Design):
    """传入Design对象，集体修改demand和case的key"""
    for demand in desgin_obj.dtField.all():
        design_key = desgin_obj.key
        demand_last_key = demand.key.split("-")[-1]
        demand.key = "-".join([design_key, demand_last_key])
        demandConvertCaseKey(demand)
        demand.save()

def demandConvertCaseKey(demand_obj:TestDemand):
    """传入Demand对象集体修改case的key"""
    for case in demand_obj.tcField.all():
        demand_key = demand_obj.key
        case_last_key = case.key.split("-")[-1]
        case.key = "-".join([demand_key, case_last_key])
        case.save()
