from copy import deepcopy
from pathlib import Path
from ninja_extra import api_controller, ControllerBase, route
from ninja_extra.permissions import IsAuthenticated
from ninja_jwt.authentication import JWTAuth
from django.db import transaction
from django.db.models import QuerySet
from docxtpl import DocxTemplate
from apps.dict.models import Dict
from utils.chen_response import ChenResponse
from django.shortcuts import get_object_or_404
from typing import Union
from docxtpl import InlineImage
from apps.project.models import Dut, Project, Round
from utils.util import get_list_dict, get_str_dict, get_ident, get_case_ident
from utils.chapter_tools.csx_chapter import create_csx_chapter_dict
from utils.path_utils import project_path
from apps.createDocument.extensions.util import delete_dir_files
from apps.createDocument.extensions.parse_rich_text import RichParser
# 导入生成日志记录模块
from apps.createSeiTaiDocument.extensions.logger import GenerateLogger

chinese_round_name: list = ['一', '二', '三', '四', '五', '六', '七', '八', '九', '十']

# @api_controller("/generateHSM", tags=['生成回归记录系列文档'], auth=JWTAuth(), permissions=[IsAuthenticated])
@api_controller("/generateHJL", tags=['生成回归记录系列文档'])
class GenerateControllerHJL(ControllerBase):
    logger = GenerateLogger('回归测试记录')

    # important：删除之前的文件
    @route.get('/create/deleteHJLDocument', url_name='delete-hjl-document')
    def delete_hjl_document(self, id: int):
        project_path_str = project_path(id)
        save_path = Path.cwd() / 'media' / project_path_str / 'output_dir/hjl'
        delete_dir_files(save_path)

    @route.get("/create/basicInformation", url_name="create-basicInformation")
    @transaction.atomic
    def create_basicInformation(self, id: int):
        """生成回归测试记录的被测软件基本信息"""
        project_path_str = project_path(id)
        tpl_path = Path.cwd() / 'media' / project_path_str / 'form_template/hjl' / '被测软件基本信息.docx'
        doc = DocxTemplate(tpl_path)
        project_obj = get_object_or_404(Project, id=id)
        # 第一轮次对象
        round1_obj: Union[Round, None] = project_obj.pField.filter(key='0').first()
        # 第一轮源代码被测件对象
        round1_so_dut: Union[Dut, None] = round1_obj.rdField.filter(type='SO').first()
        languages = get_list_dict('language', project_obj.language)
        language_list = [item['ident_version'] for item in languages]
        # 取非第一轮次
        hround_list: QuerySet = project_obj.pField.exclude(key='0')
        if len(hround_list) < 1:
            # ***Inspect-start***
            self.logger.model = '回归测试记录'
            self.logger.write_warning_log('当前文档全部片段', f'该项目没有创建轮次')
            # ***Inspect-end***
            return ChenResponse(code=400, status=400, message='您未创建轮次，请创建完毕后再试')

        context = {
            'project_name': project_obj.name,
            'language': "、".join(language_list),
            'soft_type': project_obj.get_soft_type_display(),
            'security_level': get_str_dict(project_obj.security_level, 'security_level'),
            'runtime': get_str_dict(project_obj.runtime, 'runtime'),
            'devplant': get_str_dict(project_obj.devplant, 'devplant'),
            'recv_date': project_obj.beginTime.strftime("%Y-%m-%d"),
            'dev_unit': project_obj.dev_unit,
        }

        version_info = [{'version': round1_so_dut.version,
                         'line_count': int(round1_so_dut.total_lines),
                         'effective_line': int(round1_so_dut.effective_lines)}]
        # 循环回归的轮次
        for hround in hround_list:
            # 每个轮次独立渲染context
            context_round = deepcopy(context)
            # 取中文名称
            cname = chinese_round_name[int(hround.key)]  # 输出二、三...
            # 取该轮次源代码版本放入版本列表
            so_dut: Dut = hround.rdField.filter(type='SO').first()
            if not so_dut:
                return ChenResponse(code=400, status=400, message=f'您第{cname}轮次中缺少源代码被测件，请添加')
            version_info.append(
                {'version': so_dut.version, 'line_count': int(so_dut.total_lines),
                 'effective_line': int(so_dut.effective_lines)})
            context_round['version_info'] = version_info
            # 开始渲染每个轮次的二级文档
            save_path = Path.cwd() / 'media' / project_path_str / 'output_dir/hjl' / f"第{cname}轮被测软件基本信息.docx"
            doc.render(context=context_round)
            try:
                doc.save(save_path)
            except PermissionError:
                return ChenResponse(code=400, status=400, message='您打开了生成的文档，请关闭后重试')
        return ChenResponse(code=200, status=200, message='多轮回归说明文档基本信息生成完毕')

    @route.get("/create/caseinfo", url_name="create-caseinfo")
    @transaction.atomic
    def create_caseinfo(self, id: int):
        """生成回归测试记录的-{测试用例记录}"""
        project_path_str = project_path(id)
        tpl_path = Path.cwd() / 'media' / project_path_str / 'form_template/hjl' / '测试用例记录.docx'
        doc = DocxTemplate(tpl_path)
        project_obj = get_object_or_404(Project, id=id)
        hround_list: QuerySet = project_obj.pField.exclude(key='0')
        if len(hround_list) < 1:
            return None
        demand_prefix = '3.1'
        # 循环每轮轮次对象
        for hround in hround_list:
            cname = chinese_round_name[int(hround.key)]  # var：输出二、三字样
            test_type_len = Dict.objects.get(code='testType').dictItem.count()  # 测试类型的个数
            type_number_list = [i for i in range(1, test_type_len + 1)]  # 测试类型编号对应的列表
            list_list = [[] for j in range(1, test_type_len + 1)]  # 每个测试类型组合为一个列表[[],[],[],[]]
            testType_list, last_chapter_items = create_csx_chapter_dict(hround)
            testDemands = hround.rtField.all()  # 本轮所有测试项
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
                        rich_parser2 = RichParser(one.result)
                        res_list = rich_parser2.get_final_list(doc, img_size=75)
                        # 组装用例里面的步骤dict
                        passed = '通过'
                        if one.passed == '2':
                            passed = '未通过'
                        if one.passed == '3':
                            passed = '未执行'
                        step_dict = {
                            'index': index,
                            'operation': desc_list,
                            'expect': one.expect,
                            'result': res_list,
                            'passed': passed,
                        }
                        step_list.append(step_dict)
                        index += 1
                    # 查询所有的problem
                    problem_list = []
                    problem_prefix = "PT"
                    proj_ident = project_obj.ident
                    for problem in case.caseField.all():
                        problem_list.append("_".join([problem_prefix, proj_ident, problem.ident]))
                    # fpga的时序图
                    rich_parser3 = RichParser(case.timing_diagram)
                    timing_diagram = rich_parser3.get_final_list(doc, img_size=115, height=50)
                    has_timing_diagram = False
                    if len(timing_diagram) > 0:
                        if isinstance(timing_diagram[0], InlineImage):
                            has_timing_diagram = True
                    # 组装用例的dict
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
                        'time': str(case.exe_time) if case.exe_time is not None else str(case.update_datetime),
                        'problems': "、".join(problem_list),
                        'round_num_chn': cname,
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
                qs = Dict.objects.get(code="testType").dictItem.get(key=str(index + 1))
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
            # 最后渲染
            save_path = Path.cwd() / 'media' / project_path_str / 'output_dir/hjl' / f"第{cname}轮测试用例记录.docx"
            doc.render(context)
            try:
                doc.save(save_path)
            except PermissionError:
                return ChenResponse(code=400, status=400, message='您打开了生成的文档，请关闭后重试')
        return ChenResponse(code=200, status=200, message='多轮回归测试用例记录生成完毕')
