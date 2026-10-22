from pathlib import Path
from docxtpl import DocxTemplate
from docx.table import Table
from ninja.errors import HttpError
from utils.chen_response import ChenResponse
from typing import Any
from apps.project.models import Project
from apps.dict.models import DictItem
from utils.path_utils import project_path

def merge_all_cell(table: Table) -> None:
    """生成需求研总对照表工具：逐个找第二列和第三列单元格的text，如果一致则合并"""
    col_list = [table.columns[1], table.columns[2]]
    # 合并第二列相同的单元格
    for col_right in col_list:
        index = 0
        temp_text = ""
        for cell in col_right.cells:
            if index == 0:
                temp_text = cell.text
            else:
                if cell.text == temp_text:
                    if cell.text == '':  # 不知道什么原因必须这样判断下
                        cell.text = '/'
                    text_temp = cell.text
                    ce = cell.merge(col_right.cells[index - 1])
                    ce.text = text_temp
                else:
                    temp_text = cell.text
            index += 1

def _create_docx(template_name: str, context: dict, id: int, form_sub: str, output_sub: str) -> ChenResponse:
    """统一文档生成：从 form_template/<form_sub>/ 读取模版，渲染后保存到 <output_sub>/"""
    input_path = Path.cwd() / 'media' / project_path(id) / 'form_template' / form_sub / template_name
    doc = DocxTemplate(input_path)
    doc.render(context, autoescape=True)
    try:
        doc.save(Path.cwd() / "media" / project_path(id) / output_sub / template_name)
        return ChenResponse(status=200, code=200, message="文档生成成功！")
    except PermissionError as e:
        return ChenResponse(status=400, code=400, message="模版文件已打开，请关闭后再试，{0}".format(e))

def create_sm_docx(template_name: str, context: dict, id: int) -> ChenResponse:
    """生成最终说明文档工具函数"""
    return _create_docx(template_name, context, id, 'sm', 'output_dir/sm')

def create_dg_docx(template_name: str, context: dict, id: int) -> ChenResponse:
    """生成最终大纲文档工具函数"""
    return _create_docx(template_name, context, id, 'dg', 'output_dir')

def create_bg_docx(template_name: str, context: dict, id: int) -> ChenResponse:
    """生成最终报告文档工具函数"""
    return _create_docx(template_name, context, id, 'bg', 'output_dir/bg')

def build_testtype_output(list_list: list, *, include_type: bool = True) -> list:
    """
    把“按 testType 分组”的 list_list 组装成模版渲染用的 output_list，并按 sort 排序。
    一次性取出 testType 字典项，避免在循环内逐个查库（原实现的 N+1）。
    include_type：部分文档（如用例概述）不需要 type 字段，可通过该开关控制。
    """
    dict_items = {item.key: item for item in DictItem.objects.filter(dict__code='testType')}
    output_list = []
    for index, li in enumerate(list_list):
        # 字典项可能被禁用/删除，缺失时跳过该组，避免 KeyError 使整份文档生成失败
        item = dict_items.get(str(index + 1))
        if item is None:
            continue
        if include_type:
            output_list.append({"type": item.title, "item": li, "sort": item.sort})
        else:
            output_list.append({"item": li, "sort": item.sort})
    return sorted(output_list, key=lambda x: x["sort"])

def require_project_begin_time(project: Project):
    """
    取项目开始时间（各文档中的“被测件接收时间”）。
    该字段允许为空；未填写时给出明确业务提示，避免 None.strftime / None.year 直接抛 500。
    """
    if not project.beginTime:
        raise HttpError(400, '项目开始时间（被测件接收时间）未填写，请在项目设置中补充后再生成')
    return project.beginTime


def get_round1_problem(project: Project) -> Any:
    """
    从项目返回第一轮问题单
    :param project: Project项目Model对象
    :return: 问题单的列表
    """
    all_problem_qs = project.projField.all()
    # 遍历每个问题，找出第一轮的问题
    problem_set = set()
    for problem in all_problem_qs:
        flag = False
        for case in problem.case.all():
            if case.round.key == '0':
                flag = True
        if flag:
            problem_set.add(problem)
    return list(problem_set)

def delete_dir_files(path: Path) -> Any:
    """传入一个Path对象，如果是文件夹则删除里面所有的文件（不删除文件夹）"""
    if path.is_dir():
        for file in path.iterdir():
            if file.is_file():
                file.unlink()

