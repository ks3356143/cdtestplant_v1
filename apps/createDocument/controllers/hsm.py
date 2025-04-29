import base64
import io
from pathlib import Path
from copy import deepcopy
from typing import Union
from ninja_extra import api_controller, ControllerBase, route
from ninja_extra.permissions import IsAuthenticated
from ninja_jwt.authentication import JWTAuth
from ninja.errors import HttpError
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.db.models import QuerySet, Q
from docxtpl import DocxTemplate, RichText, InlineImage
from docx.shared import Mm
from docx import Document
# 导入模型
from apps.project.models import Project, Round, Dut
from apps.dict.models import Dict, DictItem
# 导入项目工具
from utils.util import get_list_dict, get_str_dict, MyHTMLParser, get_ident, get_case_ident, get_testType
from utils.chapter_tools.csx_chapter import create_csx_chapter_dict
from utils.chen_response import ChenResponse
from apps.createDocument.extensions import util
from utils.path_utils import project_path
from apps.createDocument.extensions.util import delete_dir_files
from apps.createDocument.extensions.parse_rich_text import RichParser
from apps.createDocument.extensions.documentTime import DocTime
# 导入生成日志记录模块
from apps.createSeiTaiDocument.extensions.logger import GenerateLogger

chinese_round_name: list = ['一', '二', '三', '四', '五', '六', '七', '八', '九', '十']

