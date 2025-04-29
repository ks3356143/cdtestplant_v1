# 导入内置模块
from pathlib import Path
# 导入django、ninja等模块
from ninja_extra import api_controller, ControllerBase, route
from django.db import transaction
from django.shortcuts import get_object_or_404
# 导入文档处理模块
from docxtpl import DocxTemplate, InlineImage
# 导入ORM模型
from apps.project.models import Project
# 导入工具
from utils.util import get_str_abbr, get_str_dict
from utils.chen_response import ChenResponse
from utils.path_utils import project_path
from apps.createDocument.extensions.parse_rich_text import RichParser
# 导入生成日志记录模块
from apps.createSeiTaiDocument.extensions.logger import GenerateLogger

gloger = GenerateLogger("问题单二段文档")

# @api_controller("/generateWtd", tags=['生成问题单文档系列'], auth=JWTAuth(), permissions=[IsAuthenticated])
@api_controller('/generateWtd', tags=['生成问题单文档系列'])
class GenerateControllerWtd(ControllerBase):
    @route.get("/create/problem", url_name="create-problem")
    @transaction.atomic
    def create_problem(self, id: int):
        """生成问题单"""
        project_path_str = project_path(id)
        tpl_path = Path.cwd() / 'media' / project_path_str / 'form_template/wtd' / '问题详情表.docx'
        doc = DocxTemplate(tpl_path)
        project_obj = get_object_or_404(Project, id=id)
        problem_list = list(project_obj.projField.distinct())  # 去掉重复，因为和case是多对多
        problem_list.sort(key=lambda x: int(x.ident))
        data_list = []
        for problem in problem_list:
            problem_dict = {'ident': problem.ident, 'name': problem.name}
            # 1.生成被测对象名称、被测对象标识、被测对象版本
            cases = problem.case.all()
            # generate_log:无关联问题单进入生成日志
            if cases.count() < 1:
                gloger.write_warning_log('单个问题单表格', f'问题单{problem.ident}未关联用例，请检查')
            str_dut_name_list = []
            str_dut_ident_list = []
            str_dut_version_list = []
            # 2.所属用例标识
            case_ident_list = []
            # 3.获取依据要求
            case_design_list = []
            for case in cases:
                if case.test.testType == '8':
                    # 1.1.如果为文档审查，提取所属文档名称、文档被测件标识、文档被测件版本
                    str_dut_name_list.append(case.dut.name)
                    str_dut_ident_list.append(case.dut.ref)
                    str_dut_version_list.append(case.dut.version)
                    # 对应dut名称，design章节号，design描述
                    case_design_list.append("".join([case.dut.name, case.design.chapter]))
                else:
                    # 1.2.如果不为文档审查，则提取该轮次源代码dut的信息
                    so_dut = case.round.rdField.filter(type='SO').first()
                    if so_dut:
                        str_dut_name_list.append(project_obj.name + '软件')
                        str_dut_ident_list.append(so_dut.ref)
                        str_dut_version_list.append(so_dut.version)
                        # TODO:如何处理设计需求的内容，暂时设置为取出图片，只保留文字
                        p_list = []
                        rich_parse_remove_img = RichParser(case.design.description)
                        rich_list = rich_parse_remove_img.get_final_list(doc)
                        for rich in rich_list:
                            if isinstance(rich, dict) or isinstance(rich, InlineImage):
                                continue
                            else:
                                p_list.append(rich)

                        case_design_list.append(
                            "-".join([case.dut.name, case.design.chapter + '章节' + ":" + ''.join(p_list)]))
                # 2.用例标识修改-YL_测试项类型_测试项标识_用例key+1
                demand = case.test  # 中间变量
                demand_testType = demand.testType  # 中间变量
                testType_abbr = get_str_abbr(demand_testType, 'testType')  # 输出FT
                case_ident_list.append("_".join(
                    ['YL', testType_abbr, demand.ident, str(int(case.key[-1]) + 1).rjust(3, '0')]))
            problem_dict['duts_name'] = "/".join(set(str_dut_name_list))
            problem_dict['duts_ref'] = "/".join(set(str_dut_ident_list))
            problem_dict['duts_version'] = "/".join(set(str_dut_version_list))
            temp_name_version = []
            for i in range(len(str_dut_name_list)):
                temp_name_version.append(
                    "".join([str_dut_name_list[i] + str_dut_ident_list[i], '/V', str_dut_version_list[i]]))
            problem_dict['dut_name_version'] = "\a".join(temp_name_version)
            problem_dict['case_ident'] = "，".join(set(case_ident_list))
            problem_dict['type'] = get_str_dict(problem.type, 'problemType')
            problem_dict['grade'] = get_str_dict(problem.grade, 'problemGrade')

            # 依据要求-获取其设计需求
            problem_dict['yaoqiu'] = "\a".join(case_design_list)
            # 问题操作 - HTML解析
            desc_list = ['【问题操作】']
            rich_parser = RichParser(problem.operation)
            desc_list.extend(rich_parser.get_final_list(doc))

            # 问题影响
            desc_list_result = [f'\a【问题影响】\a{problem.result}']
            desc_list.extend(desc_list_result)
            # 问题描述赋值
            problem_dict['desc'] = desc_list

            # 4.原因分析
            desc_list_3 = [f'【原因分析】\a{problem.analysis}']
            problem_dict['cause'] = desc_list_3

            # 5.影响域分析~~~~
            desc_list_4 = [f'【影响域分析】\a{problem.effect_scope}']
            problem_dict['effect_scope'] = desc_list_4

            # 6.改正措施
            problem_dict['solve'] = problem.solve

            # 7.回归验证结果
            desc_list_5 = []
            rich_parser5 = RichParser(problem.verify_result)
            desc_list_5.extend(rich_parser5.get_final_list(doc))
            problem_dict['verify_result'] = desc_list_5

            # 8.其他日期和人员
            problem_dict['postPerson'] = problem.postPerson
            problem_dict['postDate'] = problem.postDate
            close_str = '□修改文档        □修改程序        □不修改'
            if len(problem.closeMethod) < 1:
                close_str = '□修改文档        □修改程序        ■不修改'
            elif len(problem.closeMethod) == 2:
                close_str = '■修改文档        ■修改程序        □不修改'
            else:
                if problem.closeMethod[0] == '1':
                    close_str = '■修改文档        □修改程序        □不修改'
                elif problem.closeMethod[0] == '2':
                    close_str = '□修改文档        ■修改程序        □不修改'
                else:
                    close_str = '□修改文档        □修改程序        □不修改'
            problem_dict['closeMethod'] = close_str
            problem_dict['designer'] = problem.designerPerson
            problem_dict['designDate'] = problem.designDate
            problem_dict['verifyPerson'] = problem.verifyPerson
            problem_dict['verifyDate'] = problem.verifyDate
            data_list.append(problem_dict)
        context = {
            'project_name': project_obj.name,
            'project_ident': project_obj.ident,
            'problem_list': data_list,
        }
        doc.render(context)
        try:
            doc.save(Path.cwd() / "media" / project_path_str / "output_dir/wtd" / '问题详情表.docx')
            return ChenResponse(status=200, code=200, message="文档生成成功！")
        except PermissionError as e:
            return ChenResponse(status=400, code=400, message="模版文件已打开，请关闭后再试，{0}".format(e))
