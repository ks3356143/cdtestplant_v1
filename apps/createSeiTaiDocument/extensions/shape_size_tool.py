from docx.oxml.ns import qn  # qn作用是元素的.tag属性，自动帮你处理namespace
from docx.shape import InlineShape
from apps.createSeiTaiDocument.docXmlUtils import (
    Demand_table_xqms,
    Timing_diagram_width,
    Test_result_width,
    Horizatal_width
)

def set_shape_size(shape: InlineShape):
    """调用下面辅助函数，判断字典{'in_table': True, 'row_idx': 10, 'col_idx': 3}来设置大小"""
    shape_location = get_shape_location(shape)
    # 先判断是否在table中
    if shape_location['in_table']:
        # 在table中看是否是第一列，第一列则是时序图
        if shape_location['col_idx'] == 0:
            # 在第一列：说明是时序图
            shape.width = Timing_diagram_width
        else:
            shape.width = Test_result_width
    else:
        shape.width = Horizatal_width

def get_shape_location(shape: InlineShape):
    """传入图片直接处理，注意是python-docx库，不是docxtpl"""
    # 获取父元素链
    parent_chain = list(shape._inline.iterancestors())
    # 检查是否在表格中
    for elem in parent_chain:
        if elem.tag == qn("w:tbl"):
            # 获取表格对象
            tbl = elem
            # 获取行对象并计算行索引
            tr = next(e for e in parent_chain if e.tag == qn('w:tr'))
            row_idx = tbl.index(tr)
            # 获取单元格对象并计算列索引
            tc = next(e for e in parent_chain if e.tag == qn('w:tc'))
            col_idx = tr.index(tc)
            return {
                'in_table': True,
                'row_idx': row_idx,
                'col_idx': col_idx
            }
    return {'in_table': False}
