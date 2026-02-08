"""
专门解析富文本插件tinymce的html内容
"""
import pandas as pd
from bs4 import BeautifulSoup
from bs4.element import Tag, NavigableString
import base64
import io
from docxtpl import InlineImage
from docx.shared import Mm
import re

# text.replace('\xa0', ' '))
class RichParser:
    def __init__(self, rich_text):
        # 将rich_text的None变为空字符串：鲁棒
        if rich_text is None:
            rich_text = ""
        # 对原始html解析后的bs对象
        self.bs = BeautifulSoup(rich_text, 'html.parser')
        self.content = self.remove_n_in_contents()
        # 最终的解析后的列表
        self.data_list = []
        self.line_parse()

    # 1.函数：将self.bs.contents去掉\n，获取每行数据
    def remove_n_in_contents(self):
        content_list = []
        for line in self.bs.contents:
            if line != '\n':
                content_list.append(line)
        return content_list

    # 2.逐个遍历self.content，去掉table元素Tag对象单独解析
    def line_parse(self):
        for tag in self.content:
            if isinstance(tag, NavigableString):
                self.data_list.append(tag.text)
            elif isinstance(tag, Tag):
                if tag.name == 'p':
                    img_list = tag.find_all('img')
                    if len(img_list) > 0:
                        for img_item in img_list:
                            self.data_list.append(img_item.get('src'))
                    else:
                        self.data_list.append(tag.text)
                elif tag.name == 'table':
                    df_dict_list = self.parse_tag2list(tag)
                    self.data_list.append(df_dict_list)
                elif tag.name == 'div':
                    table_list = tag.find_all('table')
                    if len(table_list) > 0:
                        for table in table_list:
                            df_dict_list = self.parse_tag2list(table)
                            self.data_list.append(df_dict_list)

    # 3.1.辅助方法，将<table>的Tag对象转为[[]]二维列表格式
    def parse_tag2list(self, table_tag):
        # str(tag)可直接变成<table>xxx</table>
        pd_list = pd.read_html(io.StringIO(str(table_tag)))
        # 将dataframe变为数组
        df = pd_list[0]
        # 处理第一行为数字的情况，如果为数字则删除第一行，让第二行为列名
        if all(isinstance(col, int) for col in df.columns):
            df.columns = df.iloc[0]
            df = df.drop(0)  # 删除原来的第一行
        # 转为列表的列表（二维列表）
        # return df.values.tolist()
        return df.fillna('').T.reset_index().T.values.tolist()

    # 3.2.辅助方法，打印解析后列表
    def print_content(self):
        for line in self.data_list:
            print(line)

    # 4.1.最终方法，生成给docxtpl可用的列表 -> 注意需要传递DocxTemplate对象，在接口函数里面初始化的
    def get_final_list(self, doc, /, *, img_size=100, height=80):
        """注意关键字传参可修改图片大小img_size:int=100"""
        final_list = []
        for oneline in self.data_list:
            # 这里要单独处理下二维列表
            if isinstance(oneline, list):
                final_list.append({'isTable': True, 'data': oneline})
                continue
            if oneline.startswith("data:image/png;base64") or oneline.startswith("data:image/jpeg;base64,") or oneline.startswith(
                    "data:image/jpg;base64,"):
                base64_bytes = base64.b64decode(oneline.replace("data:image/png;base64,", ""))
                # ~~~设置了固定宽度、高度~~~
                inline_image = InlineImage(doc, io.BytesIO(base64_bytes), width=Mm(img_size), height=Mm(height))
                final_list.append(inline_image)
            else:
                final_list.append(oneline)
        if len(final_list) <= 0:
            final_list.append("")
        # 针对tinymce中，粘贴表格最后一行显示句号问题，这里统一删除
        if final_list[-1] == '\xa0':
            final_list.pop()
        return final_list

    # 4.2.最终方法，在上面方法基础上，增加格式，例如<p>增加缩进，图片居中，<p>包含“图x”则居中
    def get_final_format_list(self, doc, /, *, img_size=115, height=80):
        final_list = []
        for oneline in self.data_list:
            # 这里要单独处理下二维列表
            if isinstance(oneline, list):
                final_list.append({'isTable': True, 'data': oneline})
                continue
            if oneline.startswith("data:image/png;base64"):
                base64_bytes = base64.b64decode(oneline.replace("data:image/png;base64,", ""))
                # 1.和上面函数变化：图片更改为dict然后isCenter属性居中
                final_list.append(
                    {'isCenter': True,
                     'data': InlineImage(doc, io.BytesIO(base64_bytes), width=Mm(img_size), height=height)})
            else:
                # 2.和上面区别：如果<p>带有“图”则居中
                if re.match(r"[表图]\d.*", oneline):
                    final_list.append({"isCenter": True, "data": oneline})
                else:
                    final_list.append({"isCenter": False, "data": oneline})
        if len(final_list) <= 0:
            final_list.append("")
        return final_list

    # 5.最终方法，去掉图片和table元素 -> 纯文本列表
    def get_final_p_list(self):
        final_list = []
        for oneline in self.data_list:
            if isinstance(oneline, list) or oneline.startswith("data:image/png;base64"):
                continue
            else:
                final_list.append(oneline)
        return final_list
