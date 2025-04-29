from typing import Tuple, Any
from copy import deepcopy
from django.shortcuts import get_object_or_404
from apps.project.models import Project
from ninja.errors import HttpError

# 1. case被移动到某测试项下面
def case_move_to_test(project_id: int, case_key: str, demand_key: str) -> Tuple[str, Any]:
    """移动case到某个测试项下面，传入project_id，case的key，测试项的key，renturn -> 元组(旧case的key,新case的key)"""
    same_root_flag = False
    if '-'.join(case_key.split('-')[:-1]) == demand_key:
        same_root_flag = True
    # 判断是否移动到自己所属的demand的，直接返回不操作
    if same_root_flag:
        raise HttpError(500, message='无法移动到自己所属测试项里面')
    project_qs = get_object_or_404(Project, id=project_id)
    case = project_qs.pcField.filter(key=case_key).first()
    demand_origin = case.test  # 未变化之前case对应的测试项
    demand = project_qs.ptField.filter(key=demand_key).first()  # 新的demand对象
    case.ident = demand.ident
    case.test = demand
    case.round = demand.round
    case.dut = demand.dut
    case.design = demand.design
    # 查询被拖拽到的demand有多少用例，用于设置key
    case.key = "".join([demand.key, '-', str(demand.tcField.count())])
    case.save()
    # 因为移动要删除之前demand的用例，所以需要重新设置key
    index = 0
    for c in demand_origin.tcField.all():
        c.key = "".join([demand_origin.key, '-', str(index)])
        c.save()
        index += 1
    return case_key, case.key

# 2.case复制到测试项中
def case_copy_to_test(project_id: int, case_key: str, demand_key: str) -> Tuple[str, Any]:
    # 初始化内容
    project_qs = get_object_or_404(Project, id=project_id)
    case = project_qs.pcField.filter(key=case_key).first()
    demand = project_qs.ptField.filter(key=demand_key).first()
    origin_case = deepcopy(case)
    case.id = None
    case.ident = demand.ident
    case.test = demand
    case.round = demand.round
    case.dut = demand.dut
    case.design = demand.design
    case.key = "".join([demand.key, '-', str(demand.tcField.count())])
    case.save()
    # 用例步骤也要复制一份过去
    for case_step in origin_case.step.all():
        case_step.id = None
        case_step.case = case
        case_step.save()
    return case_key, case.key

# 3.（需要拆分）拖拽用例到用例的函数,TODO:必须拆分
def case_to_case_copy_or_move(project_id: int, drag_key: str, drop_key: str, move: bool, position: int):
    """待优化和上面一样：TODO:封装多个函数理清思路"""
    project_qs = get_object_or_404(Project, id=project_id)
    drag_case = project_qs.pcField.filter(key=drag_key).first()
    drag_demand = drag_case.test
    drop_case = project_qs.pcField.filter(key=drop_key).first()
    drop_demand = drop_case.test
    # 判断是否移动到同级
    same_root_flag = False
    if drag_key.split('-')[:-2] == drop_key.split('-')[:-2]:
        same_root_flag = True
    if move:
        # 1.移动到同级demand - 只需要改变2个key
        if same_root_flag:
            case_list = list(drag_demand.tcField.all())  # 这是已经排序的
            case_list.pop(case_list.index(drag_case))
            # 移动出去后，查看现在drop_case索引
            drop_case_index = case_list.index(drop_case)
            if position == 0 or position == 1:  # 1和0就是往下放，首先drop的位置是不变的
                case_list.insert(drop_case_index + 1, drag_case)
            elif position == -1:
                case_list.insert(drop_case_index, drag_case)
            # 已经排序好了就开始修改key
            ca_index = 0
            for ca in case_list:
                ca.key = "".join([drag_demand.key, '-', str(ca_index)])
                ca.save()
                ca_index += 1
        # 2.移动到非同级demand
        else:
            drag_case.ident = drop_demand.ident
            drag_case.test = drop_demand
            drag_case.round = drop_demand.round
            drag_case.dut = drop_demand.dut
            drag_case.design = drop_demand.design
            drag_case.save()  # 到这里drag_case已经放入了drop_demand
            # 查询所有的drop_demand的所有用例
            drop_case_list = list(drop_demand.tcField.all())
            drop_case_list.pop(drop_case_list.index(drag_case))
            drop_case_index = drop_case_list.index(drop_case)
            if position == 0 or position == 1:  # 1和0就是往下放，首先drop的位置是不变的
                drop_case_list.insert(drop_case_index + 1, drag_case)
            elif position == -1:
                drop_case_list.insert(drop_case_index, drag_case)
            ca_ind = 0
            for ca in drop_case_list:
                ca.key = "".join([drop_demand.key, '-', str(ca_ind)])
                ca.save()
                ca_ind += 1
            # 因为移动要删除之前demand的用例，所以需要重新设置key
            index = 0
            for c in drag_demand.tcField.all():
                c.key = "".join([drag_demand.key, '-', str(index)])
                c.save()
                index += 1
    # 如果是复制
    else:
        origin_drag_case = deepcopy(drag_case)  # 深度复制被拖拽的case
        # 同一个测试项内用例的复制，还要看顺序
        if same_root_flag:
            drag_case.id = None
            drag_case.save()
            # 开始插入到被拖拽case上下
            case_sx_list = list(drag_demand.tcField.all())
            case_sx_list.pop(case_sx_list.index(drag_case))
            drop_case_in = case_sx_list.index(drop_case)
            if position == 0 or position == 1:  # 1和0就是往下放，首先drop的位置是不变的
                case_sx_list.insert(drop_case_in + 1, drag_case)
            elif position == -1:
                case_sx_list.insert(drop_case_in, drag_case)
            ind = 0
            for cas in case_sx_list:
                cas.key = "".join([drag_demand.key, '-', str(ind)])
                cas.save()
                ind += 1
            # 根据origin复制步骤
            for c_step in origin_drag_case.step.all():
                c_step.id = None
                c_step.case = drag_case  # 外键设置为新用例
                c_step.save()
        else:
            drag_case.id = None
            drag_case.ident = drop_demand.ident
            drag_case.test = drop_demand
            drag_case.round = drop_demand.round
            drag_case.dut = drop_demand.dut
            drag_case.design = drop_demand.design
            drag_case.save()
            cases_list = list(drop_demand.tcField.all())
            cases_list.pop(cases_list.index(drag_case))
            drop_case_idx = cases_list.index(drop_case)
            if position == 0 or position == 1:  # 1和0就是往下放，首先drop的位置是不变的
                cases_list.insert(drop_case_idx + 1, drag_case)
            elif position == -1:
                cases_list.insert(drop_case_idx, drag_case)
            cas_idx = 0
            for cas in cases_list:
                cas.key = "".join([drop_demand.key, '-', str(cas_idx)])
                cas.save()
                cas_idx += 1
            # 复制用例步骤
            for cs_step in origin_drag_case.step.all():
                cs_step.id = None
                cs_step.case = drag_case  # 外键设置为新用例
                cs_step.save()
