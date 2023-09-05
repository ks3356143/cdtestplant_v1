import base64
import io
from ninja_extra import ControllerBase, api_controller, route
from ninja_jwt.authentication import JWTAuth
from ninja_extra.permissions import IsAuthenticated
from django.db import transaction
from docxtpl import DocxTemplate, RichText, InlineImage
from docx.shared import Mm
from pathlib import Path
from utils.chen_response import ChenResponse
# 导入数据库ORM
from apps.project.models import TestDemand, TestDemandContent
from apps.dict.models import Dict, DictItem
# 导入工具函数
from utils.util import get_str_dict
from utils.util import MyHTMLParser

@api_controller("/generate", tags=['生成文档'], auth=JWTAuth(), permissions=[IsAuthenticated])
class GenerateController(ControllerBase):
    @route.get("/create/testdemand", url_name="create-testdemand")
    @transaction.atomic
    def create_testdeman(self):
        tplTestDemandGenerate_path = Path.cwd() / "media" / "form_template" / "dg" / "测试项及方法.docx"
        doc = DocxTemplate(tplTestDemandGenerate_path)
        # 先查询dict字典，查出总共有多少个testType
        test_type_len = Dict.objects.get(code='testType').dictItem.count()
        type_number_list = [i for i in range(1, test_type_len + 1)]
        list_list = [[] for j in range(1, test_type_len + 1)]
        # 查出所有testdemand
        testDemand_qs = TestDemand.objects.all()
        for single_qs in testDemand_qs:
            type_index = type_number_list.index(int(single_qs.testType))
            # 先查询其testDemandContent信息
            content_list = []
            for (index, content) in enumerate(single_qs.testQField.all()):
                content_dict = {
                    "index": index + 1,
                    "testXuQiu": content.testXuQiu,
                    "testYuQi": content.testYuQi
                }
                content_list.append(content_dict)
            # 查询测试项中testMethod
            testmethod_str = ''
            for dict_item_qs in Dict.objects.get(code="testMethod").dictItem.all():
                for tm_item in single_qs.testMethod:
                    if tm_item == dict_item_qs.key:
                        testmethod_str += dict_item_qs.title + " "
            # 解析富文本HTML
            parser = MyHTMLParser()
            parser.feed(single_qs.design.description)
            desc_list = []
            for strOrList in parser.allStrList:
                if strOrList.startswith("data:image/png;base64"):
                    base64_bytes = base64.b64decode(strOrList.replace("data:image/png;base64,", ""))
                    # ~~~设置了固定宽度~~~
                    desc_list.append(InlineImage(doc, io.BytesIO(base64_bytes), width=Mm(115)))
                else:
                    desc_list.append(strOrList)

            # 组装单个测试项
            testdemand_dict = {
                "name": single_qs.name,
                "ident": single_qs.ident,
                "priority": get_str_dict(single_qs.priority, "priority"),
                "dut_name": single_qs.dut.name,
                "design_chapter": single_qs.design.chapter,
                "design_name": single_qs.design.name,
                "design_description": desc_list,
                "test_demand_content": content_list,
                "testMethod": testmethod_str,
                "adequacy": single_qs.adequacy.replace("\n", "\a"),
                "termination": single_qs.termination.replace("\n", "\a"),
                "premise": single_qs.premise.replace("\n", "\a"),
            }
            list_list[type_index].append(testdemand_dict)

        # 定义渲染context字典
        context = {
            "project_name": "测试项目!!!!"
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

        # 测试
        # print(context)

        doc.render(context)
        try:
            doc.save(Path.cwd() / "media/output_dir" / "测试项及方法.docx")
        except PermissionError as e:
            return ChenResponse(status=400, code=400, message="模版文件已打开，请关闭后再试，{0}".format(e))
