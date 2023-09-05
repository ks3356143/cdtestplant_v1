from apps.dict.models import Dict, DictItem
from html.parser import HTMLParser

#  传入一个字符串数字以及字典标志code，返回真实的title名字
def get_str_dict(a, dict_code):
    return DictItem.objects.get(dict__code=dict_code, key=a).title

def get_list_dict(item, dict_code):
    pass

# 简单HTML解析器 - 解析富文本的parser
from html.parser import HTMLParser

class MyHTMLParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.allStrList = []

    def error(self, message):
        print("HTML解析器出错，error信息为：", message)

    def handle_starttag(self, tag, attrs):
        if tag == 'img':
            img_base64 = attrs[0][1]
            self.allStrList.append(img_base64)

    def handle_data(self, data):
        if data != '\n':
            self.allStrList.append(data)

