"""
本模块主要解决删除父级节点后，其他同级节点的key会重排，重排后子节点没有重排问题
"""
from apps.project.models import Round, Dut, Design, TestDemand

# 0.round删除后，重新排子节点
def round_delete_sub_node_key(round: Round):
    for dut in round.rdField.all():
        remain_dut_key: str = dut.key.split('-')[-1]
        dut_key_list = [round.key, remain_dut_key]
        dut.key = '-'.join(dut_key_list)
        dut.save()
        for design in dut.rsField.all():
            # 取出design的key最后一位，该位是正确的
            remain_key: str = design.key.split('-')[-1]
            key_list = dut.key.split('-')
            key_list.append(remain_key)
            design.key = "-".join(key_list)
            design.save()
            for demand in design.dtField.all():
                remain_demand_key = demand.key.split('-')[-1]
                demand_key_list = design.key.split('-')
                demand_key_list.append(remain_demand_key)
                demand.key = '-'.join(demand_key_list)
                demand.save()
                for case in demand.tcField.all():
                    remain_case_key = case.key.split('-')[-1]
                    case_key_list = demand.key.split('-')
                    case_key_list.append(remain_case_key)
                    case.key = '-'.join(case_key_list)
                    case.save()

# 1.dut删除后，重排同级子节点
def dut_delete_sub_node_key(dut: Dut):
    """
    传入一个删除同级dut后，遍历的dut对象，这里dut的key已经正确，依据该key遍历子节点修改key
    :param dut: dut对象
    :return: None
    """
    for design in dut.rsField.all():
        # 取出design的key最后一位，该位是正确的
        remain_key: str = design.key.split('-')[-1]
        key_list = dut.key.split('-')
        key_list.append(remain_key)
        design.key = "-".join(key_list)
        design.save()
        for demand in design.dtField.all():
            remain_demand_key = demand.key.split('-')[-1]
            demand_key_list = design.key.split('-')
            demand_key_list.append(remain_demand_key)
            demand.key = '-'.join(demand_key_list)
            demand.save()
            for case in demand.tcField.all():
                remain_case_key = case.key.split('-')[-1]
                case_key_list = demand.key.split('-')
                case_key_list.append(remain_case_key)
                case.key = '-'.join(case_key_list)
                case.save()

# 2.design删除后，重排同级子节点
def design_delete_sub_node_key(design: Design):
    for demand in design.dtField.all():
        remain_demand_key = demand.key.split('-')[-1]
        demand_key_list = design.key.split('-')
        demand_key_list.append(remain_demand_key)
        demand.key = '-'.join(demand_key_list)
        demand.save()
        for case in demand.tcField.all():
            remain_case_key = case.key.split('-')[-1]
            case_key_list = demand.key.split('-')
            case_key_list.append(remain_case_key)
            case.key = '-'.join(case_key_list)
            case.save()

# 3.demand删除后，重排case的key顺序
def demand_delete_sub_node_key(demand: TestDemand):
    for case in demand.tcField.all():
        remain_case_key = case.key.split('-')[-1]
        case_key_list = demand.key.split('-')
        case_key_list.append(remain_case_key)
        case.key = '-'.join(case_key_list)
        case.save()
