import json
import re
import docx
import base64

from docx.document import Document

from docx.text.paragraph import Paragraph
from docx.parts.image import ImagePart
from docx.table import _Cell, Table
from docx.oxml.table import CT_Tbl
from docx.oxml.text.paragraph import CT_P

from collections import OrderedDict

class DocxChapterExtractor(object):
    def __init__(self, docx_path):
        self.doc = docx.Document(docx_path)  # 解析文档

    def extract_chapter_info(self, text):
        """提取章节编号和标题"""
        pattern = r'^(\d+(?:\.\d+)*)\s+(.*?)(?:\s*\d+)?\s*$'
        match = re.match(pattern, text)
        chapter_num = None
        content = None
        if match:
            chapter_num = match.group(1)  # '4.1' or '4'
            content = match.group(2).strip()  # '外部接口需求'
        else:
            print(f"'{text}' no match")
        return chapter_num, content

    def if_valid_match(self, chaptera_name, text):
        pattern = r'^(\d+(?:\.\d+)*)\s+' + chaptera_name + r'(?:\s*\d+)?\s*$'
        return re.match(pattern, text) is not None

    def get_chapter_number(self, chapter_name):
        """获取目录结构"""
        directory = []
        chapter_num = ''
        flag = False
        for paragraph in self.doc.paragraphs:
            if self.if_valid_match(chapter_name, paragraph.text) and 'toc' in paragraph.style.name:
                chapter_num, content = self.extract_chapter_info(paragraph.text)
                directory.append((chapter_num, content))
                flag = True
                continue
            if flag and paragraph.text.startswith(chapter_num) and 'toc' in paragraph.style.name:
                num, content = self.extract_chapter_info(paragraph.text)
                directory.append((num, content))
        return directory

    def build_hierarchy(self, chapter_body_list):
        """将线性章节列表转换为嵌套结构"""
        hierarchy = {}
        path = []  # 当前路径栈，存储章节号的字符串部分（如 ["4", "2"]）
        for item in chapter_body_list:
            # 处理不同格式的输入数据
            if len(item) == 3:
                num, content, _ = item  # 忽略第三个元素
            elif len(item) == 2:
                num, content = item
            else:
                continue  # 跳过无效数据
            # 切割章节号为字符串列表（如 '4.2.1' -> ["4", "2", "1"]）
            parts = num.split('.')
            # 1. 回溯路径找到当前层级
            while len(path) >= len(parts):
                path.pop()
            # 2. 逐级构建或定位父节点
            current_level = hierarchy
            for i in range(len(path)):
                part = path[i]
                # 如果父节点不存在，自动创建占位节点
                if part not in current_level:
                    current_level[part] = {
                        "number": ".".join(parts[:i + 1]),
                        "title": "[未命名章节]",  # 占位节点标题
                        "children": {}
                    }
                current_level = current_level[part]["children"]
            # 3. 插入当前节点
            current_part = parts[len(path)]  # 当前层级的部分（如 "1"）
            if current_part not in current_level:
                current_level[current_part] = {
                    "number": num,
                    "title": content,
                    "children": {}
                }
            # 4. 更新路径栈
            path = parts.copy()
        return hierarchy

    def extract_title_ordinal(self, s):
        # 正则表达式匹配以括号结尾的字符串
        pattern = r'^(.*?)\s*[(（](.*?)[)）]$'
        match = re.match(pattern, s)
        if match:
            # 提取标题并去除前后空格
            title = match.group(1).strip()
            # 提取序号并去除前后空格
            ordinal = match.group(2).strip()
        else:
            title = s
            ordinal = None
        return title, ordinal

    def build_json_tree(self, chapter_body_list):
        """直接生成树形JSON结构"""
        root = {"number": "", "title": "ROOT", "content": "", "children": []}
        node_map = OrderedDict()
        node_map[""] = root  # 初始化根节点映射
        for item in chapter_body_list:
            # 处理不同格式的输入数据
            if len(item) == 3:
                num, chapter_name, chapter_content = item
                title, ordinal = self.extract_title_ordinal(chapter_name)
            elif len(item) == 2:
                num, chapter_name = item
                title, ordinal = self.extract_title_ordinal(chapter_name)
                chapter_content = ""
            else:
                continue  # 跳过无效数据
            parts = num.split('.')
            parent_node = root  # 始终从根节点开始查找父级
            for depth in range(len(parts)):
                current_num = ".".join(parts[:depth + 1])
                if current_num not in node_map:
                    new_node = {
                        "number": current_num,
                        "title": title if (depth == len(parts) - 1) else "[未命名章节]",
                        "ordinal": ordinal if (depth == len(parts) - 1) else "",
                        "content": chapter_content if (depth == len(parts) - 1) else "",
                        "children": []
                    }
                    parent_num = ".".join(parts[:depth])
                    parent_node = node_map[parent_num]
                    parent_node["children"].append(new_node)
                    node_map[current_num] = new_node
                parent_node = node_map[current_num]
            # 确保最终标题和内容正确
            node_map[num]["title"] = title
            node_map[num]["ordinal"] = ordinal
            node_map[num]["content"] = chapter_content
        return root["children"][0] if root["children"] else {}

    def is_image(self, graph: Paragraph, doc: Document):
        """判断段落是否图片"""
        images = graph._element.xpath('.//pic:pic')  # 获取所有图片
        for image in images:
            for img_id in image.xpath('.//a:blip/@r:embed'):  # 获取图片id
                part = doc.part.related_parts[img_id]  # 根据图片id获取对应的图片
                if isinstance(part, ImagePart):
                    return True
        return False

    def get_ImagePart(self, graph: Paragraph, doc: Document):  # 一行只能获取一个图片
        """获取图片字节流，类型为bytes"""
        images = graph._element.xpath('.//pic:pic')  # 获取所有图片
        for image in images:
            for img_id in image.xpath('.//a:blip/@r:embed'):  # 获取图片id
                part = doc.part.related_parts[img_id]  # 根据图片id获取对应的图片
                if isinstance(part, ImagePart):
                    return part.blob
        return None

    def iter_block_items(self, parent, directory):
        def custom_serializer(obj):
            if isinstance(obj, bytes):
                return {
                    '__type__': 'image',
                    'format': 'base64',
                    'data': base64.b64encode(obj).decode('utf-8')
                }
            return obj

        """
        根据目录匹配章节内容
        parent: docx解析内容, 传入self.doc
        directory: 章节目录结构，例如[('4', '工程需求'), ('4.1', '外部接口需求'),
         ('4.2', '功能需求'), ('4.2.1', '知识库大模型检索问答功能')]
        """
        if isinstance(parent, Document):
            parent_elm = parent.element.body
        elif isinstance(parent, _Cell):
            parent_elm = parent._tc
        else:
            raise ValueError("something's not right")
        i = 0
        body_list = []
        body = []
        flag = False  # 判断是否循环到章节标题
        for child in parent_elm.iterchildren():
            if isinstance(child, CT_P):
                paragraph = Paragraph(child, parent)
                if i < len(directory) - 1:
                    if paragraph.text == directory[i][1] and 'Heading' in paragraph.style.name:
                        flag = True
                        continue
                    if paragraph.text == directory[i + 1][1] and 'Heading' in paragraph.style.name:
                        # body_list.append(body)
                        new_tuple = directory[i] + (
                            json.dumps(
                                body,
                                default=custom_serializer,
                                ensure_ascii=False,
                            ),
                        )
                        body_list.append(new_tuple)
                        # print(new_tuple)
                        body = []
                        i += 1
                        continue
                    if flag:
                        if self.is_image(paragraph, parent):
                            body.append(self.get_ImagePart(paragraph, parent))

                        elif paragraph.text != '':
                            body.append(paragraph.text)
                elif i == len(directory) - 1:
                    if 'Heading' in paragraph.style.name:
                        new_tuple = directory[i] + (
                            json.dumps(
                                body,
                                default=custom_serializer,
                                ensure_ascii=False,
                            ),
                        )
                        body_list.append(new_tuple)
                        break
                    if self.is_image(paragraph, parent):
                        body.append(self.get_ImagePart(paragraph, parent))
                    elif paragraph.text != '':
                        body.append(paragraph.text)
                    # print(body_list)
                    # print(paragraph.text, '--------------->', paragraph.style.name)
                else:
                    flag = False
            elif isinstance(child, CT_Tbl):
                if flag:
                    table = []
                    for row in Table(child, parent).rows:
                        # 获取每行的单元格文本
                        row_text = [cell.text for cell in row.cells]
                        # 用制表符或其他分隔符连接单元格内容
                        table.append("\t".join(row_text))
                    body.append(table)
        return body_list

    def main(self, chapter_name):
        directory = self.get_chapter_number(chapter_name)
        # print(directory)
        chapter_body_list = self.iter_block_items(self.doc, directory)
        # print(chapter_body_list)
        # 构建层级结构
        # hierarchy = self.build_hierarchy(chapter_body_list)
        # print(hierarchy)
        json_tree = self.build_json_tree(chapter_body_list)
        return json_tree

if __name__ == '__main__':
    docx_path = 'test - 副本.docx'
    extractor = DocxChapterExtractor(docx_path)
    extractor.main('工程需求')
