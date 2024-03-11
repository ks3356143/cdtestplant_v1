import base64
import io
from pathlib import Path
# 导入框架东西
from ninja_extra import ControllerBase, api_controller, route
# 框架组件
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.db.models import Q
# 认证和权限
from ninja_extra.permissions import IsAuthenticated
from ninja_jwt.authentication import JWTAuth
# 导入模型
from apps.project.models import Project
from apps.dict.models import Dict
# 导入文档处理类
from docxtpl import DocxTemplate
from docxtpl import InlineImage
from docx.shared import Mm
# 导入自己工具
from utils.chen_response import ChenResponse
from utils.util import get_ident, get_case_ident, get_testType
from utils.chapter_tools.csx_chapter import create_csx_chapter_dict
from utils.util import MyHTMLParser

# 工具函数 - 根据文档名称和context直接生成output_dir文档
def create_sm_docx(template_name: str, context: dict) -> ChenResponse:
    input_path = Path.cwd() / 'media' / 'form_template' / 'sm' / template_name
    doc = DocxTemplate(input_path)
    doc.render(context)
    try:
        doc.save(Path.cwd() / "media/output_dir/sm" / template_name)
        return ChenResponse(status=200, code=200, message="文档生成成功！")
    except PermissionError as e:
        return ChenResponse(status=400, code=400, message="模版文件已打开，请关闭后再试，{0}".format(e))

# @api_controller("/generateSM", tags=['生成说明文档系列'], auth=JWTAuth(), permissions=[IsAuthenticated])
@api_controller("/generateSM", tags=['生成说明文档系列'])
class GenerateControllerSM(ControllerBase):
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
        # 这里大纲版本升级如何处理 - TODO：1.大纲版本升级后版本处理 2.大纲时间如何处理？
        dg_duty = {'doc_name': doc_name, 'ident_version': f'PT-{project_obj.ident}-TO-1.00',
                   'publish_date': '2024-03-17', 'source': project_obj.test_unit}
        std_documents.append(dg_duty)
        # 生成二级文档
        context = {
            'std_documents': std_documents
        }
        return create_sm_docx("技术依据文件.docx", context)

    @route.get('/create/caseList', url_name='create-caseList')
    @transaction.atomic
    def create_caseList(self, id: int):
        """创建第一轮文档"""
        # 生成测试用例需要doc对象
        case_template_doc_path = Path.cwd() / 'media/form_template/sm' / '测试用例.docx'
        doc = DocxTemplate(case_template_doc_path)
        project_obj = get_object_or_404(Project, id=id)
        # 先查询dict字典，查出总共有多少个testType
        test_type_len = Dict.objects.get(code='testType').dictItem.count()
        type_number_list = [i for i in
                            range(1, test_type_len + 1)]  # [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
        list_list = [[] for j in
                     range(1, test_type_len + 1)]  # [[], [], [], [], [], [], [], [], [], [], [], [], [], [], [], []]
        # 先找到第一轮次
        project_round_one = project_obj.pField.filter(key=0).first()
        # 测试项的章节号预置处理
        demand_prefix = '6.2'
        testType_list, last_chapter_items = create_csx_chapter_dict(project_round_one)

        testDemands = project_round_one.rtField.all()
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
                    parser = MyHTMLParser()
                    parser.feed(one.operation)
                    desc_list = []
                    for strOrList in parser.allStrList:
                        if strOrList.startswith("data:image/png;base64"):
                            base64_bytes = base64.b64decode(strOrList.replace("data:image/png;base64,", ""))
                            # ~~~设置了固定宽度~~~
                            desc_list.append(InlineImage(doc, io.BytesIO(base64_bytes), width=Mm(115)))
                        else:
                            desc_list.append(strOrList)
                    step_dict = {
                        'index': index,
                        'operation': "\a".join(desc_list),
                        'expect': one.expect,
                    }
                    step_list.append(step_dict)

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
        doc.render(context)
        try:
            doc.save(Path.cwd() / "media/output_dir/sm" / "测试用例.docx")
            return ChenResponse(status=200, code=200, message="文档生成成功！")
        except PermissionError as e:
            return ChenResponse(status=400, code=400, message="模版文件已打开，请关闭后再试，{0}".format(e))

    @route.get('/create/caseBreifList', url_name='create-caseBreifList')
    @transaction.atomic
    def create_caseBreifList(self, id: int):
        # 生成第一轮的测试说明
        project_obj = get_object_or_404(Project, id=id)
        # 先查询dict字典，查出总共有多少个testType
        test_type_len = Dict.objects.get(code='testType').dictItem.count()
        type_number_list = [i for i in
                            range(1, test_type_len + 1)]  # [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
        list_list = [[] for j in
                     range(1, test_type_len + 1)]  # [[], [], [], [], [], [], [], [], [], [], [], [], [], [], [], []]
        # 先找到第一轮次
        project_round_one = project_obj.pField.filter(key=0).first()
        # 找到第一轮的全部测试项
        testDemands = project_round_one.rtField.all()
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
        return create_sm_docx("用例说明.docx", context)

    @route.get('/create/smtrack', url_name='create-smtrack')
    @transaction.atomic
    def create_smtrack(self, id: int):
        project_obj = get_object_or_404(Project, id=id)
        demand_prefix = '6.2'
        design_list = []
        project_round_one = project_obj.pField.filter(key=0).first()
        if project_round_one:
            testType_list, last_chapter_items = create_csx_chapter_dict(project_round_one)
            # 找出第一轮的被测件为'XQ'的第一个
            xq_dut = project_round_one.rdField.filter(type='XQ').first()
            if xq_dut:
                xq_designs = xq_dut.rsField.all()
                for design in xq_designs:
                    design_dict = {'name': design.name, 'chapter': design.chapter, 'test_demand': []}
                    # 获取一个design的所有测试项
                    test_items = design.dtField.all()
                    for test_item in test_items:
                        key_index = int(test_item.key.split("-")[-1]) + 1
                        test_index = str(key_index).rjust(3, '0')
                        reveal_ident = "_".join(
                            ["XQ", get_testType(test_item.testType, "testType"), test_item.ident, test_index])
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
                return create_sm_docx("说明追踪.docx", context)