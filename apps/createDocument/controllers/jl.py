# 内置模块导入
from pathlib import Path
# 导入框架相关
from django.db import transaction
from django.shortcuts import get_object_or_404
from ninja_extra import api_controller, ControllerBase, route
# 导入权限相关
from ninja_extra.permissions import IsAuthenticated
from ninja_jwt.authentication import JWTAuth
# 导入数据库模型
from apps.project.models import Project
from apps.dict.models import Dict
from docxtpl import InlineImage
# 导入文档处理相关
from docxtpl import DocxTemplate
# 导入自己工具
from utils.chapter_tools.csx_chapter import create_csx_chapter_dict
from utils.util import get_ident, get_case_ident, get_testType
from utils.chen_response import ChenResponse
from utils.path_utils import project_path
from apps.createDocument.extensions.parse_rich_text import RichParser

# @api_controller("/generateJL", tags=['生成测试记录系列'], auth=JWTAuth(), permissions=[IsAuthenticated])
@api_controller("/generateJL", tags=['生成测试记录系列'])
class GenerateControllerJL(ControllerBase):
    @route.get("/create/caserecord", url_name="create-caserecord")
    @transaction.atomic
    def create_caserecord(self, id: int):
        """生成测试记录表格"""
        project_path_str = project_path(id)
        project_obj = get_object_or_404(Project, id=id)
        # 测试用例记录模版位置
        record_template_path = Path.cwd() / 'media' / project_path_str / 'form_template/jl' / '测试用例记录.docx'
        # 打开模版文档
        doc = DocxTemplate(record_template_path)
        # 准备返回的测试类型数组的嵌套
        test_type_len = Dict.objects.get(code='testType').dictItem.count()  # 测试类型的个数
        type_number_list = [i for i in range(1, test_type_len + 1)]  # 测试类型编号对应的列表
        list_list = [[] for j in range(1, test_type_len + 1)]  # 每个测试类型组合为一个列表[[],[],[],[]]
        # 查询出第一轮次
        round_one = project_obj.pField.filter(key=0).first()
        # 测试项的章节号预置处理 - 根据轮次生成list和dict的二维数据
        demand_prefix = '6.2'
        testType_list, last_chapter_items = create_csx_chapter_dict(round_one)
        # 找出所有测试项
        testDemands = round_one.rtField.all()
        # 首先轮询所有测试需求
        for demand in testDemands:
            type_index = type_number_list.index(int(demand.testType))
            demand_ident = get_ident(demand)
            # ~~~组装测试项~~~
            demand_last_chapter = last_chapter_items[demand.testType].index(demand.key) + 1
            demand_chapter = ".".join([demand_prefix, str(testType_list.index(demand.testType) + 1),
                                       str(demand_last_chapter)])
            demand_dict = {
                'name': demand.name,
                'ident': demand_ident,
                'chapter': demand_chapter,
                'item': []
            }
            # ~~~这里组装测试项里面的测试用例~~~
            for case in demand.tcField.all():
                step_list = []
                index = 1
                for one in case.step.all():
                    # 这里需要对operation富文本处理
                    rich_parser = RichParser(one.operation)
                    desc_list = rich_parser.get_final_list(doc, img_size=68)
                    # 这里需要对result富文本处理
                    rich_parser2 = RichParser(one.result)
                    res_list = rich_parser2.get_final_list(doc, img_size=75)
                    # 组装用例里面的步骤dict
                    passed = '通过'
                    if one.passed == '2':
                        passed = '未通过'
                    elif one.passed == '3':
                        passed = '未执行'
                    step_dict = {
                        'index': index,
                        'operation': desc_list,
                        'expect': one.expect,
                        'result': res_list,
                        'passed': passed,
                    }
                    index += 1
                    step_list.append(step_dict)
                # 这里判断里面的单个步骤的执行情况，来输出一个整个用例的执行情况
                exe_noncount = 0
                execution_str = '已执行'
                for ste in step_list:
                    if ste.get('execution') == '3':
                        exe_noncount += 1
                if exe_noncount > 0 and exe_noncount != len(step_list):
                    execution_str = '部分执行'
                elif exe_noncount == len(step_list):
                    execution_str = '未执行'
                else:
                    execution_str = '已执行'
                # 查询所有的problem
                problem_list = []
                problem_prefix = "PT"
                proj_ident = project_obj.ident
                for problem in case.caseField.all():
                    problem_list.append("_".join([problem_prefix, proj_ident, problem.ident]))
                # 组装用例的dict
                rich_parser3 = RichParser(case.timing_diagram)
                timing_diagram = rich_parser3.get_final_list(doc, img_size=115, height=50)
                has_timing_diagram = False
                if len(timing_diagram) > 0:
                    if isinstance(timing_diagram[0], InlineImage):
                        has_timing_diagram = True
                case_dict = {
                    'name': case.name,
                    'ident': get_case_ident(demand_ident, case),
                    'summary': case.summarize,
                    'initialization': case.initialization,
                    'premise': case.premise,
                    'design_person': case.designPerson,
                    'test_person': case.testPerson,
                    'monitor_person': case.monitorPerson,
                    'step': step_list,
                    'execution': execution_str,
                    'time': str(case.exe_time) if case.exe_time is not None else str(case.update_datetime),
                    'problems': "、".join(problem_list),
                    # 2025年4月24日新增
                    'has_timing_diagram': has_timing_diagram,
                    'timing_diagram': timing_diagram,
                }
                demand_dict['item'].append(case_dict)

            list_list[type_index].append(demand_dict)
        # 定义渲染上下文
        context = {}
        output_list = []
        for (index, li) in enumerate(list_list):
            qs = Dict.objects.get(code="testType").dictItem.get(key=str(index + 1))  # type:ignore
            context_str = qs.title
            sort = qs.sort
            table = {
                "type": context_str,
                "item": li,
                "sort": sort
            }
            output_list.append(table)
        # 排序
        output_list = sorted(output_list, key=(lambda x: x["sort"]))
        context["data"] = output_list

        doc.render(context, autoescape=True)
        try:
            doc.save(Path.cwd() / "media" / project_path_str / "output_dir/jl" / "测试用例记录.docx")
            return ChenResponse(status=200, code=200, message="文档生成成功！")
        except PermissionError as e:
            return ChenResponse(status=400, code=400, message="模版文件已打开，请关闭后再试，{0}".format(e))
