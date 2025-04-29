from apps.project.models import Project
from utils.util import *
from utils.chen_response import ChenResponse
from django.db.models import Q

def create_round_context(project_obj: Project, round_id: str):
    """根据轮次，生成测评报告中的测评结果"""
    # 0. 首先定义个轮次对应中文
    round_chinese = ['一', '二', '三', '四', '五', '六', '七', '八', '九', '十']
    round_id = int(round_id)
    round_str_id = str(round_id)
    # 1. 首先先查询给定轮次的round对向
    round_obj = project_obj.pField.filter(key=round_str_id).first()
    # 如果没有轮次对象则返回错误
    if not round_obj:
        return ChenResponse(code=400, status=400, message='注意您没有设置第二轮测试，请添加!')
    dut_qs_r2 = round_obj.rdField  # 当前轮被测件dut对象qs
    dut_qs_r1 = project_obj.pdField.filter(round__key=str(round_id - 1))  # 上一个轮次被测件dut对象qs

    # 查询当前轮次duts，是否有源代码，如果没有返回错误
    so_dut = dut_qs_r2.filter(type='SO').first()  # 当前轮次源代码被测件对象
    if not so_dut:
        return ChenResponse(code=400, status=400, message='注意您某轮次没有编写源代码被测件信息，务必添加...')

    # 查询上一个轮次的dut中的源代码、需求文档
    r1_so_dut = dut_qs_r1.filter(type='SO').first()

    # 3. 文档审查清单
    doc_list = []
    round_duts = round_obj.rdField.filter(Q(type='SJ') | Q(type='XQ') | Q(type='XY'))
    for dut in round_duts:
        dut_dict = {
            'name': dut.name,
            'ident': dut.ref,
            'version': dut.version
        }
        doc_list.append(dut_dict)

    # 4. 发现多少个问题，什么类型多少个问题
    problems = project_obj.projField.all().distinct()  # !important:大变量-项目所有问题
    problems_r2 = problems.filter(case__round__key=round_str_id)  # 当前轮次所有问题

    # 7. 第二轮动态测试用例个数(动态测试-非静态分析、文档审查、代码审查、代码走查4个)
    case_r2_qs = round_obj.rcField.filter(~Q(test__testType='2'), ~Q(test__testType='3'), ~Q(test__testType='8'),
                                          ~Q(test__testType='15'))  # !warning:中变量-第一轮动态测试用例qs
    testType_list, testType_count = create_str_testType_list(case_r2_qs)
    ## 动态测试(第一轮)各个类型测试用例执行表/各个测试需求表
    demand_r2_dynamic_qs = round_obj.rtField.filter(~Q(testType='2'), ~Q(testType='3'), ~Q(testType='8'),
                                                    ~Q(testType='15'))  # !warning:中变量:第一轮动态测试的测试项
    summary_r2_demand_info, summry_r2_demandType_info = create_demand_summary(demand_r2_dynamic_qs,
                                                                              project_obj.ident)

    # 8.第二轮所有动态问题统计
    problems_dynamic_r2 = problems_r2.filter(~Q(case__test__testType='2'), ~Q(case__test__testType='3'),
                                             ~Q(case__test__testType='8'),
                                             ~Q(case__test__testType='15'))  # !critical:大变量:第一轮动态问题单qs
    problem_dynamic_r2_type_str = create_problem_type_str(problems_dynamic_r2)
    problem_dynamic_r2_grade_str = create_problem_grade_str(problems_dynamic_r2)
    r2_dynamic_str = "本轮测试未发现新问题。"
    has_r2_dynamic = False
    if len(problems_dynamic_r2) > 0:
        has_r2_dynamic = True
        r2_dynamic_str = (f"第{round_chinese[int(round_id)]}轮动态测试共发现问题{problems_dynamic_r2.count()}个，"
                          f"其中{problem_dynamic_r2_type_str}；"
                          f"{problem_dynamic_r2_grade_str}。")

    context = {
        'project_name': project_obj.name,
        'r1_so_version': r1_so_dut.version,
        'so_version': so_dut.version,
        'case_dynamic_r2_count': case_r2_qs.count(),
        'dynamic_testType_list': '、'.join(testType_list),
        'dynamic_testType_count': testType_count,
        'r2_exe_info_all': summary_r2_demand_info,
        'r2_exe_info_type': summry_r2_demandType_info,
        'has_r2_dynamic': has_r2_dynamic,
        'r2_dynamic_str': r2_dynamic_str,
        'round_id': round_chinese[round_id],
    }
    return context
