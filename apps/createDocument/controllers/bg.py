from datetime import date, timedelta
from pathlib import Path
from ninja_extra import api_controller, ControllerBase, route
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.db.models import Q, QuerySet
from docxtpl import DocxTemplate
from typing import Optional
from docx import Document
from ninja_extra.permissions import IsAuthenticated
from ninja_jwt.authentication import JWTAuth
# 导入模型
from apps.project.models import Project, Dut, TestDemand, Problem
# 工具类函数
from apps.createDocument.extensions import util
from utils.chen_response import ChenResponse
from apps.createDocument.extensions.util import create_bg_docx, get_round1_problem
from utils.util import get_str_dict, get_list_dict, create_problem_grade_str, create_str_testType_list, \
    create_demand_summary, create_problem_type_str, create_problem_table, create_problem_type_table, \
    get_str_abbr
# 根据轮次生成测评内容文档context
from apps.createDocument.extensions.content_result_tool import create_round_context, create_influence_context
from apps.createDocument.extensions.zhui import create_bg_round1_zhui
from apps.createDocument.extensions.solve_problem import create_one_problem_dit
from utils.path_utils import project_path
from apps.createDocument.extensions.util import delete_dir_files
from apps.createDocument.extensions.parse_rich_text import RichParser
from apps.createDocument.extensions.documentTime import DocTime
# 导入生成日志记录模块
from apps.createSeiTaiDocument.extensions.logger import GenerateLogger

