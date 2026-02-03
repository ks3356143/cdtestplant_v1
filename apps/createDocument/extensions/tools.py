from apps.project.models import TestDemand
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

def demand_sort_by_designKey(demand_obj: TestDemand) -> tuple[int, ...]:
    """仅限于测试项排序函数，传入sorted函数的key里面"""
    parts = demand_obj.key.split('-')
    sort_tuple = tuple(int(part) for part in parts)
    return sort_tuple

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

    # 只设置外边框：top, left, bottom, right
    # 不设置 insideV 和 insideH（内部边框）
    for border_type in ['top', 'left', 'bottom', 'right']:
        border_data = kwargs.get(border_type, {"sz": "12", "val": "single", "color": "#000000"})
        border_elem = OxmlElement(f'w:{border_type}')

        # 设置边框属性
        border_elem.set(qn('w:val'), border_data.get('val', 'single'))  # 线条类型
        border_elem.set(qn('w:sz'), border_data.get('sz', '12'))  # 线条粗细（8代表1磅）
        border_elem.set(qn('w:color'), border_data.get('color', '#000000'))  # 颜色
        borders.append(border_elem) # type:ignore

    # 将边框设置添加到表格属性中
    tbl_pr.append(borders)

__all__ = ['demand_sort_by_designKey', 'set_table_border']
