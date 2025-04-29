"""该模块：选择节点新创建一个轮次，数据为选中节点"""
import re
from copy import deepcopy
from apps.project.models import Project, Round, Dut, Design, TestDemand, Case

class TreeKey(object):
    """生成一个dict，展示复制的节点tree_dict是解析后的属性名称"""
    """递归写法：
            def slide(key_list):
            tree_dict = {}
            for key in key_list:
                split_list = key.split('-', 1)
                if split_list[0] not in tree_dict:
                    tree_dict[split_list[0]] = []
                    if len(split_list) > 1:
                        tree_dict[split_list[0]].append(split_list[1])
                    else:
                        tree_dict[split_list[0]] = 'all'
                else:
                    if isinstance(tree_dict[split_list[0]], list):
                        if len(split_list) > 1:
                            tree_dict[split_list[0]].append(split_list[1])
                        else:
                            tree_dict[split_list[0]] = 'all'
        
            for k, v in tree_dict.items():
                if isinstance(v, list):
                    tree_dict[k] = slide(v)
            return tree_dict
        
        key_l = ['0-1-1-0', '0-1-2-1', '0-2-0-1']
        print(slide(key_l))
    """

    def __init__(self, key_list):
        self.tree_dict = {}
        if key_list is None:
            self.key_list = []
            return
        self.key_list = deepcopy(key_list)
        res_dict = self.list_dict(self.key_list)
        for k, v in res_dict.items():
            if isinstance(v, list):
                res_dict[k] = self.list_dict(v)
                for k1, v1 in res_dict[k].items():
                    if isinstance(v1, list):
                        res_dict[k][k1] = self.list_dict(v1)
                        for k2, v2 in res_dict[k][k1].items():
                            if isinstance(v2, list):
                                res_dict[k][k1][k2] = self.list_dict(v2)
                                for k3, v3 in res_dict[k][k1][k2].items():
                                    if isinstance(v3, list):
                                        res_dict[k][k1][k2][k3] = self.list_dict(v3)
        self.tree_dict = res_dict

    def list_dict(self, key_list) -> dict:
        tree_dict = {}
        for key in key_list:
            split_list = key.split('-', 1)
            if len(split_list) == 1:
                tree_dict[split_list[0]] = 'all'
            else:
                if split_list[0] not in tree_dict:
                    tree_dict[split_list[0]] = []
                if isinstance(tree_dict[split_list[0]], list):
                    tree_dict[split_list[0]].append(split_list[1])
        return tree_dict

    def copy_tree(self, round_count: int, project_obj: Project):
        for round_k, round_v in self.tree_dict.items():
            # 1.这是轮次层级，如果为'all'，则复制整个轮次到第二轮
            if round_v == 'all':
                round_obj: Round = Round.objects.filter(key=round_k, project=project_obj).first()
                round_obj.remark = f"第{round_count + 1}轮测试"
                round_obj.ident = round_obj.ident.replace(round_obj.ident[-1], f'{round_count + 1}')
                round_obj.name = f"第{round_count + 1}轮测试"
                round_obj.title = f"第{round_count + 1}轮测试"
                round_obj.key = f"{round_count}"
                round_obj.id = None
                round_obj.save()
                round_origin: Round = Round.objects.filter(key=round_k, project=project_obj).first()
                dut_qs = round_origin.rdField.all()
                for dut in dut_qs:
                    dut_origin = deepcopy(dut)
                    dut.ident = re.sub(r"-R\d+-", f'-R{round_count + 1}-', dut.ident)
                    dut.key = f"{round_count}-{dut.key.split('-')[-1]}"
                    dut.round = round_obj
                    dut.id = None
                    dut.save()
                    design_qs = dut_origin.rsField.all()
                    for i, design in enumerate(design_qs):
                        design_origin = deepcopy(design)
                        design.key = dut.key + f"-{i}"
                        design.dut = dut
                        design.round = round_obj
                        design.id = None
                        design.save()
                        demand_qs = design_origin.dtField.all()
                        for j, demand in enumerate(demand_qs):
                            demand_origin = deepcopy(demand)
                            # 需要将demand_item也复制一份
                            demand.key = design.key + f"-{j}"
                            demand.design = design
                            demand.dut = dut
                            demand.round = round_obj
                            demand.id = None
                            demand.save()
                            for content_obj in demand_origin.testQField.all():
                                content_origin = deepcopy(content_obj)
                                content_obj.testDemand = demand
                                content_obj.id = None
                                content_obj.save()
                                # 需要将DemandContentStep也要复制一份
                                for step_obj in content_origin.testStepField.all():
                                    step_obj.testDemandContent = content_obj
                                    step_obj.id = None
                                    step_obj.save()
                            case_qs = demand_origin.tcField.all()
                            for k, case in enumerate(case_qs):
                                case_origin = deepcopy(case)
                                case.key = demand.key + f"-{k}"
                                case.test = demand
                                case.design = design
                                case.dut = dut
                                case.round = round_obj
                                case.id = None
                                case.save()
                                for step_obj in case_origin.step.all():
                                    step_obj.case = case
                                    step_obj.id = None
                                    step_obj.save()
            # 2.如果不是all，下面有值
            if isinstance(round_v, dict):
                # 2.1 如果字典，则先要创建轮次
                round_obj: Round = Round.objects.filter(key=round_k, project=project_obj).first()
                round_obj.remark = f"第{round_count + 1}轮测试"
                round_obj.ident = round_obj.ident.replace(round_obj.ident[-1], f'{round_count + 1}')
                round_obj.name = f"第{round_count + 1}轮测试"
                round_obj.title = f"第{round_count + 1}轮测试"
                round_obj.key = f"{round_count}"
                round_obj.id = None
                round_obj.save()
                dut_index = 1
                for dut_k, dut_v in round_v.items():
                    # 2.1 如果dut_v是all，那么从该dut整体复制
                    dut_key_origin = round_k + "-" + dut_k
                    if dut_v == 'all':
                        # 查询原始dut
                        dut_obj = Dut.objects.filter(key=dut_key_origin, project=project_obj).first()
                        dut_obj.ident = dut_obj.ident[:11] + str(dut_index)
                        dut_obj.ident = re.sub(r"-R\d+-", f'-R{round_count + 1}-', dut_obj.ident)
                        dut_obj.key = f"{round_count}-{dut_index - 1}"
                        dut_obj.round = round_obj
                        dut_obj.id = None
                        dut_obj.save()
                        dut_origin = Dut.objects.filter(key=dut_key_origin, project=project_obj).first()
                        design_qs = dut_origin.rsField.all()
                        for i, design in enumerate(design_qs):
                            design_origin = deepcopy(design)
                            design.key = dut_obj.key + f"-{i}"
                            design.dut = dut_obj
                            design.round = round_obj
                            design.id = None
                            design.save()
                            demand_qs = design_origin.dtField.all()
                            for j, demand in enumerate(demand_qs):
                                demand_origin = deepcopy(demand)
                                # 需要将demand_item也复制一份
                                demand.key = design.key + f"-{j}"
                                demand.design = design
                                demand.dut = dut_obj
                                demand.round = round_obj
                                demand.id = None
                                demand.save()
                                for content_obj in demand_origin.testQField.all():
                                    content_origin = deepcopy(content_obj)
                                    content_obj.testDemand = demand
                                    content_obj.id = None
                                    content_obj.save()
                                    # 需要将DemandContentStep也要复制一份
                                    for step_obj in content_origin.testStepField.all():
                                        step_obj.testDemandContent = content_obj
                                        step_obj.id = None
                                        step_obj.save()
                                case_qs = demand_origin.tcField.all()
                                for k, case in enumerate(case_qs):
                                    case_origin = deepcopy(case)
                                    case.key = demand.key + f"-{k}"
                                    case.test = demand
                                    case.design = design
                                    case.dut = dut_obj
                                    case.round = round_obj
                                    case.id = None
                                    case.save()
                                    for step_obj in case_origin.step.all():
                                        step_obj.case = case
                                        step_obj.id = None
                                        step_obj.save()

                    if isinstance(dut_v, dict):
                        dut_obj = Dut.objects.filter(key=dut_key_origin, project=project_obj).first()
                        dut_obj.ident = dut_obj.ident[:11] + str(dut_index)
                        dut_obj.ident = re.sub(r"-R\d+-", f'-R{round_count + 1}-', dut_obj.ident)
                        dut_obj.key = f"{round_count}-{dut_index - 1}"
                        dut_obj.round = round_obj
                        dut_obj.id = None
                        dut_obj.save()
                        design_index = 1
                        for design_k, design_v in dut_v.items():
                            design_key_origin = round_k + "-" + dut_k + "-" + design_k
                            if design_v == 'all':
                                design_obj = Design.objects.filter(key=design_key_origin, project=project_obj).first()
                                design_obj.key = f"{dut_obj.key}-{design_index - 1}"
                                design_obj.dut = dut_obj
                                design_obj.round = round_obj
                                design_obj.id = None
                                design_obj.save()
                                design_origin = Design.objects.filter(key=design_key_origin,
                                                                      project=project_obj).first()
                                demand_qs = design_origin.dtField.all()
                                for j, demand in enumerate(demand_qs):
                                    demand_origin = deepcopy(demand)
                                    # 需要将demand_item也复制一份
                                    demand.key = design_obj.key + f"-{j}"
                                    demand.design = design_obj
                                    demand.dut = dut_obj
                                    demand.round = round_obj
                                    demand.id = None
                                    demand.save()
                                    for content_obj in demand_origin.testQField.all():
                                        content_origin = deepcopy(content_obj)
                                        content_obj.testDemand = demand
                                        content_obj.id = None
                                        content_obj.save()
                                        for step_obj in content_origin.testStepField.all():
                                            step_obj.testDemandContent = content_obj
                                            step_obj.id = None
                                            step_obj.save()
                                    case_qs = demand_origin.tcField.all()
                                    for k, case in enumerate(case_qs):
                                        case_origin = deepcopy(case)
                                        case.key = demand.key + f"-{k}"
                                        case.test = demand
                                        case.design = design_obj
                                        case.dut = dut_obj
                                        case.round = round_obj
                                        case.id = None
                                        case.save()
                                        for step_obj in case_origin.step.all():
                                            step_obj.case = case
                                            step_obj.id = None
                                            step_obj.save()

                            if isinstance(design_v, dict):
                                design_obj = Design.objects.filter(key=design_key_origin, project=project_obj).first()
                                design_obj.key = f"{round_count}-{dut_index - 1}-{design_index - 1}"
                                design_obj.dut = dut_obj
                                design_obj.round = round_obj
                                design_obj.id = None
                                design_obj.save()
                                demand_index = 1
                                for demand_k, demand_v in design_v.items():
                                    demand_key_origin = round_k + "-" + dut_k + "-" + design_k + "-" + demand_k
                                    if demand_v == 'all':
                                        demand_obj = TestDemand.objects.filter(key=demand_key_origin,
                                                                               project=project_obj).first()
                                        demand_obj.key = f"{design_obj.key}-{demand_index - 1}"
                                        demand_obj.design = design_obj
                                        demand_obj.dut = dut_obj
                                        demand_obj.round = round_obj
                                        demand_obj.id = None
                                        demand_obj.save()
                                        demand_origin = TestDemand.objects.filter(key=demand_key_origin,
                                                                                  project=project_obj).first()
                                        for content_obj in demand_origin.testQField.all():
                                            content_origin = deepcopy(content_obj)
                                            content_obj.testDemand = demand_obj
                                            content_obj.id = None
                                            content_obj.save()
                                            for step_obj in content_origin.testStepField.all():
                                                step_obj.testDemandContent = content_obj
                                                step_obj.id = None
                                                step_obj.save()
                                        case_qs = demand_origin.tcField.all()
                                        for k, case in enumerate(case_qs):
                                            case_origin = deepcopy(case)
                                            case.key = demand_obj.key + f"-{k}"
                                            case.test = demand_obj
                                            case.design = design_obj
                                            case.dut = dut_obj
                                            case.round = round_obj
                                            case.id = None
                                            case.save()
                                            for step_obj in case_origin.step.all():
                                                step_obj.case = case
                                                step_obj.id = None
                                                step_obj.save()

                                    if isinstance(demand_v, dict):
                                        demand_obj = TestDemand.objects.filter(key=demand_key_origin,
                                                                               project=project_obj).first()
                                        demand_obj.key = f"{round_count}-{dut_index - 1}-{design_index - 1}-{demand_index - 1}"
                                        demand_obj.design = design_obj
                                        demand_obj.dut = dut_obj
                                        demand_obj.round = round_obj
                                        demand_obj.id = None
                                        demand_obj.save()
                                        demand_origin = TestDemand.objects.filter(key=demand_key_origin,
                                                                                  project=project_obj).first()
                                        for content_obj in demand_origin.testQField.all():
                                            content_origin = deepcopy(content_obj)
                                            content_obj.testDemand = demand_obj
                                            content_obj.id = None
                                            content_obj.save()
                                            for step_obj in content_origin.testStepField.all():
                                                step_obj.testDemandContent = content_obj
                                                step_obj.id = None
                                                step_obj.save()
                                        case_index = 1
                                        for case_k, case_v in demand_v.items():
                                            case_key_origin = round_k + "-" + dut_k + "-" + design_k + "-" + demand_k + "-" + case_k
                                            if case_v == 'all':
                                                case_obj = Case.objects.filter(key=case_key_origin,
                                                                               project=project_obj).first()
                                                case_obj.key = f"{demand_obj.key}-{case_index}"
                                                case_obj.test = demand_obj
                                                case_obj.dut = dut_obj
                                                case_obj.design = design_obj
                                                case_obj.round = round_obj
                                                case_obj.id = None
                                                case_obj.save()
                                                case_origin = Case.objects.filter(key=case_key_origin,
                                                                                  project=project_obj).first()
                                                for step_obj in case_origin.step.all():
                                                    step_obj.case = case_obj
                                                    step_obj.id = None
                                                    step_obj.save()

                                            case_index += 1
                                    demand_index += 1
                            design_index += 1
                    dut_index += 1