# @api_controller("/generateBG", tags=['生成报告文档系列'], auth=JWTAuth(), permissions=[IsAuthenticated])
@api_controller("/generateBG", tags=['生成报告文档系列'])
class GenerateControllerBG(ControllerBase):
    logger = GenerateLogger('测评报告')

    # important：删除之前的文件
    @route.get('/create/deleteBGDocument', url_name='delete-bg-document')
    def delete_bg_document(self, id: int):
        project_path_str = project_path(id)
        save_path = Path.cwd() / 'media' / project_path_str / 'output_dir/bg'
        delete_dir_files(save_path)

    @route.get("/create/techyiju", url_name="create-techyiju")
    @transaction.atomic
    def create_techyiju(self, id: int):
        project_obj = get_object_or_404(Project, id=id)
        duties_qs = project_obj.pdField.filter(Q(type='XQ') | Q(type='SJ') | Q(type='XY'))
        std_documents = []
        for duty in duties_qs:
            one_duty = {'doc_name': duty.name, 'ident_version': duty.ref + '-' + duty.version,
                        'publish_date': duty.release_date, 'source': duty.release_union}
            std_documents.append(one_duty)
        # 添加大纲到这里
        ## 判断是否为鉴定
        doc_name = f'{project_obj.name}软件测评大纲'
        if project_obj.report_type == '9':
            doc_name = f'{project_obj.name}软件鉴定测评大纲'
        # 时间控制类
        timer = DocTime(id)
        # 这里大纲版本升级如何处理
        dg_duty = {'doc_name': doc_name, 'ident_version': f'PT-{project_obj.ident}-TO-1.00',
                   'publish_date': timer.dg_cover_time, 'source': project_obj.test_unit}
        std_documents.append(dg_duty)
        # 需要添加说明、记录
        sm_duty = {'doc_name': f'{project_obj.name}软件测试说明',
                   'ident_version': f'PT-{project_obj.ident}-TD-1.00',
                   'publish_date': timer.sm_cover_time, 'source': project_obj.test_unit}
        jl_duty = {'doc_name': f'{project_obj.name}软件测试记录',
                   'ident_version': f'PT-{project_obj.ident}-TN',
                   'publish_date': timer.jl_cover_time, 'source': project_obj.test_unit}
        # 循环所有轮次，除了第一轮
        std_documents.extend([sm_duty, jl_duty])
        rounds = project_obj.pField.exclude(key='0')
        name_list = ['一', '二', '三', '四', '五', '六', '七', '八', '九', '十']
        index = 1
        for r in rounds:
            hsm_duty = {'doc_name': f'{project_obj.name}软件第{name_list[index]}轮测试说明',
                        'ident_version': f'PT-{project_obj.ident}-TD{str(index + 1)}-1.00',
                        'publish_date': r.beginTime, 'source': project_obj.test_unit}
            hjl_duty = {'doc_name': f'{project_obj.name}软件第{name_list[index]}轮测试记录',
                        'ident_version': f'PT-{project_obj.ident}-TN{str(index + 1)}',
                        'publish_date': r.endTime, 'source': project_obj.test_unit}
            std_documents.extend([hsm_duty, hjl_duty])
            index += 1
        # 生成二级文档
        context = {
            'std_documents': std_documents
        }
        return create_bg_docx("技术依据文件.docx", context, id)

    # 测评地点和时间接口
    @route.get('/create/timeaddress')
    @transaction.atomic
    def create_timeaddress(self, id: int):
        timer = DocTime(id)
        context = timer.bg_address_time()
        return create_bg_docx('测评时间和地点.docx', context, id)

    # 在报告生成多个版本被测软件基本信息
    @route.get('/create/baseInformation', url_name='create-baseInformation')
    def create_information(self, id: int):
        project_obj = get_object_or_404(Project, id=id)
        languages = get_list_dict('language', project_obj.language)
        language_list = []
        for language in languages:
            language_list.append(language.get('ident_version'))

        # 获取轮次
        rounds = project_obj.pField.all()
        round_list = []
        for r in rounds:
            round_dict = {}
            # 获取SO的dut
            so_dut: Dut = r.rdField.filter(type='SO').first()
            if so_dut:
                round_dict['version'] = so_dut.version
                round_dict['line_count'] = int(so_dut.total_lines)
                round_dict['effective_line'] = int(so_dut.effective_lines)
                round_list.append(round_dict)

        context = {
            'project_name': project_obj.name,
            'soft_type': project_obj.get_soft_type_display(),
            'security_level': get_str_dict(project_obj.security_level, 'security_level'),
            'runtime': get_str_dict(project_obj.runtime, 'runtime'),
            'devplant': get_str_dict(project_obj.devplant, 'devplant'),
            'language': "\a".join(language_list),
            'recv_date': project_obj.beginTime.strftime("%Y-%m-%d"),
            'dev_unit': project_obj.dev_unit,
            'version_info': round_list
        }
        return create_bg_docx('被测软件基本信息.docx', context, id)

    # 生成测评完成情况
    @route.get('/create/completionstatus', url_name='create-completionstatus')
    def create_completionstatus(self, id: int):
        project_obj = get_object_or_404(Project, id=id)
        # 找到第一轮轮次对象、第二轮轮次对象
        round1 = project_obj.pField.filter(key='0').first()
        # 第一轮测试项个数
        round1_demand_qs = round1.rtField.all()
        # 第一轮用例个数
        round1_case_qs = round1.rcField.all()
        # 这部分找出第一轮的所有测试类型，输出字符串，并排序
        test_type_set: set = set()
        for case in round1_case_qs:
            demand: TestDemand = case.test
            test_type_set.add(demand.testType)
        round1_testType_list = list(
            map(lambda x: x['ident_version'], get_list_dict('testType', list(test_type_set))))
        # 这里找出第一轮，源代码被测件，并获取版本
        so_dut = round1.rdField.filter(type='SO').first()
        so_dut_verson = "$请添加第一轮的源代码信息$"
        if so_dut:
            so_dut_verson = so_dut.version
        # 这里找出除第一轮的其他轮次
        rounds = project_obj.pField.exclude(key='0')
        rounds_str_chinese = ['一', '二', '三', '四', '五', '六', '七', '八', '九', '十']
        round_list = []
        for r in rounds:
            # 找所属dut的so-dut
            so_dut = r.rdField.filter(type='SO').first()
            # 找出上一轮dut的so-dut
            last_problem_count = Problem.objects.filter(
                case__round__key=str(int(r.key) - 1)).distinct().count()
            current_round_problem_count = Problem.objects.filter(case__round__key=r.key).distinct().count()
            if current_round_problem_count > 0:
                current_round_description = f'引入新问题{current_round_problem_count}个'
            else:
                current_round_description = '经测试软件更改正确，并且未引入新的问题'
            r_dict = {
                'version': so_dut.version if so_dut else '$请添加该轮次源代码信息$',
                'round_index': rounds_str_chinese[int(r.key)],
                'last_problem_count': last_problem_count,
                'current_round_description': current_round_description,
                'start_year': r.beginTime.year,
                'start_month': r.beginTime.month,
                'end_year': (r.beginTime + timedelta(days=4)).year,  # 这里只是简单+4有待商榷
                'end_month': (r.beginTime + timedelta(days=4)).month,
            }
            round_list.append(r_dict)

        # 这部分找到第一轮的问题
        problem_qs = get_round1_problem(project_obj)
        context = {
            'is_JD': True if project_obj.report_type == '9' else False,
            'project_name': project_obj.name,
            'start_time_year': project_obj.beginTime.year,
            'start_time_month': project_obj.beginTime.month,
            'round1_case_count': round1_case_qs.count(),
            'round1_demand_count': round1_demand_qs.count(),
            'round1_testType_str': '、'.join(round1_testType_list),
            'testType_count': len(round1_testType_list),
            'round1_version': so_dut_verson,
            'round1_problem_count': len(problem_qs),
            'end_time_year': date.today().year,
            'end_time_month': date.today().month,
            'round_list': round_list
        }
        # 注入时间
        timer = DocTime(id)
        context.update(**timer.bg_completion_situation())
        return create_bg_docx('测评完成情况.docx', context, id)

    # 生成综述
    @route.get('/create/summary', url_name='create-summary')
    def create_summary(self, id: int):
        project_obj = get_object_or_404(Project, id=id)
        # 找出所有问题单
        problem_qs = project_obj.projField.all()
        problem_grade_dict = {}
        problem_type_dict = {}
        # 建议问题统计
        problem_suggest_count = 0
        problem_suggest_solved_count = 0
        for problem in problem_qs:
            grade_key: str = get_str_dict(problem.grade, 'problemGrade')
            type_key: str = get_str_dict(problem.type, 'problemType')
            # 问题等级字典-计数
            if grade_key in problem_grade_dict.keys():
                problem_grade_dict[grade_key] += 1
            else:
                problem_grade_dict[grade_key] = 1
            # 问题类型字典-计数
            if type_key in problem_type_dict.keys():
                problem_type_dict[type_key] += 1
            else:
                problem_type_dict[type_key] = 1
            # 建议问题统计
            if problem.grade == '3':
                problem_suggest_count += 1
                if problem.status == '1':
                    problem_suggest_solved_count += 1
        problem_grade_list = []
        problem_type_list = []
        for key, value in problem_grade_dict.items():
            problem_grade_list.append("".join([f"{key}问题", f"{value}个"]))
        for key, value in problem_type_dict.items():
            problem_type_list.append("".join([f"{key}", f"{value}个"]))
        # 用来生成建议问题信息
        if problem_suggest_count > 0 and problem_suggest_count - problem_suggest_solved_count > 0:
            all_str = (f"测评过程中提出了{problem_suggest_count}个建议改进，"
                       f"其中{problem_suggest_solved_count}个建议改进已修改，"
                       f"剩余{problem_suggest_count - problem_suggest_solved_count}个未修改并经总体单位认可同意")
        elif problem_suggest_count > 0 and problem_suggest_count - problem_suggest_solved_count == 0:
            all_str = (f"测评过程中提出了{problem_suggest_count}个建议改进，"
                       f"全部建议问题已修改")
        else:
            all_str = f"测评过程中未提出建议项。"

        context = {
            'problem_count': problem_qs.count(),
            'problem_grade_str': "、".join(problem_grade_list),
            'problem_type_str': '、'.join(problem_type_list),
            'all_str': all_str,
        }
        return create_bg_docx('综述.docx', context, id)

    # 生成测试内容和结果[报告非常关键的一环-大模块]
    @route.get('/create/contentandresults_1', url_name='create-contentandresults_1')
    @transaction.atomic
    def create_content_results_1(self, id: int):
        project_obj = get_object_or_404(Project, id=id)
        project_ident = project_obj.ident
        # ~~~~首轮信息~~~~
        round1 = project_obj.pField.filter(key='0').first()  # !warning轮次1对象

        # 1.处理首轮文档名称，新修改，这里取全部轮次的文档内容
        doc_list = []
        round1_duts = project_obj.pdField.filter(Q(type='SJ') | Q(type='XQ') | Q(type='XY'))
        index = 1
        for dut in round1_duts:
            dut_dict = {
                'name': dut.name,
                'ident': dut.ref,
                'version': dut.version,
                'index': index
            }
            doc_list.append(dut_dict)
            index += 1

        # 2.处理首轮文档问题的统计 - 注意去重
        problems = project_obj.projField.all().distinct()  # !important:大变量-项目所有问题
        problems_r1 = problems.filter(case__round__key='0')  # !important:大变量-首轮的所有问题
        problems_doc_r1 = problems_r1.filter(case__test__testType='8')  # 第一轮所有文档问题

        # 3.第一轮代码审查问题统计/版本
        source_r1_dut = round1.rdField.filter(type='SO').first()  # !warning:小变量-第一轮源代码对象
        program_r1_problems = problems_r1.filter(case__test__testType='2')

        # 4.第一轮代码走查问题统计/版本
        zou_r1_problems = problems_r1.filter(case__test__testType='3')
        # 找下是否存在代码走查测试项
        r1_demand_qs = round1.rtField.filter(testType='3')
        has_zou = True if r1_demand_qs.count() > 0 else False

        # 5.第一轮静态分析问题统计
        static_problems = problems_r1.filter(case__test__testType='15')

        # 6.第一轮动态测试用例个数(动态测试-非静态分析、文档审查、代码审查、代码走查4个)
        case_r1_qs = round1.rcField.filter(~Q(test__testType='2'), ~Q(test__testType='3'),
                                           ~Q(test__testType='8'),
                                           ~Q(test__testType='15'),
                                           round__key='0')  # !warning:中变量-第一轮动态测试用例qs
        testType_list, testType_count = create_str_testType_list(case_r1_qs)
        ## 动态测试(第一轮)各个类型测试用例执行表/各个测试需求表
        demand_r1_dynamic_qs = round1.rtField.filter(~Q(testType='2'), ~Q(testType='3'), ~Q(testType='8'),
                                                     ~Q(testType='15'))  # !warning:中变量:第一轮动态测试的测试项
        summary_r1_demand_info, summry_r1_demandType_info = create_demand_summary(demand_r1_dynamic_qs,
                                                                                  project_ident)

        # N.第一轮所有动态问题统计
        problems_dynamic_r1 = problems_r1.filter(~Q(case__test__testType='2'), ~Q(case__test__testType='3'),
                                                 ~Q(case__test__testType='8'),
                                                 ~Q(case__test__testType='15'))  # !critical:大变量:第一轮动态问题单qs
        problem_dynamic_r1_type_str = create_problem_type_str(problems_dynamic_r1)
        problem_dynamic_r1_grade_str = create_problem_grade_str(problems_dynamic_r1)

        context = {
            'project_name': project_obj.name,
            'doc_list': doc_list,
            'r1_doc_problem_count': problems_doc_r1.count(),
            'r1_doc_problem_str':
                f"{'，其中' + create_problem_grade_str(problems_doc_r1) if problems_doc_r1.count() > 0 else '即未发现问题'}",
            'r1_version': source_r1_dut.version if source_r1_dut else "未录入首轮版本信息",
            'r1_program_problem_count': program_r1_problems.count(),
            'r1_program_problem_str':
                f'{"，其中" + create_problem_grade_str(program_r1_problems) if program_r1_problems.count() > 0 else "即未发现问题"}',
            'r1_zou_problem_count': zou_r1_problems.count(),
            'r1_zou_problem_str': f'{"，其中" + create_problem_grade_str(zou_r1_problems) if zou_r1_problems.count() > 0 else "即未发现问题"}',
            'has_zou': has_zou,
            'r1_static_problem_count': static_problems.count(),
            'r1_static_problem_str': f"{'，其中' + create_problem_grade_str(static_problems) if static_problems.count() > 0 else '即未发现问题'}",
            'r1_case_count': case_r1_qs.count(),
            'r1_case_testType': "、".join(testType_list),
            'r1_case_testType_count': testType_count,
            'r1_problem_counts': len(problems_dynamic_r1),
            'r1_exe_info_all': summary_r1_demand_info,
            'r1_exe_info_type': summry_r1_demandType_info,
            'r1_dynamic_problem_str': problem_dynamic_r1_type_str,
            'r1_dynamic_problem_grade_str': problem_dynamic_r1_grade_str,
        }
        return create_bg_docx("测试内容和结果_第一轮次.docx", context, id)

    # 查询除第一轮以外，生成其他轮次测试内容和结果
    @route.get('/create/contentandresults_2', url_name='create-contentandresults_2')
    @transaction.atomic
    def create_content_results_2(self, id: int):
        project_obj = get_object_or_404(Project, id=id)
        # 查询除第一轮，其他有几轮
        round_qs = project_obj.pField.filter(~Q(key='0'))
        round_str_list = [item.key for item in round_qs]
        # 每个轮次都需要生成一个测试内容和标题
        project_path_str = project_path(id)
        for round_str in round_str_list:
            context, round_obj = create_round_context(project_obj, round_str)
            template_path = Path.cwd() / 'media' / project_path_str / 'form_template' / 'bg' / '测试内容和结果_第二轮次.docx'
            doc = DocxTemplate(template_path)
            # ~~~额外添加：除第一轮次的影响域分析~~~
            context['influence'] = create_influence_context(doc, round_obj, project_obj)
            doc.render(context, autoescape=True)
            try:
                doc.save(
                    Path.cwd() / "media" / project_path_str / "output_dir/bg" / f"测试内容和结果_第{context['round_id']}轮次.docx")
            except PermissionError:
                ChenResponse(code=400, status=400, message='您已打开生成文件，请关闭后再试...')

    # 软件问题统计
    @route.get('/create/problem_statistics')
    @transaction.atomic
    def create_problem_statistics(self, id: int):
        project_obj = get_object_or_404(Project, id=id)
        problems = project_obj.projField.all().distinct()  # 项目所有问题单
        context = {
            'closed_count': problems.filter(status='1').count(),
            'noclosed_count': problems.count() - problems.filter(status='1').count(),
            'problem_table': create_problem_table(problems),
            'problem_table_2': create_problem_type_table(problems)
        }
        return create_bg_docx("软件问题统计.docx", context, id)

    # 测试有效性充分性说明
    @route.get('/create/effect_and_adquacy', url_name='create-effect_and_adquacy')
    @transaction.atomic
    def create_effect_and_adquacy(self, id: int):
        project_obj = get_object_or_404(Project, id=id)
        # 判断是否为鉴定
        is_JD = False
        if project_obj.report_type == '9':
            is_JD = True
        # 统计测试项数量
        demand_qs = project_obj.ptField
        # 统计用例个数
        case_qs = project_obj.pcField
        # 测试用例的类型统计个数
        testType_list, testType_count = create_str_testType_list(case_qs.all())
        # 问题单总个数
        problem_qs = project_obj.projField

        context = {
            'project_name': project_obj.name,
            'demand_count': demand_qs.count(),
            'case_count': case_qs.count(),
            'testType_list': "、".join(testType_list),
            'testType_count': testType_count,
            'problem_count': problem_qs.count(),
            'is_JD': is_JD,
        }
        return create_bg_docx('测试有效性充分性说明.docx', context, id)

    # 需求指标符合性情况
    @route.get('/create/demand_effective', url_name='create-demand_effective')
    @transaction.atomic
    def create_demand_effective(self, id: int):
        project_obj = get_object_or_404(Project, id=id)
        # 查询所有需求规格说明的 - 设计需求
        round1_design_qs = project_obj.psField.filter(round__key='0', dut__type='XQ')  # qs:第一轮需求文档的设计需求
        # 将第一轮需求文档名称
        dut_name = f"《{project_obj.name}软件需求规格说明》"
        data_list = []
        design_index = 1
        for design in round1_design_qs:
            # 如果为“/”则写为隐含需求
            if design.chapter.strip() == '/':
                design_dict = {'source': "隐含需求"}
            else:
                design_dict = {'source': "".join([dut_name, design.name, ':', design.chapter])}
            # 将设计需求描述筛入
            rich_parser = RichParser(design.description)
            p_list = rich_parser.get_final_p_list()
            design_dict['description'] = '\a'.join(p_list)
            # 找出其中所有demand
            demand_qs = design.dtField.all()
            if not demand_qs.exists():
                design_dict['demands'] = '未关联测试项'
            else:
                demand_list = []
                index = 0
                for demand in demand_qs:
                    index += 1
                    demand_abbr = get_str_abbr(demand.testType, 'testType')
                    demand_list.append(f'{index}、XQ_{demand_abbr}_{demand.ident}-{demand.name}')
                design_dict['demands'] = '\a'.join(demand_list)
            # 通过还是未通过
            design_dict['pass'] = '通过'
            design_dict['index'] = design_index  # noqa
            data_list.append(design_dict)
            design_index += 1

        # ~~~~指标符合性表~~~~
        data_yz_list = []
        # qs:第一轮需求文档的设计需求
        has_YZ = False
        round1_design_yz_qs = project_obj.psField.filter(round__key='0', dut__type='YZ')
        if round1_design_yz_qs.exists():
            has_YZ = True
            # 如果有研制总要求的dut，继续
            for design in round1_design_yz_qs:
                rich_parser2 = RichParser(design.description)
                p_list = rich_parser2.get_final_p_list()
                design_dict = {
                    'yz_des': "".join([design.chapter, '章节：', design.name, '\a', '\a'.join(p_list)])}
                # 找出其中所有demand
                demand_qs = design.dtField.all()
                if not demand_qs.exists():
                    design_dict['demands'] = '未关联测评大纲条款'
                else:
                    # 大纲条款的列表
                    demand_list = []
                    demand_step_list = []
                    index = 0
                    for demand in demand_qs:
                        index += 1
                        demand_list.append(f'{index}、{demand.ident}-{demand.name}')
                        # 测试需求步骤的列表
                        step_list = []
                        for step in demand.testQField.all():
                            step_list.append(step.subName)
                        demand_step_list.append('\a'.join(step_list))

                    design_dict['demands'] = '\a'.join(demand_list)
                    design_dict['steps'] = '\a'.join(demand_step_list)

                # 通过还是未通过
                design_dict['pass'] = '通过'
                data_yz_list.append(design_dict)
                # 处理没有steps字段
                if 'steps' not in design_dict:
                    design_dict['steps'] = '该设计需求未关联测评大纲条款'

        context = {
            'data_list': data_list,
            'data_yz_list': data_yz_list,
            'has_YZ': has_YZ,
        }
        return create_bg_docx('需求指标符合性情况.docx', context, id)

    # 软件质量评价
    @route.get('/create/quality_evaluate', url_name='create-quality_evaluate')
    @transaction.atomic
    def create_quality_evaluate(self, id: int):
        project_obj = get_object_or_404(Project, id=id)
        # 找出最后一轮
        rounds = project_obj.pField.order_by('-key')  # qs：轮次
        last_dut_so: Optional[Dut] = None
        for round in rounds:
            # 查询其源代码dut
            dut_so = round.rdField.filter(type='SO').first()
            if dut_so:
                last_dut_so = dut_so
                break
        # 计算千行缺陷率
        problem_count = project_obj.projField.count()
        # 如果没有轮次信息则返回错误
        if not last_dut_so:
            return ChenResponse(code=400, status=400, message='您还未创建轮次，请进入工作区创建')
        # 计算注释率
        ## 总行数
        total_lines = int(last_dut_so.total_lines)
        ## 有效注释行
        effective_comment_lines = int(last_dut_so.comment_lines)
        comment_ratio = (effective_comment_lines / total_lines) * 100
        context = {
            'last_version': last_dut_so.version,  # 最后轮次代码版本
            'comment_percent': format(comment_ratio, '.4f'),  # 最后轮次代码注释率
            'qian_comment_rate': format(problem_count / int(last_dut_so.total_lines) * 1000, '.4f'),
            'avg_function_lines': "XXXX",
            'avg_cyclomatic': 'XXXX',
            'avg_fan_out': 'XXXX',
        }
        # 判断是否有metrics一对一模型关联
        if hasattr(last_dut_so, 'metrics'):
            context['avg_function_lines'] = str(last_dut_so.metrics.avg_function_lines)
            context['avg_cyclomatic'] = str(last_dut_so.metrics.avg_cyclomatic)
            context['avg_fan_out'] = str(last_dut_so.metrics.avg_fan_out)
        return create_bg_docx('软件质量评价.docx', context, id)

    # 软件总体结论
    @route.get('/create/entire', url_name='create-entire')
    @transaction.atomic
    def create_entire(self, id: int):
        project_obj = get_object_or_404(Project, id=id)
        # 是否鉴定
        is_JD = False
        if project_obj.report_type == '9':
            is_JD = True
        # 找出最后一轮并且有源代码的dut
        rounds = project_obj.pField.order_by('-key')  # qs：轮次
        last_dut_so: Optional[Dut] = None
        for round in rounds:
            # 查询其源代码dut
            dut_so = round.rdField.filter(type='SO').first()
            if dut_so:
                last_dut_so = dut_so
                break
        # 找出所有被测件协议（XY）、需求规格说明（XQ）、设计说明（SJ）
        duties_qs = project_obj.pdField.filter(Q(type='XQ') | Q(type='SJ') | Q(type='XY'))
        # ***Inspect-start***
        if not last_dut_so:
            self.logger.model = '测评报告'
            self.logger.write_warning_log('总体结论', f'项目没创建轮次，请检查')
            return None
        # ***Inspect-end***
        context = {
            'name': project_obj.name,
            'last_version': last_dut_so.version,
            'is_JD': is_JD,
            'dut_list': [
                {
                    'index': index + 1,
                    'name': dut_single.name,
                    'ref': dut_single.ref,
                    'version': dut_single.version,
                } for index, dut_single in enumerate(duties_qs)
            ],
            'last_dut_so_ref': last_dut_so.ref,
        }
        return create_bg_docx('总体结论.docx', context, id)

    # 研总需求追踪 - 注意生成每个轮次的追踪
    @route.get('/create/yzxq_track', url_name='create-yzxq_track')
    @transaction.atomic
    def create_yzxq_track(self, id: int):
        project_obj = get_object_or_404(Project, id=id)
        # 是否是鉴定的变量，如果为鉴定，则需要研总的追踪
        is_JD = False
        if project_obj.report_type == '9':
            is_JD = True
        # 查询多少个轮次
        round_count = project_obj.pField.count()
        round_str_list = [str(i) for i in range(round_count)]
        # 生成研总的design_list
        design_list_all = []
        for round_str in round_str_list:
            # 找寻轮次里面源代码版本
            dut_version = 'XXX'
            dut_so = Dut.objects.filter(round__key=round_str, type='SO').first()
            if dut_so:
                dut_version = dut_so.version
            if is_JD:
                design_list_yz = create_bg_round1_zhui(project_obj, dut_str='YZ', round_str=round_str)
                one_table_dict = {
                    'design_list': design_list_yz,
                    'version': 'V' + dut_version,
                    'title': '研制总要求'
                }
                design_list_all.append(one_table_dict)
                design_list_xq = create_bg_round1_zhui(project_obj, dut_str='XQ', round_str=round_str)
                one_table_dict_xq = {
                    'design_list': design_list_xq,
                    'version': 'V' + dut_version,
                    'title': '需求规格说明'
                }
                design_list_all.append(one_table_dict_xq)
            else:
                design_list_xq = create_bg_round1_zhui(project_obj, dut_str='XQ', round_str=round_str)
                one_table_dict_xq = {
                    'design_list': design_list_xq,
                    'version': 'V' + dut_version,
                    'title': '需求规格说明'
                }
                design_list_all.append(one_table_dict_xq)
        context = {
            'design_list_all': design_list_all,
        }

        # 手动渲染tpl文档
        project_path_str = project_path(id)
        input_file = Path.cwd() / 'media' / project_path_str / 'form_template' / 'bg' / '研总需归追踪.docx'
        temporary_file = Path.cwd() / 'media' / project_path_str / 'form_template' / 'bg' / 'temporary' / '研总需归追踪_temp.docx'
        out_put_file = Path.cwd() / 'media' / project_path_str / 'output_dir' / 'bg' / '研总需归追踪.docx'
        doc = DocxTemplate(input_file)
        doc.render(context, autoescape=True)
        doc.save(temporary_file)
        # 通过docx合并单元格
        if temporary_file.is_file():
            try:
                docu = Document(temporary_file)
                # 循环找到表格
                for table in docu.tables:
                    util.merge_all_cell(table)
                # 储存到合适位置
                docu.save(out_put_file)
                return ChenResponse(code=200, status=200, message='文档生成成功...')
            except PermissionError:
                return ChenResponse(code=400, status=400, message='请检查文件是否打开，如果打开则关闭...')
        else:
            return ChenResponse(code=400, status=400, message='中间文档未找到，请检查你模版是否存在...')

    # 生成问题汇总表
    @route.get('/create/problems_summary', url_name='create-problem_summary')
    @transaction.atomic
    def create_problem_summary(self, id: int):
        tpl_doc = Path.cwd() / "media" / project_path(id) / "form_template" / "bg" / "问题汇总表.docx"
        doc = DocxTemplate(tpl_doc)
        project_obj = get_object_or_404(Project, id=id)
        problem_prefix = "_".join(['PT', project_obj.ident])
        problems = project_obj.projField
        # 先查询有多少轮次
        round_count = project_obj.pField.count()
        round_str_list = [str(x) for x in range(round_count)]
        data_list = []
        for round_str in round_str_list:
            # 查询所属当前轮次的SO-dut
            so_dut = Dut.objects.filter(round__key=round_str, type='SO').first()
            round_dict = {
                'static': [],
                'dynamic': [],
                'version': so_dut.version if so_dut else "v1.0",
            }
            # 找出轮次中静态问题
            r1_static_problems = problems.filter(case__round__key=round_str,
                                                 case__test__testType__in=['2', '3', '8', '15']).distinct()
            for problem in r1_static_problems:
                problem_dict = create_one_problem_dit(problem, problem_prefix, doc)
                round_dict['static'].append(problem_dict)

            # 找出轮次中动态问题
            r1_dynamic_problems = problems.filter(case__round__key=round_str).exclude(
                case__test__testType__in=['2', '3', '8', '15']).distinct()
            for problem in r1_dynamic_problems:
                problem_dict = create_one_problem_dit(problem, problem_prefix, doc)
                round_dict['dynamic'].append(problem_dict)
            data_list.append(round_dict)

        context = {
            'data_list': data_list
        }

        doc.render(context, autoescape=True)
        try:
            doc.save(Path.cwd() / "media" / project_path(id) / "output_dir/bg" / "问题汇总表.docx")
            return ChenResponse(status=200, code=200, message="文档生成成功！")
        except PermissionError as e:
            return ChenResponse(status=400, code=400, message="模版文件已打开，请关闭后再试，{0}".format(e))

    # 生成摸底清单
    @route.get('/create/modi_list', url_name='create-modi-list')
    @transaction.atomic
    def create_modi_list(self, id: int):
        tpl_doc = Path.cwd() / "media" / project_path(id) / "form_template" / "bg" / "摸底清单.docx"
        doc = DocxTemplate(tpl_doc)
        project_obj = get_object_or_404(Project, id=id)
        # 查询所有轮次“摸底测试”的测试项
        demands_qs = project_obj.ptField.all()
        modi_list = []
        for demand in demands_qs:
            one_modi = {}
            testType_str = get_str_dict(demand.testType, 'testType')
            if "摸底" in testType_str:
                # 1.找到设计需求章节号以及描述
                design = demand.design
                one_modi['source'] = f"{design.chapter}-{design.name}" if design.chapter != '/' else "隐含需求"
                one_modi['desc'] = "\a".join(RichParser(design.description).get_final_p_list())
                # 2.找所有的case
                case_qs = demand.tcField.all()
                one_modi['result'] = []
                for case in case_qs:
                    # 找case的步骤
                    for step in case.step.all():
                        if step.passed == '1':  # 只获取通过的
                            one_modi['result'].append("\a".join(RichParser(step.result).get_final_p_list()))
                modi_list.append(one_modi)
        # 渲染上下文
        context = {
            'modi_list': modi_list,
        }
        doc.render(context, autoescape=True)
        try:
            doc.save(Path.cwd() / "media" / project_path(id) / "output_dir/bg" / "摸底清单.docx")
            return ChenResponse(status=200, code=200, message="文档生成成功！")
        except PermissionError as e:
            return ChenResponse(status=400, code=400, message="模版文件已打开，请关闭后再试，{0}".format(e))