# @api_controller("/generateHSM", tags=['生成回归说明系列文档'], auth=JWTAuth(), permissions=[IsAuthenticated])
@api_controller("/generateHSM", tags=['生成回归说明系列文档'])
class GenerateControllerHSM(ControllerBase):
    logger = GenerateLogger('回归测试说明')

    # important：删除之前的文件
    @route.get('/create/deleteHSMDocument', url_name='delete-hsm-document')
    def delete_hsm_document(self, id: int):
        project_path_str = project_path(id)
        save_path = Path.cwd() / 'media' / project_path_str / 'output_dir/hsm'
        try:
            delete_dir_files(save_path)
        except PermissionError:
            return ChenResponse(code=400, status=400, message='另一个程序正在占用文件，请关闭后重试')

    @route.get("/create/basicInformation", url_name="create-basicInformation")
    @transaction.atomic
    def create_basicInformation(self, id: int):
        """生成回归测试说明的被测软件基本信息"""
        project_path_str = project_path(id)
        tpl_path = Path.cwd() / 'media' / project_path_str / 'form_template/hsm' / '被测软件基本信息.docx'
        doc = DocxTemplate(tpl_path)
        project_obj: Project = get_object_or_404(Project, id=id)
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
            self.logger.model = '回归测试说明'
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
        version_info = [{
            'version': round1_so_dut.version,
            'line_count': round1_so_dut.total_lines,
            'effective_count': round1_so_dut.effective_lines,
        }]
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
                {
                    'version': so_dut.version,
                    'line_count': so_dut.total_lines,
                    'effective_count': so_dut.effective_lines,
                }
            )
            context_round['version_info'] = version_info
            # 开始渲染每个轮次的二级文档
            save_path = Path.cwd() / 'media' / project_path_str / 'output_dir/hsm' / f"第{cname}轮被测软件基本信息.docx"
            doc.render(context=context_round)
            try:
                doc.save(save_path)
            except PermissionError:
                return ChenResponse(code=400, status=400, message='您打开了生成的文档，请关闭后重试')
        return ChenResponse(code=200, status=200, message='多轮回归说明文档基本信息生成完毕')

    @route.get("/create/docsummary", url_name="create-docsummary")
    @transaction.atomic
    def create_docsummary(self, id: int):
        """生成回归测试说明的文档概述"""
        project_path_str = project_path(id)
        tpl_path = Path.cwd() / 'media' / project_path_str / 'form_template/hsm' / '文档概述.docx'
        doc = DocxTemplate(tpl_path)
        project_obj = get_object_or_404(Project, id=id)
        # 非第一轮轮次对象
        hround_list: QuerySet = project_obj.pField.exclude(key='0')
        if len(hround_list) < 1:
            return None

        context = {
            'project_obj': project_obj.name,
        }

        for hround in hround_list:
            # 取出当前轮次key减1就是上一轮次
            cname = chinese_round_name[int(hround.key)]  # 输出二、三...
            so_dut: Dut = hround.rdField.filter(type='SO').first()
            if not so_dut:
                return ChenResponse(code=400, status=400, message=f'您第{cname}轮次中缺少源代码被测件，请添加')
            # 取上一轮次
            so_dut_last: Dut = Dut.objects.filter(round__key=str(int(hround.key) - 1), project=project_obj,
                                                  type='SO').first()
            round_context = deepcopy(context)
            round_context['current_version'] = so_dut.version
            round_context['last_version'] = so_dut_last.version
            round_context['round_chinese'] = cname
            save_path = Path.cwd() / 'media' / project_path_str / 'output_dir/hsm' / f"第{cname}轮文档概述.docx"
            doc.render(context=round_context)
            try:
                doc.save(save_path)
            except PermissionError:
                return ChenResponse(code=400, status=400, message='您打开了生成的文档，请关闭后重试')
        return ChenResponse(code=200, status=200, message='多轮回归文档概述生成完毕')

    @route.get("/create/jstech", url_name="create-jstech")
    @transaction.atomic
    def create_jstech(self, id: int):
        """生成回归测试说明的技术依据文件"""
        project_path_str = project_path(id)
        tpl_path = Path.cwd() / 'media' / project_path_str / 'form_template/hsm' / '技术依据文件.docx'
        doc = DocxTemplate(tpl_path)
        project_obj = get_object_or_404(Project, id=id)
        duties_qs = project_obj.pdField.filter(Q(type='XQ') | Q(type='SJ') | Q(type='XY'))
        std_documents = []
        for duty in duties_qs:
            one_duty = {'doc_name': duty.name, 'ident_version': duty.ref + '-' + duty.version,
                        'publish_date': duty.release_date, 'source': duty.release_union}
            std_documents.append(one_duty)
        doc_name = f'{project_obj.name}软件测评大纲'
        if project_obj.report_type == '9':
            doc_name = f'{project_obj.name}软件鉴定测评大纲'
        # 时间控制类
        timer = DocTime(id)
        dg_duty = {'doc_name': doc_name, 'ident_version': f'PT-{project_obj.ident}-TO-1.00',
                   'publish_date': timer.dg_cover_time, 'source': project_obj.test_unit}
        std_documents.append(dg_duty)
        # 需要添加说明、记录
        sm_duty = {'doc_name': f'{project_obj.name}软件测试说明', 'ident_version': f'PT-{project_obj.ident}-TD-1.00',
                   'publish_date': timer.sm_cover_time, 'source': project_obj.test_unit}
        jl_duty = {'doc_name': f'{project_obj.name}软件测试记录', 'ident_version': f'PT-{project_obj.ident}-TN',
                   'publish_date': timer.jl_cover_time, 'source': project_obj.test_unit}
        std_documents.extend([sm_duty, jl_duty])

        # 非第一轮的轮次
        hround_list: QuerySet = project_obj.pField.exclude(key='0')
        if len(hround_list) < 1:
            return None
        for hround in hround_list:
            std_documents_round = deepcopy(std_documents)
            # 取出当前轮次key
            cname = chinese_round_name[int(hround.key)]
            hsm_duty = {'doc_name': f'{project_obj.name}软件第{cname}轮测试说明',
                        'ident_version': f'PT-{project_obj.ident}-TD{int(hround.key) + 1}-1.00',
                        'publish_date': hround.beginTime, 'source': project_obj.test_unit}
            hjl_duty = {'doc_name': f'{project_obj.name}软件第{cname}轮测试记录',
                        'ident_version': f'PT-{project_obj.ident}-TN{int(hround.key) + 1}',
                        'publish_date': hround.endTime, 'source': project_obj.test_unit}
            std_documents.extend([hsm_duty, hjl_duty])
            context = {
                'std_documents': std_documents_round
            }
            save_path = Path.cwd() / 'media' / project_path_str / 'output_dir/hsm' / f"第{cname}轮技术依据文件.docx"
            doc.render(context=context)
            try:
                doc.save(save_path)
            except PermissionError:
                return ChenResponse(code=400, status=400, message='您打开了生成的文档，请关闭后重试')
        return ChenResponse(code=200, status=200, message='多轮回归技术依据文件生成完毕')

    @route.get("/create/changePart", url_name="create-changePart")
    @transaction.atomic
    def create_changePart(self, id: int):
        """
            生成回归测试说明的软件更改部分
            暂时没想到如何处理和报告里面软件更改部分关系
        """
        project_path_str = project_path(id)
        tpl_path = Path.cwd() / 'media' / project_path_str / 'form_template/hsm' / '软件更改部分.docx'
        doc = DocxTemplate(tpl_path)
        project_obj = get_object_or_404(Project, id=id)
        context = {
            'project_name': project_obj.name,
        }
        # 非第一轮的轮次
        hround_list: QuerySet = project_obj.pField.exclude(key='0')
        if len(hround_list) < 1:
            return None
        for hround in hround_list:
            context_round = deepcopy(context)
            cname = chinese_round_name[int(hround.key)]  # 输出二、三...
            so_dut: Dut = hround.rdField.filter(type='SO').first()
            if not so_dut:
                return ChenResponse(code=400, status=400, message=f'您第{cname}轮次中缺少源代码被测件，请添加')
            xq_dut: Dut = hround.rdField.filter(type='XQ').first()
            # 处理代码版本
            last_round_key = str(int(hround.key) - 1)
            last_round: Round = project_obj.pField.filter(key=last_round_key).first()
            last_round_so_dut = last_round.rdField.filter(type='SO').first()
            if not last_round_so_dut:
                return ChenResponse(code=400, status=400,
                                    message=f'您第{chinese_round_name[int(hround.key)]}轮次中缺少源代码版本信息，请添加')
            last_dm_version = last_round_so_dut.version
            now_dm_version = so_dut.version
            # 如果存在这个轮次的需求文档，则查询上个版本
            last_xq_version = ""
            if xq_dut:
                last_xq_dut = last_round.rdField.filter(type='XQ').first()
                if not last_xq_dut:
                    return ChenResponse(code=400, status=400,
                                        message=f'您第{chinese_round_name[int(hround.key)]}轮次中缺少需求文档信息')
                last_xq_version = last_xq_dut.version
                # 如果当前轮次有需求文档的修改
                now_xq_version = xq_dut.version
                context_round['xq_str'] = f"，以及软件需求规格说明{now_xq_version}版本和{last_xq_version}版本"
            else:
                # 如果当前轮次没有需求文档则xq_str为空
                context_round['xq_str'] = ""

            context_round['so_str'] = f"被测软件代码{now_dm_version}版本和{last_dm_version}版本"
            save_path = Path.cwd() / 'media' / project_path_str / 'output_dir/hsm' / f"第{cname}轮软件更改部分.docx"
            doc.render(context_round)
            try:
                doc.save(save_path)
            except PermissionError:
                return ChenResponse(code=400, status=400, message='您打开了生成的文档，请关闭后重试')
        return ChenResponse(code=200, status=200, message='多轮回归文档概述生成完毕')

    @route.get("/create/hdemand", url_name="create-hdemand")
    @transaction.atomic
    def create_hdemand(self, id: int):
        """
            生成非第一轮的多个测试需求
        """
        project_path_str = project_path(id)
        tpl_path = Path.cwd() / 'media' / project_path_str / 'form_template/hsm' / '回归测试需求.docx'
        doc = DocxTemplate(tpl_path)
        project_obj = get_object_or_404(Project, id=id)
        # 非第一轮轮次对象
        hround_list: QuerySet = project_obj.pField.exclude(key='0')
        if len(hround_list) < 1:
            return None
        # 遍历非第一轮的轮次
        for hround in hround_list:
            cname = chinese_round_name[int(hround.key)]  # var：输出二、三字样
            # 先查询dict字典，查出总共有多少个testType
            test_type_len = Dict.objects.get(code='testType').dictItem.count()
            type_number_list = [i for i in range(1, test_type_len + 1)]
            list_list = [[] for j in range(1, test_type_len + 1)]
            # 获得本轮次所有testDemand
            testDemand_qs = hround.rtField.all()
            for demand in testDemand_qs:
                type_index = type_number_list.index(int(demand.testType))
                content_list = []
                for (index, content) in enumerate(demand.testQField.all()):
                    content_dict = {
                        "index": index + 1,
                        "rindex": str(index + 1).rjust(2, '0'),
                        "subName": content.subName,
                        # 修改遍历content下面的step，content变量是TestDemandContent表
                        "subStep": [
                            {'index': index + 1, 'operation': step_obj.operation, 'expect': step_obj.expect}
                            for (index, step_obj) in enumerate(content.testStepField.all())
                        ],
                    }
                    content_list.append(content_dict)
                testmethod_str = ''
                for dict_item_qs in Dict.objects.get(code="testMethod").dictItem.all():
                    for tm_item in demand.testMethod:
                        if tm_item == dict_item_qs.key:
                            testmethod_str += dict_item_qs.title + " "
                # 设计需求的描述，富文本
                parser = RichParser(demand.design.description)
                # 查询关联design以及普通design
                doc_list = [{'dut_name': demand.dut.name, 'design_chapter': demand.design.chapter,
                             'design_name': demand.design.name}]
                for relate_design in demand.otherDesign.all():
                    ddict = {'dut_name': relate_design.dut.name, 'design_chapter': relate_design.chapter,
                             'design_name': relate_design.name}
                    doc_list.append(ddict)
                # 组装单个测试项
                testdemand_dict = {
                    "name": demand.name,
                    "key": demand.key,
                    "ident": get_ident(demand),
                    "priority": get_str_dict(demand.priority, "priority"),
                    "doc_list": doc_list,
                    "design_description": parser.get_final_list(doc),
                    "test_demand_content": content_list,
                    "testMethod": testmethod_str,
                    "adequacy": demand.adequacy.replace("\n", "\a"),
                    "testDesciption": demand.testDesciption.replace("\n", "\a")  # 测试项描述
                }
                list_list[type_index].append(testdemand_dict)
            # 定义渲染context字典
            context = {
                "project_name": project_obj.name
            }
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
            save_path = Path.cwd() / 'media' / project_path_str / 'output_dir/hsm' / f"第{cname}轮回归测试需求.docx"
            doc.render(context)
            try:
                doc.save(save_path)
            except PermissionError:
                return ChenResponse(code=400, status=400, message='您打开了生成的文档，请关闭后重试')
        return ChenResponse(code=200, status=200, message='多轮回归测试需求生成完毕')

    @route.get("/create/caseListDesc", url_name="create-caseListDesc")
    @transaction.atomic
    def create_caseListDesc(self, id: int):
        """
            生成非第一轮的用例说明
        """
        project_path_str = project_path(id)
        tpl_path = Path.cwd() / 'media' / project_path_str / 'form_template/hsm' / '回归测试用例概述.docx'
        doc = DocxTemplate(tpl_path)
        project_obj = get_object_or_404(Project, id=id)
        # 非第一轮轮次对象
        hround_list: QuerySet = project_obj.pField.exclude(key='0')
        if len(hround_list) < 1:
            return None
        for hround in hround_list:
            # 先查询dict字典，查出总共有多少个testType
            test_type_len = Dict.objects.get(code='testType').dictItem.count()
            type_number_list = [i for i in range(1, test_type_len + 1)]
            list_list = [[] for j in range(1, test_type_len + 1)]
            cname = chinese_round_name[int(hround.key)]  # 输出二、三...
            testDemands = hround.rtField.all()
            for demand in testDemands:
                type_index = type_number_list.index(int(demand.testType))
                demand_ident = get_ident(demand)
                demand_dict = {
                    'name': demand.name,
                    'item': []
                }
                for case in demand.tcField.all():
                    case_dict = {
                        'name': case.name,
                        'ident': get_case_ident(demand_ident, case),
                        'summary': case.summarize,
                    }
                    demand_dict['item'].append(case_dict)
                list_list[type_index].append(demand_dict)
            # 定义渲染上下文
            context = {}
            output_list = []
            for (index, li) in enumerate(list_list):
                qs = Dict.objects.get(code="testType").dictItem.get(key=str(index + 1))
                sort = qs.sort
                table = {
                    "item": li,
                    "sort": sort
                }
                output_list.append(table)
            output_list = sorted(output_list, key=(lambda x: x["sort"]))
            context["data"] = output_list
            save_path = Path.cwd() / 'media' / project_path_str / 'output_dir/hsm' / f"第{cname}轮回归测试用例概述.docx"
            doc.render(context=context)
            try:
                doc.save(save_path)
            except PermissionError:
                return ChenResponse(code=400, status=400, message='您打开了生成的文档，请关闭后重试')
        return ChenResponse(code=200, status=200, message='多轮回归测试用例概述生成完毕')

    @route.get("/create/caseList", url_name="create-caseList")
    @transaction.atomic
    def create_caseList(self, id: int):
        """
            生成非第一轮的测试用例
        """
        project_path_str = project_path(id)
        tpl_path = Path.cwd() / 'media' / project_path_str / 'form_template/hsm' / '测试用例.docx'
        doc = DocxTemplate(tpl_path)
        project_obj = get_object_or_404(Project, id=id)
        # 非第一轮轮次对象
        hround_list: QuerySet = project_obj.pField.exclude(key='0')
        if len(hround_list) < 1:
            return None
        for hround in hround_list:
            cname = chinese_round_name[int(hround.key)]  # 输出二、三...
            # 先查询dict字典，查出总共有多少个testType
            test_type_len = Dict.objects.get(code='testType').dictItem.count()
            type_number_list = [i for i in range(1, test_type_len + 1)]
            list_list = [[] for j in range(1, test_type_len + 1)]
            demand_prefix = '3.1'
            testType_list, last_chapter_items = create_csx_chapter_dict(hround)
            testDemands = hround.rtField.all()
            # 首先轮询所有测试需求
            for demand in testDemands:
                type_index = type_number_list.index(int(demand.testType))
                demand_ident = get_ident(demand)
                # ~~~~~这里组装测试项~~~~~
                ## 确定测试需求章节号（后面可提取后进行复用）
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
                        desc_list = rich_parser.get_final_list(doc, img_size=70)
                        step_dict = {
                            'index': index,
                            'operation': desc_list,
                            'expect': one.expect,
                        }
                        step_list.append(step_dict)
                        index += 1

                    case_dict = {
                        'name': case.name,
                        'ident': get_case_ident(demand_ident, case),
                        'summary': case.summarize,
                        'initialization': case.initialization,
                        'premise': case.premise,
                        'design_person': case.designPerson,
                        'step': step_list
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
            context["round_han"] = cname
            save_path = Path.cwd() / 'media' / project_path_str / 'output_dir/hsm' / f"第{cname}轮测试用例.docx"
            doc.render(context=context)
            try:
                doc.save(save_path)
            except PermissionError:
                return ChenResponse(code=400, status=400, message='您打开了生成的文档，请关闭后重试')
        return ChenResponse(code=200, status=200, message='多轮测试用例生成完毕')

    @route.get("/create/track", url_name="create-track")
    @transaction.atomic
    def create_track(self, id: int):
        """
            生成非第一轮的用例追踪
        """
        project_path_str = project_path(id)
        project_obj = get_object_or_404(Project, id=id)
        # 非第一轮轮次对象
        hround_list: QuerySet = project_obj.pField.exclude(key='0')
        demand_prefix = '4.1'
        if len(hround_list) < 1:
            return
        for hround in hround_list:
            # 取出当前轮次key减1就是上一轮次
            cname = chinese_round_name[int(hround.key)]  # 输出二、三...
            design_list = []
            testType_list, last_chapter_items = create_csx_chapter_dict(hround)
            # 找出当前轮次被测件为'SO'的
            so_dut = hround.rdField.filter(type='SO').first()
            if not so_dut:
                return ChenResponse(code=400, status=400, message=f'第{cname}轮次无源代码被测件')
            so_designs = so_dut.rsField.filter()
            for design in so_designs:
                design_dict = {'name': design.name, 'chapter': design.chapter, 'test_demand': []}
                test_items = []
                test_items.extend(design.dtField.all())
                test_items.extend(design.odField.all())
                for test_item in test_items:
                    if test_item.testType in ['2', '3', '15', '8']:
                        design_dict.update({'name': "/", 'chapter': "/"})
                    reveal_ident = "_".join(
                        ["XQ", get_testType(test_item.testType, "testType"), test_item.ident])
                    # 查字典方式确认章节号最后一位
                    test_item_last_chapter = last_chapter_items[test_item.testType].index(test_item.key) + 1
                    test_chapter = ".".join([demand_prefix, str(testType_list.index(test_item.testType) + 1),
                                             str(test_item_last_chapter)])
                    test_item_dict = {'name': test_item.name, 'chapter': test_chapter, 'ident': reveal_ident,
                                      'case_list': []}
                    for case in test_item.tcField.all():
                        case_dict = {
                            'name': case.name,
                            'ident': get_case_ident(reveal_ident, case)
                        }
                        test_item_dict['case_list'].append(case_dict)
                    design_dict['test_demand'].append(test_item_dict)
                design_list.append(design_dict)
            # 找出当前轮次的被测件为'XQ'的第一个
            xq_dut = hround.rdField.filter(type='XQ').first()
            if not xq_dut:
                return ChenResponse(code=400, status=400,
                                    message=f'第{cname}轮次没有找到需求被测件，只有放在被测件为<需求>的设计需求、测试项、用例才会被追踪')
            xq_designs = xq_dut.rsField.all()
            for design in xq_designs:
                design_dict = {'name': design.name, 'chapter': design.chapter, 'test_demand': []}
                test_items = []
                test_items.extend(design.dtField.all())
                test_items.extend(design.odField.all())
                for test_item in test_items:
                    reveal_ident = "_".join(
                        ["XQ", get_testType(test_item.testType, "testType"), test_item.ident])
                    # 查字典方式确认章节号最后一位
                    test_item_last_chapter = last_chapter_items[test_item.testType].index(test_item.key) + 1
                    test_chapter = ".".join([demand_prefix, str(testType_list.index(test_item.testType) + 1),
                                             str(test_item_last_chapter)])
                    test_item_dict = {'name': test_item.name, 'chapter': test_chapter, 'ident': reveal_ident,
                                      'case_list': []}
                    for case in test_item.tcField.all():
                        case_dict = {
                            'name': case.name,
                            'ident': get_case_ident(reveal_ident, case)
                        }
                        test_item_dict['case_list'].append(case_dict)
                    design_dict['test_demand'].append(test_item_dict)
                design_list.append(design_dict)
            context = {
                'design_list': design_list,
            }

            # 手动渲染tpl生成文档
            input_file = Path.cwd() / 'media' / project_path_str / 'form_template' / 'hsm' / '用例追踪.docx'
            temporary_file = Path.cwd() / 'media' / project_path_str / 'form_template' / 'hsm' / 'temporary' / f'第{cname}轮用例追踪_temp.docx'
            out_put_file = Path.cwd() / 'media' / project_path_str / 'output_dir' / 'hsm' / f'第{cname}轮用例追踪.docx'
            doc = DocxTemplate(input_file)
            doc.render(context)
            doc.save(temporary_file)
            # 通过docx合并单元格
            if temporary_file.is_file():
                try:
                    docu = Document(temporary_file)
                    # 找到其中的表格
                    util.merge_all_cell(docu.tables[0])
                    # 储存到合适位置
                    docu.save(out_put_file)
                except PermissionError:
                    return ChenResponse(code=400, status=400, message='请检查文件是否打开，如果打开则关闭...')
            else:
                return ChenResponse(code=400, status=400, message='中间文档未找到，请检查你模版是否存在...')
        return ChenResponse(code=200, status=200, message='文档生成成功...')
