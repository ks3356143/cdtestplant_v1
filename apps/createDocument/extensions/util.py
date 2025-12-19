from pathlib import Path
from docxtpl import DocxTemplate
from docx.table import Table
from utils.chen_response import ChenResponse
from typing import Any
from apps.project.models import Project
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

def create_sm_docx(template_name: str, context: dict, id: int) -> ChenResponse:
    """生成最终说明文档工具函数"""
    input_path = Path.cwd() / 'media' / project_path(id) / 'form_template' / 'sm' / template_name
    doc = DocxTemplate(input_path)
    doc.render(context, autoescape=True)
    try:
        doc.save(Path.cwd() / "media" / project_path(id) / "output_dir/sm" / template_name)
        return ChenResponse(status=200, code=200, message="文档生成成功！")
    except PermissionError as e:
        return ChenResponse(status=400, code=400, message="模版文件已打开，请关闭后再试，{0}".format(e))

def create_dg_docx(template_name: str, context: dict, id: int) -> ChenResponse:
    """生成最终大纲文档工具函数"""
    input_path = Path.cwd() / 'media' / project_path(id) / 'form_template' / 'dg' / template_name
    doc = DocxTemplate(input_path)
    doc.render(context, autoescape=True)
    try:
        doc.save(Path.cwd() / "media" / project_path(id) / "output_dir" / template_name)
        return ChenResponse(status=200, code=200, message="文档生成成功！")
    except PermissionError as e:
        return ChenResponse(status=400, code=400, message="模版文件已打开，请关闭后再试，{0}".format(e))

def create_bg_docx(template_name: str, context: dict, id: int) -> ChenResponse:
    """生成最终报告文档工具函数"""
    input_path = Path.cwd() / 'media' / project_path(id) / 'form_template' / 'bg' / template_name
    doc = DocxTemplate(input_path)
    doc.render(context, autoescape=True)
    try:
        doc.save(Path.cwd() / "media" / project_path(id) / "output_dir/bg" / template_name)
        return ChenResponse(status=200, code=200, message="文档生成成功！")
    except PermissionError as e:
        return ChenResponse(status=400, code=400, message="模版文件已打开，请关闭后再试，{0}".format(e))

def create_wtd_docx(template_name: str, context: dict, id: int) -> ChenResponse:
    """生成最终问题单文档工具函数"""
    input_path = Path.cwd() / 'media' / project_path(id) / 'form_template' / 'wtd' / template_name
    doc = DocxTemplate(input_path)
    doc.render(context, autoescape=True)
    try:
        doc.save(Path.cwd() / "media" / project_path(id) / "output_dir/wtd" / template_name)
        return ChenResponse(status=200, code=200, message="文档生成成功！")
    except PermissionError as e:
        return ChenResponse(status=400, code=400, message="模版文件已打开，请关闭后再试，{0}".format(e))

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
