from apps.project.models import TestDemand
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.table import _Cell, Table

def demand_sort_by_designKey(demand_obj: TestDemand) -> tuple[int, ...]:
    """仅限于测试项排序函数，传入sorted函数的key里面"""
    parts = demand_obj.key.split('-')
    sort_tuple = tuple(int(part) for part in parts)
    return sort_tuple

# 传入cell设置边框
def set_cell_border(cell: _Cell, **kwargs):
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()

    # 检查标签是否存在，如果没有找到，则创建一个
    tcBorders = tcPr.first_child_found_in("w:tcBorders")
    if tcBorders is None:
        tcBorders = OxmlElement('w:tcBorders')
        tcPr.append(tcBorders)

    for border_type in ['left', 'top', 'right', 'bottom']:
        # 设置为固定的“黑色加粗”
        border_data = kwargs.get(border_type, {"sz": "6", "val": "single", "color": "#000000", "space": "0"})
        tag = 'w:{}'.format(border_type)
        element = tcBorders.find(qn(tag))
        if element is None:
            element = OxmlElement(tag)
            tcBorders.append(element)
        for key in ["sz", "val", "color", "space", "shadow"]:
            if key in border_data:
                element.set(qn('w:{}'.format(key)), str(border_data[key]))

# 弃用，请使用下面函数
def set_table_border(table, **kwargs):
    """docx-设置表格上下左右边框"""
    # 获取或创建表格属性
    tbl_pr = table._tbl.tblPr

    # 查找并移除现有的边框设置
    existing_borders = tbl_pr.find(qn('w:tblBorders'))
    if existing_borders is not None:
        tbl_pr.remove(existing_borders)

    # 创建新的边框元素
    borders = OxmlElement('w:tblBorders')

    # 只设置外边框：top, left, bottom, right - 设置为固定“黑色加粗”
    # 不设置 insideV 和 insideH（内部边框）
    for border_type in ['top', 'left', 'bottom', 'right']:
        border_data = kwargs.get(border_type, {"sz": "12", "val": "single", "color": "#000000"})
        border_elem = OxmlElement(f'w:{border_type}')

        # 设置边框属性
        border_elem.set(qn('w:val'), border_data.get('val', 'single'))  # 线条类型
        border_elem.set(qn('w:sz'), border_data.get('sz', '12'))  # 线条粗细（8代表1磅）
        border_elem.set(qn('w:color'), border_data.get('color', '#000000'))  # 颜色
        borders.append(border_elem)  # type:ignore

    # 将边框设置添加到表格属性中
    tbl_pr.append(borders)

# ~~~新解决方案：传入table对象，遍历cell，判断cell是否在外层~~~
def set_table_border_by_cell_position(table: Table):
    """
    智能设置表格边框：外边框粗，内边框细。
    """
    # 获取表格的总行数和总列数
    total_rows = len(table.rows)
    total_cols = len(table.columns)

    for row_idx, row in enumerate(table.rows):
        for col_idx, cell in enumerate(row.cells):
            # 初始化边框参数字典
            border_kwargs = {}

            # 1. 判断上边框：如果是第一行，则设置粗上边框，否则不设置（由上一行的下边框决定，或单独设置细线）
            if row_idx == 0:
                border_kwargs['top'] = {"sz": "12", "val": "single", "color": "#000000"}
            # 2. 判断下边框：如果是最后一行，则设置粗下边框
            if row_idx == total_rows - 1:
                border_kwargs['bottom'] = {"sz": "12", "val": "single", "color": "#000000"}
            # 3. 判断左边框：如果是第一列，则设置粗左边框
            if col_idx == 0:
                border_kwargs['left'] = {"sz": "12", "val": "single", "color": "#000000"}
            # 4. 判断右边框：如果是最后一列，则设置粗右边框
            if col_idx == total_cols - 1:
                border_kwargs['right'] = {"sz": "12", "val": "single", "color": "#000000"}

            # 5. 设置内部网格线（细线）
            # 内部横线 (insideH): 所有单元格都需要，但最后一行不需要（已经是外边框）
            if row_idx < total_rows - 1:
                border_kwargs['insideH'] = {"sz": "6", "val": "single", "color": "#000000"}
            # 内部竖线 (insideV): 所有单元格都需要，但最后一列不需要（已经是外边框）
            if col_idx < total_cols - 1:
                border_kwargs['insideV'] = {"sz": "6", "val": "single", "color": "#000000"}

            # 调用您已有的 set_cell_border 函数
            set_cell_border(cell, **border_kwargs)

# 设置cell的左右边距
def set_cell_margins(cell: _Cell, **kwargs):
    """
    设置单元格边距，确保在Office和WPS中均能生效。
    参数示例: set_cell_margins(cell, left=50, right=50, top=100, bottom=100)
    参数单位: 为二十分之一磅 (dxa, 1/1440英寸)。
    """
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()

    # 关键步骤1：检查或创建 w:tcMar 元素
    tcMar = tcPr.find(qn('w:tcMar'))
    if tcMar is None:
        tcMar = OxmlElement('w:tcMar')
        tcPr.append(tcMar)

    # 关键步骤2：为每个指定的边距方向创建元素，并同时设置新旧两套属性以保证兼容性[2](@ref)
    # 定义映射：我们的参数名 -> (XML元素名, 备用的XML元素名)
    margin_map = {
        'left': ('left', 'start'),
        'right': ('right', 'end'),
        'top': ('top', None),
        'bottom': ('bottom', None)
    }

    for margin_key, value in kwargs.items():
        if margin_key in margin_map:
            primary_tag, alternate_tag = margin_map[margin_key]
            tags_to_set = [primary_tag]
            if alternate_tag:  # 如果存在备选标签（如left/start），则同时设置
                tags_to_set.append(alternate_tag)

            for tag in tags_to_set:
                # 检查该边距元素是否已存在
                margin_element = tcMar.find(qn(f'w:{tag}'))
                if margin_element is None:
                    margin_element = OxmlElement(f'w:{tag}')
                    tcMar.append(margin_element) # type:ignore
                # 设置边距值和单位类型
                margin_element.set(qn('w:w'), str(value))
                margin_element.set(qn('w:type'), 'dxa')
